# Generador de documentos PDF (ADR-005, RNF-09: en 5 s o menos). Devuelve los bytes del PDF.
import io

from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas


def recibo_pdf(pago):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(60, 720, "ESCUELA DE MANEJO CALLE DE ORO, S.A.")
    c.setFont("Helvetica", 12)
    lineas = [f"RECIBO REC-{pago['id_pago']}", f"Fecha: {pago['fecha']}", f"Recibimos de: {pago['alumno']}",
              f"Monto: B/. {pago['monto']:.2f}", f"Método: {pago['metodo']}  Referencia: {pago['referencia'] or '-'}",
              f"Saldo pendiente actual: B/. {pago['saldo']:.2f}"]
    for i, texto in enumerate(lineas):
        c.drawString(60, 680 - i * 22, texto)
    c.save()
    return buffer.getvalue()


def certificado_pdf(cert, alumno):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    ancho = landscape(letter)[0]
    c.rect(25, 25, ancho - 50, 562)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(ancho / 2, 500, "CERTIFICADO DE FINALIZACIÓN")
    c.setFont("Helvetica", 14)
    c.drawCentredString(ancho / 2, 460, "La Escuela de Manejo Calle de Oro, S.A. certifica que")
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(ancho / 2, 420, alumno["nombre"])
    c.setFont("Helvetica", 14)
    c.drawCentredString(ancho / 2, 390, f"cédula {alumno['cedula']}, completó el curso {alumno['curso']}")
    c.drawCentredString(ancho / 2, 368, f"con {alumno['horas_teoricas']} h teóricas y {alumno['horas_practicas']} h "
                                        "prácticas (Resolución N.º 380 de la ATTT).")
    c.setFont("Helvetica", 11)
    c.drawString(60, 70, f"CERT-{cert['id_certificado']}   Fecha: {cert['fecha']}   Estado: {cert['estado']}")
    c.save()
    return buffer.getvalue()
