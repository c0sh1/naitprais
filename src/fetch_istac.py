"""
fetch_istac.py
--------------
Descarga los datos REALES del ISTAC sobre viviendas vacacionales por municipio y mes
(dataset C00065A_000061) y los carga en la tabla mercado_istac de data/naitprais.db.

Solo se guardan los 5 municipios donde trabaja Tabaiba Stays.

Uso:
    python src/fetch_istac.py
    python src/fetch_istac.py --archivo ruta/al/fichero.tsv   (si lo has descargado a mano)

Primero hay que ejecutar src/generate_data.py, que crea la base de datos.
"""

import argparse
import sqlite3
import unicodedata
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parent.parent
RUTA_DB = RAIZ / "data" / "naitprais.db"
RUTA_DESCARGA = RAIZ / "data" / "istac_raw.tsv"          # fichero completo (no se sube a GitHub)
RUTA_FILTRADO = RAIZ / "data" / "istac_municipios.csv"   # solo nuestros municipios

# API del catálogo: devuelve la lista de ficheros del dataset con su versión actual
URL_CATALOGO = (
    "https://datos.canarias.es/catalogos/estadisticas/api/3/action/package_show"
    "?id=urn-siemac-org-siemac-metamac-infomodel-statisticalresources-dataset-istac-c00065a_000061"
)
# Si el catálogo falla, se usa esta versión (la última conocida)
URL_RESERVA = (
    "https://datos.canarias.es/api/estadisticas/statistical-resources/v1.0/"
    "datasets/ISTAC/C00065A_000061/1.28.tsv"
)

# Qué columna de mercado_istac corresponde a cada medida del ISTAC.
# Se busca por palabras del nombre de la medida, porque los códigos pueden cambiar.
# Ojo: el ISTAC no da la ocupación por noches, sino el % de viviendas que tuvieron
# al menos una reserva en el mes (tasa de vivienda reservada).
MEDIDAS_BUSCADAS = {
    "viviendas_disponibles": [["viviendas", "disponibles"]],
    "viviendas_reservadas": [["viviendas", "reservadas"]],
    "plazas": [["plazas", "disponibles"], ["plazas"]],
    "tasa_vivienda_reservada": [["tasa", "reservada"]],
    "estancia_media": [["estancia", "media"]],
    "ingresos": [["ingresos", "totales"], ["ingresos"]],
}


def normalizar(texto):
    """Pasa a minúsculas y quita las tildes, para comparar textos."""
    texto = unicodedata.normalize("NFKD", str(texto).lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def buscar_url_tsv():
    try:
        respuesta = requests.get(URL_CATALOGO, timeout=30)
        respuesta.raise_for_status()
        for recurso in respuesta.json()["result"]["resources"]:
            if recurso.get("url", "").endswith(".tsv"):
                return recurso["url"]
    except Exception as error:
        print(f"No se pudo leer el catálogo ({error}). Uso la versión conocida.")
    return URL_RESERVA


def descargar():
    url = buscar_url_tsv()
    print(f"Descargando {url} ...")
    with requests.get(url, timeout=300, stream=True) as respuesta:
        respuesta.raise_for_status()
        with open(RUTA_DESCARGA, "wb") as fichero:
            for trozo in respuesta.iter_content(chunk_size=1024 * 1024):
                fichero.write(trozo)
    print(f"Guardado en {RUTA_DESCARGA}")
    return RUTA_DESCARGA


def elegir_medidas(medidas):
    """Relaciona cada columna de mercado_istac con un código de medida del ISTAC."""
    elegidas = {}
    for columna, opciones in MEDIDAS_BUSCADAS.items():
        for palabras in opciones:
            candidatas = [
                codigo for codigo, nombre in medidas.items()
                if all(p in normalizar(nombre) for p in palabras)
            ]
            if candidatas:
                elegidas[columna] = candidatas[0]
                break
    return elegidas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archivo", help="TSV del ISTAC descargado a mano")
    args = parser.parse_args()

    ruta = Path(args.archivo) if args.archivo else descargar()
    datos = pd.read_csv(ruta, sep="\t", dtype=str)

    con = sqlite3.connect(RUTA_DB)
    municipios = dict(con.execute("SELECT codigo_ine, id_municipio FROM municipios").fetchall())

    # Solo nuestros municipios, datos mensuales y el total de plazas
    datos = datos[datos["TERRITORIO_CODE"].isin(list(municipios))]
    datos = datos[datos["TIME_PERIOD_CODE"].str.contains("-M", na=False)]
    if "INTERVALOS_PLAZAS_CODE" in datos.columns:
        datos = datos[datos["INTERVALOS_PLAZAS_CODE"] == "_T"]

    if datos.empty:
        print("No hay filas para nuestros municipios. Revisa los códigos INE.")
        return

    datos.to_csv(RUTA_FILTRADO, index=False)
    print(f"Filas de nuestros municipios: {len(datos)} (guardadas en {RUTA_FILTRADO})")

    medidas = dict(zip(datos["MEDIDAS_CODE"], datos["MEDIDAS#es"]))
    print("\nMedidas disponibles en el ISTAC:")
    for codigo, nombre in medidas.items():
        print(f"  {codigo:<40} {nombre}")

    elegidas = elegir_medidas(medidas)
    print("\nMedidas usadas:")
    for columna in MEDIDAS_BUSCADAS:
        print(f"  {columna:<22} <- {elegidas.get(columna, 'NO ENCONTRADA (se deja vacía)')}")

    # Una fila por municipio y mes, una columna por medida
    datos["valor"] = pd.to_numeric(datos["OBS_VALUE"], errors="coerce")
    tabla = datos.pivot_table(
        index=["TERRITORIO_CODE", "TIME_PERIOD_CODE"],
        columns="MEDIDAS_CODE",
        values="valor",
        aggfunc="first",
    ).reset_index()

    filas = []
    for _, fila in tabla.iterrows():
        periodo = fila["TIME_PERIOD_CODE"].replace("-M", "-")   # 2025-M01 -> 2025-01
        valores = []
        for columna in MEDIDAS_BUSCADAS:
            codigo = elegidas.get(columna)
            dato = fila.get(codigo) if codigo else None
            valores.append(None if dato is None or pd.isna(dato) else float(dato))
        filas.append((municipios[fila["TERRITORIO_CODE"]], periodo, *valores))

    con.execute("DELETE FROM mercado_istac")
    con.executemany("INSERT INTO mercado_istac VALUES (?, ?, ?, ?, ?, ?, ?, ?)", filas)
    con.commit()

    total = con.execute("SELECT COUNT(*) FROM mercado_istac").fetchone()[0]
    periodo = con.execute("SELECT MIN(periodo), MAX(periodo) FROM mercado_istac").fetchone()
    print(f"\nmercado_istac: {total} filas, de {periodo[0]} a {periodo[1]}")
    con.close()


if __name__ == "__main__":
    main()
