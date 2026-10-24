"""Pruebas del marco de validadores (tarea 4.3).

Spec: creacion-reservas / Orden de validación y atomicidad. Sin base de datos.
"""

import pytest

from reservas import errores
from reservas.errores import ErrorDominio
from reservas.services.validadores import (
    VALIDADORES_RESERVA,
    ejecutar_validadores,
    validar_datos_obligatorios,
    validar_espacio_activo,
    validar_no_en_el_pasado,
    validar_no_solapamiento,
    validar_rango_horario,
)


def test_se_ejecutan_en_orden():
    """Spec: creacion-reservas / Orden de validación y atomicidad / Se informa el primer error en orden (marco)."""
    llamadas = []
    validadores = [lambda c, n=n: llamadas.append(n) for n in ("a", "b", "c")]
    ejecutar_validadores(object(), validadores)
    assert llamadas == ["a", "b", "c"]


def test_se_detiene_en_la_primera_falla():
    """Spec: creacion-reservas / Orden de validación y atomicidad / Se informa el primer error en orden (marco)."""
    llamadas = []

    def ok(c):
        llamadas.append("ok")

    def falla(c):
        llamadas.append("falla")
        raise ErrorDominio(errores.HORARIO_INVALIDO)

    def nunca(c):
        llamadas.append("nunca")

    with pytest.raises(ErrorDominio) as info:
        ejecutar_validadores(object(), [ok, falla, nunca])
    assert info.value.codigo == errores.HORARIO_INVALIDO
    assert llamadas == ["ok", "falla"]


def test_sin_fallas_no_devuelve_nada():
    assert ejecutar_validadores(object(), []) is None


def test_el_orden_registrado_es_el_de_la_spec():
    assert VALIDADORES_RESERVA == (
        validar_datos_obligatorios,
        validar_rango_horario,
        validar_espacio_activo,
        validar_no_en_el_pasado,
        validar_no_solapamiento,
    )
