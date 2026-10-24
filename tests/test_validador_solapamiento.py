"""Pruebas unitarias del validador de no solapamiento (tarea 5.1).

Spec: validacion-conflictos-horario. Sin base de datos ni sesión: la regla se
evalúa solo con las reservas existentes y el rango solicitado.
"""

from datetime import datetime, time
from zoneinfo import ZoneInfo

import pytest

from reservas import errores
from reservas.errores import ErrorDominio
from reservas.services.validadores import (
    ContextoReserva,
    hay_solapamiento,
    validar_no_solapamiento,
)

BOGOTA = ZoneInfo("America/Bogota")


def contexto(inicio, fin, existentes):
    """Contexto con el rango solicitado y reservas existentes como pares de horas."""
    return ContextoReserva(
        espacio_id=1,
        fecha="2030-03-15",
        hora_inicio=inicio,
        hora_fin=fin,
        espacio=None,
        ahora=datetime(2030, 3, 1, 8, 0, tzinfo=BOGOTA),
        reservas_existentes=tuple(existentes),
    )


def hay_conflicto(inicio, fin, existentes):
    try:
        validar_no_solapamiento(contexto(inicio, fin, existentes))
    except ErrorDominio as error:
        assert error.codigo == errores.CONFLICTO_HORARIO
        return True
    return False


EXISTENTE_10_A_12 = [(time(10, 0), time(12, 0))]


def test_solapamiento_parcial_por_el_final():
    """Spec: validacion-conflictos-horario / No solapamiento de reservas activas / Solapamiento parcial por el final."""
    assert hay_conflicto("11:00", "13:00", EXISTENTE_10_A_12)


def test_solapamiento_parcial_por_el_inicio():
    """Spec: validacion-conflictos-horario / No solapamiento de reservas activas / Solapamiento parcial por el inicio."""
    assert hay_conflicto("09:00", "11:00", EXISTENTE_10_A_12)


def test_rango_contenido_en_otro():
    """Spec: validacion-conflictos-horario / No solapamiento de reservas activas / Rango contenido en otro."""
    assert hay_conflicto("11:00", "12:00", [(time(10, 0), time(14, 0))])


def test_rango_que_contiene_a_otro():
    """Spec: validacion-conflictos-horario / No solapamiento de reservas activas / Rango que contiene a otro."""
    assert hay_conflicto("10:00", "14:00", [(time(11, 0), time(12, 0))])


def test_horario_identico():
    """Spec: validacion-conflictos-horario / No solapamiento de reservas activas / Horario idéntico."""
    assert hay_conflicto("10:00", "12:00", EXISTENTE_10_A_12)


def test_inicio_igual_al_fin_de_otra_reserva_no_es_conflicto():
    """Spec: validacion-conflictos-horario / Reservas contiguas permitidas / Inicio igual al fin de otra reserva."""
    assert not hay_conflicto("12:00", "14:00", EXISTENTE_10_A_12)


def test_fin_igual_al_inicio_de_otra_reserva_no_es_conflicto():
    """Spec: validacion-conflictos-horario / Reservas contiguas permitidas / Fin igual al inicio de otra reserva."""
    assert not hay_conflicto("08:00", "10:00", EXISTENTE_10_A_12)


def test_sin_reservas_existentes_no_hay_conflicto():
    """Spec: validacion-conflictos-horario / Regla verificable de forma aislada / Evaluación sin interfaz."""
    assert not hay_conflicto("10:00", "12:00", [])


def test_rango_lejano_no_es_conflicto():
    assert not hay_conflicto("14:00", "15:00", EXISTENTE_10_A_12)


def test_basta_con_chocar_con_una_de_varias_reservas():
    existentes = [(time(8, 0), time(9, 0)), (time(10, 0), time(12, 0)), (time(15, 0), time(16, 0))]
    assert hay_conflicto("11:30", "11:45", existentes)
    assert not hay_conflicto("12:00", "15:00", existentes)


def test_reserva_de_un_minuto_dentro_de_otra_es_conflicto():
    assert hay_conflicto("10:30", "10:31", EXISTENTE_10_A_12)


def test_el_mensaje_del_conflicto_es_el_que_fija_la_spec():
    """Spec: validacion-conflictos-horario / No solapamiento de reservas activas / Horario idéntico."""
    with pytest.raises(ErrorDominio) as info:
        validar_no_solapamiento(contexto("10:00", "12:00", EXISTENTE_10_A_12))
    assert info.value.codigo == errores.CONFLICTO_HORARIO
    assert info.value.mensaje == "El espacio ya está reservado en ese horario"


@pytest.mark.parametrize(
    "a, b, esperado",
    [
        ((time(10), time(12)), (time(11), time(13)), True),
        ((time(10), time(12)), (time(12), time(14)), False),
        ((time(10), time(12)), (time(8), time(10)), False),
        ((time(10), time(14)), (time(11), time(12)), True),
    ],
)
def test_hay_solapamiento_es_simetrica(a, b, esperado):
    """Spec: validacion-conflictos-horario / Regla verificable de forma aislada / Evaluación sin interfaz."""
    assert hay_solapamiento(*a, *b) is esperado
    assert hay_solapamiento(*b, *a) is esperado
