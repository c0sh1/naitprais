"""
check_data.py
-------------
Comprueba que los datos de data/naitprais.db son coherentes y guarda un resumen
en data/resumen_datos.json.

Uso:
    python src/check_data.py
"""

import json
import sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTA_DB = RAIZ / "data" / "naitprais.db"
RUTA_RESUMEN = RAIZ / "data" / "resumen_datos.json"


def valor(con, sql):
    return con.execute(sql).fetchone()[0]


def comprobar(nombre, correcto, detalle=""):
    estado = "OK   " if correcto else "ERROR"
    print(f"  [{estado}] {nombre} {detalle}")
    return correcto


def main():
    con = sqlite3.connect(RUTA_DB)
    con.execute("PRAGMA foreign_keys = ON")

    # 1. Número de filas por tabla
    tablas = ["municipios", "viviendas", "reservas", "calendario_precios", "mercado_istac"]
    filas = {t: valor(con, f"SELECT COUNT(*) FROM {t}") for t in tablas}
    print("Filas por tabla:")
    for t, n in filas.items():
        print(f"  {t:<20} {n:>7}")

    # 2. Comprobaciones de coherencia
    print("\nComprobaciones:")
    resultados = []

    fk = con.execute("PRAGMA foreign_key_check").fetchall()
    resultados.append(comprobar("Claves foráneas correctas", len(fk) == 0))

    fechas_mal = valor(con, """
        SELECT COUNT(*) FROM reservas
        WHERE fecha_salida <= fecha_entrada
           OR fecha_reserva > fecha_entrada
           OR noches != julianday(fecha_salida) - julianday(fecha_entrada)
    """)
    resultados.append(comprobar("Fechas y noches de las reservas", fechas_mal == 0, f"({fechas_mal} errores)"))

    solapes = valor(con, """
        SELECT COUNT(*) FROM reservas a
        JOIN reservas b ON a.id_vivienda = b.id_vivienda AND a.id_reserva < b.id_reserva
        WHERE a.estado = 'confirmada' AND b.estado = 'confirmada'
          AND a.fecha_entrada < b.fecha_salida AND b.fecha_entrada < a.fecha_salida
    """)
    resultados.append(comprobar("Sin reservas solapadas en la misma vivienda", solapes == 0, f"({solapes} solapes)"))

    exceso = valor(con, """
        SELECT COUNT(*) FROM reservas r JOIN viviendas v USING (id_vivienda)
        WHERE r.num_huespedes > v.plazas
    """)
    resultados.append(comprobar("Huéspedes dentro de las plazas de cada vivienda", exceso == 0, f"({exceso} errores)"))

    noches_reservas = valor(con, "SELECT SUM(noches) FROM reservas WHERE estado = 'confirmada'")
    noches_calendario = valor(con, "SELECT SUM(ocupada) FROM calendario_precios")
    resultados.append(comprobar(
        "Noches ocupadas del calendario = noches de las reservas",
        noches_reservas == noches_calendario,
        f"({noches_calendario} / {noches_reservas})",
    ))

    puntuaciones_mal = valor(con, "SELECT COUNT(*) FROM reservas WHERE puntuacion NOT BETWEEN 1 AND 5")
    resultados.append(comprobar("Puntuaciones entre 1 y 5", puntuaciones_mal == 0))

    if filas["mercado_istac"] == 0:
        print("  [AVISO] mercado_istac está vacía: ejecuta python src/fetch_istac.py")

    # 3. Indicadores por año (para comparar con la ficha del cliente)
    print("\nIndicadores por año:")
    indicadores = {}
    for anio, reservas, confirmadas, huespedes, ingresos, estancia in con.execute("""
        SELECT substr(fecha_entrada, 1, 4),
               COUNT(*),
               SUM(estado = 'confirmada'),
               SUM(CASE WHEN estado = 'confirmada' THEN num_huespedes END),
               ROUND(SUM(CASE WHEN estado = 'confirmada' THEN precio_noche * noches END)),
               ROUND(AVG(noches), 1)
        FROM reservas GROUP BY 1
    """):
        ocupacion, precio, viviendas = con.execute("""
            SELECT ROUND(AVG(ocupada) * 100, 1), ROUND(AVG(precio_noche), 1),
                   COUNT(DISTINCT id_vivienda)
            FROM calendario_precios WHERE substr(fecha, 1, 4) = ?
        """, (anio,)).fetchone()
        dias = valor(con, f"SELECT COUNT(DISTINCT fecha) FROM calendario_precios WHERE fecha LIKE '{anio}%'")
        indicadores[anio] = {
            "viviendas_con_actividad": viviendas,
            "reservas": reservas,
            "reservas_confirmadas": confirmadas,
            "reservas_por_dia": round(reservas / dias, 1),
            "huespedes": huespedes,
            "ingresos_gestionados_eur": ingresos,
            "ocupacion_pct": ocupacion,
            "precio_medio_publicado_eur": precio,
            "estancia_media_noches": estancia,
        }
        print(f"  {anio}: {indicadores[anio]}")

    resumen = {
        "descripcion": "Resumen de los datos de Tabaiba Stays (simulados) y del ISTAC (reales)",
        "periodo_cliente": [
            valor(con, "SELECT MIN(fecha) FROM calendario_precios"),
            valor(con, "SELECT MAX(fecha) FROM calendario_precios"),
        ],
        "filas_por_tabla": filas,
        "comprobaciones_correctas": all(resultados),
        "indicadores_por_anio": indicadores,
    }
    RUTA_RESUMEN.write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResumen guardado en {RUTA_RESUMEN}")
    con.close()


if __name__ == "__main__":
    main()
