# RNF-06: copia de seguridad de la base de datos.  Uso: python scripts/respaldo.py
# Para que sea diaria, se programa con el Programador de tareas de Windows (ver README).
import os
import shutil
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # noqa: E402

destino = os.path.join(config.CARPETA, "respaldos")
os.makedirs(destino, exist_ok=True)
archivo = os.path.join(destino, f"respaldo_{datetime.now():%Y%m%d_%H%M%S}.db")
shutil.copy(config.BASE_DATOS, archivo)
print("Respaldo creado:", os.path.relpath(archivo, config.CARPETA))
