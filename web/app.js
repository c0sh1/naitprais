// =============================================================
// NaitPrais - interacción de la web
// 1. Calendario de la portada (precio actual / con NaitPrais)
// 2. Formulario de contacto (abre el correo con los datos)
// =============================================================

// ---------- 1. Calendario ----------
// Datos de febrero de 2026 de un apartamento de Tabaiba Stays (datos simulados del proyecto).
// "1" = noche reservada, "0" = noche libre.
const OCUPACION_FEBRERO = "1110111111111111111111111111";
const PRIMER_DIA_SEMANA = 6;          // el 1 de febrero de 2026 es domingo (lunes = 0)
const CARNAVAL = { desde: 12, hasta: 22 };

const PRECIOS = {
  actual: { normal: 100, carnaval: 100 },
  naitprais: { normal: 115, carnaval: 125 },
};

const EXPLICACIONES = {
  actual:
    "La gestora cobró 100\u00a0€ todas las noches, también en Carnaval. " +
    "El mes se llenó al 96\u00a0% y las reservas de Carnaval llegaron con casi un mes de antelación.",
  naitprais:
    "Con la ocupación que tuvo, 115\u00a0€ de base y 125\u00a0€ en Carnaval habrían dejado 515\u00a0€ más. " +
    "Es un máximo: con precios más altos puede entrar alguna reserva menos.",
};

const formatoEuros = new Intl.NumberFormat("es-ES", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 0,
});

function esCarnaval(dia) {
  return dia >= CARNAVAL.desde && dia <= CARNAVAL.hasta;
}

function pintarCalendario(modo) {
  const contenedor = document.getElementById("calendario-dias");
  if (!contenedor) return;

  contenedor.innerHTML = "";
  let total = 0;

  // Huecos antes del día 1
  for (let i = 0; i < PRIMER_DIA_SEMANA; i++) {
    const hueco = document.createElement("div");
    hueco.className = "dia dia--vacio";
    hueco.setAttribute("aria-hidden", "true");
    contenedor.appendChild(hueco);
  }

  for (let dia = 1; dia <= OCUPACION_FEBRERO.length; dia++) {
    const ocupada = OCUPACION_FEBRERO[dia - 1] === "1";
    const carnaval = esCarnaval(dia);
    const precio = carnaval ? PRECIOS[modo].carnaval : PRECIOS[modo].normal;
    const precioAntes = carnaval ? PRECIOS.actual.carnaval : PRECIOS.actual.normal;

    if (ocupada) total += precio;

    const celda = document.createElement("div");
    celda.className = "dia";
    if (ocupada) celda.classList.add("dia--ocupada");
    if (carnaval) celda.classList.add("dia--evento");
    if (precio !== precioAntes) celda.classList.add("dia--cambio");

    const estado = ocupada ? "reservada" : "libre";
    celda.setAttribute("aria-label", `${dia} de febrero, ${precio} euros, ${estado}`);
    celda.innerHTML = `
      <span class="dia__numero">${dia}</span>
      <span class="dia__precio">${precio}\u00a0€</span>
    `;
    contenedor.appendChild(celda);
  }

  document.getElementById("calendario-total").textContent = formatoEuros.format(total);
  document.getElementById("calendario-explicacion").textContent = EXPLICACIONES[modo];
}

function prepararSelector() {
  const botones = document.querySelectorAll(".selector__opcion");
  botones.forEach((boton) => {
    boton.addEventListener("click", () => {
      botones.forEach((b) => b.setAttribute("aria-pressed", "false"));
      boton.setAttribute("aria-pressed", "true");
      pintarCalendario(boton.dataset.modo);
    });
  });
}

// ---------- 2. Formulario ----------
function prepararFormulario() {
  const formulario = document.getElementById("formulario");
  const estado = document.getElementById("formulario-estado");
  if (!formulario) return;

  formulario.addEventListener("submit", (evento) => {
    evento.preventDefault();

    const nombre = formulario.nombre;
    const email = formulario.email;
    let correcto = true;

    [nombre, email].forEach((campo) => {
      const valido = campo.value.trim() !== "" && campo.checkValidity();
      campo.setAttribute("aria-invalid", valido ? "false" : "true");
      if (!valido) correcto = false;
    });

    if (!correcto) {
      estado.textContent = "Escribe tu nombre y un correo electrónico válido para continuar.";
      estado.className = "formulario__estado formulario__estado--error";
      return;
    }

    const asunto = `Demo de NaitPrais para ${nombre.value.trim()}`;
    const cuerpo =
      `Nombre: ${nombre.value.trim()}\n` +
      `Correo: ${email.value.trim()}\n` +
      `Viviendas que gestiono: ${formulario.viviendas.value}\n\n` +
      `${formulario.mensaje.value.trim()}`;

    window.location.href =
      `mailto:hola@naitprais.es?subject=${encodeURIComponent(asunto)}&body=${encodeURIComponent(cuerpo)}`;

    estado.textContent =
      "Hemos abierto tu programa de correo con la solicitud. Si no se ha abierto, escríbenos a hola@naitprais.es.";
    estado.className = "formulario__estado";
  });
}

pintarCalendario("actual");
prepararSelector();
prepararFormulario();
