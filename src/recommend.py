"""
recommend.py
------------
Usa el modelo entrenado para recomendar el precio de cada vivienda activa en los
próximos 12 meses (septiembre 2026 - agosto 2027) y guarda el resultado para el panel web.

Para cada vivienda, mes y tipo de día (normal o fecha especial):
1. Parte del precio actual de la gestora (su tarifa de 2026 para ese mes).
2. Prueba precios entre -15 % y +15 % (hasta +25 % en fechas especiales).
3. Con el modelo calcula la ocupación esperada de cada precio.
4. Elige el precio que deja más ingresos (precio x ocupación). La gestora cobra un
   porcentaje de los ingresos, así que ese es su objetivo.

Decisiones prudentes:
- El histórico no permite medir bien cuánto baja la ocupación al subir el precio:
  la gestora casi no cambia sus precios y sus precios altos coinciden con los meses
  de más demanda. Por eso el modelo estima un efecto del precio pequeño (train.py),
  y ese error siempre va en la misma dirección: hace creer que subir precios sale gratis.
- Para no exagerar lo que se gana subiendo precios, usamos un efecto del precio más
  fuerte que el estimado (EFECTO_PRECIO_PRUDENTE) y mostramos cómo cambia el resultado
  con otros valores (análisis de sensibilidad).
- Los cambios están limitados y, si la mejora es menor del 2 %, se mantiene el precio.

Guarda:
- data/recomendaciones.csv
- web/assets/recomendaciones.json  (lo usa web/panel.html)

Uso:
    python src/recommend.py
"""

import json
import pickle
from datetime import date

import numpy as np
import pandas as pd

from features import (EVENTOS, RAIZ, RUTA_MODELOS, VARIABLES, calcular_segmentos, conectar,
                      indice_demanda, matriz, preparar)

MESES_FUTUROS = pd.period_range("2026-09", "2027-08", freq="M")
CAMBIOS_NORMAL = np.arange(-0.15, 0.151, 0.05)
CAMBIOS_EVENTO = np.arange(-0.15, 0.251, 0.05)
UMBRAL_MANTENER = 0.02       # si los ingresos mejoran menos de un 2 %, se mantiene el precio
EFECTO_PRECIO_PRUDENTE = -2.5
SENSIBILIDAD = [-1.3, -2.0, -2.5, -3.5]   # valores para comprobar cómo cambia el resultado

TARIFAS = {11: "alta", 12: "alta", 1: "alta", 2: "alta", 3: "alta", 4: "alta",
           7: "media", 8: "media", 5: "baja", 6: "baja", 9: "baja", 10: "baja"}
NOMBRES_MES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
               "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def redondear(precio):
    return float(round(precio / 5) * 5)


def dias_del_mes(periodo):
    """Cuenta los días normales y los días de fechas especiales de un mes."""
    dias = pd.date_range(periodo.start_time, periodo.end_time.normalize(), freq="D")
    especiales = pd.Series(False, index=dias)
    nombres = set()
    for inicio, fin, nombre in EVENTOS:
        dentro = (dias >= inicio) & (dias <= fin)
        if dentro.any():
            nombres.add(nombre)
        especiales |= dentro
    return int((~especiales).sum()), int(especiales.sum()), sorted(nombres)


def tarifas_actuales(con):
    """Precio de 2026 de cada vivienda para cada tarifa (alta, media, baja)."""
    cal = pd.read_sql("""
        SELECT id_vivienda, fecha, precio_noche FROM calendario_precios
        WHERE fecha >= '2026-01-01'
    """, con, parse_dates=["fecha"])
    cal["tarifa"] = cal["fecha"].dt.month.map(TARIFAS)
    return cal.groupby(["id_vivienda", "tarifa"])["precio_noche"].median().unstack()


def motivo(fila):
    demanda = fila["indice_demanda"]
    ocupacion = fila["ocupacion_actual"]
    if fila["tipo_dia"] == "especial":
        if fila["accion"] == "Subir":
            return (f"{fila['fechas_especiales']}: ocupación prevista del {ocupacion * 100:.0f}\u00a0% con el precio actual. "
                    "Estas fechas se reservan con mucha antelación.")
        return f"{fila['fechas_especiales']}: el precio actual ya está cerca del óptimo."
    if fila["accion"] == "Subir":
        if demanda >= 1.1:
            return f"Mes de mucha demanda en {fila['municipio']} y ocupación prevista del {ocupacion * 100:.0f}\u00a0% con el precio actual."
        return f"Ocupación prevista del {ocupacion * 100:.0f}\u00a0% con el precio actual: hay margen para cobrar más sin perder muchas reservas."
    if fila["accion"] == "Bajar":
        if demanda <= 0.9:
            return f"Mes flojo en {fila['municipio']} y ocupación prevista del {ocupacion * 100:.0f}\u00a0%: un precio más bajo atrae reservas que ahora se pierden."
        return f"Ocupación prevista del {ocupacion * 100:.0f}\u00a0%: el precio actual está por encima de lo que paga el mercado para esta vivienda."
    return f"El precio actual está cerca del óptimo (ocupación prevista del {ocupacion * 100:.0f}\u00a0%)."


def ocupacion_esperada(logit_sin_precio, efecto_precio, precios, precio_medio):
    """Probabilidad de ocupación para cada precio (misma fórmula que usa el panel web)."""
    return 1 / (1 + np.exp(-(logit_sin_precio + efecto_precio * np.log(precios / precio_medio))))


def main():
    with open(RUTA_MODELOS / "modelo_ocupacion.pkl", "rb") as f:
        guardado = pickle.load(f)
    modelo = guardado["modelo"]
    ids = guardado["ids_viviendas"]
    precio_medio = pd.Series(guardado["precio_medio"])
    coef = dict(zip(VARIABLES, modelo.coef_[0][:len(VARIABLES)]))

    metricas = json.loads((RUTA_MODELOS / "metricas.json").read_text(encoding="utf-8"))
    print(f"Efecto del precio estimado por el modelo: {coef['log_precio_rel']:.2f} "
          f"(intervalo 90 %: {metricas['efecto_precio_intervalo_90']})")
    print(f"Efecto del precio usado (prudente): {EFECTO_PRECIO_PRUDENTE}\n")

    con = conectar()
    viviendas = pd.read_sql("""
        SELECT v.*, m.nombre AS municipio, m.isla
        FROM viviendas v JOIN municipios m ON m.id_municipio = v.id_municipio
        WHERE v.activa = 1
    """, con)
    demanda = indice_demanda(con)
    tarifas = tarifas_actuales(con)
    segmentos = calcular_segmentos(con)      # mismos grupos que en el EDA
    con.close()

    def calcular(efecto_precio):
        filas = []
        for _, v in viviendas.iterrows():
            for periodo in MESES_FUTUROS:
                normales, especiales, nombres_eventos = dias_del_mes(periodo)
                precio_actual = float(tarifas.loc[v["id_vivienda"], TARIFAS[periodo.month]])
                indice = float(demanda.loc[(demanda["id_municipio"] == v["id_municipio"]) &
                                           (demanda["mes"] == periodo.month), "indice_demanda"].iloc[0])

                for tipo_dia, dias, cambios in [("normal", normales, CAMBIOS_NORMAL),
                                                ("especial", especiales, CAMBIOS_EVENTO)]:
                    if dias == 0:
                        continue
                    precios = np.array(sorted({redondear(precio_actual * (1 + c)) for c in cambios}))

                    # Parte del modelo que no depende del precio (la usa también el simulador web)
                    base = pd.DataFrame({
                        "id_vivienda": [v["id_vivienda"]], "precio_noche": [precio_medio[v["id_vivienda"]]],
                        "plazas": [v["plazas"]], "mes": [periodo.month], "indice_demanda": [indice],
                        "evento": [1 if tipo_dia == "especial" else 0],
                    })
                    p_base = modelo.predict_proba(matriz(preparar(base, precio_medio), ids))[0, 1]
                    logit_sin_precio = float(np.log(p_base / (1 - p_base)))

                    ocupacion = ocupacion_esperada(logit_sin_precio, efecto_precio, precios,
                                                   precio_medio[v["id_vivienda"]])
                    ingresos = precios * ocupacion * dias

                    i_actual = int(np.argmin(np.abs(precios - precio_actual)))
                    i_mejor = int(np.argmax(ingresos))
                    if ingresos[i_mejor] < ingresos[i_actual] * (1 + UMBRAL_MANTENER):
                        i_mejor = i_actual

                    filas.append({
                        "id_vivienda": int(v["id_vivienda"]),
                        "periodo": str(periodo),
                        "mes_nombre": f"{NOMBRES_MES[periodo.month - 1]} de {periodo.year}",
                        "tipo_dia": tipo_dia,
                        "fechas_especiales": ", ".join(nombres_eventos) if tipo_dia == "especial" else "",
                        "dias": dias,
                        "municipio": v["municipio"],
                        "indice_demanda": indice,
                        "precio_actual": precio_actual,
                        "precio_recomendado": float(precios[i_mejor]),
                        "ocupacion_actual": float(ocupacion[i_actual]),
                        "ocupacion_recomendada": float(ocupacion[i_mejor]),
                        "ingresos_actuales": float(precios[i_actual] * ocupacion[i_actual] * dias),
                        "ingresos_recomendados": float(precios[i_mejor] * ocupacion[i_mejor] * dias),
                        "logit_sin_precio": logit_sin_precio,
                    })

        return pd.DataFrame(filas)

    # Análisis de sensibilidad: ¿cuánto cambia el resultado según el efecto del precio?
    sensibilidad = []
    for valor in SENSIBILIDAD:
        prueba_rec = calcular(valor)
        cambio = prueba_rec["precio_recomendado"] / prueba_rec["precio_actual"] - 1
        sensibilidad.append({
            "efecto_precio": valor,
            "mejora_ingresos_pct": round((prueba_rec["ingresos_recomendados"].sum()
                                          / prueba_rec["ingresos_actuales"].sum() - 1) * 100, 1),
            "subir": int((cambio > 0.001).sum()),
            "mantener": int((cambio.abs() <= 0.001).sum()),
            "bajar": int((cambio < -0.001).sum()),
        })
    print("Sensibilidad al efecto del precio:")
    print(pd.DataFrame(sensibilidad).to_string(index=False), "\n")

    efecto_precio = EFECTO_PRECIO_PRUDENTE
    rec = calcular(efecto_precio)
    cambio = rec["precio_recomendado"] / rec["precio_actual"] - 1
    rec["accion"] = np.select([cambio > 0.001, cambio < -0.001], ["Subir", "Bajar"], "Mantener")
    rec["ganancia"] = rec["ingresos_recomendados"] - rec["ingresos_actuales"]
    rec["motivo"] = rec.apply(motivo, axis=1)
    rec.to_csv(RAIZ / "data" / "recomendaciones.csv", index=False)

    # ---------- JSON para la web ----------
    viviendas["tamano"] = pd.cut(viviendas["plazas"], [0, 3, 5, 16],
                                 labels=["Pequeña", "Mediana", "Grande"]).astype(str)
    viviendas = viviendas.merge(segmentos, on="id_vivienda", how="left")

    tipos = {"apartamento": "Apartamento", "casa": "Casa", "villa": "Villa"}
    salida = {
        "generado": date.today().isoformat(),
        "cliente": "Tabaiba Stays",
        "datos_hasta": "2026-08-31",
        "comision_gestora": 0.22,
        "modelo": {
            "efecto_precio": float(efecto_precio),
            "efecto_precio_central": round(float(coef["log_precio_rel"]), 3),
            "error_mensual_pts": metricas["error_ocupacion_mensual_modelo_pts"],
            "error_referencia_pts": metricas["error_ocupacion_mensual_referencia_pts"],
        },
        "sensibilidad": sensibilidad,
        "meses": [{"periodo": str(p), "nombre": f"{NOMBRES_MES[p.month - 1]} de {p.year}"} for p in MESES_FUTUROS],
        "viviendas": [
            {
                "id": int(v["id_vivienda"]),
                "nombre": f"{tipos[v['tipo']]} de {int(v['plazas'])} plazas en {v['municipio']} (n.º {int(v['id_vivienda'])})",
                "tipo": tipos[v["tipo"]],
                "plazas": int(v["plazas"]),
                "municipio": v["municipio"],
                "isla": v["isla"],
                "piscina": bool(v["piscina"]),
                "vista_mar": bool(v["vista_mar"]),
                "segmento": v["segmento"] if isinstance(v["segmento"], str) else "",
                "precio_medio": round(float(precio_medio[v["id_vivienda"]]), 2),
            }
            for _, v in viviendas.iterrows()
        ],
        "recomendaciones": [
            {
                "v": int(r.id_vivienda), "p": r.periodo, "t": r.tipo_dia, "e": r.fechas_especiales,
                "d": int(r.dias), "pa": r.precio_actual, "pr": r.precio_recomendado,
                "oa": round(r.ocupacion_actual, 3), "or": round(r.ocupacion_recomendada, 3),
                "ia": round(r.ingresos_actuales), "ir": round(r.ingresos_recomendados),
                "g": round(r.ganancia), "a": r.accion, "m": r.motivo,
                "l": round(r.logit_sin_precio, 4), "dem": round(r.indice_demanda, 3),
            }
            for r in rec.itertuples()
        ],
    }
    ruta_json = RAIZ / "web" / "assets" / "recomendaciones.json"
    ruta_json.write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # ---------- Resumen en pantalla ----------
    total_actual = rec["ingresos_actuales"].sum()
    total_rec = rec["ingresos_recomendados"].sum()
    print(f"Recomendaciones: {len(rec)} (60 viviendas x 12 meses, días normales y fechas especiales)")
    print(rec["accion"].value_counts().to_string())
    print(f"\nIngresos esperados 12 meses con los precios actuales: {total_actual:,.0f} €")
    print(f"Ingresos esperados con los precios recomendados:      {total_rec:,.0f} €")
    print(f"Diferencia: {total_rec - total_actual:+,.0f} € ({(total_rec / total_actual - 1) * 100:+.1f} %)")
    print(f"Comisión extra para la gestora (22 %): {(total_rec - total_actual) * 0.22:+,.0f} €")
    metricas["efecto_precio_usado"] = EFECTO_PRECIO_PRUDENTE
    metricas["sensibilidad_efecto_precio"] = sensibilidad
    (RUTA_MODELOS / "metricas.json").write_text(json.dumps(metricas, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nGuardado en data/recomendaciones.csv y {ruta_json.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
