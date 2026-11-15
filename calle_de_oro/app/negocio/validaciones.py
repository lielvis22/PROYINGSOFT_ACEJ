# Validaciones en el servidor (ADR-004).
# El navegador ya revisa los campos con "required" y "pattern" en el HTML (RNF-02),
# pero aquí se revisan otra vez porque alguien podría saltarse el formulario (RNF-04).
import re


def convertir_a_numero(texto):
    """Convierte el texto a número. Si no se puede, devuelve None."""
    try:
        return round(float(texto), 2)
    except ValueError:
        return None


def validar_datos_alumno(datos):
    """Devuelve un diccionario {campo: mensaje de error}. Si está vacío, todo está bien."""
    errores = {}
    if len(datos["nombre"].split()) < 2:
        errores["nombre"] = "Escriba nombre y apellido."
    if not re.match(r"^\d{1,2}-\d{1,4}-\d{1,6}$", datos["cedula"]):
        errores["cedula"] = "Cédula no válida. Ejemplo: 8-123-4567."
    if not re.match(r"^\d{3,4}-?\d{4}$", datos["telefono"]):
        errores["telefono"] = "Teléfono no válido. Ejemplo: 6000-0000."
    if "@" not in datos["correo"] or "." not in datos["correo"]:
        errores["correo"] = "Correo no válido. Ejemplo: correo@ejemplo.com."
    if len(datos["direccion"]) < 5:
        errores["direccion"] = "Escriba la dirección."
    if datos["tipo_vehiculo"] not in ["Manual", "Automático"]:
        errores["tipo_vehiculo"] = "Seleccione el tipo de vehículo."
    return errores
