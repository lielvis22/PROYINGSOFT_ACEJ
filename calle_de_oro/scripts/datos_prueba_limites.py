# Fase 4: agrega dos alumnos para probar los valores límite de CU-03 (CP-11).
#   Laura Pinto: aprobada, 20/15 h (le falta 1 h práctica), saldo 0
#   Raúl Mena:   aprobado, 20/16 h, debe B/. 0.01
# Uso (con la base de datos ya creada):  python scripts/datos_prueba_limites.py
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.datos.base_datos import conectar  # noqa: E402

ALUMNOS = [
    # nombre, cédula, curso, horas T, horas P, tarifa, pagado
    ("Laura Pinto", "8-777-0001", 1, 20, 15, 180.00, 180.00),
    ("Raúl Mena", "8-777-0002", 1, 20, 16, 180.00, 179.99),
]


def agregar(con):
    for nombre, cedula, curso, ht, hp, tarifa, pagado in ALUMNOS:
        if con.execute("SELECT 1 FROM alumno WHERE cedula = ?", (cedula,)).fetchone():
            continue
        cur = con.execute("INSERT INTO alumno (nombre, cedula, telefono, correo, direccion, tipo_vehiculo, estado, id_curso, fecha) "
                          "VALUES (?, ?, '6000-7777', 'limite@correo.com', 'Panamá, Bella Vista', 'Manual', 'Aprobado', ?, "
                          "'2026-11-01 09:00:00')", (nombre, cedula, curso))
        id_alumno = cur.lastrowid
        con.execute("INSERT INTO expediente (id_alumno, horas_teoricas, horas_practicas) VALUES (?, ?, ?)", (id_alumno, ht, hp))
        saldo = round(tarifa - pagado, 2)
        cur = con.execute("INSERT INTO factura (id_alumno, monto_total, saldo, estado, fecha) VALUES (?, ?, ?, ?, '2026-11-01 09:00:00')",
                          (id_alumno, tarifa, saldo, "Pagada" if saldo == 0 else "Pendiente"))
        con.execute("INSERT INTO pago (id_factura, monto, metodo, referencia, fecha, id_usuario) "
                    "VALUES (?, ?, 'Efectivo', 'Abono inicial', '2026-11-01 09:00:00', 1)", (cur.lastrowid, pagado))
    con.commit()


if __name__ == "__main__":
    c = conectar()
    agregar(c)
    c.close()
    print("Alumnos de valores límite agregados: Laura Pinto (20/15 h) y Raúl Mena (debe B/. 0.01).")
