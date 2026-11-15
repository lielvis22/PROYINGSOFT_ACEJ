# Revisión contra la rúbrica de la Fase 3

| Lo que pide la rúbrica | ✔ | Dónde está |
|---|---|---|
| Los tres CU funcionando de principio a fin | ✅ | CU-01, CU-03 y CU-04 guardan en la base de datos (capturas 04 a 15) |
| Interfaz | ✅ | `app/templates/` |
| Reglas de negocio | ✅ | 50 % de abono, 20+16 h, saldo 0 para certificar, monto ≤ saldo |
| Validaciones | ✅ | En JavaScript (`static/js/funciones.js`) y en Python (`validaciones.py` y servicios) |
| Persistencia | ✅ | SQLite (`schema.sql`, `repositorios.py`) |
| Manejo de errores | ✅ | Mensajes en rojo por campo, cuadro de motivos en CU-03, páginas 403/404/500, rollback |
| Código coherente con la arquitectura | ✅ | Carpetas `presentacion/`, `negocio/` y `datos/` = las 3 capas (ver `GUIA_DEFENSA.md`) |
| Ajustes justificados | ✅ | `AJUSTES_DISENO.md` |
| Repositorio | ⚠️ | La carpeta ya es un repositorio git. **Falta subirlo a GitHub** |
| Instrucciones de ejecución | ✅ | `README.md` |
| Configuración y datos de demostración | ✅ | `config.py`, `requirements.txt`, datos de prueba automáticos |
| Evidencia | ✅ | `docs/evidencia/` (18 capturas, pruebas, prueba de carga y respaldo) |
| Trazabilidad hasta archivo y función | ✅ | `MATRIZ_TRAZABILIDAD.md` |

**Para la comprobación individual:** cada integrante debe leer `GUIA_DEFENSA.md`.
