# CAPA DE PRESENTACIÓN: recibe lo que el usuario hace en el navegador,
# llama al servicio que corresponde (capa de negocio) y muestra la página HTML.
import time

from flask import abort, flash, redirect, render_template, request, session, Response

import config
from app import app
from app.negocio import pdf, servicio_alumnos, servicio_certificados, servicio_pagos, servicio_usuarios


# ===================== SEGURIDAD (RNF-03 y RF-09) =====================

def revisar_acceso(roles_permitidos):
    """Se llama al inicio de cada página. Devuelve None si el usuario puede entrar.
    Si no, devuelve a dónde mandarlo. Se revisa en el servidor, así que no sirve escribir la URL a mano."""
    # 1. ¿Inició sesión?
    if "usuario" not in session:
        return redirect("/login")

    # 2. ¿Pasaron más de 15 minutos sin usar el sistema?
    segundos_sin_uso = time.time() - session["ultimo_uso"]
    if segundos_sin_uso > config.MINUTOS_SESION * 60:
        session.clear()
        flash("Su sesión expiró por inactividad. Inicie sesión de nuevo.")
        return redirect("/login")
    session["ultimo_uso"] = time.time()

    # 3. ¿Su rol tiene permiso para esta página?
    if session["usuario"]["rol"] not in roles_permitidos:
        abort(403)
    return None


@app.errorhandler(403)
def sin_permiso(error):
    return render_template("error.html", mensaje="Su rol no tiene permiso para esta página."), 403


@app.errorhandler(404)
def no_existe(error):
    if "usuario" not in session:
        return redirect("/login")
    return render_template("error.html", mensaje="La página no existe."), 404


@app.errorhandler(500)
def error_interno(error):
    if "usuario" not in session:
        return redirect("/login")
    return render_template("error.html", mensaje="Ocurrió un error. No se guardó ningún cambio."), 500


# ===================== INICIO DE SESIÓN =====================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ok, resultado = servicio_usuarios.iniciar_sesion(request.form["usuario"], request.form["clave"])
        if not ok:
            return render_template("login.html", error=resultado), 401
        session["usuario"] = resultado
        session["ultimo_uso"] = time.time()
        return redirect("/")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/")
def inicio():
    respuesta = revisar_acceso(["Recepcionista", "Administrador", "Instructor"])
    if respuesta:
        return respuesta
    return render_template("inicio.html", pagina="inicio", resumen=servicio_alumnos.resumen())


@app.route("/bitacora")
def bitacora():
    respuesta = revisar_acceso(["Administrador"])
    if respuesta:
        return respuesta
    return render_template("bitacora.html", pagina="bitacora", registros=servicio_usuarios.leer_bitacora())


# ===================== CU-01 REGISTRAR ALUMNO =====================

def mostrar_alumnos(errores, datos, abrir, motivos):
    """Muestra la página Alumnos. Si "abrir" es True, la ventana del formulario se abre sola."""
    buscar = request.args.get("buscar", "")
    return render_template("alumnos.html", pagina="alumnos",
                           alumnos=servicio_alumnos.listar_alumnos(buscar), buscar=buscar,
                           cursos=servicio_alumnos.listar_cursos(),
                           errores=errores, datos=datos, abrir=abrir, motivos=motivos)


@app.route("/alumnos")
def alumnos():
    respuesta = revisar_acceso(["Recepcionista", "Administrador"])
    if respuesta:
        return respuesta
    abrir = request.args.get("nuevo") == "1"
    return mostrar_alumnos({}, {}, abrir, None)


@app.route("/alumnos/nuevo", methods=["POST"])
def alumno_nuevo():
    respuesta = revisar_acceso(["Recepcionista"])
    if respuesta:
        return respuesta
    ok, resultado = servicio_alumnos.registrar_alumno(request.form, session["usuario"])
    if ok:
        flash(resultado)
        return redirect("/alumnos")
    # Hubo errores: se vuelve a abrir la ventana con los mensajes en rojo
    return mostrar_alumnos(resultado, request.form, True, None), 422


# ===================== CU-04 GESTIONAR PAGOS =====================

def mostrar_pagos(errores, datos, abrir):
    return render_template("pagos.html", pagina="pagos", pagos=servicio_pagos.listar_pagos(),
                           resumen=servicio_alumnos.resumen(), alumnos=servicio_pagos.alumnos_que_deben(),
                           metodos=config.METODOS_PAGO, errores=errores, datos=datos, abrir=abrir)


@app.route("/pagos")
def pagos():
    respuesta = revisar_acceso(["Recepcionista"])
    if respuesta:
        return respuesta
    abrir = request.args.get("nuevo") == "1"
    return mostrar_pagos({}, request.args, abrir)


@app.route("/pagos/nuevo", methods=["POST"])
def pago_nuevo():
    respuesta = revisar_acceso(["Recepcionista"])
    if respuesta:
        return respuesta
    ok, resultado = servicio_pagos.registrar_pago(request.form, session["usuario"])
    if ok:
        flash(resultado)
        return redirect("/pagos")
    return mostrar_pagos(resultado, request.form, True), 422


@app.route("/pagos/recibo/<int:id_pago>")
def recibo(id_pago):
    respuesta = revisar_acceso(["Recepcionista", "Administrador"])
    if respuesta:
        return respuesta
    pago = servicio_pagos.buscar_pago(id_pago)
    if pago is None:
        abort(404)
    return Response(pdf.recibo_pdf(pago), mimetype="application/pdf")


# ===================== CU-03 GENERAR CERTIFICADO =====================

@app.route("/certificados")
def certificados():
    respuesta = revisar_acceso(["Administrador"])
    if respuesta:
        return respuesta
    return render_template("certificados.html", pagina="certificados", certificados=servicio_certificados.listar_certificados())


@app.route("/certificados/generar/<int:id_alumno>", methods=["POST"])
def generar_certificado(id_alumno):
    respuesta = revisar_acceso(["Administrador"])
    if respuesta:
        return respuesta

    ok, resultado = servicio_certificados.generar_certificado(id_alumno, session["usuario"])
    if ok:
        flash(resultado)
        return redirect("/certificados")
    # No cumple: se muestra la lista de alumnos con el cuadro "No se puede generar el certificado"
    return mostrar_alumnos({}, {}, False, resultado), 409


@app.route("/certificados/<int:id_certificado>/pdf")
def certificado_pdf(id_certificado):
    respuesta = revisar_acceso(["Administrador"])
    if respuesta:
        return respuesta
    certificado, alumno = servicio_certificados.buscar_certificado_y_alumno(id_certificado)
    if certificado is None:
        abort(404)
    return Response(pdf.certificado_pdf(certificado, alumno), mimetype="application/pdf")
