# Guía para la defensa

## La idea principal
El programa está separado en **3 capas**, igual que el diagrama de componentes de la Fase 2:

```
Página HTML + JS  →  presentacion/rutas.py  →  negocio/servicio_xxx.py  →  datos/repositorios.py  →  Base de datos
 (lo que ve)     (recibe el clic)          (aplica las reglas)          (guarda y lee con SQL)
```

Regla: **las rutas nunca escriben SQL**, y **los repositorios nunca deciden reglas**.

## Qué hay en cada archivo

| Archivo | Capa | Para qué sirve |
|---|---|---|
| `run.py` | — | Crea la base de datos y enciende el servidor |
| `config.py` | — | Números de las reglas: 3 intentos, 15 minutos, 20+16 horas, 50 % de abono |
| `app/__init__.py` | — | Crea la aplicación Flask |
| `app/templates/*.html` | Presentación | Las páginas que ve el usuario (copiadas del prototipo de Figma). Los formularios de CU-01 y CU-04 son ventanas emergentes (`<dialog>`) |
| `app/static/css/estilos.css` | Presentación | Colores y forma de las pantallas (azul y dorado del prototipo) |
| `app/static/js/funciones.js` | Presentación | `abrirVentana()`/`cerrarVentana()` y `validarCampo()`/`validarFormulario()`: marca en rojo los errores mientras se escribe |
| `app/presentacion/rutas.py` | Presentación | Todas las páginas (rutas). `revisar_acceso()` revisa sesión, 15 minutos y rol |
| `app/negocio/servicio_usuarios.py` | Negocio | `iniciar_sesion()`, con bloqueo tras 3 intentos |
| `app/negocio/servicio_alumnos.py` | Negocio | **CU-01**: `registrar_alumno()` |
| `app/negocio/servicio_pagos.py` | Negocio | **CU-04**: `registrar_pago()` |
| `app/negocio/servicio_certificados.py` | Negocio | **CU-03**: `revisar_requisitos()` y `generar_certificado()` |
| `app/negocio/validaciones.py` | Negocio | Revisa cédula, teléfono, correo, etc. |
| `app/negocio/pdf.py` | Negocio | Crea el PDF del recibo y del certificado |
| `app/datos/base_datos.py` | Datos | `conectar()` y los datos de prueba |
| `app/datos/repositorios.py` | Datos | **Todas** las consultas SQL |
| `app/datos/schema.sql` | Datos | Las tablas |

## Paso a paso de cada caso de uso

**CU-01 Registrar alumno** (`servicio_alumnos.registrar_alumno`)
1. Revisa que los campos estén bien escritos (`validar_datos_alumno`).
2. Revisa que el curso exista.
3. Revisa que el abono sea al menos el 50 % de la tarifa.
4. Revisa que la cédula no esté repetida (`existe_cedula`).
5. Guarda todo junto: alumno, expediente, factura, abono y saldo. Si algo falla, `rollback()` y no se guarda nada.

**CU-04 Registrar pago** (`servicio_pagos.registrar_pago`)
1. Busca la factura del alumno.
2. Revisa que el monto sea mayor que 0 y no supere lo que debe, y que haya referencia si no es efectivo.
3. Guarda el pago y baja el saldo. Si todavía debe, la factura queda "Pendiente" (pago parcial).
4. El recibo es el número del pago (REC-7, por ejemplo); el PDF se crea al abrirlo.

**CU-03 Generar certificado** (`servicio_certificados.generar_certificado`)
1. `revisar_requisitos()` junta los motivos: ya tiene certificado, no está aprobado, le faltan horas o debe dinero.
2. Si hay motivos, se muestran en un cuadro rojo y no se genera.
3. Si no hay motivos, se guarda con estado "Falta validar".

## Preguntas que les pueden hacer

| Pregunta | Respuesta |
|---|---|
| ¿Dónde se valida que el pago no supere el saldo? | `servicio_pagos.py`, función `registrar_pago`, paso 2 |
| ¿Cómo evitan alumnos repetidos? | `repositorios.existe_cedula()` y `UNIQUE` en `cedula` (archivo `schema.sql`) |
| ¿Qué pasa si falla algo a mitad del registro? | `con.rollback()` deshace todo (prueba `test_si_algo_falla_no_se_guarda_nada`) |
| ¿Cómo impiden que la recepcionista genere certificados? | En `rutas.py`, `generar_certificado()` llama a `revisar_acceso(["Administrador"])` |
| ¿Dónde está el bloqueo de 3 intentos? | `servicio_usuarios.iniciar_sesion()`; el número está en `config.MAX_INTENTOS` |
| ¿Dónde se cierra la sesión a los 15 min? | `rutas.revisar_acceso()`, compara con `config.MINUTOS_SESION` |
| ¿Por qué validan en JavaScript y en Python? | JavaScript (`funciones.js`) avisa al momento; Python vuelve a revisar porque el JavaScript se puede desactivar (ADR-004) |
| ¿Cómo guardan las contraseñas? | Cifradas con `generate_password_hash` (en `base_datos.py`) |
| Cambie el abono mínimo al 40 % | En `config.py`: `ABONO_MINIMO = 0.40` y en `funciones.js` cambiar `0.5` por `0.4` |
| Agregue el método de pago "Yappy" | En `config.py`: agregarlo a `METODOS_PAGO` |
