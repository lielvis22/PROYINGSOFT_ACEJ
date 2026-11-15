# Matriz de trazabilidad (Fase 3)

## Requisitos funcionales

| Requisito | CU | Página HTML | Ruta (`presentacion/rutas.py`) | Servicio (negocio) | Repositorio (`datos/repositorios.py`) | Prueba |
|---|---|---|---|---|---|---|
| RF-01 Registro de alumnos | CU-01 | `alumnos.html` (ventana `ventana-alumno`) | `alumno_nuevo()` | `servicio_alumnos.registrar_alumno()` | `guardar_alumno()`, `crear_expediente()`, `existe_cedula()` | `test_cu01.py` |
| RF-04 Factura y abono inicial | CU-01 | `alumnos.html` (ventana `ventana-alumno`) | `alumno_nuevo()` | `servicio_alumnos.registrar_alumno()` (paso 3 y 5) | `crear_factura()`, `guardar_pago()`, `cambiar_saldo()` | `test_abono_menor_al_50_por_ciento` |
| RF-04 Pagos y recibos | CU-04 | `pagos.html` (ventana `ventana-pago`) | `pago_nuevo()`, `pagos()`, `recibo()` | `servicio_pagos.registrar_pago()`, `pdf.recibo_pdf()` | `buscar_factura()`, `guardar_pago()`, `cambiar_saldo()` | `test_cu04.py` |
| RF-03 Generación de certificados | CU-03 | `alumnos.html`, `certificados.html` | `generar_certificado()`, `certificados()`, `certificado_pdf()` | `servicio_certificados.revisar_requisitos()`, `generar_certificado()`, `pdf.certificado_pdf()` | `tiene_certificado()`, `guardar_certificado()` | `test_cu03.py` |
| RF-08 Roles y permisos | Todos | `base.html` (menú) | `revisar_acceso()` | — | — | `test_cada_rol_solo_entra_a_lo_suyo` |
| RF-09 Autenticación | Todos | `login.html` | `login()`, `revisar_acceso()` | `servicio_usuarios.iniciar_sesion()` | `buscar_usuario()`, `guardar_intentos()` | `test_bloqueo_tras_3_intentos`, `test_sesion_expira_a_los_15_minutos` |
| RF-12 Búsqueda | CU-01 | `alumnos.html` | `alumnos()` | `servicio_alumnos.listar_alumnos()` | `leer_alumnos()` | captura 04 |

## Requisitos no funcionales

| RNF | Dónde se cumple | Cómo se comprueba |
|---|---|---|
| RNF-01 Fácil de usar | `base.html`: menú lateral solo con las opciones del rol y la opción actual resaltada; ventanas emergentes como en el prototipo | Capturas 03, 04 y 12 |
| RNF-02 Prevenir errores | `static/js/funciones.js` → `validarCampo()` y `validarFormulario()`: marcan en rojo mientras se escribe y no dejan enviar con errores | Capturas 05, 06 y 09 |
| RNF-03 Seguridad por rol | `rutas.revisar_acceso()`; contraseñas cifradas en `base_datos.py` | `test_cada_rol_solo_entra_a_lo_suyo`, captura 16 |
| RNF-04 Datos correctos | `validaciones.py` y los servicios; `commit()`/`rollback()`; `CHECK` en `schema.sql` | `test_si_algo_falla_no_se_guarda_nada`, `test_monto_mayor_que_el_saldo` |
| RNF-05 Sin duplicados | `UNIQUE` en `schema.sql` y `existe_cedula()` | `test_cedula_repetida`, `test_no_genera_dos_veces` |
| RNF-06 Respaldo | `scripts/respaldo.py` | `evidencia/respaldo.txt` |
| RNF-07, RNF-10, RNF-11 Tiempo de respuesta | Servidor con `threaded=True` | `test_responde_en_menos_de_3_segundos`, `prueba_carga_30_usuarios.txt` |
| RNF-08 30 usuarios | `run.py` (`threaded=True`) | `scripts/prueba_carga.py` (30 usuarios, 0 errores) |
| RNF-09 PDF en 5 s | `negocio/pdf.py` | Los PDF abren al instante |
| RNF-12 Registro de cambios | Tabla `bitacora`, `repositorios.guardar_en_bitacora()`, página `/bitacora` | Captura 17 |

## Reglas de negocio

| Regla | Dónde |
|---|---|
| Abono mínimo del 50 % | `servicio_alumnos.registrar_alumno()`, paso 3 |
| 20 h teóricas + 16 h prácticas | `servicio_certificados.revisar_requisitos()` |
| No se entrega el certificado si debe dinero | `servicio_certificados.revisar_requisitos()` |
| El certificado nace "Falta validar" | `repositorios.guardar_certificado()` |
| Monto mayor que 0 y no mayor que el saldo | `servicio_pagos.registrar_pago()`, paso 2 |
| Pago parcial deja la factura "Pendiente" | `repositorios.cambiar_saldo()` |
