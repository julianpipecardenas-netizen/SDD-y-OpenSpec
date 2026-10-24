"""Pruebas unitarias del validador de reserva en el pasado (tarea 4.6).

Spec: creacion-reservas / No se reserva en el pasado. Reloj fijo inyectado
(design D9); sin base de datos.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from reservas import errores
from reservas.errores import ErrorDominio
from reservas.services.validadores import ContextoReserva, validar_no_en_el_pasado

BOGOTA = ZoneInfo("America/Bogota")
AHORA = datetime(2030, 3, 15, 10, 0, tzinfo=BOGOTA)


def contexto(fecha, inicio, fin="23:00"):
    return ContextoReserva(
        espacio_id=1, fecha=fecha, hora_inicio=inicio, hora_fin=fin, espacio=None, ahora=AHORA
    )


def test_inicio_ya_transcurrido():
    """Spec: creacion-reservas / No se reserva en el pasado / Inicio ya transcurrido."""
    with pytest.raises(ErrorDominio) as info:
        validar_no_en_el_pasado(contexto("2030-03-15", "09:00"))
    assert info.value.codigo == errores.RESERVA_EN_PASADO


def test_dia_anterior():
    """Spec: creacion-reservas / No se reserva en el pasado / Inicio ya transcurrido."""
    with pytest.raises(ErrorDominio) as info:
        validar_no_en_el_pasado(contexto("2030-03-14", "22:00"))
    assert info.value.codigo == errores.RESERVA_EN_PASADO


def test_inicio_igual_al_instante_actual_no_es_posterior():
    """Spec: creacion-reservas / No se reserva en el pasado / Inicio ya transcurrido (borde)."""
    with pytest.raises(ErrorDominio) as info:
        validar_no_en_el_pasado(contexto("2030-03-15", "10:00"))
    assert info.value.codigo == errores.RESERVA_EN_PASADO


def test_inicio_un_minuto_despues_es_valido():
    """Spec: creacion-reservas / No se reserva en el pasado / Inicio en el futuro (borde)."""
    assert validar_no_en_el_pasado(contexto("2030-03-15", "10:01")) is None


def test_inicio_en_el_futuro():
    """Spec: creacion-reservas / No se reserva en el pasado / Inicio en el futuro."""
    assert validar_no_en_el_pasado(contexto("2030-03-16", "08:00")) is None
