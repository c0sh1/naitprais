# NaitPrais

Precios para viviendas vacacionales en Canarias.

Este es mi proyecto del segundo módulo de Big Data del bootcamp. La idea era montar una startup ficticia, inventarnos un cliente y resolverle un problema real con datos. La mía se llama NaitPrais (*night price*) y se dedica a decirle a las gestoras de viviendas vacacionales qué precio poner cada mes.

El cliente es **Tabaiba Stays**, una gestora inventada de Adeje con 60 viviendas en Tenerife y Gran Canaria. Su problema: ponen los precios (sintéticos) con tres tarifas al año en un Excel, así que cobran lo mismo un martes de octubre que la semana de Carnaval.

**Web y panel:** https://naitprais.vercel.app/index.html

## Lo que encontré

Lo que más me sorprendió salió de cruzar los datos del cliente con los del ISTAC (el instituto de estadística de Canarias):

- **Sus tres tarifas no encajan con la demanda real.** Abril lo cobran como temporada alta y es de los meses más flojos. Noviembre y diciembre son los más fuertes del año y los cobran igual que abril.
- **Navidad, Carnaval y Semana Santa se llenan al 95 % con casi dos meses de antelación, y al mismo precio que un día normal.** Si algo se agota tan pronto, es que está barato.
- **En Adeje, que es donde más viviendas tienen, ingresan un 31 % menos que la media del municipio.**
- En 2026 hay un 10 % menos de viviendas vacacionales en la zona, pero cada una ingresa más. Menos competencia.

Con eso monté un modelo que predice si una noche se va a ocupar según su precio, y un panel donde el cliente ve qué precio poner a cada vivienda y por cuáles empezar.

## Estructura

```
naitprais/
├── data/        Base de datos SQLite, el esquema y los datos del ISTAC
├── docs/        La documentación de cada fase del proyecto
├── models/      El modelo entrenado y sus métricas
├── notebooks/   El análisis exploratorio
├── src/         Los scripts de Python
└── web/         La web de la startup y el panel de precios
```

## Cómo ejecutarlo

```bash
pip install -r requirements.txt

python src/generate_data.py   # genera los datos simulados del cliente
python src/fetch_istac.py     # descarga los datos reales del ISTAC (necesita internet)
python src/check_data.py      # comprueba que los datos son coherentes
python src/train.py           # entrena el modelo y lo evalúa
python src/recommend.py       # calcula los precios recomendados
```

Hay que ejecutarlos en ese orden, porque cada uno necesita lo del anterior.

Para ver la web y el panel:

```bash
cd web
python -m http.server
```

Y abrir `http://localhost:8000`. El panel está en `/panel.html`. **Ojo:** si abres el HTML con doble clic el panel sale vacío, porque el navegador no deja leer el JSON de los datos. Hay que levantar el servidor.

## Documentación

| Documento | De qué va |
|---|---|
| [idea_startup.md](docs/idea_startup.md) | Las cuatro ideas que barajé y por qué elegí esta |
| [cliente_tabaiba_stays.md](docs/cliente_tabaiba_stays.md) | Quién es el cliente y cómo diseñé la base de datos |
| [datos_web.md](docs/datos_web.md) | De dónde salen los datos y cómo hice la web |
| [analisis_exploratorio.md](docs/analisis_exploratorio.md) | Los hallazgos del análisis ([notebook](notebooks/eda.ipynb)) |
| [modelo_panel_solucion.md](docs/modelo_panel_solucion.md) | El modelo, las recomendaciones y el panel |
| [datos_reales_y_simulados.md](docs/datos_reales_y_simulados.md) | Qué datos son reales y cuáles me inventé |
| [fuentes.md](docs/fuentes.md) | Las fuentes que usé |
| [modelo_datos_ER.mmd](docs/modelo_datos_ER.mmd) | El diagrama entidad-relación ([imagen](docs/img/modelo_datos_ER.png)) |

## Sobre los datos

Esto es importante y lo explico mejor en [datos_reales_y_simulados.md](docs/datos_reales_y_simulados.md):

- **Los datos del cliente son simulados.** Tabaiba Stays no existe, así que sus reservas las genero yo con un script. Eso sí, la estacionalidad está calibrada con los ingresos reales de Canarias, para que los patrones tengan sentido.
- **Los datos del mercado son reales.** Son 455 filas del ISTAC con los datos de los cinco municipios, de 2019 a 2026.

## Lo que no funciona del todo

Prefiero decirlo yo:

- **El modelo no puede medir bien cuánto baja la ocupación al subir el precio.** El cliente casi nunca ha cambiado sus precios, así que no hay casos de los que aprender. Además sus precios altos coinciden con los meses de más demanda, así que el modelo se cree que subir no penaliza. Como ese error siempre empuja a subir, en las recomendaciones uso un valor más conservador que el que estima el modelo, y enseño qué pasaría con otros valores.
- **El modelo se equivoca en unos 13 puntos** al predecir la ocupación de un mes. Sirve para saber si hay que subir o bajar, no para prometer una ocupación exacta. Aun así es mejor que la alternativa, que sería repetir lo del año pasado (15,3 puntos).
- **La estancia media que genero (8,3 noches) es casi el doble que la real del ISTAC (4,8).** Me di cuenta tarde y no me dio tiempo a rehacer la simulación.

## Tecnologías

- **Python** para los datos y el modelo: pandas, scikit-learn y matplotlib.
- **SQLite** para la base de datos.
- **HTML, CSS y JavaScript** para la web y el panel, sin frameworks. Están en Vercel.
- **Mermaid** para el diagrama entidad-relación.

## Lo que aprendí

Que la parte difícil no es el modelo. Lo difícil fue darme cuenta de que el ISTAC no publica la ocupación por noches sino el porcentaje de viviendas con alguna reserva, que no es lo mismo. Tuve que rehacer una tabla de la base de datos y cambiar la forma de comparar al cliente con su mercado.

Y que un modelo que acierta poco pero explica por qué recomienda cada cosa es más útil para un cliente que uno que acierta más y no se puede explicar.