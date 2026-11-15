# RNF-07 y RNF-08: 30 usuarios a la vez abren los módulos. Con el servidor encendido:
#   python scripts/prueba_carga.py
import threading
import time
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar

tiempos, errores = [], []


def usuario_virtual():
    navegador = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    try:
        datos = urllib.parse.urlencode({"usuario": "recepcion", "clave": "Recepcion2026!"}).encode()
        navegador.open("http://127.0.0.1:5000/login", datos)
        for ruta in ["/", "/alumnos", "/pagos"]:
            inicio = time.perf_counter()
            navegador.open("http://127.0.0.1:5000" + ruta).read()
            tiempos.append(time.perf_counter() - inicio)
    except Exception as e:
        errores.append(e)


hilos = [threading.Thread(target=usuario_virtual) for _ in range(30)]
for h in hilos:
    h.start()
for h in hilos:
    h.join()
print(f"30 usuarios simultáneos, {len(tiempos)} peticiones, {len(errores)} errores")
print(f"Promedio {sum(tiempos) / len(tiempos):.3f} s (meta 3 s) | Máximo {max(tiempos):.3f} s (meta 5 s)")
