"""Fixtures compartidas por todas las pruebas."""

import pytest

from reservas.models import Espacio, Rol, TipoEspacio, Usuario

CONTRASENA = "clave-de-prueba-123"


@pytest.fixture
def estudiante(db):
    return Usuario.objects.create_user(
        "estudiante@uni.edu", "Estela Estudiante", CONTRASENA, rol=Rol.ESTUDIANTE
    )


@pytest.fixture
def docente(db):
    return Usuario.objects.create_user(
        "docente@uni.edu", "Daniel Docente", CONTRASENA, rol=Rol.DOCENTE
    )


@pytest.fixture
def administrador(db):
    return Usuario.objects.create_superuser("admin@uni.edu", "Ana Admin", CONTRASENA)


@pytest.fixture
def espacio(db):
    return Espacio.objects.create(
        nombre="Lab 301", tipo=TipoEspacio.LABORATORIO, capacidad=30
    )
