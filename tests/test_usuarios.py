"""Pruebas del modelo de usuario (tarea 2.2).

Specs: autenticacion-roles / Roles reconocidos y Contraseñas protegidas.
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from reservas.models import Rol, Usuario

from .conftest import CONTRASENA


def test_el_sistema_reconoce_exactamente_tres_roles():
    """Spec: autenticacion-roles / Roles reconocidos."""
    assert sorted(Rol.values) == ["administrador", "docente", "estudiante"]


@pytest.mark.parametrize("rol", Rol.values)
def test_usuario_con_un_unico_rol(db, rol):
    """Spec: autenticacion-roles / Roles reconocidos / Usuario con un único rol."""
    usuario = Usuario.objects.create_user(
        f"{rol}@uni.edu", "Persona", CONTRASENA, rol=rol
    )
    usuario.refresh_from_db()
    assert usuario.rol == rol
    assert usuario.rol in Rol.values


def test_el_rol_es_obligatorio_al_crear_un_usuario(db):
    with pytest.raises(TypeError):
        Usuario.objects.create_user("sin-rol@uni.edu", "Sin Rol", CONTRASENA)


def test_un_rol_inventado_se_rechaza_en_validacion(db):
    usuario = Usuario(email="x@uni.edu", nombre="X", rol="superhéroe")
    with pytest.raises(ValidationError):
        usuario.full_clean(exclude=["password"])


def test_la_base_de_datos_rechaza_un_rol_inventado(db):
    """El rol válido se garantiza también en base de datos (PLAN 7.3)."""
    with pytest.raises(IntegrityError), transaction.atomic():
        Usuario.objects.create_user("x@uni.edu", "X", CONTRASENA, rol="superhéroe")


def test_el_correo_es_unico_sin_distinguir_mayusculas(db):
    Usuario.objects.create_user("Ana@uni.edu", "Ana", CONTRASENA, rol=Rol.DOCENTE)
    with pytest.raises(IntegrityError), transaction.atomic():
        Usuario.objects.create_user("ana@UNI.edu", "Otra Ana", CONTRASENA, rol=Rol.DOCENTE)


def test_el_correo_se_guarda_en_minusculas(db):
    usuario = Usuario.objects.create_user(
        "  Pedro@Uni.EDU ", "Pedro", CONTRASENA, rol=Rol.ESTUDIANTE
    )
    assert usuario.email == "pedro@uni.edu"


def test_contrasena_no_aparece_en_texto_plano(estudiante):
    """Spec: autenticacion-roles / Contraseñas protegidas / Contraseña no recuperable."""
    guardado = Usuario.objects.values_list("password", flat=True).get(pk=estudiante.pk)
    assert CONTRASENA not in guardado
    assert guardado.startswith("pbkdf2_")  # hash con sal, no reversible
    assert estudiante.check_password(CONTRASENA)
    assert not estudiante.check_password("otra-clave")


def test_el_superusuario_es_administrador_con_acceso_al_panel(administrador):
    assert administrador.rol == Rol.ADMINISTRADOR
    assert administrador.is_staff
    assert administrador.is_superuser
