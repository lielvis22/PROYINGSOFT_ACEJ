// JavaScript básico del sistema:
//  1) abrir y cerrar las ventanas emergentes
//  2) validar los campos mientras el usuario escribe (RNF-02)
// Python vuelve a validar todo en el servidor, por seguridad (ADR-004).

// ---------- 1. Ventanas emergentes ----------
function abrirVentana(id) {
  document.getElementById(id).showModal();
}

function cerrarVentana(id) {
  document.getElementById(id).close();
}

// Si el servidor devolvió errores, la página trae data-abrir="true" y la ventana se abre sola
window.onload = function () {
  let ventanas = document.querySelectorAll("dialog[data-abrir='true']");
  for (let i = 0; i < ventanas.length; i++) {
    ventanas[i].showModal();
  }
};

// ---------- 2. Validación mientras se escribe ----------
function mostrarError(campo, mensaje) {
  let texto = document.getElementById("error-" + campo.name);
  if (mensaje === "") {
    campo.classList.remove("campo-error");
  } else {
    campo.classList.add("campo-error");
  }
  if (texto) {
    texto.innerText = mensaje;
  }
}

function validarCampo(campo) {
  let valor = campo.value.trim();
  let mensaje = "";

  if (valor === "") {
    mensaje = "Este campo es obligatorio.";
  } else if (campo.name === "nombre" && valor.split(" ").length < 2) {
    mensaje = "Escriba nombre y apellido.";
  } else if (campo.name === "cedula" && !/^\d{1,2}-\d{1,4}-\d{1,6}$/.test(valor)) {
    mensaje = "Cédula no válida. Ejemplo: 8-123-4567.";
  } else if (campo.name === "telefono" && !/^\d{3,4}-?\d{4}$/.test(valor)) {
    mensaje = "Teléfono no válido. Ejemplo: 6000-0000.";
  } else if (campo.name === "correo" && (!valor.includes("@") || !valor.includes("."))) {
    mensaje = "Correo no válido. Ejemplo: correo@ejemplo.com.";
  } else if (campo.name === "abono") {
    // CU-01: el abono debe ser al menos el 50 % de la tarifa del curso elegido
    let curso = document.getElementById("curso");
    let tarifa = Number(curso.options[curso.selectedIndex].dataset.tarifa);
    if (tarifa > 0 && Number(valor) < tarifa * 0.5) {
      mensaje = "El abono mínimo es B/. " + (tarifa * 0.5).toFixed(2) + ".";
    }
  } else if (campo.name === "monto") {
    // CU-04: el monto debe ser mayor que 0 y no puede pasar lo que el alumno debe
    let alumno = document.getElementById("alumno");
    let saldo = Number(alumno.options[alumno.selectedIndex].dataset.saldo);
    if (Number(valor) <= 0) {
      mensaje = "Monto no válido: debe ser mayor que 0.";
    } else if (saldo > 0 && Number(valor) > saldo) {
      mensaje = "Monto no válido: supera el saldo de B/. " + saldo.toFixed(2) + ".";
    }
  }
  mostrarError(campo, mensaje);
  return mensaje === "";
}

// Antes de enviar, revisa todos los campos marcados con la clase "validar".
// Si alguno está mal, el formulario no se envía.
function validarFormulario(formulario) {
  let campos = formulario.querySelectorAll(".validar");
  let todoBien = true;
  for (let i = 0; i < campos.length; i++) {
    if (!validarCampo(campos[i])) {
      todoBien = false;
    }
  }
  // CU-04: la referencia es obligatoria si el pago no es en efectivo
  let referencia = formulario.querySelector("[name=referencia]");
  if (referencia) {
    let metodo = formulario.querySelector("[name=metodo]").value;
    if (metodo !== "Efectivo" && referencia.value.trim() === "") {
      mostrarError(referencia, "La referencia es obligatoria para transferencia o tarjeta.");
      todoBien = false;
    } else {
      mostrarError(referencia, "");
    }
  }
  return todoBien;
}
