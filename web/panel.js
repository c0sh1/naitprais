// =============================================================
// NaitPrais - Panel de precios
// Lee assets/recomendaciones.json (generado con src/recommend.py)
// =============================================================

const COLORES = { actual: "#9A958F", recomendado: "#103A5C", acento: "#B3336B" };

const estado = {
  datos: null,
  mes: null,
  municipio: "",
  segmento: "",
  soloCambios: false,
  vivienda: null,
  precioSimulado: null,
};

const euros = new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });
const eurosConSigno = (n) => (n > 0 ? "+" : n < 0 ? "−" : "") + euros.format(Math.abs(n));
const porcentaje = (n) => `${Math.round(n * 100)}\u00a0%`;
const $ = (id) => document.getElementById(id);
const capitalizar = (texto) => texto.charAt(0).toUpperCase() + texto.slice(1);

// ---------- Datos ----------
function viviendasFiltradas() {
  return estado.datos.viviendas.filter(
    (v) =>
      (!estado.municipio || v.municipio === estado.municipio) &&
      (!estado.segmento || v.segmento === estado.segmento)
  );
}

function recomendacion(idVivienda, periodo, tipoDia) {
  return estado.datos.indice[`${idVivienda}|${periodo}|${tipoDia}`];
}

// Resumen de una vivienda en un mes (días normales + fechas especiales)
function resumenVivienda(v, periodo) {
  const normal = recomendacion(v.id, periodo, "normal");
  const especial = recomendacion(v.id, periodo, "especial");
  const partes = [normal, especial].filter(Boolean);
  return {
    vivienda: v,
    normal,
    especial,
    ingresosActuales: partes.reduce((s, r) => s + r.ia, 0),
    ingresosRecomendados: partes.reduce((s, r) => s + r.ir, 0),
    ganancia: partes.reduce((s, r) => s + r.g, 0),
  };
}

function resumenMes(periodo) {
  return viviendasFiltradas().map((v) => resumenVivienda(v, periodo));
}

// ---------- Resumen del mes ----------
function pintarCifras(filas) {
  const actual = filas.reduce((s, f) => s + f.ingresosActuales, 0);
  const recomendado = filas.reduce((s, f) => s + f.ingresosRecomendados, 0);
  const diferencia = recomendado - actual;
  const subir = filas.filter((f) => f.normal && f.normal.a === "Subir").length;
  const bajar = filas.filter((f) => f.normal && f.normal.a === "Bajar").length;

  $("cifra-actual").textContent = euros.format(actual);
  $("cifra-recomendado").textContent = euros.format(recomendado);
  $("cifra-diferencia").innerHTML = actual
    ? `${eurosConSigno(diferencia)} <span class="cifra__extra">${diferencia >= 0 ? "+" : ""}${((diferencia / actual) * 100).toFixed(1).replace(".", ",")}\u00a0%</span>`
    : "–";
  $("cifra-cambios").textContent = `Subir ${subir}, bajar ${bajar}, mantener ${filas.length - subir - bajar}`;
}

function pintarAvisoEvento(filas) {
  const aviso = $("aviso-evento");
  const conEvento = filas.filter((f) => f.especial);
  if (!conEvento.length) {
    aviso.hidden = true;
    return;
  }
  const nombre = conEvento[0].especial.e;
  const dias = conEvento[0].especial.d;
  const suben = conEvento.filter((f) => f.especial.a === "Subir");
  const subidaMedia = suben.length
    ? suben.reduce((s, f) => s + (f.especial.pr / f.especial.pa - 1), 0) / suben.length
    : 0;
  const extra = conEvento.reduce((s, f) => s + f.especial.g, 0);
  aviso.hidden = false;
  aviso.innerHTML = `
    <strong>Fechas especiales este mes: ${nombre} (${dias} días).</strong>
    Recomendamos subir el precio en ${suben.length} de ${conEvento.length} viviendas,
    un ${Math.round(subidaMedia * 100)}\u00a0% de media, porque estas fechas se reservan con mucha antelación.
    Ingresos extra esperados: ${eurosConSigno(extra)}.`;
}

// ---------- Prioridades ----------
function textoAccion(r) {
  if (r.a === "Mantener") return `Mantener ${euros.format(r.pa)}`;
  return `${r.a} de ${euros.format(r.pa)} a ${euros.format(r.pr)}`;
}

function pintarPrioridades(filas) {
  const lista = $("prioridades");
  const top = filas.filter((f) => f.ganancia > 0).sort((a, b) => b.ganancia - a.ganancia).slice(0, 5);
  if (!top.length) {
    lista.innerHTML = `<li class="prioridades__vacia">Este mes no hay cambios que mejoren los ingresos con los filtros elegidos.</li>`;
    return;
  }
  lista.innerHTML = top
    .map((f) => {
      const principal = f.normal && f.normal.a !== "Mantener" ? f.normal : f.especial || f.normal;
      const etiqueta = principal.t === "especial" ? `En ${principal.e}: ` : "";
      return `
        <li>
          <button type="button" class="prioridad" data-vivienda="${f.vivienda.id}">
            <span class="prioridad__nombre">${f.vivienda.nombre}</span>
            <span class="prioridad__accion prioridad__accion--${principal.a.toLowerCase()}">${etiqueta}${textoAccion(principal)}</span>
            <span class="prioridad__motivo">${principal.m}</span>
            <span class="prioridad__ganancia">${eurosConSigno(f.ganancia)} este mes</span>
          </button>
        </li>`;
    })
    .join("");
  lista.querySelectorAll(".prioridad").forEach((b) =>
    b.addEventListener("click", () => abrirDetalle(Number(b.dataset.vivienda)))
  );
}

// ---------- Gráficos (SVG sencillo) ----------
function graficoBarras(contenedor, etiquetas, series, opciones = {}) {
  const ancho = 640;
  const alto = 240;
  const margen = { arriba: 12, derecha: 8, abajo: 34, izquierda: 56 };
  const w = ancho - margen.izquierda - margen.derecha;
  const h = alto - margen.arriba - margen.abajo;
  const maximo = Math.max(...series.flatMap((s) => s.valores)) * 1.1 || 1;
  const grupo = w / etiquetas.length;
  const barra = (grupo * 0.7) / series.length;
  const y = (valor) => margen.arriba + h - (valor / maximo) * h;

  let svg = `<svg viewBox="0 0 ${ancho} ${alto}" role="img" aria-label="${opciones.titulo || "Gráfico"}">`;
  for (let i = 0; i <= 4; i++) {
    const valor = (maximo / 4) * i;
    svg += `<line x1="${margen.izquierda}" x2="${ancho - margen.derecha}" y1="${y(valor)}" y2="${y(valor)}" class="grafico__linea"/>`;
    svg += `<text x="${margen.izquierda - 6}" y="${y(valor) + 4}" text-anchor="end" class="grafico__eje">${opciones.formato ? opciones.formato(valor) : Math.round(valor)}</text>`;
  }
  etiquetas.forEach((etiqueta, i) => {
    const x0 = margen.izquierda + i * grupo;
    if (i === opciones.resaltado) {
      svg += `<rect x="${x0}" y="${margen.arriba}" width="${grupo}" height="${h}" class="grafico__resaltado"/>`;
    }
    series.forEach((s, j) => {
      const valor = s.valores[i];
      const x = x0 + grupo * 0.15 + j * barra;
      svg += `<rect x="${x}" y="${y(valor)}" width="${barra - 2}" height="${margen.arriba + h - y(valor)}" fill="${s.color}" rx="2"><title>${etiqueta}, ${s.nombre}: ${opciones.formato ? opciones.formato(valor) : valor}</title></rect>`;
    });
    svg += `<text x="${x0 + grupo / 2}" y="${alto - 14}" text-anchor="middle" class="grafico__eje">${etiqueta}</text>`;
    if (opciones.alPulsar) {
      svg += `<rect x="${x0}" y="${margen.arriba}" width="${grupo}" height="${h + 20}" fill="transparent" class="grafico__zona" data-indice="${i}"><title>Ver ${etiqueta}</title></rect>`;
    }
  });
  svg += `</svg>`;
  const leyenda = series
    .map((s) => `<span><i style="background:${s.color}"></i>${s.nombre}</span>`)
    .join("");
  contenedor.innerHTML = svg + `<div class="grafico__leyenda">${leyenda}</div>`;

  if (opciones.alPulsar) {
    contenedor.querySelectorAll(".grafico__zona").forEach((zona) =>
      zona.addEventListener("click", () => opciones.alPulsar(Number(zona.dataset.indice)))
    );
  }
}

const mesCorto = (periodo) => {
  const [anio, mes] = periodo.split("-");
  const nombres = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
  return `${nombres[Number(mes) - 1]} ${anio.slice(2)}`;
};
const miles = (n) => (n >= 1000 ? `${Math.round(n / 1000)} mil` : `${Math.round(n)}`);

function pintarGraficoAnual() {
  const meses = estado.datos.meses.map((m) => m.periodo);
  const totales = meses.map((p) => {
    const filas = resumenMes(p);
    return {
      actual: filas.reduce((s, f) => s + f.ingresosActuales, 0),
      recomendado: filas.reduce((s, f) => s + f.ingresosRecomendados, 0),
    };
  });
  graficoBarras(
    $("grafico-anual"),
    meses.map(mesCorto),
    [
      { nombre: "Con tus precios", color: COLORES.actual, valores: totales.map((t) => t.actual) },
      { nombre: "Con NaitPrais", color: COLORES.recomendado, valores: totales.map((t) => t.recomendado) },
    ],
    {
      titulo: "Ingresos esperados por mes",
      formato: (v) => `${miles(v)} €`,
      resaltado: meses.indexOf(estado.mes),
      alPulsar: (i) => {
        estado.mes = meses[i];
        $("filtro-mes").value = estado.mes;
        pintarTodo();
      },
    }
  );
  const actual = totales.reduce((s, t) => s + t.actual, 0);
  const recomendado = totales.reduce((s, t) => s + t.recomendado, 0);
  const comision = (recomendado - actual) * estado.datos.comision_gestora;
  $("total-anual").innerHTML =
    `En 12 meses: <strong>${eurosConSigno(recomendado - actual)}</strong> para los propietarios ` +
    `(${(((recomendado - actual) / actual) * 100).toFixed(1).replace(".", ",")}\u00a0%), ` +
    `de los que <strong>${eurosConSigno(comision)}</strong> son comisión para la gestora.`;
}

// ---------- Tabla ----------
function pintarTabla(filas) {
  const cuerpo = $("tabla-cuerpo");
  let lista = [...filas].sort((a, b) => b.ganancia - a.ganancia);
  if (estado.soloCambios) {
    lista = lista.filter(
      (f) => (f.normal && f.normal.a !== "Mantener") || (f.especial && f.especial.a !== "Mantener")
    );
  }
  if (!lista.length) {
    cuerpo.innerHTML = `<tr><td colspan="7">No hay viviendas con cambios para estos filtros.</td></tr>`;
    return;
  }
  cuerpo.innerHTML = lista
    .map((f) => {
      const r = f.normal;
      let accion = r.a;
      if (r.a === "Mantener" && f.especial && f.especial.a !== "Mantener") {
        accion = `${f.especial.a} en ${f.especial.e}`;
      }
      const claseAccion = accion.split(" ")[0].toLowerCase();
      const etiquetaEvento = f.especial ? `<span class="etiqueta-evento">${f.especial.e}: ${euros.format(f.especial.pr)}</span>` : "";
      return `
        <tr data-vivienda="${f.vivienda.id}" tabindex="0" class="${estado.vivienda === f.vivienda.id ? "fila-activa" : ""}">
          <td>${f.vivienda.nombre}</td>
          <td>${f.vivienda.segmento}</td>
          <td class="num">${euros.format(r.pa)}</td>
          <td class="num"><strong>${euros.format(r.pr)}</strong>${etiquetaEvento}</td>
          <td class="num">${porcentaje(r.oa)} → ${porcentaje(r.or)}</td>
          <td class="num">${eurosConSigno(f.ganancia)}</td>
          <td><span class="accion accion--${claseAccion}">${accion}</span></td>
        </tr>`;
    })
    .join("");
  cuerpo.querySelectorAll("tr[data-vivienda]").forEach((fila) => {
    const abrir = () => abrirDetalle(Number(fila.dataset.vivienda));
    fila.addEventListener("click", abrir);
    fila.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        abrir();
      }
    });
  });
}

// ---------- Detalle y simulador ----------
function abrirDetalle(idVivienda) {
  estado.vivienda = idVivienda;
  estado.precioSimulado = null;
  pintarTodo();
  $("detalle").scrollIntoView({ behavior: "smooth", block: "start" });
  $("detalle").focus({ preventScroll: true });
}

function ocupacionEsperada(r, precio, vivienda) {
  const efecto = estado.datos.modelo.efecto_precio;
  const z = r.l + efecto * Math.log(precio / vivienda.precio_medio);
  return 1 / (1 + Math.exp(-z));
}

function pintarDetalle() {
  const seccion = $("detalle");
  const v = estado.datos.viviendas.find((x) => x.id === estado.vivienda);
  if (!v) {
    seccion.hidden = true;
    return;
  }
  seccion.hidden = false;
  const r = recomendacion(v.id, estado.mes, "normal");
  const extras = [v.piscina ? "piscina" : null, v.vista_mar ? "vistas al mar" : null].filter(Boolean);

  $("detalle-titulo").textContent = v.nombre;
  $("detalle-datos").textContent =
    `${v.isla}. Segmento: ${v.segmento}.` + (extras.length ? ` Con ${extras.join(" y ")}.` : "");
  $("detalle-motivo").textContent = `${capitalizar(estado.datos.mesesNombre[estado.mes])}: ${r.m}`;

  const meses = estado.datos.meses.map((m) => m.periodo);
  const normales = meses.map((p) => recomendacion(v.id, p, "normal"));
  graficoBarras(
    $("grafico-vivienda"),
    meses.map(mesCorto),
    [
      { nombre: "Precio actual", color: COLORES.actual, valores: normales.map((x) => x.pa) },
      { nombre: "Precio recomendado", color: COLORES.recomendado, valores: normales.map((x) => x.pr) },
    ],
    {
      titulo: "Precio por mes",
      formato: (x) => `${Math.round(x)} €`,
      resaltado: meses.indexOf(estado.mes),
      alPulsar: (i) => {
        estado.mes = meses[i];
        estado.precioSimulado = null;
        $("filtro-mes").value = estado.mes;
        pintarTodo();
      },
    }
  );

  // Simulador
  const rango = $("sim-rango");
  const minimo = Math.max(20, Math.round((r.pa * 0.6) / 5) * 5);
  const maximo = Math.round((r.pa * 1.5) / 5) * 5;
  rango.min = minimo;
  rango.max = maximo;
  if (estado.precioSimulado === null) estado.precioSimulado = r.pr;
  rango.value = estado.precioSimulado;
  $("simulador-titulo").textContent = `Simulador: ${estado.datos.mesesNombre[estado.mes]}`;
  pintarSimulacion(r, v);
}

function pintarSimulacion(r, v) {
  const precio = Number($("sim-rango").value);
  const ocupacion = ocupacionEsperada(r, precio, v);
  const ingresos = precio * ocupacion * r.d;
  $("sim-precio").textContent = euros.format(precio);
  $("sim-ocupacion").textContent = porcentaje(ocupacion);
  $("sim-noches").textContent = `${(ocupacion * r.d).toFixed(1).replace(".", ",")} de ${r.d}`;
  $("sim-ingresos").textContent = euros.format(ingresos);
  $("sim-diferencia").textContent = eurosConSigno(ingresos - r.ia);
}

// ---------- Explicación ----------
function pintarExplicacion() {
  const m = estado.datos.modelo;
  $("explicacion-modelo").textContent =
    `Probado con enero-agosto de 2026 (meses que el modelo no había visto), la ocupación mensual de cada vivienda ` +
    `se predice con un error medio de ${String(m.error_mensual_pts).replace(".", ",")} puntos, frente a ` +
    `${String(m.error_referencia_pts).replace(".", ",")} si se repite la ocupación de años anteriores.`;
  $("tabla-sensibilidad").innerHTML = estado.datos.sensibilidad
    .map(
      (s) => `
      <tr class="${s.efecto_precio === m.efecto_precio ? "fila-activa" : ""}">
        <td>${String(s.efecto_precio).replace(".", ",")}${s.efecto_precio === m.efecto_precio ? " (usado)" : ""}${s.efecto_precio === Math.round(m.efecto_precio_central * 10) / 10 ? " (estimado)" : ""}</td>
        <td class="num">+${String(s.mejora_ingresos_pct).replace(".", ",")}\u00a0%</td>
        <td class="num">${s.subir}</td>
        <td class="num">${s.mantener}</td>
        <td class="num">${s.bajar}</td>
      </tr>`
    )
    .join("");
}

// ---------- Todo junto ----------
function pintarTodo() {
  const filas = resumenMes(estado.mes);
  $("panel-sub").textContent =
    `${estado.datos.cliente}: ${viviendasFiltradas().length} viviendas, ` +
    `${estado.datos.mesesNombre[estado.mes]}. Datos hasta agosto de 2026.`;
  pintarCifras(filas);
  pintarAvisoEvento(filas);
  pintarPrioridades(filas);
  pintarGraficoAnual();
  pintarTabla(filas);
  pintarDetalle();
}

function prepararFiltros() {
  const d = estado.datos;
  $("filtro-mes").innerHTML = d.meses
    .map((m) => `<option value="${m.periodo}">${m.nombre[0].toUpperCase() + m.nombre.slice(1)}</option>`)
    .join("");
  const municipios = [...new Set(d.viviendas.map((v) => v.municipio))].sort();
  const segmentos = [...new Set(d.viviendas.map((v) => v.segmento))].sort();
  $("filtro-municipio").innerHTML += municipios.map((m) => `<option>${m}</option>`).join("");
  $("filtro-segmento").innerHTML += segmentos.map((s) => `<option>${s}</option>`).join("");

  $("filtro-mes").addEventListener("change", (e) => {
    estado.mes = e.target.value;
    estado.precioSimulado = null;
    pintarTodo();
  });
  $("filtro-municipio").addEventListener("change", (e) => {
    estado.municipio = e.target.value;
    pintarTodo();
  });
  $("filtro-segmento").addEventListener("change", (e) => {
    estado.segmento = e.target.value;
    pintarTodo();
  });
  $("solo-cambios").addEventListener("change", (e) => {
    estado.soloCambios = e.target.checked;
    pintarTabla(resumenMes(estado.mes));
  });
  $("detalle-cerrar").addEventListener("click", () => {
    estado.vivienda = null;
    pintarTodo();
  });
  $("sim-rango").addEventListener("input", () => {
    const v = d.viviendas.find((x) => x.id === estado.vivienda);
    const r = recomendacion(v.id, estado.mes, "normal");
    estado.precioSimulado = Number($("sim-rango").value);
    pintarSimulacion(r, v);
  });
  const fijarPrecio = (campo) => () => {
    const r = recomendacion(estado.vivienda, estado.mes, "normal");
    $("sim-rango").value = r[campo];
    $("sim-rango").dispatchEvent(new Event("input"));
  };
  $("sim-actual").addEventListener("click", fijarPrecio("pa"));
  $("sim-recomendado").addEventListener("click", fijarPrecio("pr"));
}

async function iniciar() {
  try {
    const respuesta = await fetch("assets/recomendaciones.json");
    if (!respuesta.ok) throw new Error(respuesta.status);
    const datos = await respuesta.json();
    datos.indice = {};
    datos.recomendaciones.forEach((r) => (datos.indice[`${r.v}|${r.p}|${r.t}`] = r));
    datos.mesesNombre = Object.fromEntries(datos.meses.map((m) => [m.periodo, m.nombre]));
    estado.datos = datos;
    // Empezamos en diciembre: el mes con más cambios y con Navidad
    estado.mes = datos.meses.some((m) => m.periodo === "2026-12") ? "2026-12" : datos.meses[0].periodo;
    prepararFiltros();
    $("filtro-mes").value = estado.mes;
    pintarExplicacion();
    pintarTodo();
  } catch (error) {
    $("aviso-error").hidden = false;
    $("panel-sub").textContent = "";
    console.error(error);
  }
}

iniciar();
