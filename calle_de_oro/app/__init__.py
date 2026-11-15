# Crea la aplicación web y carga las rutas (capa de presentación).
from flask import Flask

import config

app = Flask(__name__)
app.secret_key = config.CLAVE_SECRETA

from app.presentacion import rutas  # noqa: E402,F401  (se importa al final para registrar las rutas)
