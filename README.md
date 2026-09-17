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
└── web/         Web de la startup y panel de precios (se despliega en Vercel)
```

## Documentación

| Documento | Contenido | Estado |
|---|---|---|
| [01_idea_startup.md](docs/01_idea_startup.md) | Ideas iniciales, idea elegida y definición de la startup | Hecho |
| [02_datos_cliente.md](docs/02_datos_cliente.md) | Ficha del cliente, datos disponibles y diseño de la base de datos | Hecho |
| [03_datos_web.md](docs/03_datos_web.md) | Construcción de los datos, base de datos, identidad y web | Hecho |
| [04_analisis.md](docs/04_analisis.md) | Análisis exploratorio, problemas encontrados y problema seleccionado ([notebook](notebooks/04_eda.ipynb)) | Hecho |
| [05_solucion.md](docs/05_solucion.md) | Modelo, recomendaciones de precio y panel web | Hecho |
| [06_presentacion.md](docs/06_presentacion.md) | Guion de la presentación al cliente, demostración y preguntas frecuentes | Hecho |
| [07_fuentes.md](docs/07_fuentes.md) | Fuentes de datos, normativa y herramientas | Hecho |
| [08_datos_reales.md](docs/08_datos_reales.md) | Qué datos son reales y cuáles simulados | Hecho |
| [ER_diagram.mmd](docs/ER_diagram.mmd) | Diagrama entidad-relación ([imagen](docs/img/er_diagram.png)) | Hecho |

## Tecnologías

- **Python** para datos y modelos (pandas, matplotlib, scikit-learn).
- **SQLite** como base de datos.
- **HTML, CSS y JavaScript** (sin frameworks) para la web, publicada en **Vercel**.

## Cómo ejecutarlo

```bash
pip install -r requirements.txt
python src/generate_data.py    # crea data/naitprais.db con los datos simulados del cliente
python src/fetch_istac.py      # añade los datos reales del ISTAC (necesita internet)
python src/check_data.py       # comprueba la coherencia de los datos
python src/train.py            # entrena y evalúa el modelo de ocupación
python src/recommend.py        # genera las recomendaciones y el JSON del panel
```

Para ver la web y el panel en local:

```bash
cd web
python -m http.server
```

y abrir `http://localhost:8000` (web) o `http://localhost:8000/panel.html` (panel de precios).
