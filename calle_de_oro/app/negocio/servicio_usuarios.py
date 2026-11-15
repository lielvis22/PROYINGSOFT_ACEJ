# Inicio de sesión (RF-09). El rol sale de la cuenta del usuario, no se elige.
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash

import config
from app.datos import repositorios
from app.datos.base_datos import conectar


def iniciar_sesion(usuario, clave):
    """Devuelve (True, datos del usuario) o (False, mensaje de error)."""
    con = conectar()
    u = repositorios.buscar_usuario(con, usuario.strip().lower())

    if u is None:
        con.close()
        return False, "Usuario o contraseña incorrectos."

    # ¿La cuenta está bloqueada?
    if u["bloqueado_hasta"] is not None:
        hasta = datetime.fromisoformat(u["bloqueado_hasta"])
        if datetime.now() < hasta:
            con.close()
            return False, "Cuenta bloqueada por intentos fallidos. Espere 15 minutos."

    # ¿La contraseña es incorrecta?
    if not check_password_hash(u["clave_hash"], clave):
        intentos = u["intentos"] + 1
        if intentos >= config.MAX_INTENTOS:
            hasta = datetime.now() + timedelta(minutes=config.MINUTOS_BLOQUEO)
            repositorios.guardar_intentos(con, u["id_usuario"], 0, hasta.isoformat(timespec="seconds"))
            repositorios.guardar_en_bitacora(con, u["usuario"], "CUENTA_BLOQUEADA", "3 intentos fallidos")
            mensaje = "Cuenta bloqueada por 15 minutos tras 3 intentos fallidos."
        else:
            repositorios.guardar_intentos(con, u["id_usuario"], intentos, None)
            mensaje = "Usuario o contraseña incorrectos. Le quedan " + str(config.MAX_INTENTOS - intentos) + " intento(s)."
        con.commit()
        con.close()
        return False, mensaje

    # Todo bien: se reinician los intentos
    repositorios.guardar_intentos(con, u["id_usuario"], 0, None)
    repositorios.guardar_en_bitacora(con, u["usuario"], "LOGIN", "Inició sesión")
    con.commit()
    con.close()
    datos_usuario = {"id_usuario": u["id_usuario"], "usuario": u["usuario"], "nombre": u["nombre"], "rol": u["rol"]}
    return True, datos_usuario


def leer_bitacora():
    """RNF-12: lista de todo lo que se ha hecho en el sistema."""
    con = conectar()
    registros = repositorios.leer_bitacora(con)
    con.close()
    return registros
