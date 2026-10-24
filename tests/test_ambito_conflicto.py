"""Pruebas de base de datos del ámbito de la regla de conflicto (tarea 5.2).

Spec: validacion-conflictos-horario / Ámbito del conflicto. La consulta
`intervalos_ocupados` decide qué reservas cuentan; la regla (validador) solo
compara rangos. Se prueban juntas.
"""

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest

from reservas import errores
from reservas.errores import ErrorDominio
from reservas.models import Espacio, EstadoReserva, TipoEspacio
from reservas.services.reservas import intervalos_ocupados
from reservas.services.validadores import ContextoReserva, validar_no_solapamiento

FECHA = date(2030, 3, 15)


def conflicto(espacio, inicio, fin, fecha=FECHA):
    """Aplica la regla con las reservas que la consulta entrega para ese espacio y fecha."""
    contexto = ContextoReserva(
        espacio_id=espacio.pk,
        fecha=fecha,
        hora_inicio=inicio,
        hora_fin=fin,
        espacio=espacio,
        ahora=datetime(2030, 3, 1, 8, 0, tzinfo=ZoneInfo("America/Bogota")),
        reservas_existentes=intervalos_ocupados(espacio, fecha),
    )
    try:
        validar_no_solapamiento(contexto)
    except ErrorDominio as error:
        assert error.codigo == errores.CONFLICTO_HORARIO
        return True
    return False


def test_una_reserva_activa_bloquea(espacio, fabrica_reservas):
    fabrica_reservas()
    assert intervalos_ocupados(espacio, FECHA) == ((time(10, 0), time(12, 0)),)
    assert conflicto(espacio, "11:00", "13:00")


def test_una_reserva_cancelada_no_bloquea(espacio, fabrica_reservas):
    """Spec: validacion-conflictos-horario / Ámbito del conflicto / Reserva cancelada no bloquea."""
    fabrica_reservas(estado=EstadoReserva.CANCELADA)
    assert intervalos_ocupados(espacio, FECHA) == ()
    assert not conflicto(espacio, "10:00", "12:00")


def test_otro_espacio_mismo_horario(espacio, fabrica_reservas):
    """Spec: validacion-conflictos-horario / Ámbito del conflicto / Otro espacio, mismo horario."""
    fabrica_reservas()
    otro = Espacio.objects.create(nombre="Lab 302", tipo=TipoEspacio.LABORATORIO, capacidad=20)
    assert intervalos_ocupados(otro, FECHA) == ()
    assert not conflicto(otro, "10:00", "12:00")


def test_otra_fecha_mismo_horario(espacio, fabrica_reservas):
    """Spec: validacion-conflictos-horario / Ámbito del conflicto / Otra fecha, mismo horario."""
    fabrica_reservas()
    siguiente = date(2030, 3, 16)
    assert intervalos_ocupados(espacio, siguiente) == ()
    assert not conflicto(espacio, "10:00", "12:00", fecha=siguiente)


def test_conflicto_con_una_reserva_del_mismo_usuario(estudiante, espacio, fabrica_reservas):
    """Spec: validacion-conflictos-horario / No solapamiento de reservas activas / Conflicto con una reserva del mismo usuario."""
    fabrica_reservas(usuario=estudiante)
    assert conflicto(espacio, "11:00", "13:00")


def test_conflicto_con_una_reserva_de_otro_usuario(docente, espacio, fabrica_reservas):
    fabrica_reservas(usuario=docente)
    assert conflicto(espacio, "11:00", "13:00")


def test_solo_cuentan_las_activas_entre_varias(estudiante, espacio, fabrica_reservas):
    fabrica_reservas(inicio=time(8, 0), fin=time(9, 0))
    fabrica_reservas(inicio=time(10, 0), fin=time(12, 0), estado=EstadoReserva.CANCELADA)
    fabrica_reservas(inicio=time(14, 0), fin=time(15, 0))
    assert intervalos_ocupados(espacio, FECHA) == (
        (time(8, 0), time(9, 0)),
        (time(14, 0), time(15, 0)),
    )
    assert not conflicto(espacio, "10:00", "12:00")
    assert conflicto(espacio, "14:30", "16:00")


def test_un_usuario_puede_reservar_a_la_vez_en_espacios_distintos(estudiante, espacio, fabrica_reservas):
    """Spec: validacion-conflictos-horario / Ámbito del conflicto / Otro espacio, mismo horario."""
    fabrica_reservas(usuario=estudiante)
    otro = Espacio.objects.create(nombre="Aula 5", tipo=TipoEspacio.AULA, capacidad=30)
    assert not conflicto(otro, "10:00", "12:00")
