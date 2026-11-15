# CAPA DE DATOS: conexión a la base de datos y datos de prueba.
import os
import sqlite3

from werkzeug.security import generate_password_hash

import config


def conectar():
    """Abre una conexión. Las filas se pueden leer como diccionario: fila["nombre"]."""
    con = sqlite3.connect(config.BASE_DATOS)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def crear_base_de_datos():
    """Crea las tablas y, si la base está vacía, agrega usuarios, cursos y alumnos de prueba."""
    os.makedirs(os.path.dirname(config.BASE_DATOS), exist_ok=True)
    con = conectar()
    archivo = open(os.path.join(os.path.dirname(__file__), "schema.sql"), encoding="utf-8")
    con.executescript(archivo.read())
    archivo.close()

    cantidad = con.execute("SELECT COUNT(*) FROM usuario").fetchone()[0]
    if cantidad == 0:
        cargar_datos_de_prueba(con)
    con.close()


def cargar_datos_de_prueba(con):
    usuarios = [
        ("recepcion", "Fidelis Rodríguez", "Recepcionista", "Recepcion2026!"),
        ("admin", "Luis Padilla", "Administrador", "Admin2026!"),
        ("instructor", "Mario Castillo", "Instructor", "Instructor2026!"),
    ]
    for usuario in usuarios:
        clave_cifrada = generate_password_hash(usuario[3])      # nunca se guarda la clave real
        con.execute("INSERT INTO usuario (usuario, nombre, rol, clave_hash) VALUES (?, ?, ?, ?)",
                    (usuario[0], usuario[1], usuario[2], clave_cifrada))

    cursos = [("Licencia A (36h)", 180), ("Licencia B (36h)", 220), ("Licencia C (36h)", 260),
              ("Licencia D (36h)", 280), ("Ampliación E1 (36h)", 300)]
    for curso in cursos:
        con.execute("INSERT INTO curso (nombre, tarifa) VALUES (?, ?)", curso)

    # nombre, cédula, id del curso, vehículo, estado, horas teóricas, horas prácticas, lo que ya pagó
    alumnos = [
        ("Mariela Vega", "8-902-1145", 2, "Manual", "En formación", 12, 6, 110),
        ("Carlos Espino", "4-771-2290", 1, "Automático", "Pendiente de examen", 20, 16, 180),
        ("Ana Gómez", "9-103-5567", 5, "Manual", "Aprobado", 20, 16, 300),
        ("José Herrera", "2-455-8821", 3, "Manual", "Aprobado", 20, 16, 150),
        ("Brenda Solís", "6-321-0099", 2, "Automático", "Retirado", 8, 2, 200),
        ("Iván Castillo", "3-880-1123", 4, "Manual", "En formación", 4, 0, 280),
    ]
    fecha = "2026-11-01 09:00:00"
    numero = 1
    for a in alumnos:
        tarifa = cursos[a[2] - 1][1]
        saldo = tarifa - a[7]
        if saldo == 0:
            estado_factura = "Pagada"
        else:
            estado_factura = "Pendiente"
        con.execute("INSERT INTO alumno (nombre, cedula, telefono, correo, direccion, tipo_vehiculo, estado, "
                    "id_curso, fecha) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (a[0], a[1], "6000-000" + str(numero), "alumno" + str(numero) + "@correo.com",
                     "Panamá, Bella Vista", a[3], a[4], a[2], fecha))
        con.execute("INSERT INTO expediente (id_alumno, horas_teoricas, horas_practicas) VALUES (?, ?, ?)",
                    (numero, a[5], a[6]))
        con.execute("INSERT INTO factura (id_alumno, monto_total, saldo, estado, fecha) VALUES (?, ?, ?, ?, ?)",
                    (numero, tarifa, saldo, estado_factura, fecha))
        con.execute("INSERT INTO pago (id_factura, monto, metodo, referencia, fecha, id_usuario) "
                    "VALUES (?, ?, 'Efectivo', 'Abono inicial', ?, 1)", (numero, a[7], fecha))
        numero = numero + 1
    con.commit()
