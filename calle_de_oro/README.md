# Sistema de la Escuela de Manejo Calle de Oro, S.A. (Fase 3)

Programa en **Python (Flask) + HTML + CSS + JavaScript básico** con los **tres casos de uso aprobados** en la Fase 2:

| CU | Qué hace | Quién lo usa | Dónde está |
|---|---|---|---|
| CU-01 | Registrar alumno: crea su expediente, su factura y el abono inicial | Recepcionista | Alumnos → **+ Registrar alumno** |
| CU-03 | Generar certificado si está aprobado, tiene 36 h y no debe nada | Administrador | Alumnos → **Generar certificado** |
| CU-04 | Registrar pagos y ver los recibos | Recepcionista | Pagos y facturas → **+ Registrar pago** |

## Cómo ejecutarlo (Windows)

1. Instalar Python 3.10 o superior (en el instalador marcar **"Add Python to PATH"**).
2. Abrir una terminal en la carpeta `calle_de_oro` y escribir **uno por uno**:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   python -m pip install -r requirements.txt
   python run.py
   ```
3. Abrir en el navegador: **http://127.0.0.1:5000**

| Usuario | Contraseña | Rol |
|---|---|---|
| `recepcion` | `Recepcion2026!` | Recepcionista |
| `admin` | `Admin2026!` | Administrador |
| `instructor` | `Instructor2026!` | Instructor (para mostrar que no puede entrar a otras páginas) |

La primera vez se crea la base de datos con datos de prueba. Para empezar de cero: cerrar con Ctrl+C, borrar la carpeta `instancia` y volver a ejecutar `python run.py`.

## Datos de prueba

| Alumno | Estado | Horas T/P | Debe | Para probar |
|---|---|---|---|---|
| Mariela Vega | En formación | 12/6 | B/. 110 | Pago (CU-04) y certificado rechazado por horas (CU-03) |
| Carlos Espino | Pendiente de examen | 20/16 | 0 | Certificado rechazado: no está aprobado |
| **Ana Gómez** | Aprobado | 20/16 | 0 | **Certificado generado correctamente** |
| José Herrera | Aprobado | 20/16 | B/. 110 | Certificado rechazado por saldo |
| Brenda Solís | Retirado | 8/2 | B/. 20 | — |
| Iván Castillo | En formación | 4/0 | 0 | — |

Cédula ya registrada para probar el error de CU-01: `8-902-1145`.

## Pruebas

```
python -m pytest -v                 (19 pruebas automáticas)
python scripts\prueba_carga.py      (30 usuarios a la vez; con el servidor encendido)
python scripts\respaldo.py          (copia de seguridad de la base de datos)
```

Las capturas de pantalla y los resultados están en `docs/evidencia/`.
