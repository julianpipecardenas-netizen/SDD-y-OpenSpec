"""Pruebas del servicio de inicio de sesión (tarea 2.3).

Spec: autenticacion-roles / Inicio de sesión con credenciales.
"""

import pytest

from reservas.errores import CREDENCIALES_INVALIDAS, ErrorDominio
from reservas.services.autenticacion import autenticar

from .conftest import CONTRASENA


def test_credenciales_validas_devuelven_el_usuario_con_su_rol(docente):
    """Spec: autenticacion-roles / Inicio de sesión con credenciales / Credenciales válidas."""
    usuario = autenticar("docente@uni.edu", CONTRASENA)
    assert usuario == docente
    assert usuario.rol == "docente"


def test_contrasena_incorrecta(estudiante):
    """Spec: autenticacion-roles / Inicio de sesión con credenciales / Contraseña incorrecta."""
    with pytest.raises(ErrorDominio) as info:
        autenticar("estudiante@uni.edu", "no-es-la-clave")
    assert info.value.codigo == CREDENCIALES_INVALIDAS


def test_correo_no_registrado_da_el_mismo_error_que_contrasena_incorrecta(estudiante):
    """Spec: autenticacion-roles / Inicio de sesión con credenciales / Correo no registrado."""
    with pytest.raises(ErrorDominio) as por_contrasena:
        autenticar("estudiante@uni.edu", "no-es-la-clave")
    with pytest.raises(ErrorDominio) as por_correo:
        autenticar("nadie@uni.edu", CONTRASENA)
    assert por_correo.value.codigo == CREDENCIALES_INVALIDAS
    assert por_correo.value.codigo == por_contrasena.value.codigo
    assert por_correo.value.mensaje == por_contrasena.value.mensaje


@pytest.mark.parametrize("correo, contrasena", [("", ""), (None, None), ("x@uni.edu", "")])
def test_datos_vacios_se_rechazan_como_credenciales_invalidas(db, correo, contrasena):
    with pytest.raises(ErrorDominio) as info:
        autenticar(correo, contrasena)
    assert info.value.codigo == CREDENCIALES_INVALIDAS


def test_un_usuario_inactivo_no_puede_iniciar_sesion(estudiante):
    estudiante.is_active = False
    estudiante.save()
    with pytest.raises(ErrorDominio) as info:
        autenticar("estudiante@uni.edu", CONTRASENA)
    assert info.value.codigo == CREDENCIALES_INVALIDAS


def test_el_correo_no_distingue_mayusculas(estudiante):
    assert autenticar("ESTUDIANTE@Uni.EDU", CONTRASENA) == estudiante
