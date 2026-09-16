# Fase 1: Idea y definición de la startup

**Startup:** NaitPrais

Hemos seguido el orden **Problema → Cliente → Datos → Solución**. Antes de pensar en algoritmos, buscamos problemas reales en los que un cliente concreto pierda dinero o tiempo, y comprobamos que hay datos para trabajar con ellos.

**Índice**
1. Resumen del entregable
2. Ideas iniciales
3. Comparación y elección
4. La startup
5. Riesgos y cómo los tratamos
6. Datos previstos
7. Fuentes

## 1. Resumen del entregable

| Apartado | Respuesta |
|---|---|
| **Ideas iniciales** | 1) Precios para viviendas vacacionales en Canarias · 2) Desperdicio de comida en restaurantes · 3) Mantenimiento predictivo en pymes industriales · 4) Tensión social en Europa para empresas de logística |
| **Idea elegida** | Idea 1: precios y ocupación para viviendas vacacionales en Canarias |
| **Problema** | Las gestoras y propietarios fijan los precios "a ojo", sin tener en cuenta la temporada ni el mercado de su municipio, y pierden ingresos por meses con poca ocupación o por vender por debajo del mercado. |
| **Cliente objetivo** | Gestoras pequeñas y medianas de viviendas vacacionales en Canarias (de 5 a 50 viviendas) y propietarios con varias viviendas registradas. |
| **Nombre de la startup** | NaitPrais |
| **Propuesta de valor** | Te decimos qué precio poner a cada vivienda cada mes y qué ocupación esperar, combinando tu histórico de reservas con los datos oficiales del mercado canario. |

## 2. Ideas iniciales

### Idea 1: Precios y ocupación para viviendas vacacionales en Canarias

- **¿Qué problema existe?** Muchas gestoras y propietarios fijan el precio de sus viviendas vacacionales "a ojo" y casi no lo cambian. No tienen en cuenta la temporada (en Canarias la temporada alta es en invierno, al revés que en la península), la ocupación de su municipio ni lo que cobran viviendas parecidas.
- **¿Quién tiene ese problema?** Gestoras pequeñas y medianas y propietarios con varias viviendas inscritas en el Registro General Turístico de Canarias. Tienen datos de sus reservas, pero no tiempo ni conocimientos para analizarlos.
- **¿Por qué es importante?** Es un sector grande: según el ISTAC, en enero de 2026 había 45.253 viviendas vacacionales disponibles en Canarias, el 41 % en Tenerife y el 23 % en Gran Canaria. El precio es lo que más influye en que una vivienda se reserve o no.
- **¿Qué pierde actualmente ese cliente?** Si el precio es alto, meses con poca ocupación. Si es bajo, llena pero deja dinero sin ganar en temporada alta. Una gestora, además, pierde horas revisando precios vivienda por vivienda y le cuesta justificar ante los propietarios por qué pone un precio u otro.
- **¿Cómo podrían ayudar los datos?** Cruzando el histórico de reservas de cada vivienda con los datos oficiales del ISTAC (ocupación, tarifas medias e ingresos por municipio y mes, desde 2019) se puede recomendar un rango de precio y prever la ocupación de cada vivienda.
- **¿Por qué alguien pagaría?** Porque el problema se traduce directamente en euros, y en una gestora cualquier mejora se multiplica por todas sus viviendas. Ya existen herramientas de precios para alquiler vacacional (por ejemplo PriceLabs o Beyond), lo que demuestra que hay gente dispuesta a pagar. Hay hueco para algo más sencillo, en español y basado en datos oficiales de Canarias.

### Idea 2: Menos desperdicio de comida en restaurantes

- **¿Qué problema existe?** Los restaurantes compran y preparan comida según la intuición del cocinero. Unos días sobra mucha comida y otros se acaban platos antes de tiempo.
- **¿Quién tiene ese problema?** Restaurantes pequeños y medianos y comedores colectivos (colegios, empresas).
- **¿Por qué es importante?** La comida tirada es dinero perdido y, además, en España ya existe una ley específica contra el desperdicio alimentario (Ley 1/2025) que obliga al sector a tomar medidas.
- **¿Qué pierde actualmente ese cliente?** Dinero en materia prima que acaba en la basura, horas de preparación inútiles y clientes que se quedan sin el plato que querían.
- **¿Cómo podrían ayudar los datos?** Con el histórico de ventas por plato, día de la semana, festivos, clima y reservas se puede predecir cuánto se va a vender cada día.
- **¿Por qué alguien pagaría?** Porque se ahorra en compras desde el primer mes y ayuda a cumplir la normativa.
- **Problema para nosotros:** no hay datos públicos de referencia sobre ventas de restaurantes en España con los que comparar o dar realismo a los datos del cliente.

### Idea 3: Mantenimiento predictivo para pymes industriales

- **¿Qué problema existe?** Las máquinas se averían sin avisar. Muchas pymes solo hacen mantenimiento por calendario o cuando algo ya se ha roto.
- **¿Quién tiene ese problema?** Talleres y pequeñas fábricas con maquinaria (envasado, metal, carpintería).
- **¿Por qué es importante?** Una parada no planificada frena toda la producción.
- **¿Qué pierde actualmente ese cliente?** Horas de producción, reparaciones urgentes más caras y pedidos entregados tarde.
- **¿Cómo podrían ayudar los datos?** Con datos de sensores (temperatura, vibración, velocidad) y el historial de averías se puede entrenar un modelo que avise antes de que falle una máquina.
- **¿Por qué alguien pagaría?** Evitar una sola parada importante puede cubrir el coste del servicio.
- **Problema para nosotros:** muchas pymes no tienen sensores, así que el cliente no tendría datos de partida y habría que venderle también hardware.

### Idea 4: Tensión social en Europa para empresas de logística

- **¿Qué problema existe?** Huelgas de transporte o de puertos, bloqueos de fronteras y crisis políticas en países europeos retrasan envíos sin que las empresas lo vean venir.
- **¿Quién tiene ese problema?** Empresas españolas exportadoras y empresas de transporte y logística que operan en Europa.
- **¿Por qué es importante?** Las cadenas de suministro europeas están muy conectadas: un bloqueo en un país afecta a envíos de muchos otros.
- **¿Qué pierde actualmente ese cliente?** Camiones y mercancía parados, penalizaciones por retraso y rutas alternativas más caras.
- **¿Cómo podrían ayudar los datos?** Con eventos extraídos de noticias (GDELT) y datos económicos (Eurostat) se podría calcular un índice de tensión por país y semana y avisar de subidas.
- **¿Por qué alguien pagaría?** Evitar unos pocos envíos bloqueados compensa el coste del servicio.
- **Problema para nosotros:** los datos basados en noticias tienen mucho ruido y miden la cobertura de los medios más que los hechos. Además, exigen una infraestructura pesada (BigQuery) y es difícil demostrar que las predicciones son fiables en el plazo del proyecto.

## 3. Comparación y elección

| Criterio | 1. Viviendas vacacionales | 2. Restaurantes | 3. Mantenimiento | 4. Tensión en Europa |
|---|---|---|---|---|
| Datos públicos de referencia | Sí, oficiales (ISTAC y Registro Turístico) | No | Solo sintéticos | Sí, pero con mucho ruido |
| El cliente tiene datos propios | Sí (reservas y precios) | Sí (ventas) | No (sin sensores) | Parcialmente (envíos) |
| Cliente fácil de identificar | Sí (viviendas registradas) | Sí | Medio | Medio |
| Prototipo viable en el plazo | Sí | Sí | Difícil | Arriesgado |
| Riesgo principal | Mercado limitado por la nueva ley | Poca referencia externa | El cliente necesita sensores | Validar las predicciones |

**Idea elegida: Idea 1 (precios y ocupación para viviendas vacacionales en Canarias).**

Motivos:
1. Combina **datos propios del cliente** (reservas y precios de cada vivienda) con **datos oficiales del mercado** actualizados cada mes desde 2019. Los datos del cliente aportan el detalle y los del ISTAC la referencia del mercado.
2. Permite estudiar cosas interesantes: la estacionalidad de invierno, la caída de 2020 por la pandemia y la recuperación posterior.
3. El impacto para el cliente se mide fácilmente en euros.
4. Es un tema de actualidad en Canarias, con una ley nueva que cambia el mercado.

## 4. La startup

| | |
|---|---|
| **Nombre** | NaitPrais (viene de "night price", precio por noche, escrito como se pronuncia en español) |
| **Sector** | PropTech / Turismo (software de análisis de datos) |
| **Qué hace** | Analiza el histórico de reservas de cada vivienda junto con los datos oficiales del mercado canario para recomendar qué precio poner cada mes y qué ocupación esperar. |
| **Cliente objetivo** | Gestoras pequeñas y medianas de viviendas vacacionales en Canarias (de 5 a 50 viviendas) y propietarios con varias viviendas inscritas en el Registro General Turístico. |
| **Problema que resuelve** | Precios fijos o puestos "a ojo" que no tienen en cuenta la temporada ni el mercado, y que provocan meses con poca ocupación o meses vendidos por debajo de lo que paga el mercado. |

**Propuesta de valor:**
> Te decimos qué precio poner a cada vivienda cada mes y qué ocupación esperar, combinando tu histórico de reservas con los datos oficiales del mercado canario.

**Servicios principales:**
1. **Precio recomendado** para cada vivienda y mes (rango mínimo y máximo).
2. **Previsión de ocupación** para los próximos meses.
3. **Comparativa con el mercado:** cómo está cada vivienda frente a la media de su municipio y de su tamaño.
4. **Panel de cartera:** para gestoras, qué viviendas están por encima o por debajo del mercado, con un resumen que pueden enseñar a los propietarios.

**Modelo de negocio (idea inicial):** suscripción mensual por vivienda. El objetivo es que la cuota se pague sola con lo que el cliente gana ajustando mejor sus precios en temporada alta.

## 5. Riesgos y cómo los tratamos

**La nueva ley limita el mercado.**
La Ley 6/2025, de Ordenación Sostenible del Uso Turístico de Viviendas, está en vigor desde el 13 de diciembre de 2025. Supedita las nuevas viviendas vacacionales al planeamiento de cada municipio y limita el uso turístico al 10 % de la edificabilidad residencial. En la práctica, las nuevas altas van a ser pocas, y el ISTAC ya refleja un 5 % menos de viviendas disponibles en enero de 2026 que un año antes.
*Cómo lo tratamos:* nuestro cliente son las viviendas que **ya están registradas**. Si casi no entran viviendas nuevas, las que ya existen tienen más interés en sacar el máximo partido a lo que tienen.

**Tema polémico.**
La vivienda vacacional está muy relacionada con el problema de acceso a la vivienda en Canarias.
*Cómo lo tratamos:* solo trabajamos con viviendas inscritas en el registro oficial. La herramienta no busca que haya más viviendas vacacionales, sino que las que ya son legales se gestionen mejor.

**Competencia.**
Ya existen herramientas de precios para alquiler vacacional.
*Cómo lo tratamos:* nos diferenciamos por ser sencillos, en español, centrados en Canarias, basados en datos oficiales y porque explicamos cada recomendación.

**Datos del cliente con distinta calidad.**
Cada gestora usa un programa distinto o incluso hojas de cálculo.
*Cómo lo tratamos:* empezamos con una importación sencilla desde CSV con un formato fijo.

## 6. Datos previstos (avance para las siguientes fases)

**Datos del cliente**

| Datos | Contenido |
|---|---|
| Viviendas | Municipio, número de plazas, tipo de vivienda |
| Reservas | Fechas de entrada y salida, precio por noche, canal de venta |

En el proyecto estos datos **se simularán** a partir de patrones reales del ISTAC (estacionalidad, ocupación y tarifas medias por municipio y tamaño), para que se parezcan a los de una gestora real.

**Datos públicos**

| Fuente | Qué contiene | Nivel de detalle | Formato |
|---|---|---|---|
| ISTAC: viviendas vacacionales por islas y municipios | Viviendas disponibles y reservadas, plazas, tasa de ocupación, estancia media e ingresos | Municipio y mes, desde 2019 | JSON, XML, TSV |
| ISTAC: tarifas medias por intervalos de plazas | Tarifa media según el tamaño de la vivienda | Mensual, desde 2019 | Banco de datos del ISTAC |
| Registro General Turístico de Canarias | Listado de viviendas vacacionales inscritas | Por vivienda | CSV, XLSX (con diccionario de datos) |

**Pendiente de comprobar en las siguientes fases**
- Qué columnas trae exactamente el registro y su calidad (valores vacíos o desconocidos).
- Que las tarifas del ISTAC se puedan cruzar con los datos de ocupación por municipio.
- Cuántos municipios tienen datos suficientes para usarlos como referencia.

## 7. Fuentes

- ISTAC, Estadística Experimental de Vivienda Vacacional (nota de enero de 2026): https://www.gobiernodecanarias.org/istac/.content/noticias/estadistica-experimental-vivienda-vacacional-noticia-2026-enero.html
- ISTAC, series mensuales y anuales sobre viviendas vacacionales (2019-2026): https://www3.gobiernodecanarias.org/istac/statistical-visualizer/visualizer/collection.html?resourceType=collection&agencyId=ISTAC&resourceId=C00065A_000003
- Portal de datos abiertos del Gobierno de Canarias, viviendas vacacionales por islas y municipios: https://datos.canarias.es/catalogos/general/dataset/viviendas-vacacionales-plazas-tasas-de-ocupacion-estancia-media-e-ingresos-islas-y-municipios-d
- Portal de datos abiertos del Gobierno de Canarias, Registro General Turístico (vivienda vacacional): https://datos.canarias.es/catalogos/general/dataset/establecimientos-extrahoteleros-de-tipologia-vivienda-vacacional-inscritos-en-el-registro
- Ley 6/2025, de 10 de diciembre, de Ordenación Sostenible del Uso Turístico de Viviendas (BOE): https://www.boe.es/diario_boe/txt.php?id=BOE-A-2025-26358
- GDELT Project (idea 4): https://www.gdeltproject.org/
