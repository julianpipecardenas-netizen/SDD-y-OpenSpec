"""Pruebas unitarias de los validadores de datos y de rango horario (tarea 4.4).

Specs: creacion-reservas / Datos obligatorios y bien formados y Rango horario
válido. Sin base de datos ni sesión (RNF-02).
"""

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest

from reservas import errores
from reservas.errores import ErrorDominio
from reservas.services.validadores import (
    ContextoReserva,
    validar_datos_obligatorios,
    validar_rango_horario,
)

BOGOTA = ZoneInfo("America/Bogota")


def contexto(**cambios):
    datos = dict(
        espacio_id=1,
        fecha="2030-03-15",
        hora_inicio="10:00",
        hora_fin="12:00",
        espacio=None,
        ahora=datetime(2030, 3, 1, 8, 0, tzinfo=BOGOTA),
    )
    datos.update(cambios)
    return ContextoReserva(**datos)


def codigo_de(validador, ctx):
    with pytest.raises(ErrorDominio) as info:
        validador(ctx)
    return info.value.codigo


# --- Datos obligatorios y bien formados ----------------------------------------


def test_datos_completos_son_validos():
    assert validar_datos_obligatorios(contexto()) is None


def test_acepta_objetos_de_fecha_y_hora():
    ctx = contexto(fecha=date(2030, 3, 15), hora_inicio=time(10, 0), hora_fin=time(12, 0))
    assert validar_datos_obligatorios(ctx) is None


@pytest.mark.parametrize("campo", ["espacio_id", "fecha", "hora_inicio", "hora_fin"])
@pytest.mark.parametrize("vacio", [None, "", "   "])
def test_falta_un_dato(campo, vacio):
    """Spec: creacion-reservas / Datos obligatorios y bien formados / Falta un dato."""
    assert codigo_de(validar_datos_obligatorios, contexto(**{campo: vacio})) == errores.DATOS_INVALIDOS


@pytest.mark.parametrize("fecha", ["2030-02-30", "2030-13-01", "15/03/2030", "ayer", 20300315, datetime(2030, 3, 15)])
def test_fecha_inexistente_o_mal_formada(fecha):
    """Spec: creacion-reservas / Datos obligatorios y bien formados / Fecha inexistente."""
    assert codigo_de(validar_datos_obligatorios, contexto(fecha=fecha)) == errores.DATOS_INVALIDOS


@pytest.mark.parametrize("campo", ["hora_inicio", "hora_fin"])
@pytest.mark.parametrize("hora", ["25:00", "10:60", "10", "mediodía", 10])
def test_hora_fuera_de_rango_o_mal_formada(campo, hora):
    """Spec: creacion-reservas / Datos obligatorios y bien formados / Hora fuera de rango."""
    assert codigo_de(validar_datos_obligatorios, contexto(**{campo: hora})) == errores.DATOS_INVALIDOS


# --- Rango horario válido --------------------------------------------------------


def test_rango_valido():
    assert validar_rango_horario(contexto()) is None


def test_fin_igual_al_inicio():
    """Spec: creacion-reservas / Rango horario válido / Fin igual al inicio."""
    ctx = contexto(hora_inicio="10:00", hora_fin="10:00")
    assert codigo_de(validar_rango_horario, ctx) == errores.HORARIO_INVALIDO


def test_fin_anterior_al_inicio():
    """Spec: creacion-reservas / Rango horario válido / Fin anterior al inicio."""
    ctx = contexto(hora_inicio="12:00", hora_fin="10:00")
    assert codigo_de(validar_rango_horario, ctx) == errores.HORARIO_INVALIDO


def test_reserva_que_cruza_la_medianoche():
    """Spec: creacion-reservas / Rango horario válido / Reserva que cruza la medianoche."""
    ctx = contexto(hora_inicio="23:00", hora_fin="01:00")
    assert codigo_de(validar_rango_horario, ctx) == errores.HORARIO_INVALIDO


def test_reserva_minima_de_un_minuto():
    """Spec: creacion-reservas / Rango horario válido / Reserva mínima de un minuto."""
    assert validar_rango_horario(contexto(hora_inicio="10:00", hora_fin="10:01")) is None
