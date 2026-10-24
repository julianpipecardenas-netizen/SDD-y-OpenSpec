"""Pruebas del servicio de creación de reservas (tarea 4.7).

Spec: creacion-reservas / Creación de una reserva y Orden de validación y
atomicidad. Reloj fijo inyectado (design D9).
"""

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import pytest
from django.contrib.auth.models import AnonymousUser

from reservas import errores
from reservas.errores import ErrorDominio
from reservas.models import Espacio, EstadoReserva, Reserva, TipoEspacio
from reservas.services import reservas as servicio

AHORA = datetime(2030, 3, 1, 8, 0, tzinfo=ZoneInfo("America/Bogota"))


def reservar(actor, espacio_id, fecha="2030-03-15", inicio="10:00", fin="12:00"):
    return servicio.crear_reserva(actor, espacio_id, fecha, inicio, fin, ahora=AHORA)


def codigo_de(*args, **kwargs):
    with pytest.raises(ErrorDominio) as info:
        reservar(*args, **kwargs)
    return info.value.codigo


def test_reserva_valida(estudiante, espacio):
    """Spec: creacion-reservas / Creación de una reserva / Reserva válida."""
    reserva = reservar(estudiante, espacio.pk)
    reserva.refresh_from_db()
    assert reserva.pk is not None
    assert reserva.estado == EstadoReserva.ACTIVA
    assert reserva.usuario == estudiante
    assert reserva.espacio == espacio
    assert (reserva.fecha, reserva.hora_inicio, reserva.hora_fin) == (
        date(2030, 3, 15),
        time(10, 0),
        time(12, 0),
    )
    assert reserva.creada_en == AHORA


def test_reserva_a_nombre_de_quien_la_crea(administrador, estudiante, espacio):
    """Spec: creacion-reservas / Creación de una reserva / Reserva a nombre de quien la crea."""
    reserva = reservar(administrador, espacio.pk)
    assert reserva.usuario == administrador
    assert reserva.usuario != estudiante


def test_el_docente_tambien_reserva(docente, espacio):
    """Spec: autenticacion-roles / Roles reconocidos / Estudiante y docente tienen los mismos permisos."""
    assert reservar(docente, espacio.pk).usuario == docente


def test_reserva_minima_de_un_minuto(estudiante, espacio):
    """Spec: creacion-reservas / Rango horario válido / Reserva mínima de un minuto."""
    reserva = reservar(estudiante, espacio.pk, inicio="10:00", fin="10:01")
    assert reserva.pk is not None


def test_sin_sesion_no_se_reserva(espacio):
    """Spec: autenticacion-roles / Operaciones protegidas exigen autenticación / Creación de reserva sin sesión."""
    assert codigo_de(AnonymousUser(), espacio.pk) == errores.NO_AUTENTICADO
    assert Reserva.objects.count() == 0


@pytest.mark.parametrize(
    "cambios, esperado",
    [
        ({"fin": ""}, errores.DATOS_INVALIDOS),
        ({"fecha": "2030-02-30"}, errores.DATOS_INVALIDOS),
        ({"inicio": "25:00"}, errores.DATOS_INVALIDOS),
        ({"inicio": "12:00", "fin": "10:00"}, errores.HORARIO_INVALIDO),
        ({"fecha": "2020-01-01"}, errores.RESERVA_EN_PASADO),
    ],
)
def test_rechazo_sin_efectos(estudiante, espacio, cambios, esperado):
    """Spec: creacion-reservas / Orden de validación y atomicidad / Rechazo sin efectos."""
    assert codigo_de(estudiante, espacio.pk, **cambios) == esperado
    assert Reserva.objects.count() == 0


def test_rechazo_por_espacio_inexistente_o_inactivo_sin_efectos(estudiante, espacio):
    """Spec: creacion-reservas / Orden de validación y atomicidad / Rechazo sin efectos."""
    assert codigo_de(estudiante, 9999) == errores.ESPACIO_NO_ENCONTRADO
    assert codigo_de(estudiante, "no-es-un-numero") == errores.ESPACIO_NO_ENCONTRADO
    espacio.activo = False
    espacio.save()
    assert codigo_de(estudiante, espacio.pk) == errores.ESPACIO_INACTIVO
    assert Reserva.objects.count() == 0


def test_se_informa_el_primer_error_en_orden(estudiante):
    """Spec: creacion-reservas / Orden de validación y atomicidad / Se informa el primer error en orden."""
    inactivo = Espacio.objects.create(
        nombre="Aula cerrada", tipo=TipoEspacio.AULA, capacidad=20, activo=False
    )
    assert codigo_de(estudiante, inactivo.pk, inicio="12:00", fin="10:00") == errores.HORARIO_INVALIDO


def test_datos_invalidos_se_informan_antes_que_el_espacio_inexistente(estudiante):
    """Spec: creacion-reservas / Orden de validación y atomicidad / Se informa el primer error en orden."""
    assert codigo_de(estudiante, 9999, fin="") == errores.DATOS_INVALIDOS


def test_reloj_real_por_defecto(estudiante, espacio):
    """Spec: creacion-reservas / No se reserva en el pasado / Inicio ya transcurrido (reloj real)."""
    with pytest.raises(ErrorDominio) as info:
        servicio.crear_reserva(estudiante, espacio.pk, "2000-01-01", "10:00", "12:00")
    assert info.value.codigo == errores.RESERVA_EN_PASADO


def test_servicio_rechaza_reserva_de_mas_de_cuatro_horas_sin_guardarla(estudiante, espacio):
    """Spec: limite-duracion-reserva / Duración máxima individual / Más de cuatro horas."""
    assert codigo_de(estudiante, espacio.pk, inicio="10:00", fin="14:01") == errores.DURACION_RESERVA_EXCEDIDA
    assert Reserva.objects.count() == 0


def test_servicio_acepta_reserva_de_exactamente_cuatro_horas(estudiante, espacio):
    """Spec: limite-duracion-reserva / Duración máxima individual / Cuatro horas exactas."""
    reserva = reservar(estudiante, espacio.pk, inicio="10:00", fin="14:00")
    assert reserva.pk is not None
    assert (reserva.hora_inicio, reserva.hora_fin) == (time(10, 0), time(14, 0))


def test_reserva_de_dia_anterior_no_acumula_duracion(estudiante, espacio):
    """Spec: limite-duracion-reserva / Duración máxima individual / Las horas de días anteriores no se acumulan."""
    anterior = reservar(estudiante, espacio.pk, fecha="2030-03-15", inicio="10:00", fin="14:00")
    nueva = reservar(estudiante, espacio.pk, fecha="2030-03-16", inicio="10:00", fin="14:00")
    assert anterior.pk != nueva.pk
    assert nueva.fecha.isoformat() == "2030-03-16"
