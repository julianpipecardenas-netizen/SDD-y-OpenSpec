"""Pruebas de integración de las vistas de sesión (tarea 2.5).

Specs: autenticacion-roles / Inicio de sesión con credenciales, Cierre de
sesión, Operaciones protegidas exigen autenticación y Contraseñas protegidas.
"""

import pytest
from django.urls import reverse

from reservas import errores
from reservas.presentacion import ESTADO_HTTP

from .conftest import CONTRASENA


def iniciar_sesion(client, correo, contrasena):
    return client.post(reverse("login"), {"correo": correo, "contrasena": contrasena})


def test_la_pagina_de_login_se_muestra(client, db):
    respuesta = client.get(reverse("login"))
    assert respuesta.status_code == 200
    assert "Iniciar sesión" in respuesta.content.decode()


def test_login_valido_abre_sesion_y_muestra_el_rol(client, docente):
    """Spec: autenticacion-roles / Inicio de sesión con credenciales / Credenciales válidas."""
    respuesta = iniciar_sesion(client, "docente@uni.edu", CONTRASENA)
    assert respuesta.status_code == 302
    pagina = client.get(reverse("inicio"))
    assert pagina.status_code == 200
    contenido = pagina.content.decode()
    assert "Daniel Docente" in contenido
    assert "Docente" in contenido


def test_login_con_contrasena_incorrecta_no_abre_sesion(client, estudiante):
    """Spec: autenticacion-roles / Inicio de sesión con credenciales / Contraseña incorrecta."""
    respuesta = iniciar_sesion(client, "estudiante@uni.edu", "no-es-la-clave")
    assert respuesta.status_code == 401
    assert errores.CREDENCIALES_INVALIDAS in respuesta.content.decode()
    assert client.get(reverse("inicio")).status_code == 401


def test_login_con_correo_no_registrado_muestra_el_mismo_error(client, estudiante):
    """Spec: autenticacion-roles / Inicio de sesión con credenciales / Correo no registrado."""
    mala_clave = iniciar_sesion(client, "estudiante@uni.edu", "no-es-la-clave")
    sin_correo = iniciar_sesion(client, "nadie@uni.edu", CONTRASENA)
    assert sin_correo.status_code == mala_clave.status_code == 401
    assert errores.CREDENCIALES_INVALIDAS in sin_correo.content.decode()
    assert errores.MENSAJES[errores.CREDENCIALES_INVALIDAS] in sin_correo.content.decode()
    assert errores.MENSAJES[errores.CREDENCIALES_INVALIDAS] in mala_clave.content.decode()


def test_cierre_de_sesion_invalida_la_sesion(client, estudiante):
    """Spec: autenticacion-roles / Cierre de sesión / Cierre de sesión exitoso."""
    iniciar_sesion(client, "estudiante@uni.edu", CONTRASENA)
    assert client.get(reverse("inicio")).status_code == 200

    respuesta = client.post(reverse("logout"))
    assert respuesta.status_code == 302

    despues = client.get(reverse("inicio"))
    assert despues.status_code == 401
    assert errores.NO_AUTENTICADO in despues.content.decode()


def test_cerrar_sesion_solo_se_permite_por_post(client, estudiante):
    iniciar_sesion(client, "estudiante@uni.edu", CONTRASENA)
    assert client.get(reverse("logout")).status_code == 405
    assert client.get(reverse("inicio")).status_code == 200  # la sesión sigue abierta


def test_operacion_protegida_sin_sesion_responde_no_autenticado(client, db):
    """Spec: autenticacion-roles / Operaciones protegidas exigen autenticación (vista de inicio)."""
    respuesta = client.get(reverse("inicio"))
    assert respuesta.status_code == 401
    assert errores.NO_AUTENTICADO in respuesta.content.decode()


def test_quien_ya_tiene_sesion_es_redirigido_desde_el_login(client, estudiante):
    iniciar_sesion(client, "estudiante@uni.edu", CONTRASENA)
    respuesta = client.get(reverse("login"))
    assert respuesta.status_code == 302
    assert respuesta.url == reverse("inicio")


def test_ninguna_respuesta_incluye_la_contrasena(client, estudiante):
    """Spec: autenticacion-roles / Contraseñas protegidas / Contraseña ausente en respuestas."""
    fallido = iniciar_sesion(client, "estudiante@uni.edu", "clave-que-se-envia-mal")
    assert "clave-que-se-envia-mal" not in fallido.content.decode()

    iniciar_sesion(client, "estudiante@uni.edu", CONTRASENA)
    inicio = client.get(reverse("inicio")).content.decode()
    assert CONTRASENA not in inicio
    assert estudiante.password not in inicio  # tampoco el hash almacenado


def test_todo_codigo_de_dominio_tiene_estado_http():
    """Design D2: la tabla código -> estado HTTP cubre todos los códigos."""
    assert set(ESTADO_HTTP) == set(errores.CODIGOS)
    assert all(400 <= estado < 500 for estado in ESTADO_HTTP.values())
