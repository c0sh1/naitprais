# NaitPrais

Startup de análisis de datos para **gestoras de viviendas vacacionales en Canarias**.
Cliente del proyecto: **Tabaiba Stays** (gestora ficticia con 60 viviendas en Tenerife y Gran Canaria).
Recomendamos qué precio poner a cada vivienda cada mes y qué ocupación esperar, combinando el histórico de reservas de la gestora con los datos oficiales del mercado canario (ISTAC).

## Estructura del proyecto

```
naitprais/
├── data/        Base de datos SQLite, esquema SQL (schema.sql) y resumen de datos
├── docs/        Documentación de cada fase y diagrama entidad-relación
├── models/      Modelos entrenados y sus métricas
├── notebooks/   Análisis exploratorio
├── src/         Scripts de Python (descarga, generación de datos, entrenamiento)
└── web/         Web de la startup y demo (se despliega en Vercel)
```

## Documentación

| Documento | Contenido | Estado |
|---|---|---|
| [01_idea_startup.md](docs/01_idea_startup.md) | Ideas iniciales, idea elegida y definición de la startup | Hecho |
| [02_datos_cliente.md](docs/02_datos_cliente.md) | Ficha del cliente, datos disponibles y diseño de la base de datos | Hecho |
| [03_datos_web.md](docs/03_datos_web.md) | Datos y web de la startup | Pendiente |
| [04_analisis.md](docs/04_analisis.md) | Descubrimientos del análisis | Pendiente |
| [05_solucion.md](docs/05_solucion.md) | Solución y prototipo | Pendiente |
| [07_fuentes.md](docs/07_fuentes.md) | Fuentes de datos externas | Pendiente |
| [08_datos_reales.md](docs/08_datos_reales.md) | Qué datos son reales y cuáles simulados | Pendiente |
| [ER_diagram.mmd](docs/ER_diagram.mmd) | Diagrama entidad-relación ([imagen](docs/img/er_diagram.png)) | Hecho |

## Tecnologías

- **Python** para datos y modelos (pandas, scikit-learn).
- **SQLite** como base de datos.
- **HTML, CSS y JavaScript** para la web y la demo, publicadas en **Vercel**.

## Cómo ejecutarlo

Se completará en las siguientes fases.

```bash
pip install -r requirements.txt
```