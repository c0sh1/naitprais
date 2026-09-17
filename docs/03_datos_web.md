# Fase 3: Datos y web de la startup

**Startup:** NaitPrais · **Cliente:** Tabaiba Stays Gestión Vacacional, S.L. (ficticia)

**Índice**
1. Resumen del entregable
2. Construcción de los datos
3. Base de datos: primera versión
4. Identidad de la startup
5. Website
6. Pendiente para la fase 4

---

## 1. Resumen del entregable

| Pide el entregable | Dónde está |
|---|---|
| Primera versión funcional de la base de datos | `data/naitprais.db` (SQLite, 5 tablas) |
| Datos cargados | Apartado 2 y 3. Scripts en `src/` |
| Website funcional | Carpeta `web/` (apartado 5) |
| Identidad básica de la startup | Apartado 4 y `web/assets/logo.svg` |

---

## 2. Construcción de los datos

### Estrategia: datos simulados + datos reales

Tabaiba Stays es una empresa ficticia, así que sus datos internos no existen. Por eso combinamos dos fuentes:

| Tabla | Tipo de dato | Cómo se obtiene | Filas |
|---|---|---|---|
| `municipios` | Real | Nombres y códigos INE oficiales de los 5 municipios | 5 |
| `viviendas` | Simulado | `src/generate_data.py` | 64 |
| `reservas` | Simulado | `src/generate_data.py` | 5.331 |
| `calendario_precios` | Simulado | `src/generate_data.py` | 59.930 |
| `mercado_istac` | Real (Open Data) | `src/fetch_istac.py` descarga los datos del ISTAC | 455 (5 municipios × 91 meses) |

Periodo de los datos del cliente: **del 1 de enero de 2024 al 31 de agosto de 2026**.

### Cómo se simulan los datos del cliente

El script `src/generate_data.py` crea las viviendas y simula, día a día, las reservas de cada una. Sigue estas reglas:

1. **Viviendas.** 60 activas repartidas como indica la ficha (Adeje 20, Arona 16, Puerto de la Cruz 8, San Bartolomé de Tirajana 10 y Mogán 6) y 4 que se dieron de baja en 2025. El 70 % son apartamentos, el 20 % casas y el 10 % villas. El precio base depende del tamaño, del municipio, de si tienen piscina y de si tienen vistas al mar.
2. **Precio publicado.** La gestora aplica solo **3 tarifas al año** (alta de noviembre a abril, media en julio y agosto, baja el resto), igual que en la ficha del cliente. Cada año las sube un poco.
3. **Precio de mercado.** Cada vivienda tiene además un "precio justo" que cambia cada mes y sube en Navidad, Carnaval y Semana Santa. La gestora no lo conoce.
4. **Ocupación.** Si el precio publicado está por encima del precio de mercado, la vivienda se reserva menos; si está por debajo, se reserva más y con más antelación.
5. **Estacionalidad calibrada con datos reales.** La demanda de cada mes se ha calculado con los **ingresos reales de las viviendas vacacionales de Canarias en 2025** publicados por el ISTAC (enero y noviembre son los meses más fuertes; mayo y junio, los más flojos).
6. **Detalles de cada reserva.** Estancia media más larga en invierno, un 7 % de cancelaciones, canal de venta (Airbnb, Booking, Vrbo o web propia), país del huésped (más españoles en verano, más británicos y nórdicos en invierno) y reseña en el 62 % de las estancias.

Se usa una semilla fija (`SEMILLA = 42`), así que el script genera siempre los mismos datos.

### Coherencia de los datos

El enunciado pide que los datos sean coherentes con el tamaño de la empresa. Estos son los indicadores de 2025 comparados con la ficha del cliente:

| Indicador (2025) | Ficha del cliente | Datos generados |
|---|---|---|
| Viviendas gestionadas | 60 (más 4 que se dieron de baja) | 64 con actividad |
| Reservas al año | unas 2.100 | 2.070 (1.935 confirmadas) |
| Huéspedes al año | unos 5.800 | 5.786 |
| Importe de las reservas gestionadas | unos 1,6 millones de euros | 1.585.755 € |
| Ocupación media | - | 71,4 % |
| Precio medio publicado | - | 99,9 € por noche |
| Estancia media | - | 8,3 noches |

Una gestora de 60 viviendas con unas **5,7 reservas al día** es un volumen realista.

El script `src/check_data.py` comprueba automáticamente que:
- las claves foráneas son correctas;
- las fechas de las reservas tienen sentido (salida después de entrada, reserva antes de la entrada) y las noches coinciden;
- no hay dos reservas confirmadas a la vez en la misma vivienda;
- ninguna reserva tiene más huéspedes que plazas;
- las noches ocupadas del calendario coinciden con las noches de las reservas;
- las puntuaciones están entre 1 y 5.

Todas las comprobaciones salen correctas. El resumen se guarda en `data/resumen_datos.json`.

### Datos reales del ISTAC

- **Dataset:** *Viviendas vacacionales, plazas, tasas de ocupación, estancia media e ingresos. Islas y municipios de Canarias por periodos* (código C00065A_000061).
- **Formato:** TSV descargado de la API de datos abiertos del Gobierno de Canarias. Una fila por territorio, mes y medida.
- **Qué hace `src/fetch_istac.py`:** busca la versión más reciente del dataset, lo descarga, se queda con nuestros 5 municipios y con los datos mensuales, pasa cada medida a una columna y carga el resultado en `mercado_istac`. Guarda también una copia filtrada en `data/istac_municipios.csv`.
- **Detalle importante:** en el ISTAC hay dos "San Bartolomé": el de Lanzarote (35018) y San Bartolomé de Tirajana (35019). Usamos el código INE, no el nombre, para no confundirlos.
- **Última actualización consultada:** versión 1.28 (agosto de 2026), con datos de enero de 2019 a julio de 2026 (455 filas cargadas).
- **Medidas que publica:** viviendas disponibles y reservadas, plazas disponibles, tasa de vivienda reservada, estancia media e ingresos totales. **No publica la ocupación por noches**: la tasa de vivienda reservada es el porcentaje de viviendas que tuvieron al menos una reserva en el mes, así que no se puede comparar directamente con nuestra ocupación. Por eso la tabla guarda esa tasa con su nombre real y la comparación con el mercado se hace con los ingresos por vivienda disponible.

### Cómo generar los datos

```bash
pip install -r requirements.txt
python src/generate_data.py    # crea data/naitprais.db con los datos simulados
python src/fetch_istac.py      # añade los datos reales del ISTAC (necesita internet)
python src/check_data.py       # comprueba la coherencia y guarda el resumen
```

---

## 3. Base de datos: primera versión

La base de datos está en `data/naitprais.db` y sigue el diseño de la fase 2 (`data/schema.sql`). Se puede abrir con [DB Browser for SQLite](https://sqlitebrowser.org/) o desde Python.

**Consultas de ejemplo**

Ocupación media por municipio en 2025:

```sql
SELECT m.nombre, ROUND(AVG(c.ocupada) * 100, 1) AS ocupacion
FROM calendario_precios c
JOIN viviendas v ON v.id_vivienda = c.id_vivienda
JOIN municipios m ON m.id_municipio = v.id_municipio
WHERE c.fecha LIKE '2025%'
GROUP BY m.nombre;
```

Reservas por canal de venta:

```sql
SELECT canal, COUNT(*) AS reservas
FROM reservas
GROUP BY canal
ORDER BY reservas DESC;
```

Ingresos medios por vivienda al mes: gestora frente al mercado (ISTAC). Es una comparación orientativa, porque no sabemos si los ingresos del ISTAC incluyen, por ejemplo, la limpieza:

```sql
WITH gestora AS (
    SELECT v.id_municipio,
           substr(c.fecha, 1, 7) AS periodo,
           SUM(c.precio_noche * c.ocupada) / COUNT(DISTINCT c.id_vivienda) AS ingresos_vivienda
    FROM calendario_precios c
    JOIN viviendas v ON v.id_vivienda = c.id_vivienda
    GROUP BY v.id_municipio, periodo
)
SELECT m.nombre, g.periodo,
       ROUND(g.ingresos_vivienda) AS gestora,
       ROUND(i.ingresos / i.viviendas_disponibles) AS mercado
FROM gestora g
JOIN mercado_istac i ON i.id_municipio = g.id_municipio AND i.periodo = g.periodo
JOIN municipios m ON m.id_municipio = g.id_municipio
ORDER BY m.nombre, g.periodo;
```

---

## 4. Identidad de la startup

**Nombre:** NaitPrais, de *night price* (precio por noche) escrito como se pronuncia en español.

**Eslogan:** *Cada noche tiene su precio.*

**Logotipo:** una luna creciente (la noche) sobre un cuadrado azul, con un punto rosa que recuerda al agujero de una etiqueta de precio. Archivo: `web/assets/logo.svg`.

**Colores**, inspirados en Canarias:

| Nombre | Color | Uso |
|---|---|---|
| Atlántico | `#103A5C` | Color principal, títulos y logotipo |
| Buganvilla | `#B3336B` | Botones y detalles |
| Cal | `#F6F7F4` | Fondo (el blanco de las fachadas encaladas) |
| Picón | `#221E1B` | Texto (el color de la arena volcánica) |
| Bruma | `#DDE7EF` | Fondos suaves |

**Tipografía:** Schibsted Grotesk (Google Fonts), una sola familia para toda la web, con números de ancho fijo para que los precios se alineen.

**Tono:** cercano y directo, en español, sin tecnicismos. Hablamos de precios, noches y reservas, no de algoritmos.

---

## 5. Website

La web está en la carpeta `web/` y usa solo HTML, CSS y JavaScript, sin frameworks ni servidor.

### Qué incluye

| Pide el enunciado | Sección de la web |
|---|---|
| Nombre e identidad visual | Cabecera, logotipo, colores y tipografía |
| Qué hace la empresa | Portada y sección "Qué hacemos" |
| Problema que resuelve | Sección "Tres tarifas al año no bastan" |
| Servicios | Sección "Qué hacemos" (4 servicios) y "Cómo funciona" (3 pasos) |
| Sectores o clientes | Sección "Para quién es" |
| Propuesta de valor | Banda azul antes del contacto |
| Ejemplo de solución | Calendario interactivo de la portada y sección "Un caso práctico: Tabaiba Stays" |
| Contacto | Formulario (abre el correo con los datos rellenados), correo y oficina |

**Elemento principal:** el calendario de la portada muestra febrero de 2026 de un apartamento de Tabaiba Stays con los datos generados: 100 € todas las noches, también en Carnaval, y un 96 % de ocupación. El botón "Con NaitPrais" cambia a los precios recomendados (115 € y 125 € en Carnaval, los mismos que recomienda el panel para febrero de 2027) y muestra cuánto habría ingresado con la misma ocupación.

**Vibe coding:** la web se ha hecho con ayuda de IA para acelerar el desarrollo, como permite el enunciado. Después se ha revisado en escritorio y en móvil.

### Cómo verla en local

Desde la carpeta `web`:

```bash
python -m http.server
```

y abrir `http://localhost:8000` en el navegador.

### Cómo publicarla en Vercel

1. Entrar en [vercel.com](https://vercel.com) con la cuenta de GitHub.
2. **Add New → Project** e importar el repositorio `naitprais`.
3. En **Root Directory**, elegir `web`.
4. En **Framework Preset**, dejar **Other**, sin comando de build.
5. Pulsar **Deploy**. Cada `git push` actualizará la web automáticamente.

---

## 6. Pendiente para la fase 4

- Ejecutar `src/fetch_istac.py` para tener los datos reales del mercado en la base de datos.
- Analizar los datos: estacionalidad, diferencias entre viviendas grandes y pequeñas, fechas especiales y comparación con el mercado.
