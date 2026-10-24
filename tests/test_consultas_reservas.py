from datetime import date, time, datetime
import pytest
from django.utils import timezone
from reservas.errores import ErrorDominio
from reservas.models import EstadoReserva
from reservas.services.consultas_reservas import listar_reservas, consultar_reserva, cancelar_reserva


def test_listado_aislado_y_admin(fabrica_reservas, estudiante, docente, administrador):
    """Spec: consulta-cancelacion-reservas / Listado de reservas propias / Aislamiento entre usuarios y Consulta total para el administrador / Administrador lista todo"""
    propia = fabrica_reservas()
    ajena = fabrica_reservas(usuario=docente, fecha=date(2030, 3, 16))
    assert list(listar_reservas(estudiante)) == [propia]
    assert set(listar_reservas(administrador)) == {propia, ajena}


def test_detalle_ajeno_y_no_existente(fabrica_reservas, estudiante, docente):
    """Spec: consulta-cancelacion-reservas / Consulta de una reserva / Reserva ajena y Reserva inexistente"""
    r = fabrica_reservas(usuario=docente)
    with pytest.raises(ErrorDominio) as exc: consultar_reserva(estudiante, r.pk)
    assert exc.value.codigo == 'SIN_PERMISO'
    with pytest.raises(ErrorDominio) as exc: consultar_reserva(estudiante, 999999)
    assert exc.value.codigo == 'RESERVA_NO_ENCONTRADA'


def test_cancelacion_logica_y_horario_liberado(fabrica_reservas, estudiante, espacio):
    """Spec: consulta-cancelacion-reservas / Cancelación de una reserva / Usuario cancela su reserva y La cancelación libera el horario"""
    r = fabrica_reservas(fecha=date(2035, 3, 15), inicio=time(10), fin=time(12))
    ahora = timezone.make_aware(datetime(2035, 3, 14, 9, 0))
    cancelada = cancelar_reserva(estudiante, r.pk, ahora=ahora)
    assert cancelada.estado == EstadoReserva.CANCELADA
    assert cancelada.cancelada_en == ahora and cancelada.cancelada_por == estudiante
    assert listar_reservas(estudiante).count() == 1


def test_permiso_precede_estado_cancelado(fabrica_reservas, estudiante, docente):
    """Spec: consulta-cancelacion-reservas / Orden de validación al cancelar / Reserva ajena y ya cancelada"""
    r = fabrica_reservas(usuario=docente, estado=EstadoReserva.CANCELADA)
    with pytest.raises(ErrorDominio) as exc: cancelar_reserva(estudiante, r.pk)
    assert exc.value.codigo == 'SIN_PERMISO'
