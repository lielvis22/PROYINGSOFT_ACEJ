# CU-04 GESTIONAR PAGOS, FACTURAS Y RECIBOS  (en el VOPC: "ControlGestionarPagos")
import config
from app.datos import repositorios
from app.datos.base_datos import conectar
from app.negocio.validaciones import convertir_a_numero


def listar_pagos():
    con = conectar()
    pagos = repositorios.leer_pagos(con)
    con.close()
    return pagos


def alumnos_que_deben():
    """Solo los alumnos con saldo pendiente aparecen en la lista para pagar."""
    lista = []
    for alumno in listar_alumnos_todos():
        if alumno["saldo"] > 0:
            lista.append(alumno)
    return lista


def listar_alumnos_todos():
    con = conectar()
    alumnos = repositorios.leer_alumnos(con, "")
    con.close()
    return alumnos


def buscar_pago(id_pago):
    con = conectar()
    pago = repositorios.buscar_pago(con, id_pago)
    con.close()
    return pago


def registrar_pago(formulario, usuario):
    """Devuelve (True, mensaje de éxito) o (False, diccionario de errores)."""
    id_alumno = formulario.get("id_alumno", "")
    monto = convertir_a_numero(formulario.get("monto", ""))
    metodo = formulario.get("metodo", "")
    referencia = formulario.get("referencia", "").strip()
    con = conectar()

    # Paso 1: buscar la factura del alumno
    factura = repositorios.buscar_factura(con, id_alumno)

    # Paso 2: validar (excepción del CU: "monto no válido")
    errores = {}
    if factura is None:
        errores["id_alumno"] = "Seleccione el alumno."
    if monto is None or monto <= 0:
        errores["monto"] = "Monto no válido: debe ser mayor que 0."
    elif factura is not None and monto > factura["saldo"]:
        errores["monto"] = "Monto no válido: supera el saldo de B/. " + format(factura["saldo"], ".2f") + "."
    if metodo not in config.METODOS_PAGO:
        errores["metodo"] = "Seleccione el método de pago."
    if metodo != "Efectivo" and referencia == "":
        errores["referencia"] = "La referencia es obligatoria para transferencia o tarjeta."

    if len(errores) > 0:
        con.close()
        return False, errores

    # Paso 3: guardar el pago, bajar el saldo y crear el recibo, todo junto (transacción)
    try:
        id_pago = repositorios.guardar_pago(con, factura["id_factura"], monto, metodo, referencia, usuario["id_usuario"])
        nuevo_saldo = factura["saldo"] - monto
        repositorios.cambiar_saldo(con, factura["id_factura"], nuevo_saldo)
        repositorios.guardar_en_bitacora(con, usuario["usuario"], "REGISTRAR_PAGO", "REC-" + str(id_pago))
        con.commit()
    except Exception:
        con.rollback()
        con.close()
        raise
    con.close()

    # Flujo alterno: pago parcial
    if nuevo_saldo > 0:
        estado = "Pago parcial: todavía debe B/. " + format(nuevo_saldo, ".2f") + "."
    else:
        estado = "La cuenta quedó al día."
    return True, "Pago registrado. Recibo REC-" + str(id_pago) + " por B/. " + format(monto, ".2f") + ". " + estado
