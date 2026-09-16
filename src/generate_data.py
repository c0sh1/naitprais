"""
generate_data.py
----------------
Genera los datos SIMULADOS de Tabaiba Stays (cliente ficticio de NaitPrais)
y los carga en la base de datos data/naitprais.db.

Tablas que rellena: municipios, viviendas, reservas y calendario_precios.
La tabla mercado_istac se rellena con datos reales usando src/fetch_istac.py.

Cómo se simulan los datos (resumen):
- Cada vivienda tiene un "precio justo" de mercado que cambia cada mes y sube en
  fechas especiales (Navidad, Carnaval, Semana Santa).
- La gestora NO usa ese precio: aplica solo 3 tarifas al año (alta, media y baja),
  como explica la ficha del cliente.
- Si el precio publicado está por encima del precio justo, la vivienda se ocupa menos.
  Si está por debajo, se ocupa más y se reserva con más antelación.
- El patrón de meses (qué meses tienen más demanda) está calibrado con los ingresos
  reales de las viviendas vacacionales de Canarias en 2025 (ISTAC).

Uso:
    python src/generate_data.py
"""

import math
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

# ------------------------------------------------------------------
# Configuración general
# ------------------------------------------------------------------
SEMILLA = 42                      # misma semilla = mismos datos cada vez
FECHA_INICIO = date(2024, 1, 1)
FECHA_FIN = date(2026, 8, 31)     # último día con datos

RAIZ = Path(__file__).resolve().parent.parent
RUTA_DB = RAIZ / "data" / "naitprais.db"
RUTA_SCHEMA = RAIZ / "data" / "schema.sql"

random.seed(SEMILLA)

# ------------------------------------------------------------------
# Datos fijos
# ------------------------------------------------------------------
# (id, nombre, isla, código INE, factor de precio del municipio)
MUNICIPIOS = [
    (1, "Adeje", "Tenerife", "38001", 1.12),
    (2, "Arona", "Tenerife", "38006", 1.00),
    (3, "Puerto de la Cruz", "Tenerife", "38028", 0.85),
    (4, "San Bartolomé de Tirajana", "Gran Canaria", "35019", 1.08),
    (5, "Mogán", "Gran Canaria", "35013", 1.10),
]

# Viviendas activas por municipio (total 60) y viviendas que se dieron de baja
VIVIENDAS_ACTIVAS = {1: 20, 2: 16, 3: 8, 4: 10, 5: 6}
# (municipio, fecha en la que el propietario se marchó)
VIVIENDAS_BAJA = [
    (1, date(2025, 3, 31)),
    (1, date(2025, 6, 30)),
    (2, date(2025, 6, 30)),
    (4, date(2025, 10, 31)),
]
# Viviendas que entraron en la gestora durante 2024
FECHAS_ALTA_2024 = [date(2024, 3, 1), date(2024, 5, 1), date(2024, 9, 1), date(2024, 11, 1)]

# Índice de demanda por mes, calculado con los ingresos totales de las viviendas
# vacacionales de Canarias en 2025 (ISTAC, dataset C00065A_000061), divididos
# entre la media del año. 1 = mes normal.
INDICE_DEMANDA = {
    1: 1.18, 2: 1.11, 3: 1.14, 4: 0.95, 5: 0.72, 6: 0.74,
    7: 1.00, 8: 1.14, 9: 0.90, 10: 0.87, 11: 1.15, 12: 1.10,
}

# Tarifas de la gestora (ficha del cliente): solo 3 niveles al año
TARIFA_ALTA = 1.12    # noviembre a abril
TARIFA_MEDIA = 1.02   # julio y agosto
TARIFA_BAJA = 0.90    # mayo, junio, septiembre y octubre

# Subida anual del mercado frente a la subida que aplica la gestora
SUBIDA_MERCADO = {2024: 1.00, 2025: 1.07, 2026: 1.11}
SUBIDA_GESTORA = {2024: 1.00, 2025: 1.04, 2026: 1.07}

# Fechas con más demanda: (inicio, fin, subida del precio justo)
EVENTOS = [
    (date(2023, 12, 20), date(2024, 1, 6), 1.35),   # Navidad
    (date(2024, 2, 8), date(2024, 2, 18), 1.25),    # Carnaval
    (date(2024, 3, 23), date(2024, 3, 31), 1.20),   # Semana Santa
    (date(2024, 12, 20), date(2025, 1, 6), 1.35),
    (date(2025, 2, 27), date(2025, 3, 9), 1.25),
    (date(2025, 4, 12), date(2025, 4, 20), 1.20),
    (date(2025, 12, 20), date(2026, 1, 6), 1.35),
    (date(2026, 2, 12), date(2026, 2, 22), 1.25),
    (date(2026, 3, 28), date(2026, 4, 5), 1.20),
]

CANALES = [("Airbnb", 0.44), ("Booking", 0.34), ("Vrbo", 0.08), ("Web", 0.14)]

PAISES_INVIERNO = [
    ("Reino Unido", 0.28), ("Alemania", 0.14), ("España", 0.10), ("Países Bajos", 0.08),
    ("Suecia", 0.07), ("Bélgica", 0.06), ("Noruega", 0.05), ("Irlanda", 0.05),
    ("Italia", 0.05), ("Francia", 0.04), ("Otros", 0.08),
]
PAISES_VERANO = [
    ("España", 0.35), ("Reino Unido", 0.18), ("Italia", 0.10), ("Alemania", 0.07),
    ("Francia", 0.06), ("Países Bajos", 0.05), ("Irlanda", 0.05), ("Bélgica", 0.04),
    ("Otros", 0.10),
]


# ------------------------------------------------------------------
# Funciones de ayuda
# ------------------------------------------------------------------
def elegir(opciones):
    """Elige un valor de una lista [(valor, peso), ...]."""
    valores = [o[0] for o in opciones]
    pesos = [o[1] for o in opciones]
    return random.choices(valores, weights=pesos, k=1)[0]


def poisson(media):
    """Número aleatorio con distribución de Poisson (método de Knuth)."""
    limite = math.exp(-media)
    k, p = 0, 1.0
    while True:
        p *= random.random()
        if p <= limite:
            return k
        k += 1


def tarifa_gestora(mes):
    if mes in (11, 12, 1, 2, 3, 4):
        return TARIFA_ALTA
    if mes in (7, 8):
        return TARIFA_MEDIA
    return TARIFA_BAJA


def factor_evento(dia):
    for inicio, fin, factor in EVENTOS:
        if inicio <= dia <= fin:
            return factor
    return 1.0


def es_evento(dia):
    return factor_evento(dia) > 1.0


# ------------------------------------------------------------------
# 1. Viviendas
# ------------------------------------------------------------------
def crear_viviendas():
    """Devuelve una lista de diccionarios con las viviendas y sus fechas de gestión."""
    viviendas = []
    lista = [(m, None) for m, n in VIVIENDAS_ACTIVAS.items() for _ in range(n)]
    lista += [(m, fecha_baja) for m, fecha_baja in VIVIENDAS_BAJA]

    altas_2024 = list(FECHAS_ALTA_2024)
    registros_usados = set()
    for num, (id_municipio, fecha_baja) in enumerate(lista, start=1):
        municipio = MUNICIPIOS[id_municipio - 1]
        tipo = elegir([("apartamento", 0.70), ("casa", 0.20), ("villa", 0.10)])

        if tipo == "apartamento":
            plazas = random.choice([2, 2, 3, 4, 4])
            precio_base = 25 + 11 * plazas
            piscina = 1 if random.random() < 0.45 else 0   # piscina comunitaria
        elif tipo == "casa":
            plazas = random.choice([4, 5, 6, 6])
            precio_base = 32 + 12 * plazas
            piscina = 1 if random.random() < 0.50 else 0
        else:
            plazas = random.choice([6, 8, 8])
            precio_base = 50 + 16 * plazas
            piscina = 1 if random.random() < 0.90 else 0

        dormitorios = max(1, plazas // 2)
        vista_mar = 1 if random.random() < 0.40 else 0

        precio_base *= municipio[4]
        precio_base *= 1.12 if piscina else 1.0
        precio_base *= 1.10 if vista_mar else 1.0
        precio_base *= random.uniform(0.92, 1.08)
        calidad = random.uniform(0.90, 1.10)   # lo bien que se vende el anuncio

        # Fechas de gestión: algunas entran en 2024 y otras se dan de baja en 2025
        fecha_alta = FECHA_INICIO
        if fecha_baja is None and altas_2024 and random.random() < 0.10:
            fecha_alta = altas_2024.pop(0)
        fecha_fin = fecha_baja if fecha_baja else FECHA_FIN

        codigo_isla = "4" if municipio[2] == "Tenerife" else "1"
        numero = random.randint(1000, 99999)
        while numero in registros_usados:       # el número de registro no se puede repetir
            numero = random.randint(1000, 99999)
        registros_usados.add(numero)
        viviendas.append({
            "id": num,
            "id_municipio": id_municipio,
            "num_registro": f"VV-{municipio[3][:2]}-{codigo_isla}-{numero:07d}",
            "tipo": tipo,
            "plazas": plazas,
            "dormitorios": dormitorios,
            "piscina": piscina,
            "vista_mar": vista_mar,
            "activa": 0 if fecha_baja else 1,
            "precio_base": precio_base,
            "calidad": calidad,
            "desde": fecha_alta,
            "hasta": fecha_fin,
        })
    return viviendas


# ------------------------------------------------------------------
# 2. Precios de cada día
# ------------------------------------------------------------------
def precio_publicado(v, dia):
    """Precio que pone la gestora: 3 tarifas al año, redondeado a 5 €."""
    precio = v["precio_base"] * tarifa_gestora(dia.month) * SUBIDA_GESTORA[dia.year]
    return round(precio / 5) * 5


def precio_justo(v, dia):
    """Precio que pagaría el mercado ese día (la gestora no lo conoce)."""
    demanda = INDICE_DEMANDA[dia.month]
    precio = v["precio_base"] * demanda ** 0.6 * SUBIDA_MERCADO[dia.year]
    precio *= factor_evento(dia)
    # Las viviendas grandes tienen poca demanda en temporada baja
    if v["plazas"] >= 6 and dia.month in (5, 6, 9, 10):
        precio *= 0.85
    # Las pequeñas son muy buscadas en invierno (estancias largas de parejas)
    if v["plazas"] <= 3 and dia.month in (11, 12, 1, 2, 3):
        precio *= 1.10
    return precio


# ------------------------------------------------------------------
# 3. Reservas y calendario
# ------------------------------------------------------------------
def simular_vivienda(v, siguiente_id):
    """Simula día a día las reservas de una vivienda."""
    reservas = []
    ocupadas = set()
    precios = {}

    dia = v["desde"]
    while dia <= v["hasta"]:
        precios[dia] = precio_publicado(v, dia)
        dia += timedelta(days=1)

    dia = v["desde"]
    while dia < v["hasta"]:
        precio = precios[dia]
        ratio = precio / precio_justo(v, dia)          # >1 = caro, <1 = barato

        # Ocupación esperada según la demanda del mes y lo caro que esté
        ocupacion = 0.64 * INDICE_DEMANDA[dia.month] ** 0.5 * v["calidad"] * ratio ** -1.6
        ocupacion = min(max(ocupacion, 0.15), 0.96)

        invierno = dia.month in (11, 12, 1, 2, 3, 4)
        estancia_media = 10.0 if invierno else 7.0
        prob_inicio = ocupacion / (estancia_media * (1 - ocupacion))

        if random.random() >= prob_inicio:
            dia += timedelta(days=1)
            continue

        noches = max(2, 1 + poisson(estancia_media - 1))
        salida = dia + timedelta(days=noches)
        if salida > v["hasta"]:
            break

        # Antelación: más días cuanto más barata está la vivienda
        antelacion_media = 25 * (1 / ratio) ** 2 * (1.4 if invierno else 1.0)
        antelacion = int(random.expovariate(1 / antelacion_media))
        fecha_reserva = dia - timedelta(days=min(antelacion, 365))

        cancelada = random.random() < 0.07
        noches_estancia = [dia + timedelta(days=i) for i in range(noches)]
        precio_medio = sum(precios[n] for n in noches_estancia) / noches

        paises = PAISES_INVIERNO if dia.month not in (6, 7, 8, 9) else PAISES_VERANO
        num_huespedes = random.randint(max(1, v["plazas"] // 2), v["plazas"])

        # Reseña: el 62 % deja reseña; peor nota si la vivienda estaba cara
        puntuacion = None
        if not cancelada and random.random() < 0.62:
            pesos = [0.01, 0.02, 0.07, 0.28, 0.62]
            if ratio > 1.15:
                pesos = [0.03, 0.05, 0.15, 0.35, 0.42]
            puntuacion = random.choices([1, 2, 3, 4, 5], weights=pesos, k=1)[0]

        reservas.append((
            siguiente_id + len(reservas),
            v["id"],
            fecha_reserva.isoformat(),
            dia.isoformat(),
            salida.isoformat(),
            noches,
            num_huespedes,
            round(precio_medio, 2),
            elegir(CANALES),
            elegir(paises),
            puntuacion,
            "cancelada" if cancelada else "confirmada",
        ))

        if cancelada:
            dia += timedelta(days=1)     # las noches quedan libres
        else:
            ocupadas.update(noches_estancia)
            dia = salida

    calendario = [
        (v["id"], d.isoformat(), float(p), 1 if d in ocupadas else 0)
        for d, p in sorted(precios.items())
    ]
    return reservas, calendario


# ------------------------------------------------------------------
# Programa principal
# ------------------------------------------------------------------
def main():
    if RUTA_DB.exists():
        RUTA_DB.unlink()   # empezamos siempre desde cero

    con = sqlite3.connect(RUTA_DB)
    con.executescript(RUTA_SCHEMA.read_text(encoding="utf-8"))

    con.executemany(
        "INSERT INTO municipios VALUES (?, ?, ?, ?)",
        [m[:4] for m in MUNICIPIOS],
    )

    viviendas = crear_viviendas()
    con.executemany(
        "INSERT INTO viviendas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [(v["id"], v["id_municipio"], v["num_registro"], v["tipo"], v["plazas"],
          v["dormitorios"], v["piscina"], v["vista_mar"], v["activa"]) for v in viviendas],
    )

    total_reservas, total_calendario = 0, 0
    for v in viviendas:
        reservas, calendario = simular_vivienda(v, total_reservas + 1)
        con.executemany("INSERT INTO reservas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", reservas)
        con.executemany("INSERT INTO calendario_precios VALUES (?, ?, ?, ?)", calendario)
        total_reservas += len(reservas)
        total_calendario += len(calendario)

    con.commit()
    con.close()

    print(f"Base de datos creada en {RUTA_DB}")
    print(f"  municipios:          {len(MUNICIPIOS)}")
    print(f"  viviendas:           {len(viviendas)}")
    print(f"  reservas:            {total_reservas}")
    print(f"  calendario_precios:  {total_calendario}")


if __name__ == "__main__":
    main()
