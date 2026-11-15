# Pruebas de CU-04 Gestionar pagos
from conftest import consultar


def test_pago_parcial(recepcion):
    r = recepcion.post("/pagos/nuevo", data={"id_alumno": "1", "monto": "60", "metodo": "Efectivo"})
    assert r.status_code == 302
    assert tuple(consultar("SELECT saldo, estado FROM factura WHERE id_alumno = 1")) == (50, "Pendiente")


def test_pago_total_y_recibo(recepcion):
    recepcion.post("/pagos/nuevo", data={"id_alumno": "1", "monto": "110", "metodo": "Transferencia", "referencia": "T-1"})
    assert tuple(consultar("SELECT saldo, estado FROM factura WHERE id_alumno = 1")) == (0, "Pagada")
    assert recepcion.get("/pagos/recibo/7").data[:4] == b"%PDF"


def test_monto_cero(recepcion):
    r = recepcion.post("/pagos/nuevo", data={"id_alumno": "1", "monto": "0", "metodo": "Efectivo"})
    assert "debe ser mayor que 0" in r.text


def test_monto_mayor_que_el_saldo(recepcion):
    r = recepcion.post("/pagos/nuevo", data={"id_alumno": "1", "monto": "500", "metodo": "Efectivo"})
    assert "supera el saldo" in r.text
    assert consultar("SELECT saldo FROM factura WHERE id_alumno = 1")[0] == 110


def test_referencia_obligatoria(recepcion):
    r = recepcion.post("/pagos/nuevo", data={"id_alumno": "1", "monto": "10", "metodo": "Tarjeta"})
    assert "La referencia es obligatoria" in r.text
