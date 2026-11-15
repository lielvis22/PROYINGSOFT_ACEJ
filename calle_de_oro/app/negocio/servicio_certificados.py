# CU-03 GENERACIÓN AUTOMÁTICA DE CERTIFICADOS  (en el VOPC: "Servicio Certificados")
import config
from app.datos import repositorios
from app.datos.base_datos import conectar


def listar_certificados():
    con = conectar()
    certificados = repositorios.leer_certificados(con)
    con.close()
    return certificados


def buscar_certificado_y_alumno(id_certificado):
    con = conectar()
    certificado = repositorios.buscar_certificado(con, id_certificado)
    alumno = None
    if certificado is not None:
        alumno = repositorios.buscar_alumno(con, certificado["id_alumno"])
    con.close()
    return certificado, alumno


def revisar_requisitos(con, alumno):
    """Devuelve la lista de motivos por los que NO se puede generar. Si está vacía, sí se puede."""
    motivos = []
    if repositorios.tiene_certificado(con, alumno["id_alumno"]):
        motivos.append("El alumno ya tiene un certificado.")
        return motivos
    if alumno["estado"] != "Aprobado":
        motivos.append("El alumno no está aprobado (estado: " + alumno["estado"] + ").")
    if alumno["horas_teoricas"] < config.HORAS_TEORICAS or alumno["horas_practicas"] < config.HORAS_PRACTICAS:
        motivos.append("No cumple las 36 horas: tiene " + str(alumno["horas_teoricas"]) + "/20 teóricas y "
                       + str(alumno["horas_practicas"]) + "/16 prácticas.")
    if alumno["saldo"] > 0:
        motivos.append("Tiene saldo pendiente de B/. " + format(alumno["saldo"], ".2f")
                       + ". El certificado se entrega cuando pague todo.")
    return motivos


def generar_certificado(id_alumno, usuario):
    """Devuelve (True, mensaje de éxito) o (False, lista de motivos)."""
    con = conectar()
    alumno = repositorios.buscar_alumno(con, id_alumno)

    motivos = revisar_requisitos(con, alumno)
    if len(motivos) > 0:
        repositorios.guardar_en_bitacora(con, usuario["usuario"], "CERTIFICADO_RECHAZADO", alumno["nombre"])
        con.commit()
        con.close()
        return False, motivos

    # Cumple todo: se guarda con estado "Falta validar"
    id_certificado = repositorios.guardar_certificado(con, id_alumno, usuario["id_usuario"])
    repositorios.guardar_en_bitacora(con, usuario["usuario"], "GENERAR_CERTIFICADO", alumno["nombre"])
    con.commit()
    con.close()
    return True, "Certificado CERT-" + str(id_certificado) + " generado para " + alumno["nombre"] + " con estado «Falta validar»."

