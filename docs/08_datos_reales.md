# Datos reales y datos simulados

Este proyecto mezcla datos reales y datos simulados. Este documento explica qué es cada cosa para que no haya dudas.

## Resumen

| Dato | ¿Real o simulado? | Por qué |
|---|---|---|
| Tabaiba Stays (la empresa, sus cifras y su plantilla) | Simulado | Es un cliente ficticio creado para el proyecto |
| Viviendas, reservas y calendario de precios | Simulado | Son datos internos de una empresa; no existen datos públicos de este tipo |
| Municipios y códigos INE | Real | Códigos oficiales |
| Mercado por municipio y mes (`mercado_istac`) | Real | Datos abiertos del ISTAC |
| Estacionalidad usada para simular (qué meses tienen más demanda) | Real | Calculada con los ingresos de las viviendas vacacionales de Canarias en 2025 (ISTAC) |
| Número de viviendas vacacionales en Canarias (45.253 en enero de 2026) | Real | Nota del ISTAC |
| Ley 6/2025 | Real | Publicada en el BOE |
| Números de registro de las viviendas | Simulados | Tienen un formato parecido al real, pero son inventados |

## Qué significa para el análisis

- Los **patrones de las reservas** (por ejemplo, que las viviendas grandes se ocupen menos en temporada baja) salen de las reglas de la simulación, que están explicadas en `03_datos_web.md`. Esas reglas se basan en cómo funciona el mercado, pero no son datos de una empresa real.
- Las **comparaciones con el mercado** usan datos reales del ISTAC.
- Para usar NaitPrais con una gestora real, solo habría que sustituir las tablas `viviendas`, `reservas` y `calendario_precios` por sus datos. El resto del proyecto no cambia.
