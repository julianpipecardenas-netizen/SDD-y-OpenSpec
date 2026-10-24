"""Pruebas del modelo Reserva (tarea 4.1).

Spec: creacion-reservas / Rango horario válido. La base de datos aplica por sí
sola la restricción `hora_fin > hora_inicio` (PLAN 7.3, design D3).
"""

from datetime import time

import pytest
from django.db import IntegrityError, transaction

from reservas.models import EstadoReserva, Reserva


def test_la_base_de_datos_rechaza_un_rango_invertido(fabrica_reservas):
    """Spec: creacion-reservas / Rango horario válido / Fin anterior al inicio (modelo)."""
    with pytest.raises(IntegrityError), transaction.atomic():
        fabrica_reservas(inicio=time(12, 0), fin=time(10, 0))
    assert Reserva.objects.count() == 0


def test_la_base_de_datos_rechaza_fin_igual_al_inicio(fabrica_reservas):
    """Spec: creacion-reservas / Rango horario válido / Fin igual al inicio (modelo)."""
    with pytest.raises(IntegrityError), transaction.atomic():
        fabrica_reservas(inicio=time(10, 0), fin=time(10, 0))
    assert Reserva.objects.count() == 0


def test_la_base_de_datos_acepta_una_reserva_de_un_minuto(fabrica_reservas):
    """Spec: creacion-reservas / Rango horario válido / Reserva mínima de un minuto (modelo)."""
    reserva = fabrica_reservas(inicio=time(10, 0), fin=time(10, 1))
    assert reserva.pk is not None


def test_una_reserva_nueva_queda_activa_con_fecha_de_creacion(fabrica_reservas):
    """Spec: creacion-reservas / Creación de una reserva / Reserva válida (modelo)."""
    reserva = fabrica_reservas()
    reserva.refresh_from_db()
    assert reserva.estado == EstadoReserva.ACTIVA
    assert reserva.creada_en is not None


def test_el_estado_solo_admite_los_valores_de_la_spec():
    assert set(EstadoReserva.values) == {"activa", "cancelada"}


def test_la_base_de_datos_rechaza_un_estado_desconocido(fabrica_reservas):
    with pytest.raises(IntegrityError), transaction.atomic():
        fabrica_reservas(estado="pendiente")
