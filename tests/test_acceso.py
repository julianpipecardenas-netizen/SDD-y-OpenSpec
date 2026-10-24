"""Pruebas de autenticación obligatoria y control por rol (tarea 2.4).

Specs: autenticacion-roles / Operaciones protegidas exigen autenticación y
Roles reconocidos. Estas pruebas cubren las guardas de los servicios; los
escenarios completos («Consulta sin sesión», «Creación de reserva sin sesión»,
«Operación reservada al administrador») se prueban de punta a punta cuando
existan los servicios de disponibilidad, reservas y espacios.
"""

import pytest
from django.contrib.auth.models import AnonymousUser

from reservas.errores import NO_AUTENTICADO, SIN_PERMISO, ErrorDominio
from reservas.services.acceso import (
    ROLES_ADMINISTRADOR,
    ROLES_TODOS,
    es_administrador,
    exigir_autenticado,
    exigir_rol,
)


@pytest.mark.parametrize("actor", [None, AnonymousUser()], ids=["sin-actor", "anonimo"])
def test_sin_sesion_se_rechaza_con_no_autenticado(actor):
    """Spec: autenticacion-roles / Operaciones protegidas exigen autenticación (guarda)."""
    with pytest.raises(ErrorDominio) as info:
        exigir_autenticado(actor)
    assert info.value.codigo == NO_AUTENTICADO


@pytest.mark.parametrize("actor", [None, AnonymousUser()], ids=["sin-actor", "anonimo"])
def test_exigir_rol_sin_sesion_informa_no_autenticado_antes_que_sin_permiso(actor):
    with pytest.raises(ErrorDominio) as info:
        exigir_rol(actor, *ROLES_ADMINISTRADOR)
    assert info.value.codigo == NO_AUTENTICADO


def test_con_sesion_valida_se_devuelve_al_actor(estudiante):
    assert exigir_autenticado(estudiante) is estudiante


def test_operacion_reservada_al_administrador_rechaza_estudiante_y_docente(estudiante, docente):
    """Spec: autenticacion-roles / Roles reconocidos / Operación reservada al administrador (guarda)."""
    for actor in (estudiante, docente):
        with pytest.raises(ErrorDominio) as info:
            exigir_rol(actor, *ROLES_ADMINISTRADOR)
        assert info.value.codigo == SIN_PERMISO


def test_el_administrador_pasa_la_guarda_de_administrador(administrador):
    assert exigir_rol(administrador, *ROLES_ADMINISTRADOR) is administrador


def test_estudiante_y_docente_tienen_los_mismos_permisos(estudiante, docente):
    """Spec: autenticacion-roles / Roles reconocidos / Estudiante y docente tienen los mismos permisos (guarda)."""

    def resultado(actor, roles):
        try:
            exigir_rol(actor, *roles)
            return "permitido"
        except ErrorDominio as error:
            return error.codigo

    for roles in (ROLES_TODOS, ROLES_ADMINISTRADOR):
        assert resultado(estudiante, roles) == resultado(docente, roles)
    assert resultado(estudiante, ROLES_TODOS) == "permitido"
    assert resultado(estudiante, ROLES_ADMINISTRADOR) == SIN_PERMISO


def test_es_administrador(estudiante, docente, administrador):
    assert es_administrador(administrador)
    assert not es_administrador(estudiante)
    assert not es_administrador(docente)
    assert not es_administrador(None)
    assert not es_administrador(AnonymousUser())
