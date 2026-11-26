# Pruebas de CU-03 Generar certificado
from conftest import consultar


def test_genera_certificado(admin):
    r = admin.post("/certificados/generar/3")          # Ana Gómez: aprobada, 36 h, sin deuda
    assert r.status_code == 302
    assert consultar("SELECT estado FROM certificado WHERE id_alumno = 3")[0] == "Falta validar"
    assert admin.get("/certificados/1/pdf").data[:4] == b"%PDF"


def test_no_genera_si_debe(admin):
    r = admin.post("/certificados/generar/4")          # José Herrera debe B/. 110
    assert r.status_code == 409
    assert "saldo pendiente de B/. 110.00" in r.text


def test_no_genera_sin_horas_ni_aprobacion(admin):
    r = admin.post("/certificados/generar/1")          # Mariela Vega: en formación, 12/6 h
    assert "No cumple las 36 horas" in r.text
    assert "no está aprobado" in r.text


def test_no_genera_dos_veces(admin):
    admin.post("/certificados/generar/3")
    r = admin.post("/certificados/generar/3")
    assert "ya tiene un certificado" in r.text


# Fase 4: valores límite de las reglas de CU-03 (CP-11)
def _limites():
    import importlib.util
    import os
    from app.datos.base_datos import conectar
    ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "datos_prueba_limites.py")
    spec = importlib.util.spec_from_file_location("limites", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    con = conectar()
    modulo.agregar(con)
    con.close()


def test_limite_le_falta_una_hora_practica(admin):
    _limites()                                          # Laura Pinto (id 7): 20/15 h
    r = admin.post("/certificados/generar/7")
    assert r.status_code == 409
    assert "15/16 prácticas" in r.text


def test_limite_debe_un_centavo(admin):
    _limites()                                          # Raúl Mena (id 8): debe B/. 0.01
    r = admin.post("/certificados/generar/8")
    assert r.status_code == 409
    assert "saldo pendiente de B/. 0.01" in r.text
