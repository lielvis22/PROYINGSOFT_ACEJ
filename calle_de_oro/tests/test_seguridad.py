# Pruebas de seguridad (RF-09, RNF-03) y de tiempo de respuesta (RNF-07)
import time

from conftest import entrar


def test_sin_sesion_manda_al_login(app):
    r = app.test_client().get("/alumnos")
    assert r.headers["Location"].endswith("/login")


def test_bloqueo_tras_3_intentos(app):
    cliente = app.test_client()
    assert "Le quedan 2" in entrar(cliente, "recepcion", "mala").text
    entrar(cliente, "recepcion", "mala")
    assert "Cuenta bloqueada" in entrar(cliente, "recepcion", "mala").text
    assert "Cuenta bloqueada" in entrar(cliente, "recepcion", "Recepcion2026!").text   # aun con la clave correcta


def test_sesion_expira_a_los_15_minutos(recepcion):
    with recepcion.session_transaction() as sesion:
        sesion["ultimo_uso"] = time.time() - 16 * 60      # simulamos 16 minutos sin uso
    assert recepcion.get("/alumnos").headers["Location"].endswith("/login")


def test_cada_rol_solo_entra_a_lo_suyo(app, recepcion, admin):
    assert recepcion.post("/certificados/generar/3").status_code == 403    # la recepcionista no certifica
    assert admin.get("/pagos").status_code == 403                           # el administrador no cobra
    instructor = app.test_client()
    entrar(instructor, "instructor", "Instructor2026!")
    assert instructor.get("/alumnos").status_code == 403


def test_responde_en_menos_de_3_segundos(recepcion):
    for pagina in ["/", "/alumnos", "/pagos"]:
        inicio = time.time()
        recepcion.get(pagina)
        assert time.time() - inicio < 3
