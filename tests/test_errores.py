"""Pruebas del error de dominio (tarea 2.1, design D5).

No corresponden a un escenario de las specs: verifican la base común que
usan todas las reglas para informar sus códigos.
"""

import pytest

from reservas import errores
from reservas.errores import CODIGOS, ErrorDominio, MENSAJES

# Lista de design D5, escrita a mano a propósito: si cambia, el diseño también.
CODIGOS_DEL_DISENO = [
    "CREDENCIALES_INVALIDAS",
    "NO_AUTENTICADO",
    "SIN_PERMISO",
    "DATOS_INVALIDOS",
    "HORARIO_INVALIDO",
    "RESERVA_EN_PASADO",
    "CONFLICTO_HORARIO",
    "ESPACIO_NO_ENCONTRADO",
    "ESPACIO_INACTIVO",
    "ESPACIO_DUPLICADO",
    "ESPACIO_CON_RESERVAS",
    "RESERVA_NO_ENCONTRADA",
    "RESERVA_YA_CANCELADA",
    "RESERVA_NO_CANCELABLE",
    "DURACION_RESERVA_EXCEDIDA",
]


def test_los_codigos_son_exactamente_los_del_diseno():
    assert sorted(CODIGOS) == sorted(CODIGOS_DEL_DISENO)


@pytest.mark.parametrize("codigo", CODIGOS_DEL_DISENO)
def test_cada_codigo_tiene_constante_y_mensaje(codigo):
    assert getattr(errores, codigo) == codigo
    assert MENSAJES[codigo].strip()


def test_el_error_expone_codigo_y_mensaje():
    error = ErrorDominio(errores.SIN_PERMISO)
    assert error.codigo == "SIN_PERMISO"
    assert error.mensaje == MENSAJES["SIN_PERMISO"]


def test_el_mensaje_se_puede_personalizar():
    error = ErrorDominio(errores.DATOS_INVALIDOS, "Falta la hora de fin.")
    assert error.codigo == "DATOS_INVALIDOS"
    assert error.mensaje == "Falta la hora de fin."


def test_es_una_excepcion_que_se_puede_capturar():
    with pytest.raises(ErrorDominio) as info:
        raise ErrorDominio(errores.NO_AUTENTICADO)
    assert info.value.codigo == "NO_AUTENTICADO"


def test_un_codigo_desconocido_se_rechaza():
    with pytest.raises(ValueError):
        ErrorDominio("CODIGO_INVENTADO")


def test_el_mensaje_de_conflicto_es_el_que_fija_la_spec():
    """Spec: validacion-conflictos-horario / No solapamiento de reservas activas."""
    assert MENSAJES["CONFLICTO_HORARIO"] == "El espacio ya está reservado en ese horario"
