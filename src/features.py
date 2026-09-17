"""
features.py
-----------
Funciones compartidas por train.py y recommend.py para preparar las variables del modelo.

El modelo predice la probabilidad de que una noche esté ocupada a partir de:
- log_precio_rel: precio publicado frente al precio medio de esa vivienda (en logaritmo)
- log_demanda:    demanda real del mercado en ese municipio y mes (índice del ISTAC)
- evento:         1 si la noche es Navidad, Carnaval o Semana Santa
- grande_x_demanda: las viviendas grandes dependen más de la demanda (visto en el EDA)
- pequena_invierno: las viviendas pequeñas se llenan más en invierno (visto en el EDA)
- una variable por vivienda, que recoge lo que la hace distinta (ubicación, calidad del anuncio...)
"""

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
RUTA_DB = RAIZ / "data" / "naitprais.db"
RUTA_MODELOS = RAIZ / "models"

VARIABLES = ["log_precio_rel", "log_demanda", "evento", "grande_x_demanda", "pequena_invierno"]
MESES_INVIERNO = [11, 12, 1, 2, 3]

# Fechas especiales: Navidad, Carnaval y Semana Santa (incluye las del próximo año)
EVENTOS = [
    ("2023-12-20", "2024-01-06", "Navidad"), ("2024-02-08", "2024-02-18", "Carnaval"),
    ("2024-03-23", "2024-03-31", "Semana Santa"), ("2024-12-20", "2025-01-06", "Navidad"),
    ("2025-02-27", "2025-03-09", "Carnaval"), ("2025-04-12", "2025-04-20", "Semana Santa"),
    ("2025-12-20", "2026-01-06", "Navidad"), ("2026-02-12", "2026-02-22", "Carnaval"),
    ("2026-03-28", "2026-04-05", "Semana Santa"), ("2026-12-20", "2027-01-06", "Navidad"),
    ("2027-02-04", "2027-02-14", "Carnaval"), ("2027-03-20", "2027-03-28", "Semana Santa"),
]


def conectar():
    return sqlite3.connect(RUTA_DB)


def marcar_eventos(fechas):
    """Devuelve 1 si la fecha cae en una fecha especial y 0 si no."""
    marca = pd.Series(0, index=fechas.index)
    for inicio, fin, _ in EVENTOS:
        marca[fechas.between(inicio, fin)] = 1
    return marca


def indice_demanda(con):
    """
    Índice de demanda real por municipio y mes, con los datos del ISTAC:
    ingresos por vivienda disponible (media 2023-2025) dividido entre la media del municipio.
    1 = mes normal, 1.2 = un 20 % más de demanda que un mes normal.
    """
    mercado = pd.read_sql("SELECT * FROM mercado_istac", con)
    mercado["anio"] = mercado["periodo"].str[:4].astype(int)
    mercado["mes"] = mercado["periodo"].str[5:].astype(int)
    mercado["ingresos_por_vivienda"] = mercado["ingresos"] / mercado["viviendas_disponibles"]

    tabla = (mercado[mercado["anio"].between(2023, 2025)]
             .groupby(["id_municipio", "mes"])["ingresos_por_vivienda"].mean().reset_index())
    media = tabla.groupby("id_municipio")["ingresos_por_vivienda"].transform("mean")
    tabla["indice_demanda"] = tabla["ingresos_por_vivienda"] / media
    return tabla[["id_municipio", "mes", "indice_demanda"]]


def preparar(datos, precio_medio):
    """Añade las variables del modelo a una tabla con una fila por vivienda y día."""
    datos = datos.copy()
    datos["log_precio_rel"] = np.log(datos["precio_noche"] / datos["id_vivienda"].map(precio_medio))
    datos["log_demanda"] = np.log(datos["indice_demanda"])
    datos["grande_x_demanda"] = (datos["plazas"] >= 6) * datos["log_demanda"]
    datos["pequena_invierno"] = ((datos["plazas"] <= 3) & datos["mes"].isin(MESES_INVIERNO)).astype(int)
    return datos


def matriz(datos, ids_viviendas):
    """Tabla de entrada del modelo: variables + una columna por vivienda."""
    X = datos[VARIABLES].reset_index(drop=True).astype(float)
    for vid in ids_viviendas:
        X[f"vivienda_{vid}"] = (datos["id_vivienda"].values == vid).astype(float)
    return X


def calcular_segmentos(con):
    """
    Segmentos de viviendas, igual que en el EDA (notebooks/04_eda.ipynb):
    K-Means con 3 grupos según ocupación en temporada alta y baja, precio medio y antelación.
    """
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    tarifas = {11: "alta", 12: "alta", 1: "alta", 2: "alta", 3: "alta", 4: "alta",
               7: "media", 8: "media", 5: "baja", 6: "baja", 9: "baja", 10: "baja"}
    cal = pd.read_sql("SELECT id_vivienda, fecha, precio_noche, ocupada FROM calendario_precios",
                      con, parse_dates=["fecha"])
    cal["tarifa"] = cal["fecha"].dt.month.map(tarifas)
    res = pd.read_sql("""SELECT id_vivienda, fecha_reserva, fecha_entrada FROM reservas
                         WHERE estado = 'confirmada'""", con, parse_dates=["fecha_reserva", "fecha_entrada"])
    res["antelacion"] = (res["fecha_entrada"] - res["fecha_reserva"]).dt.days

    perfil = cal.pivot_table(index="id_vivienda", columns="tarifa", values="ocupada").add_prefix("ocupacion_")
    perfil["precio_medio"] = cal.groupby("id_vivienda")["precio_noche"].mean()
    perfil["antelacion_media"] = res.groupby("id_vivienda")["antelacion"].mean()

    columnas = ["ocupacion_alta", "ocupacion_baja", "precio_medio", "antelacion_media"]
    X = StandardScaler().fit_transform(perfil[columnas])
    perfil["grupo"] = KMeans(n_clusters=3, n_init=10, random_state=42).fit(X).labels_

    resumen = perfil.groupby("grupo")[["precio_medio", "ocupacion_alta"]].mean()
    caro = resumen["precio_medio"].idxmax()
    resto = resumen.drop(caro)
    nombres = {caro: "Grandes y caras",
               resto["ocupacion_alta"].idxmax(): "Se llenan con facilidad",
               resto["ocupacion_alta"].idxmin(): "Con margen de mejora"}
    perfil["segmento"] = perfil["grupo"].map(nombres)
    return perfil["segmento"].reset_index()
