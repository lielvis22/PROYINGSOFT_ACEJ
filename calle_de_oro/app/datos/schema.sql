-- Base de datos relacional (ADR-002). UNIQUE y CHECK evitan datos duplicados o inválidos (RNF-04, RNF-05).
CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario    TEXT NOT NULL UNIQUE,
    nombre     TEXT NOT NULL,
    rol        TEXT NOT NULL CHECK (rol IN ('Recepcionista', 'Administrador', 'Instructor')),
    clave_hash TEXT NOT NULL,
    intentos   INTEGER NOT NULL DEFAULT 0,
    bloqueado_hasta TEXT
);

CREATE TABLE IF NOT EXISTS curso (
    id_curso INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre   TEXT NOT NULL,
    tarifa   REAL NOT NULL CHECK (tarifa > 0)
);

CREATE TABLE IF NOT EXISTS alumno (
    id_alumno INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre    TEXT NOT NULL,
    cedula    TEXT NOT NULL UNIQUE,
    telefono  TEXT NOT NULL,
    correo    TEXT NOT NULL,
    direccion TEXT NOT NULL,
    tipo_vehiculo TEXT NOT NULL,
    estado    TEXT NOT NULL DEFAULT 'En formación',
    id_curso  INTEGER NOT NULL REFERENCES curso(id_curso),
    fecha     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS expediente (
    id_expediente   INTEGER PRIMARY KEY AUTOINCREMENT,
    id_alumno       INTEGER NOT NULL UNIQUE REFERENCES alumno(id_alumno),
    horas_teoricas  INTEGER NOT NULL DEFAULT 0,
    horas_practicas INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS factura (
    id_factura  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_alumno   INTEGER NOT NULL UNIQUE REFERENCES alumno(id_alumno),
    monto_total REAL NOT NULL CHECK (monto_total > 0),
    saldo       REAL NOT NULL CHECK (saldo >= 0),
    estado      TEXT NOT NULL,              -- 'Pendiente' o 'Pagada'
    fecha       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pago (
    id_pago    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_factura INTEGER NOT NULL REFERENCES factura(id_factura),
    monto      REAL NOT NULL CHECK (monto > 0),
    metodo     TEXT NOT NULL,
    referencia TEXT,
    fecha      TEXT NOT NULL,
    id_usuario INTEGER NOT NULL REFERENCES usuario(id_usuario)
);

-- El recibo usa el mismo número que el pago (REC-<id_pago>), por eso no necesita tabla aparte.

CREATE TABLE IF NOT EXISTS certificado (
    id_certificado INTEGER PRIMARY KEY AUTOINCREMENT,
    id_alumno  INTEGER NOT NULL UNIQUE REFERENCES alumno(id_alumno),
    fecha      TEXT NOT NULL,
    estado     TEXT NOT NULL DEFAULT 'Falta validar',
    id_usuario INTEGER NOT NULL REFERENCES usuario(id_usuario)
);

-- RNF-12: bitácora (quién hizo qué y cuándo)
CREATE TABLE IF NOT EXISTS bitacora (
    id_bitacora INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha   TEXT NOT NULL,
    usuario TEXT,
    accion  TEXT NOT NULL,
    detalle TEXT
);
