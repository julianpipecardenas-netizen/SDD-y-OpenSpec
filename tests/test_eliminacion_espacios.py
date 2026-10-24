"""Pruebas de eliminación y desactivación de espacios con reservas (tarea 4.2).

Spec: gestion-espacios / Activación y desactivación.
"""

import pytest

from reservas.errores import (
    ESPACIO_CON_RESERVAS,
    ESPACIO_NO_ENCONTRADO,
    NO_AUTENTICADO,
    SIN_PERMISO,
    ErrorDominio,
)
from reservas.models import Espacio, EstadoReserva, Reserva
from reservas.services import espacios


def codigo_de(funcion, *args, **kwargs):
    with pytest.raises(ErrorDominio) as info:
        funcion(*args, **kwargs)
    return info.value.codigo


def test_eliminacion_bloqueada_con_reservas(administrador, espacio, fabrica_reservas):
    """Spec: gestion-espacios / Activación y desactivación / Eliminación bloqueada con reservas."""
    fabrica_reservas()
    assert codigo_de(espacios.eliminar_espacio, administrador, espacio.pk) == ESPACIO_CON_RESERVAS
    assert Espacio.objects.filter(pk=espacio.pk).exists()
    assert Reserva.objects.count() == 1


def test_eliminacion_bloqueada_tambien_con_reservas_canceladas(
    administrador, espacio, fabrica_reservas
):
    """Spec: gestion-espacios / Activación y desactivación / Eliminación bloqueada con reservas."""
    fabrica_reservas(estado=EstadoReserva.CANCELADA)
    assert codigo_de(espacios.eliminar_espacio, administrador, espacio.pk) == ESPACIO_CON_RESERVAS
    assert Espacio.objects.filter(pk=espacio.pk).exists()


def test_un_espacio_sin_reservas_se_puede_eliminar(administrador, espacio):
    espacios.eliminar_espacio(administrador, espacio.pk)
    assert not Espacio.objects.filter(pk=espacio.pk).exists()


def test_solo_el_administrador_elimina(estudiante, docente, espacio):
    assert codigo_de(espacios.eliminar_espacio, estudiante, espacio.pk) == SIN_PERMISO
    assert codigo_de(espacios.eliminar_espacio, docente, espacio.pk) == SIN_PERMISO
    assert Espacio.objects.filter(pk=espacio.pk).exists()


def test_eliminar_sin_sesion(espacio):
    from django.contrib.auth.models import AnonymousUser

    assert codigo_de(espacios.eliminar_espacio, AnonymousUser(), espacio.pk) == NO_AUTENTICADO


def test_eliminar_un_espacio_inexistente(administrador):
    assert codigo_de(espacios.eliminar_espacio, administrador, 9999) == ESPACIO_NO_ENCONTRADO


def test_reservas_existentes_se_conservan_al_desactivar(administrador, espacio, fabrica_reservas):
    """Spec: gestion-espacios / Activación y desactivación / Reservas existentes se conservan."""
    reserva = fabrica_reservas()
    espacios.desactivar_espacio(administrador, espacio.pk)
    reserva.refresh_from_db()
    assert reserva.estado == EstadoReserva.ACTIVA
    espacio.refresh_from_db()
    assert espacio.activo is False
