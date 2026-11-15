# Configuración del sistema. Aquí se cambian las reglas sin tocar el resto del código.
import os

CARPETA = os.path.dirname(os.path.abspath(__file__))
BASE_DATOS = os.path.join(CARPETA, "instancia", "calle_de_oro.db")
CLAVE_SECRETA = "cambiar-esta-clave"

MAX_INTENTOS = 3          # RF-09: se bloquea la cuenta al tercer intento fallido
MINUTOS_BLOQUEO = 15
MINUTOS_SESION = 15       # RF-09: la sesión se cierra tras 15 minutos sin uso

HORAS_TEORICAS = 20       # Resolución 380 de la ATTT
HORAS_PRACTICAS = 16
ABONO_MINIMO = 0.50       # el alumno paga al menos el 50 % al inscribirse
METODOS_PAGO = ["Efectivo", "Transferencia", "Tarjeta"]
