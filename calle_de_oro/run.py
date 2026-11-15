# Para iniciar el sistema:  python run.py
# Luego abrir en el navegador:  http://127.0.0.1:5000
from app import app
from app.datos.base_datos import crear_base_de_datos

crear_base_de_datos()           # crea las tablas y los datos de prueba (solo la primera vez)
app.run(port=5000, threaded=True)   # threaded=True: atiende a varios usuarios a la vez (RNF-08)
