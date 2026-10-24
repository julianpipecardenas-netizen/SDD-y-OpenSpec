"""Pruebas unitarias del validador de espacio existente y activo (tarea 4.5).

Spec: creacion-reservas / Espacio existente y activo. Sin base de datos: el
espacio es un objeto sin guardar.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from reservas import errores
from reservas.errores import ErrorDominio
from reservas.models import Espacio, TipoEspacio
from reservas.services.validadores import ContextoReserva, validar_espacio_activo


def contexto(espacio):
    return ContextoReserva(
        espacio_id=1,
        fecha="2030-03-15",
        hora_inicio="10:00",
        hora_fin="12:00",
        espacio=espacio,
        ahora=datetime(2030, 3, 1, 8, 0, tzinfo=ZoneInfo("America/Bogota")),
    )


def test_espacio_activo_es_valido():
    espacio = Espacio(nombre="Lab", tipo=TipoEspacio.LABORATORIO, capacidad=10, activo=True)
    assert validar_espacio_activo(contexto(espacio)) is None


def test_espacio_inexistente():
    """Spec: creacion-reservas / Espacio existente y activo / Espacio inexistente."""
    with pytest.raises(ErrorDominio) as info:
        validar_espacio_activo(contexto(None))
    assert info.value.codigo == errores.ESPACIO_NO_ENCONTRADO


def test_espacio_inactivo():
    """Spec: creacion-reservas / Espacio existente y activo / Espacio inactivo."""
    espacio = Espacio(nombre="Lab", tipo=TipoEspacio.LABORATORIO, capacidad=10, activo=False)
    with pytest.raises(ErrorDominio) as info:
        validar_espacio_activo(contexto(espacio))
    assert info.value.codigo == errores.ESPACIO_INACTIVO
