"""Pruebas de integración de las vistas de espacios (tarea 3.5).

Specs: gestion-espacios (todos los requisitos) y autenticacion-roles / Roles
reconocidos. Se entra con `force_login` porque el inicio de sesión ya se
prueba en test_vistas_autenticacion.py.
"""

from django.urls import reverse

from reservas import errores
from reservas.models import Espacio
from reservas.services import espacios as servicio


def entrar(client, usuario):
    client.force_login(usuario)
    return client


def pagina(respuesta):
    return respuesta.content.decode()


def datos_de_formulario(**cambios):
    datos = {"nombre": "Lab 301", "tipo": "laboratorio", "capacidad": "30"}
    datos.update(cambios)
    return datos


# --- Crear ---------------------------------------------------------------


def test_el_administrador_crea_un_espacio(client, administrador):
    """Spec: gestion-espacios / Datos de un espacio / Espacio creado con datos válidos."""
    entrar(client, administrador)
    respuesta = client.post(reverse("espacio_nuevo"), datos_de_formulario())
    espacio = Espacio.objects.get(nombre="Lab 301")
    assert respuesta.status_code == 302
    assert respuesta.url == reverse("espacio_detalle", args=[espacio.pk])
    assert espacio.activo and espacio.capacidad == 30
    assert "Lab 301" in pagina(client.get(reverse("espacios")))


def test_el_formulario_de_nuevo_espacio_se_muestra_al_administrador(client, administrador):
    entrar(client, administrador)
    respuesta = client.get(reverse("espacio_nuevo"))
    assert respuesta.status_code == 200
    assert "Nuevo espacio" in pagina(respuesta)


def test_un_docente_no_puede_ver_ni_enviar_el_formulario_de_creacion(client, docente):
    """Spec: autenticacion-roles / Roles reconocidos / Operación reservada al administrador."""
    entrar(client, docente)
    pantalla = client.get(reverse("espacio_nuevo"))
    envio = client.post(reverse("espacio_nuevo"), datos_de_formulario())
    for respuesta in (pantalla, envio):
        assert respuesta.status_code == 403
        assert errores.SIN_PERMISO in pagina(respuesta)
    assert Espacio.objects.count() == 0


def test_dato_invalido_vuelve_al_formulario_con_el_error(client, administrador):
    """Spec: gestion-espacios / Datos de un espacio / Capacidad inválida."""
    entrar(client, administrador)
    respuesta = client.post(reverse("espacio_nuevo"), datos_de_formulario(capacidad="0"))
    contenido = pagina(respuesta)
    assert respuesta.status_code == 422
    assert errores.DATOS_INVALIDOS in contenido
    assert "Lab 301" in contenido  # conserva lo que se escribió
    assert Espacio.objects.count() == 0


def test_nombre_duplicado_se_informa_en_el_formulario(client, administrador, espacio):
    """Spec: gestion-espacios / Datos de un espacio / Nombre duplicado."""
    entrar(client, administrador)
    respuesta = client.post(reverse("espacio_nuevo"), datos_de_formulario(nombre="LAB 301"))
    assert respuesta.status_code == 409
    assert errores.ESPACIO_DUPLICADO in pagina(respuesta)
    assert Espacio.objects.count() == 1


def test_tipo_no_permitido_se_informa_en_el_formulario(client, administrador):
    """Spec: gestion-espacios / Datos de un espacio / Tipo no permitido."""
    entrar(client, administrador)
    respuesta = client.post(reverse("espacio_nuevo"), datos_de_formulario(tipo="cafeteria"))
    assert respuesta.status_code == 422
    assert errores.DATOS_INVALIDOS in pagina(respuesta)
    assert Espacio.objects.count() == 0


# --- Sesión obligatoria --------------------------------------------------


def test_sin_sesion_las_paginas_de_espacios_responden_no_autenticado(client, espacio):
    for ruta in (
        reverse("espacios"),
        reverse("espacio_detalle", args=[espacio.pk]),
        reverse("espacio_nuevo"),
    ):
        respuesta = client.get(ruta)
        assert respuesta.status_code == 401
        assert errores.NO_AUTENTICADO in pagina(respuesta)


# --- Listar y consultar --------------------------------------------------


def test_el_estudiante_solo_ve_espacios_activos(client, estudiante, administrador, espacio):
    """Spec: gestion-espacios / Consulta de espacios / Estudiante lista espacios."""
    inactivo = servicio.crear_espacio(administrador, "Auditorio Mayor", "auditorio", 300)
    servicio.desactivar_espacio(administrador, inactivo.pk)
    entrar(client, estudiante)
    contenido = pagina(client.get(reverse("espacios")))
    assert "Lab 301" in contenido
    assert "Auditorio Mayor" not in contenido


def test_el_administrador_ve_activos_e_inactivos_con_su_estado(client, administrador, espacio):
    """Spec: gestion-espacios / Consulta de espacios / Administrador lista espacios."""
    inactivo = servicio.crear_espacio(administrador, "Auditorio Mayor", "auditorio", 300)
    servicio.desactivar_espacio(administrador, inactivo.pk)
    entrar(client, administrador)
    contenido = pagina(client.get(reverse("espacios")))
    assert "Lab 301" in contenido and "Auditorio Mayor" in contenido
    assert "Inactivo" in contenido and "Activo" in contenido


def test_espacio_inexistente_responde_no_encontrado(client, estudiante):
    """Spec: gestion-espacios / Consulta de espacios / Espacio inexistente."""
    entrar(client, estudiante)
    respuesta = client.get(reverse("espacio_detalle", args=[9999]))
    assert respuesta.status_code == 404
    assert errores.ESPACIO_NO_ENCONTRADO in pagina(respuesta)


def test_el_estudiante_consulta_un_espacio_inactivo(client, estudiante, administrador, espacio):
    """Spec: gestion-espacios / Consulta de espacios / Estudiante consulta un espacio inactivo."""
    servicio.desactivar_espacio(administrador, espacio.pk)
    entrar(client, estudiante)
    respuesta = client.get(reverse("espacio_detalle", args=[espacio.pk]))
    assert respuesta.status_code == 409
    assert errores.ESPACIO_INACTIVO in pagina(respuesta)


def test_las_acciones_de_administracion_solo_se_ofrecen_al_administrador(
    client, estudiante, administrador, espacio
):
    ruta = reverse("espacio_detalle", args=[espacio.pk])
    assert "Editar" not in pagina(entrar(client, estudiante).get(ruta))
    client.logout()
    contenido = pagina(entrar(client, administrador).get(ruta))
    assert "Editar" in contenido and "Desactivar" in contenido


# --- Editar --------------------------------------------------------------


def test_el_administrador_edita_la_capacidad(client, administrador, espacio):
    """Spec: gestion-espacios / Solo el administrador gestiona espacios / Administrador edita un espacio."""
    entrar(client, administrador)
    ruta = reverse("espacio_editar", args=[espacio.pk])
    assert client.get(ruta).status_code == 200
    respuesta = client.post(ruta, datos_de_formulario(capacidad="45"))
    assert respuesta.status_code == 302
    espacio.refresh_from_db()
    assert espacio.capacidad == 45


def test_un_docente_no_puede_editar_un_espacio(client, docente, espacio):
    """Spec: gestion-espacios / Solo el administrador gestiona espacios / Docente intenta editar un espacio."""
    entrar(client, docente)
    respuesta = client.post(
        reverse("espacio_editar", args=[espacio.pk]), datos_de_formulario(capacidad="99")
    )
    assert respuesta.status_code == 403
    assert errores.SIN_PERMISO in pagina(respuesta)
    espacio.refresh_from_db()
    assert espacio.capacidad == 30


def test_editar_con_un_dato_invalido_no_cambia_el_espacio(client, administrador, espacio):
    entrar(client, administrador)
    respuesta = client.post(
        reverse("espacio_editar", args=[espacio.pk]), datos_de_formulario(capacidad="-4")
    )
    assert respuesta.status_code == 422
    espacio.refresh_from_db()
    assert espacio.capacidad == 30


# --- Activar y desactivar ------------------------------------------------


def test_el_administrador_desactiva_y_reactiva(client, administrador, espacio):
    """Spec: gestion-espacios / Activación y desactivación / Desactivar un espacio y Reactivar un espacio."""
    entrar(client, administrador)
    client.post(reverse("espacio_desactivar", args=[espacio.pk]))
    espacio.refresh_from_db()
    assert espacio.activo is False

    client.post(reverse("espacio_activar", args=[espacio.pk]))
    espacio.refresh_from_db()
    assert espacio.activo is True


def test_un_estudiante_no_puede_desactivar_un_espacio(client, estudiante, espacio):
    entrar(client, estudiante)
    respuesta = client.post(reverse("espacio_desactivar", args=[espacio.pk]))
    assert respuesta.status_code == 403
    espacio.refresh_from_db()
    assert espacio.activo is True


def test_activar_y_desactivar_solo_aceptan_post(client, administrador, espacio):
    entrar(client, administrador)
    assert client.get(reverse("espacio_desactivar", args=[espacio.pk])).status_code == 405
    assert client.get(reverse("espacio_activar", args=[espacio.pk])).status_code == 405
