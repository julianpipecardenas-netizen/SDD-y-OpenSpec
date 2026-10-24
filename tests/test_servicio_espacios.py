"""Pruebas del servicio de espacios: crear y editar (tarea 3.2).

Specs: gestion-espacios / Datos de un espacio y Solo el administrador gestiona
espacios; autenticacion-roles / Roles reconocidos.
"""

import pytest
from django.contrib.auth.models import AnonymousUser

from reservas.errores import (
    DATOS_INVALIDOS,
    ESPACIO_DUPLICADO,
    ESPACIO_INACTIVO,
    ESPACIO_NO_ENCONTRADO,
    NO_AUTENTICADO,
    SIN_PERMISO,
    ErrorDominio,
)
from reservas.models import Espacio
from reservas.services import espacios


def codigo_de(funcion, *args, **kwargs):
    """Ejecuta `funcion` y devuelve el código del error de dominio que lanza."""
    with pytest.raises(ErrorDominio) as info:
        funcion(*args, **kwargs)
    return info.value.codigo


def test_crear_espacio_con_datos_validos(administrador):
    """Spec: gestion-espacios / Datos de un espacio / Espacio creado con datos válidos."""
    espacio = espacios.crear_espacio(administrador, "Lab 301", "laboratorio", 30)
    assert espacio.pk is not None
    assert (espacio.nombre, espacio.tipo, espacio.capacidad) == ("Lab 301", "laboratorio", 30)
    assert espacio.activo is True
    assert Espacio.objects.count() == 1


def test_crear_espacio_recorta_espacios_del_nombre_y_acepta_capacidad_como_texto(administrador):
    espacio = espacios.crear_espacio(administrador, "  Aula 5  ", "aula", "25")
    assert (espacio.nombre, espacio.capacidad) == ("Aula 5", 25)


def test_nombre_duplicado_sin_distinguir_mayusculas(administrador, espacio):
    """Spec: gestion-espacios / Datos de un espacio / Nombre duplicado."""
    assert codigo_de(espacios.crear_espacio, administrador, "lab 301", "aula", 10) == ESPACIO_DUPLICADO
    assert Espacio.objects.count() == 1


@pytest.mark.parametrize("capacidad", [0, -1, "0", "-3", "abc", "", "3.5", 3.5, None, True])
def test_capacidad_invalida(administrador, capacidad):
    """Spec: gestion-espacios / Datos de un espacio / Capacidad inválida."""
    assert codigo_de(espacios.crear_espacio, administrador, "Aula X", "aula", capacidad) == DATOS_INVALIDOS
    assert Espacio.objects.count() == 0


@pytest.mark.parametrize("tipo", ["cafeteria", "", None, "AULA"])
def test_tipo_no_permitido(administrador, tipo):
    """Spec: gestion-espacios / Datos de un espacio / Tipo no permitido."""
    assert codigo_de(espacios.crear_espacio, administrador, "Sitio", tipo, 10) == DATOS_INVALIDOS
    assert Espacio.objects.count() == 0


@pytest.mark.parametrize("nombre", ["", "   ", None, 123, "x" * 101])
def test_nombre_invalido(administrador, nombre):
    assert codigo_de(espacios.crear_espacio, administrador, nombre, "aula", 10) == DATOS_INVALIDOS
    assert Espacio.objects.count() == 0


def test_estudiante_y_docente_no_pueden_crear_espacios(estudiante, docente):
    """Spec: autenticacion-roles / Roles reconocidos / Operación reservada al administrador."""
    for actor in (estudiante, docente):
        assert codigo_de(espacios.crear_espacio, actor, "Sala 1", "sala_estudio", 8) == SIN_PERMISO
    assert Espacio.objects.count() == 0


@pytest.mark.parametrize("actor", [None, AnonymousUser()], ids=["sin-actor", "anonimo"])
def test_crear_espacio_sin_sesion(actor, db):
    assert codigo_de(espacios.crear_espacio, actor, "Sala 1", "sala_estudio", 8) == NO_AUTENTICADO
    assert Espacio.objects.count() == 0


def test_docente_no_puede_editar_un_espacio(docente, espacio):
    """Spec: gestion-espacios / Solo el administrador gestiona espacios / Docente intenta editar un espacio."""
    assert codigo_de(espacios.editar_espacio, docente, espacio.pk, capacidad=99) == SIN_PERMISO
    espacio.refresh_from_db()
    assert espacio.capacidad == 30


def test_administrador_edita_la_capacidad(administrador, espacio):
    """Spec: gestion-espacios / Solo el administrador gestiona espacios / Administrador edita un espacio."""
    editado = espacios.editar_espacio(administrador, espacio.pk, capacidad=45)
    assert editado.capacidad == 45
    espacio.refresh_from_db()
    assert espacio.capacidad == 45
    assert (espacio.nombre, espacio.tipo) == ("Lab 301", "laboratorio")  # lo demás no cambia


def test_editar_con_capacidad_invalida_no_cambia_nada(administrador, espacio):
    assert codigo_de(espacios.editar_espacio, administrador, espacio.pk, capacidad=0) == DATOS_INVALIDOS
    espacio.refresh_from_db()
    assert espacio.capacidad == 30


def test_editar_el_nombre_a_uno_que_ya_existe(administrador, espacio):
    espacios.crear_espacio(administrador, "Aula 101", "aula", 40)
    assert codigo_de(espacios.editar_espacio, administrador, espacio.pk, nombre="AULA 101") == ESPACIO_DUPLICADO
    espacio.refresh_from_db()
    assert espacio.nombre == "Lab 301"


def test_editar_el_nombre_cambiando_solo_mayusculas_esta_permitido(administrador, espacio):
    editado = espacios.editar_espacio(administrador, espacio.pk, nombre="LAB 301")
    assert editado.nombre == "LAB 301"


@pytest.mark.parametrize("identificador", [9999, "abc", None])
def test_editar_un_espacio_inexistente(administrador, db, identificador):
    assert codigo_de(espacios.editar_espacio, administrador, identificador, capacidad=5) == ESPACIO_NO_ENCONTRADO


# --- Activación y desactivación (tarea 3.3) -------------------------------


def test_desactivar_un_espacio(administrador, espacio):
    """Spec: gestion-espacios / Activación y desactivación / Desactivar un espacio (estado)."""
    resultado = espacios.desactivar_espacio(administrador, espacio.pk)
    assert resultado.activo is False
    espacio.refresh_from_db()
    assert espacio.activo is False


def test_reactivar_un_espacio(administrador, espacio):
    """Spec: gestion-espacios / Activación y desactivación / Reactivar un espacio."""
    espacios.desactivar_espacio(administrador, espacio.pk)
    resultado = espacios.activar_espacio(administrador, espacio.pk)
    assert resultado.activo is True
    espacio.refresh_from_db()
    assert espacio.activo is True


def test_activar_y_desactivar_son_idempotentes(administrador, espacio):
    assert espacios.activar_espacio(administrador, espacio.pk).activo is True
    espacios.desactivar_espacio(administrador, espacio.pk)
    assert espacios.desactivar_espacio(administrador, espacio.pk).activo is False


def test_solo_el_administrador_activa_o_desactiva(estudiante, docente, espacio):
    for actor in (estudiante, docente):
        assert codigo_de(espacios.desactivar_espacio, actor, espacio.pk) == SIN_PERMISO
    espacio.refresh_from_db()
    assert espacio.activo is True


def test_activar_o_desactivar_sin_sesion(espacio):
    assert codigo_de(espacios.desactivar_espacio, None, espacio.pk) == NO_AUTENTICADO


def test_activar_o_desactivar_un_espacio_inexistente(administrador, db):
    assert codigo_de(espacios.desactivar_espacio, administrador, 9999) == ESPACIO_NO_ENCONTRADO
    assert codigo_de(espacios.activar_espacio, administrador, 9999) == ESPACIO_NO_ENCONTRADO


# --- Listado y consulta según el rol (tarea 3.4) ---------------------------


@pytest.fixture
def espacios_activo_e_inactivo(administrador):
    activo = espacios.crear_espacio(administrador, "Aula 101", "aula", 40)
    inactivo = espacios.crear_espacio(administrador, "Auditorio Mayor", "auditorio", 300)
    espacios.desactivar_espacio(administrador, inactivo.pk)
    return activo, inactivo


def test_estudiante_lista_solo_espacios_activos(estudiante, espacios_activo_e_inactivo):
    """Spec: gestion-espacios / Consulta de espacios / Estudiante lista espacios."""
    activo, _ = espacios_activo_e_inactivo
    assert espacios.listar_espacios(estudiante) == [activo]


def test_docente_lista_solo_espacios_activos(docente, espacios_activo_e_inactivo):
    activo, _ = espacios_activo_e_inactivo
    assert espacios.listar_espacios(docente) == [activo]


def test_administrador_lista_activos_e_inactivos(administrador, espacios_activo_e_inactivo):
    """Spec: gestion-espacios / Consulta de espacios / Administrador lista espacios."""
    activo, inactivo = espacios_activo_e_inactivo
    listado = espacios.listar_espacios(administrador)
    assert set(listado) == {activo, inactivo}
    assert {e.pk: e.activo for e in listado} == {activo.pk: True, inactivo.pk: False}
    nombres = [e.nombre for e in listado]
    assert nombres == sorted(nombres)  # ordenados por nombre


def test_el_listado_sin_espacios_es_vacio(estudiante):
    assert espacios.listar_espacios(estudiante) == []


def test_listar_sin_sesion(db):
    assert codigo_de(espacios.listar_espacios, None) == NO_AUTENTICADO


def test_consultar_un_espacio_activo(estudiante, espacios_activo_e_inactivo):
    activo, _ = espacios_activo_e_inactivo
    assert espacios.obtener_espacio(estudiante, activo.pk) == activo


def test_consultar_un_espacio_inexistente(estudiante, db):
    """Spec: gestion-espacios / Consulta de espacios / Espacio inexistente."""
    assert codigo_de(espacios.obtener_espacio, estudiante, 9999) == ESPACIO_NO_ENCONTRADO


def test_estudiante_y_docente_consultan_un_espacio_inactivo(estudiante, docente, espacios_activo_e_inactivo):
    """Spec: gestion-espacios / Consulta de espacios / Estudiante consulta un espacio inactivo."""
    _, inactivo = espacios_activo_e_inactivo
    for actor in (estudiante, docente):
        assert codigo_de(espacios.obtener_espacio, actor, inactivo.pk) == ESPACIO_INACTIVO


def test_el_administrador_consulta_un_espacio_inactivo(administrador, espacios_activo_e_inactivo):
    _, inactivo = espacios_activo_e_inactivo
    assert espacios.obtener_espacio(administrador, inactivo.pk) == inactivo


def test_consultar_sin_sesion(espacio):
    assert codigo_de(espacios.obtener_espacio, None, espacio.pk) == NO_AUTENTICADO
