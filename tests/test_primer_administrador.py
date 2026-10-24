"""Pruebas del primer administrador y del alta de usuarios (tarea 2.6, design D11).

Spec: autenticacion-roles / Roles reconocidos y Contraseñas protegidas.
"""

import pytest
from django.core.management import call_command
from django.urls import reverse

from reservas.models import Rol, Usuario
from reservas.services.autenticacion import autenticar

from .conftest import CONTRASENA


def test_createsuperuser_crea_un_administrador_que_puede_iniciar_sesion(db, monkeypatch):
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", CONTRASENA)
    call_command(
        "createsuperuser",
        interactive=False,
        email="Primero@uni.edu",
        nombre="Primer Administrador",
        verbosity=0,
    )
    usuario = Usuario.objects.get(email="primero@uni.edu")
    assert usuario.rol == Rol.ADMINISTRADOR
    assert usuario.is_staff and usuario.is_superuser
    assert autenticar("primero@uni.edu", CONTRASENA) == usuario


def test_el_administrador_crea_usuarios_desde_el_panel(client, administrador):
    client.force_login(administrador)
    assert client.get("/admin/reservas/usuario/add/").status_code == 200

    respuesta = client.post(
        "/admin/reservas/usuario/add/",
        {
            "email": "Nueva@uni.edu",
            "nombre": "Nueva Docente",
            "rol": Rol.DOCENTE,
            "password1": CONTRASENA,
            "password2": CONTRASENA,
        },
    )
    assert respuesta.status_code == 302, respuesta.content.decode()[:500]

    creada = Usuario.objects.get(email="nueva@uni.edu")
    assert creada.rol == Rol.DOCENTE
    assert creada.password != CONTRASENA  # guardada con hash
    assert creada.check_password(CONTRASENA)
    assert not creada.is_staff  # un docente no entra al panel


def test_el_panel_exige_elegir_un_rol_valido(client, administrador):
    client.force_login(administrador)
    respuesta = client.post(
        "/admin/reservas/usuario/add/",
        {
            "email": "sinrol@uni.edu",
            "nombre": "Sin Rol",
            "rol": "superhéroe",
            "password1": CONTRASENA,
            "password2": CONTRASENA,
        },
    )
    assert respuesta.status_code == 200  # vuelve al formulario con el error
    assert not Usuario.objects.filter(email="sinrol@uni.edu").exists()


def test_un_estudiante_no_entra_al_panel(client, estudiante):
    client.force_login(estudiante)
    respuesta = client.get("/admin/reservas/usuario/")
    assert respuesta.status_code == 302  # el panel lo redirige al login del panel
    assert "/admin/login/" in respuesta.url
