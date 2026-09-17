"""
train.py
--------
Entrena el modelo que predice la ocupación de cada vivienda y lo evalúa con datos
que no ha visto.

- Entrenamiento: 2024 y 2025.
- Prueba: enero a agosto de 2026.
- Referencia para comparar: repetir la ocupación que tuvo cada vivienda ese mismo mes
  en los años anteriores (lo que haría la gestora "a ojo").

Guarda:
- models/modelo_ocupacion.pkl
- models/metricas.json

Uso:
    python src/train.py
"""

import json
import pickle

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, mean_absolute_error, roc_auc_score

from features import RUTA_MODELOS, VARIABLES, conectar, indice_demanda, marcar_eventos, matriz, preparar

FECHA_CORTE = "2026-01-01"
REPETICIONES_BOOTSTRAP = 30


def cargar_datos(con):
    datos = pd.read_sql("""
        SELECT c.id_vivienda, c.fecha, c.precio_noche, c.ocupada,
               v.id_municipio, v.plazas
        FROM calendario_precios c
        JOIN viviendas v ON v.id_vivienda = c.id_vivienda
    """, con, parse_dates=["fecha"])
    datos["mes"] = datos["fecha"].dt.month
    datos["evento"] = marcar_eventos(datos["fecha"])
    datos = datos.merge(indice_demanda(con), on=["id_municipio", "mes"], how="left")
    return datos


def entrenar(X, y):
    modelo = LogisticRegression(C=1.0, max_iter=5000)
    modelo.fit(X, y)
    return modelo


def main():
    con = conectar()
    datos = cargar_datos(con)
    con.close()

    entrenamiento = datos[datos["fecha"] < FECHA_CORTE]
    prueba = datos[datos["fecha"] >= FECHA_CORTE]

    precio_medio = entrenamiento.groupby("id_vivienda")["precio_noche"].mean()
    ids = sorted(entrenamiento["id_vivienda"].unique())

    entrenamiento = preparar(entrenamiento, precio_medio)
    prueba = preparar(prueba, precio_medio)
    X_ent, y_ent = matriz(entrenamiento, ids), entrenamiento["ocupada"]
    X_pru, y_pru = matriz(prueba, ids), prueba["ocupada"]

    modelo = entrenar(X_ent, y_ent)
    prob = modelo.predict_proba(X_pru)[:, 1]

    # 1. Métricas por noche
    auc = roc_auc_score(y_pru, prob)
    brier = brier_score_loss(y_pru, prob)

    # 2. Métricas por vivienda y mes (lo que usa el cliente)
    prueba = prueba.assign(prediccion=prob, periodo=prueba["fecha"].dt.strftime("%Y-%m"))
    mensual = prueba.groupby(["id_vivienda", "periodo", "mes"]).agg(
        real=("ocupada", "mean"), prediccion=("prediccion", "mean")).reset_index()
    referencia = entrenamiento.groupby(["id_vivienda", "mes"])["ocupada"].mean().rename("referencia")
    mensual = mensual.merge(referencia, on=["id_vivienda", "mes"], how="left")
    error_modelo = mean_absolute_error(mensual["real"], mensual["prediccion"])
    error_referencia = mean_absolute_error(mensual["real"], mensual["referencia"])

    # Modelo final: se vuelve a entrenar con todos los datos para recomendar el futuro
    todo = preparar(datos, precio_medio)
    modelo_final = entrenar(matriz(todo, ids), todo["ocupada"])

    # 3. Incertidumbre del efecto del precio en el modelo final (bootstrap por viviendas):
    #    se repite el entrenamiento con muestras de viviendas elegidas al azar
    rng = np.random.default_rng(42)
    coef_precio = []
    for _ in range(REPETICIONES_BOOTSTRAP):
        muestra_ids = rng.choice(ids, size=len(ids), replace=True)
        muestra = pd.concat([todo[todo["id_vivienda"] == v] for v in muestra_ids])
        m = entrenar(matriz(muestra, ids), muestra["ocupada"])
        coef_precio.append(m.coef_[0][0])

    coeficientes = dict(zip(VARIABLES, modelo_final.coef_[0][:len(VARIABLES)]))
    metricas = {
        "modelo": "Regresión logística (probabilidad de que una noche esté ocupada)",
        "entrenamiento": f"{entrenamiento['fecha'].min():%Y-%m-%d} a {entrenamiento['fecha'].max():%Y-%m-%d}",
        "prueba": f"{prueba['fecha'].min():%Y-%m-%d} a {prueba['fecha'].max():%Y-%m-%d}",
        "noches_entrenamiento": int(len(entrenamiento)),
        "noches_prueba": int(len(prueba)),
        "auc_noche": round(auc, 3),
        "brier_noche": round(brier, 3),
        "error_ocupacion_mensual_modelo_pts": round(error_modelo * 100, 1),
        "error_ocupacion_mensual_referencia_pts": round(error_referencia * 100, 1),
        "mejora_frente_a_referencia_pct": round((1 - error_modelo / error_referencia) * 100, 1),
        "ocupacion_real_prueba_pct": round(mensual["real"].mean() * 100, 1),
        "ocupacion_predicha_prueba_pct": round(mensual["prediccion"].mean() * 100, 1),
        "coeficientes_modelo_final": {k: round(float(v), 3) for k, v in coeficientes.items()},
        "efecto_precio_intervalo_90": [round(float(np.percentile(coef_precio, 5)), 3),
                                       round(float(np.percentile(coef_precio, 95)), 3)],
    }

    RUTA_MODELOS.mkdir(exist_ok=True)
    with open(RUTA_MODELOS / "modelo_ocupacion.pkl", "wb") as f:
        pickle.dump({"modelo": modelo_final, "ids_viviendas": ids,
                     "precio_medio": precio_medio.to_dict(), "variables": VARIABLES}, f)
    (RUTA_MODELOS / "metricas.json").write_text(json.dumps(metricas, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(metricas, indent=2, ensure_ascii=False))
    print("\nModelo guardado en models/modelo_ocupacion.pkl")


if __name__ == "__main__":
    main()
