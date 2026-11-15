# Preparación de las pruebas: cada prueba usa una base de datos nueva y temporal.
import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # noqa: E402
from app import app as aplicacion  # noqa: E402
from app.datos.base_datos import crear_base_de_datos  # noqa: E402


@pytest.fixture
def app(tmp_path):
    config.BASE_DATOS = str(tmp_path / "prueba.db")
    crear_base_de_datos()
    aplicacion.config["TESTING"] = True
    return aplicacion


def entrar(cliente, usuario, clave):
    return cliente.post("/login", data={"usuario": usuario, "clave": clave})


@pytest.fixture
def recepcion(app):
    cliente = app.test_client()
    entrar(cliente, "recepcion", "Recepcion2026!")
    return cliente


@pytest.fixture
def admin(app):
    cliente = app.test_client()
    entrar(cliente, "admin", "Admin2026!")
    return cliente


def consultar(sql):
    con = sqlite3.connect(config.BASE_DATOS)
    fila = con.execute(sql).fetchone()
    con.close()
    return fila
