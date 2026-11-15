# Pruebas de CU-01 Registrar alumno
from conftest import consultar

DATOS = {"nombre": "María Fernández", "cedula": "8-123-4567", "telefono": "6000-1234",
         "correo": "maria@correo.com", "direccion": "Panamá, San Francisco", "id_curso": "2",
         "tipo_vehiculo": "Manual", "abono": "110"}


def test_registro_crea_alumno_expediente_factura_y_pago(recepcion):
    r = recepcion.post("/alumnos/nuevo", data=DATOS)
    assert r.status_code == 302
    assert consultar("SELECT COUNT(*) FROM alumno")[0] == 7
    assert consultar("SELECT COUNT(*) FROM expediente")[0] == 7
    assert consultar("SELECT saldo FROM factura WHERE id_alumno = 7")[0] == 110


def test_campos_invalidos(recepcion):
    datos = dict(DATOS, nombre="", cedula="123", correo="x")
    r = recepcion.post("/alumnos/nuevo", data=datos)
    assert r.status_code == 422
    assert "Escriba nombre y apellido" in r.text
    assert "Cédula no válida" in r.text
    assert "Correo no válido" in r.text


def test_cedula_repetida(recepcion):
    r = recepcion.post("/alumnos/nuevo", data=dict(DATOS, cedula="8-902-1145"))
    assert "Ya existe un alumno con esta cédula" in r.text


def test_abono_menor_al_50_por_ciento(recepcion):
    r = recepcion.post("/alumnos/nuevo", data=dict(DATOS, abono="50"))
    assert "El abono mínimo es B/. 110.00" in r.text


def test_si_algo_falla_no_se_guarda_nada(app, recepcion, monkeypatch):
    from app.datos import repositorios

    def falla(*args):
        raise Exception("error simulado")
    monkeypatch.setattr(repositorios, "crear_factura", falla)
    app.config["PROPAGATE_EXCEPTIONS"] = False
    r = recepcion.post("/alumnos/nuevo", data=DATOS)
    app.config["PROPAGATE_EXCEPTIONS"] = None
    assert r.status_code == 500
    assert consultar("SELECT COUNT(*) FROM alumno")[0] == 6     # el alumno NO quedó guardado
