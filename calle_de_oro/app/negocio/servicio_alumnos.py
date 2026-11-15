# CU-01 REGISTRAR ALUMNO  (en el VOPC: clase de control "controlRegistrarAlumno")
import config
from app.datos import repositorios
from app.datos.base_datos import conectar
from app.negocio.validaciones import convertir_a_numero, validar_datos_alumno


def listar_alumnos(texto_buscado=""):
    con = conectar()
    alumnos = repositorios.leer_alumnos(con, texto_buscado)
    con.close()
    return alumnos


def listar_cursos():
    con = conectar()
    cursos = repositorios.leer_cursos(con)
    con.close()
    return cursos


def registrar_alumno(formulario, usuario):
    """Devuelve (True, mensaje de éxito) o (False, diccionario de errores)."""
    datos = {
        "nombre": formulario.get("nombre", "").strip(),
        "cedula": formulario.get("cedula", "").strip(),
        "telefono": formulario.get("telefono", "").strip(),
        "correo": formulario.get("correo", "").strip(),
        "direccion": formulario.get("direccion", "").strip(),
        "id_curso": formulario.get("id_curso", ""),
        "tipo_vehiculo": formulario.get("tipo_vehiculo", ""),
    }
    abono = convertir_a_numero(formulario.get("abono", ""))
    con = conectar()

    # Paso 1: revisar que los campos estén bien escritos
    errores = validar_datos_alumno(datos)

    # Paso 2: el curso debe existir
    curso = repositorios.buscar_curso(con, datos["id_curso"])
    if curso is None:
        errores["id_curso"] = "Seleccione el curso."

    # Paso 3: regla del negocio, el abono debe ser al menos el 50 % de la tarifa
    if curso is not None:
        minimo = curso["tarifa"] * config.ABONO_MINIMO
        if abono is None or abono < minimo:
            errores["abono"] = "El abono mínimo es B/. " + format(minimo, ".2f") + " (50 % de la tarifa)."
        elif abono > curso["tarifa"]:
            errores["abono"] = "El abono no puede ser mayor que la tarifa."

    # Paso 4: no puede haber dos alumnos con la misma cédula
    if repositorios.existe_cedula(con, datos["cedula"]):
        errores["cedula"] = "Ya existe un alumno con esta cédula."

    if len(errores) > 0:
        con.close()
        return False, errores

    # Paso 5: guardar TODO junto (transacción). Si algo falla, no se guarda nada (rollback).
    try:
        id_alumno = repositorios.guardar_alumno(con, datos)
        repositorios.crear_expediente(con, id_alumno)
        id_factura = repositorios.crear_factura(con, id_alumno, curso["tarifa"])
        id_pago = repositorios.guardar_pago(con, id_factura, abono, "Efectivo", "Abono inicial", usuario["id_usuario"])
        saldo = curso["tarifa"] - abono
        repositorios.cambiar_saldo(con, id_factura, saldo)
        repositorios.guardar_en_bitacora(con, usuario["usuario"], "REGISTRAR_ALUMNO", datos["nombre"])
        con.commit()
    except Exception:
        con.rollback()
        con.close()
        raise
    con.close()

    mensaje = ("Alumno " + datos["nombre"] + " registrado. Se creó su expediente, la factura FAC-" + str(id_factura)
               + " y el recibo REC-" + str(id_pago) + ". Saldo pendiente: B/. " + format(saldo, ".2f"))
    return True, mensaje


def resumen():
    """Números que se muestran en las tarjetas del panel principal y de pagos."""
    con = conectar()
    datos = {
        "en_formacion": repositorios.contar_alumnos(con, "En formación"),
        "pendiente_examen": repositorios.contar_alumnos(con, "Pendiente de examen"),
        "aprobados": repositorios.contar_alumnos(con, "Aprobado"),
        "por_cobrar": repositorios.total_por_cobrar(con),
        "cobrado": repositorios.total_cobrado(con),
        "recibos": repositorios.contar_pagos(con),
    }
    con.close()
    return datos
