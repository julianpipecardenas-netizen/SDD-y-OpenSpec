"""Pruebas del conflicto de horario dentro del servicio de reservas (tarea 5.3).

Specs: validacion-conflictos-horario y creacion-reservas / Orden de
validación y atomicidad. Reloj fijo inyectado (design D9).
"""

from datetime import datetime, time
from zoneinfo import ZoneInfo

import pytest

from reservas import errores
from reservas.errores import ErrorDominio
from reservas.models import Reserva
from reservas.services import reservas as servicio
from reservas.services.validadores import VALIDADORES_RESERVA, validar_no_solapamiento

BOGOTA = ZoneInfo("America/Bogota")
AHORA = datetime(2030, 3, 1, 8, 0, tzinfo=BOGOTA)


def reservar(actor, espacio_id, fecha="2030-03-15", inicio="10:00", fin="12:00", ahora=AHORA):
    return servicio.crear_reserva(actor, espacio_id, fecha, inicio, fin, ahora=ahora)


def codigo_de(*args, **kwargs):
    with pytest.raises(ErrorDominio) as info:
        reservar(*args, **kwargs)
    return info.value.codigo


def test_el_conflicto_es_la_ultima_regla_de_la_lista():
    """Spec: creacion-reservas / Orden de validación y atomicidad / Se informa el primer error en orden."""
    assert VALIDADORES_RESERVA[-1] is validar_no_solapamiento


@pytest.mark.parametrize(
    "inicio, fin",
    [("11:00", "13:00"), ("09:00", "11:00"), ("11:00", "11:30"), ("09:00", "13:00"), ("10:00", "12:00")],
)
def test_el_servicio_rechaza_el_solapamiento(estudiante, docente, espacio, fabrica_reservas, inicio, fin):
    """Spec: validacion-conflictos-horario / No solapamiento de reservas activas / Horario idéntico."""
    fabrica_reservas(usuario=estudiante)
    assert codigo_de(docente, espacio.pk, inicio=inicio, fin=fin) == errores.CONFLICTO_HORARIO
    assert Reserva.objects.count() == 1


def test_el_servicio_rechaza_el_conflicto_con_una_reserva_propia(estudiante, espacio):
    """Spec: validacion-conflictos-horario / No solapamiento de reservas activas / Conflicto con una reserva del mismo usuario."""
    reservar(estudiante, espacio.pk)
    assert codigo_de(estudiante, espacio.pk, inicio="11:00", fin="13:00") == errores.CONFLICTO_HORARIO


def test_el_mensaje_del_conflicto_es_el_de_la_spec(estudiante, espacio, fabrica_reservas):
    """Spec: validacion-conflictos-horario / No solapamiento de reservas activas / Horario idéntico."""
    fabrica_reservas()
    with pytest.raises(ErrorDominio) as info:
        reservar(estudiante, espacio.pk)
    assert info.value.mensaje == "El espacio ya está reservado en ese horario"


def test_reservas_contiguas_se_aceptan(estudiante, espacio, fabrica_reservas):
    """Spec: validacion-conflictos-horario / Reservas contiguas permitidas / Inicio igual al fin de otra reserva."""
    fabrica_reservas()
    assert reservar(estudiante, espacio.pk, inicio="12:00", fin="14:00").pk is not None


def test_reserva_contigua_por_el_inicio(estudiante, espacio, fabrica_reservas):
    """Spec: validacion-conflictos-horario / Reservas contiguas permitidas / Fin igual al inicio de otra reserva."""
    fabrica_reservas()
    assert reservar(estudiante, espacio.pk, inicio="08:00", fin="10:00").pk is not None


def test_una_reserva_cancelada_no_bloquea_en_el_servicio(estudiante, espacio, fabrica_reservas):
    """Spec: validacion-conflictos-horario / Ámbito del conflicto / Reserva cancelada no bloquea."""
    from reservas.models import EstadoReserva

    fabrica_reservas(estado=EstadoReserva.CANCELADA)
    assert reservar(estudiante, espacio.pk).pk is not None


def test_horario_invalido_se_informa_antes_que_el_conflicto(estudiante, espacio, fabrica_reservas):
    """Spec: creacion-reservas / Orden de validación y atomicidad / Se informa el primer error en orden."""
    fabrica_reservas(inicio=time(10, 0), fin=time(12, 0))
    # Fin anterior al inicio, y además dentro del horario ocupado.
    assert codigo_de(estudiante, espacio.pk, inicio="11:30", fin="10:30") == errores.HORARIO_INVALIDO


def test_espacio_inactivo_se_informa_antes_que_el_conflicto(estudiante, espacio, fabrica_reservas):
    """Spec: creacion-reservas / Orden de validación y atomicidad / Se informa el primer error en orden."""
    fabrica_reservas()
    espacio.activo = False
    espacio.save()
    assert codigo_de(estudiante, espacio.pk) == errores.ESPACIO_INACTIVO


def test_reserva_en_el_pasado_se_informa_antes_que_el_conflicto(estudiante, espacio, fabrica_reservas):
    """Spec: creacion-reservas / Orden de validación y atomicidad / Se informa el primer error en orden."""
    fabrica_reservas()
    durante = datetime(2030, 3, 15, 11, 0, tzinfo=BOGOTA)
    codigo = codigo_de(estudiante, espacio.pk, inicio="10:30", fin="11:30", ahora=durante)
    assert codigo == errores.RESERVA_EN_PASADO


def test_un_conflicto_no_deja_registros(estudiante, espacio, fabrica_reservas):
    """Spec: creacion-reservas / Orden de validación y atomicidad / Rechazo sin efectos."""
    fabrica_reservas()
    assert codigo_de(estudiante, espacio.pk, inicio="11:00", fin="13:00") == errores.CONFLICTO_HORARIO
    assert Reserva.objects.count() == 1
