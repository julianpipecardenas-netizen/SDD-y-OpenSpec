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


@pytest.fixture
def fabrica_reservas(db, estudiante, espacio):
    """Crea reservas directamente en la base de datos, sin pasar por el servicio."""
    from datetime import date, time

    from reservas.models import EstadoReserva, Reserva

    def crear(
        *,
        usuario=None,
        espacio_=None,
        fecha=date(2030, 3, 15),
        inicio=time(10, 0),
        fin=time(12, 0),
        estado=EstadoReserva.ACTIVA,
    ):
        return Reserva.objects.create(
            usuario=usuario or estudiante,
            espacio=espacio_ or espacio,
            fecha=fecha,
            hora_inicio=inicio,
            hora_fin=fin,
            estado=estado,
        )

    return crear
