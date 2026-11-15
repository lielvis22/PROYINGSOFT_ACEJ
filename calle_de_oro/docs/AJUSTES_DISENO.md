# Ajustes respecto al diseño de la Fase 2

| # | Fase 2 | Fase 3 | Por qué |
|---|---|---|---|
| 1 | En el prototipo se **elige el rol** al iniciar sesión | El rol viene de la cuenta del usuario | Si se pudiera elegir, cualquiera entraría con más permisos (RNF-03). |
| 2 | ORM | Un archivo de repositorios con SQL (`repositorios.py`) | Cumple la misma función y es más fácil de leer y explicar. |
| 3 | Base de datos en un servidor | SQLite (relacional y con transacciones) | No hay que instalar nada extra para la demostración. |
| 4 | Clases de control (`controlRegistrarAlumno`, `ControlGestionarPagos`, `Servicio Certificados`) | Archivos `servicio_alumnos.py`, `servicio_pagos.py` y `servicio_certificados.py` | En Python cada archivo con sus funciones cumple el papel de la clase de control. |
| 5 | Entidad Recibo | El recibo usa el número del pago (REC-<número del pago>) | Cada pago tiene un solo recibo, así que una tabla aparte repetiría datos. |
| 6 | PDF guardado en un almacén | El PDF se crea cuando se pide | Siempre sale con los datos actuales. |
| 7 | Validación en el cliente | `static/js/funciones.js` con funciones simples (`validarCampo`, `validarFormulario`) | Avisa los errores mientras se escribe (RNF-02); Python vuelve a validar todo. |
| 8 | CU-01 sin pago inicial | CU-01 registra el abono inicial (mínimo 50 %) | Es regla del negocio y está en el prototipo. |
| 9 | 36 horas | 20 h teóricas + 16 h prácticas por separado | Así lo pide la Resolución N.º 380 de la ATTT. |
| 10 | HTTPS y respaldo en la nube | HTTP local y `scripts/respaldo.py` | Dependen del servidor donde se instale. |
