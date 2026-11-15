# CAPA DE DATOS: aquí están TODAS las consultas SQL.
# Cada función recibe la conexión "con" que abre el servicio.
from datetime import datetime


def fecha_actual():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ===================== USUARIOS Y BITÁCORA =====================

def buscar_usuario(con, usuario):
    return con.execute("SELECT * FROM usuario WHERE usuario = ?", (usuario,)).fetchone()


def guardar_intentos(con, id_usuario, intentos, bloqueado_hasta):
    con.execute("UPDATE usuario SET intentos = ?, bloqueado_hasta = ? WHERE id_usuario = ?",
                (intentos, bloqueado_hasta, id_usuario))


def guardar_en_bitacora(con, usuario, accion, detalle):
    """RNF-12: deja anotado quién hizo qué y cuándo."""
    con.execute("INSERT INTO bitacora (fecha, usuario, accion, detalle) VALUES (?, ?, ?, ?)",
                (fecha_actual(), usuario, accion, detalle))


def leer_bitacora(con):
    return con.execute("SELECT * FROM bitacora ORDER BY id_bitacora DESC").fetchall()


# ===================== ALUMNOS (CU-01) =====================

def leer_cursos(con):
    return con.execute("SELECT * FROM curso").fetchall()


def buscar_curso(con, id_curso):
    return con.execute("SELECT * FROM curso WHERE id_curso = ?", (id_curso,)).fetchone()


def existe_cedula(con, cedula):
    fila = con.execute("SELECT id_alumno FROM alumno WHERE cedula = ?", (cedula,)).fetchone()
    return fila is not None


def guardar_alumno(con, datos):
    cursor = con.execute(
        "INSERT INTO alumno (nombre, cedula, telefono, correo, direccion, tipo_vehiculo, id_curso, fecha) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (datos["nombre"], datos["cedula"], datos["telefono"], datos["correo"], datos["direccion"],
         datos["tipo_vehiculo"], datos["id_curso"], fecha_actual()))
    return cursor.lastrowid          # el id del alumno nuevo


def crear_expediente(con, id_alumno):
    con.execute("INSERT INTO expediente (id_alumno) VALUES (?)", (id_alumno,))


# Esta consulta junta el alumno con su curso, sus horas y su saldo
SELECT_ALUMNO = """
    SELECT alumno.*, curso.nombre AS curso, curso.tarifa,
           expediente.horas_teoricas, expediente.horas_practicas,
           factura.id_factura, factura.saldo
    FROM alumno
    JOIN curso      ON curso.id_curso = alumno.id_curso
    JOIN expediente ON expediente.id_alumno = alumno.id_alumno
    JOIN factura    ON factura.id_alumno = alumno.id_alumno
"""


def buscar_alumno(con, id_alumno):
    return con.execute(SELECT_ALUMNO + " WHERE alumno.id_alumno = ?", (id_alumno,)).fetchone()


def leer_alumnos(con, texto_buscado):
    """RF-12: busca por nombre o cédula. Si el texto está vacío, trae todos."""
    texto = "%" + texto_buscado + "%"
    return con.execute(SELECT_ALUMNO + " WHERE alumno.nombre LIKE ? OR alumno.cedula LIKE ? "
                       "ORDER BY alumno.id_alumno DESC", (texto, texto)).fetchall()


# ===================== FACTURAS Y PAGOS (CU-01 y CU-04) =====================

def crear_factura(con, id_alumno, monto_total):
    cursor = con.execute(
        "INSERT INTO factura (id_alumno, monto_total, saldo, estado, fecha) VALUES (?, ?, ?, 'Pendiente', ?)",
        (id_alumno, monto_total, monto_total, fecha_actual()))
    return cursor.lastrowid


def buscar_factura(con, id_alumno):
    return con.execute("SELECT * FROM factura WHERE id_alumno = ?", (id_alumno,)).fetchone()


def cambiar_saldo(con, id_factura, nuevo_saldo):
    if nuevo_saldo == 0:
        estado = "Pagada"
    else:
        estado = "Pendiente"          # pago parcial: todavía debe
    con.execute("UPDATE factura SET saldo = ?, estado = ? WHERE id_factura = ?", (nuevo_saldo, estado, id_factura))


def guardar_pago(con, id_factura, monto, metodo, referencia, id_usuario):
    cursor = con.execute(
        "INSERT INTO pago (id_factura, monto, metodo, referencia, fecha, id_usuario) VALUES (?, ?, ?, ?, ?, ?)",
        (id_factura, monto, metodo, referencia, fecha_actual(), id_usuario))
    return cursor.lastrowid          # este número es también el número del recibo


def leer_pagos(con):
    return con.execute("""
        SELECT pago.*, alumno.nombre AS alumno
        FROM pago
        JOIN factura ON factura.id_factura = pago.id_factura
        JOIN alumno  ON alumno.id_alumno = factura.id_alumno
        ORDER BY pago.id_pago DESC""").fetchall()


def buscar_pago(con, id_pago):
    return con.execute("""
        SELECT pago.*, alumno.nombre AS alumno, factura.saldo
        FROM pago
        JOIN factura ON factura.id_factura = pago.id_factura
        JOIN alumno  ON alumno.id_alumno = factura.id_alumno
        WHERE pago.id_pago = ?""", (id_pago,)).fetchone()


# ===================== CERTIFICADOS (CU-03) =====================

def tiene_certificado(con, id_alumno):
    fila = con.execute("SELECT id_certificado FROM certificado WHERE id_alumno = ?", (id_alumno,)).fetchone()
    return fila is not None


def guardar_certificado(con, id_alumno, id_usuario):
    cursor = con.execute(
        "INSERT INTO certificado (id_alumno, fecha, estado, id_usuario) VALUES (?, ?, 'Falta validar', ?)",
        (id_alumno, fecha_actual(), id_usuario))
    return cursor.lastrowid


def leer_certificados(con):
    return con.execute("""
        SELECT certificado.*, alumno.nombre AS alumno, curso.nombre AS curso
        FROM certificado
        JOIN alumno ON alumno.id_alumno = certificado.id_alumno
        JOIN curso  ON curso.id_curso = alumno.id_curso
        ORDER BY certificado.id_certificado DESC""").fetchall()


def buscar_certificado(con, id_certificado):
    return con.execute("SELECT * FROM certificado WHERE id_certificado = ?", (id_certificado,)).fetchone()


# ===================== RESUMEN PARA EL PANEL =====================

def contar_alumnos(con, estado):
    return con.execute("SELECT COUNT(*) FROM alumno WHERE estado = ?", (estado,)).fetchone()[0]


def total_por_cobrar(con):
    return con.execute("SELECT SUM(saldo) FROM factura").fetchone()[0] or 0


def total_cobrado(con):
    return con.execute("SELECT SUM(monto) FROM pago").fetchone()[0] or 0


def contar_pagos(con):
    return con.execute("SELECT COUNT(*) FROM pago").fetchone()[0]
