# Fase 4: pruebas de regresión de los defectos encontrados (ver Entregable 4, sección de defectos)
import pytest

from conftest import consultar
from app.negocio.validaciones import convertir_a_numero


# ---------- DEF-01: un monto "NaN" pasaba la validación y la app respondía con error 500 ----------
@pytest.mark.parametrize("texto", ["nan", "NaN", "inf", "-inf", "abc", ""])
def test_def01_convertir_a_numero_rechaza_lo_que_no_es_un_numero(texto):
    assert convertir_a_numero(texto) is None


@pytest.mark.parametrize("texto", ["NaN", "nan"])
def test_def01_pago_con_monto_nan_muestra_error_y_no_se_cae(recepcion, texto):
    r = recepcion.post("/pagos/nuevo", data={"id_alumno": "4", "monto": texto, "metodo": "Efectivo"})
    assert r.status_code == 422
    assert "Monto no válido" in r.text
    assert consultar("SELECT saldo FROM factura WHERE id_alumno = 4")[0] == 110


def test_def01_abono_nan_al_registrar_alumno(recepcion):
    datos = {"nombre": "Pedro Ruiz", "cedula": "8-111-2222", "telefono": "6000-1111", "correo": "p@correo.com",
             "direccion": "Panamá, Centro", "id_curso": "2", "tipo_vehiculo": "Manual", "abono": "NaN"}
    r = recepcion.post("/alumnos/nuevo", data=datos)
    assert r.status_code == 422
    assert "El abono mínimo es" in r.text
    assert consultar("SELECT COUNT(*) FROM alumno")[0] == 6


# ---------- DEF-02: generar certificado de un alumno que no existe daba error 500 ----------
def test_def02_certificado_de_alumno_inexistente(admin):
    r = admin.post("/certificados/generar/999")
    assert r.status_code == 404
    assert "No se encontró el alumno" in r.text
    assert consultar("SELECT COUNT(*) FROM certificado")[0] == 0
