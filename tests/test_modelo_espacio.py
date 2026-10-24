"""Pruebas del modelo Espacio (tarea 3.1).

Spec: gestion-espacios / Datos de un espacio. Aquí se comprueba que la base de
datos aplica por sí sola las restricciones (PLAN 7.3), sin pasar por el servicio.
"""

import pytest
from django.db import IntegrityError, transaction

from reservas.models import Espacio, TipoEspacio


def crear(**datos):
    base = {"nombre": "Aula 101", "tipo": TipoEspacio.AULA, "capacidad": 40}
    base.update(datos)
    return Espacio.objects.create(**base)


def test_un_espacio_nuevo_queda_activo_por_defecto(db):
    """Spec: gestion-espacios / Datos de un espacio / Espacio creado con datos válidos (modelo)."""
    espacio = crear()
    espacio.refresh_from_db()
    assert espacio.activo is True
    assert espacio.pk is not None


def test_los_tipos_permitidos_son_los_de_la_spec():
    assert set(TipoEspacio.values) == {"aula", "laboratorio", "sala_estudio", "auditorio"}


def test_la_base_de_datos_rechaza_nombres_duplicados_sin_distinguir_mayusculas(db):
    crear(nombre="Lab 301")
    with pytest.raises(IntegrityError), transaction.atomic():
        crear(nombre="LAB 301")


@pytest.mark.parametrize("capacidad", [0, -1, -50])
def test_la_base_de_datos_rechaza_capacidad_no_positiva(db, capacidad):
    """Spec: gestion-espacios / Datos de un espacio / Capacidad inválida (modelo)."""
    with pytest.raises(IntegrityError), transaction.atomic():
        crear(capacidad=capacidad)


def test_la_base_de_datos_rechaza_un_tipo_no_permitido(db):
    """Spec: gestion-espacios / Datos de un espacio / Tipo no permitido (modelo)."""
    with pytest.raises(IntegrityError), transaction.atomic():
        crear(tipo="cafeteria")


def test_nombres_distintos_conviven(db):
    crear(nombre="Aula 101")
    crear(nombre="Aula 102")
    assert Espacio.objects.count() == 2
