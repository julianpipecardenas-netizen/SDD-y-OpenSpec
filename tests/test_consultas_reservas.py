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
    """Spec: consulta-cancelacion-reservas / Cancelación de una reserva / Usuario cancela su reserva"""
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


def test_usuario_con_reservas_ve_activas_y_canceladas(fabrica_reservas, estudiante):
    """Spec: consulta-cancelacion-reservas / Listado de reservas propias / Usuario con reservas."""
    activa = fabrica_reservas(fecha=date(2030, 3, 15), inicio=time(10), fin=time(11))
    cancelada = fabrica_reservas(fecha=date(2030, 3, 16), inicio=time(10), fin=time(11), estado=EstadoReserva.CANCELADA)
    resultado = list(listar_reservas(estudiante))
    assert resultado == [activa, cancelada]
    assert {r.estado for r in resultado} == {EstadoReserva.ACTIVA, EstadoReserva.CANCELADA}


def test_usuario_sin_reservas_recibe_lista_vacia(estudiante):
    """Spec: consulta-cancelacion-reservas / Listado de reservas propias / Usuario sin reservas."""
    assert list(listar_reservas(estudiante)) == []


def test_administrador_consulta_reserva_ajena(fabrica_reservas, administrador, docente):
    """Spec: consulta-cancelacion-reservas / Consulta total para el administrador / Administrador consulta una reserva ajena."""
    reserva = fabrica_reservas(usuario=docente)
    assert consultar_reserva(administrador, reserva.pk) == reserva


def test_administrador_cancela_reserva_ajena(fabrica_reservas, administrador, estudiante):
    """Spec: consulta-cancelacion-reservas / Cancelación de una reserva / Administrador cancela una reserva ajena."""
    reserva = fabrica_reservas(usuario=estudiante, fecha=date(2035, 3, 15))
    ahora = timezone.make_aware(datetime(2035, 3, 14, 9, 0))
    resultado = cancelar_reserva(administrador, reserva.pk, ahora=ahora)
    assert resultado.estado == EstadoReserva.CANCELADA
    assert resultado.cancelada_por == administrador


def test_usuario_no_administrador_no_cancela_reserva_ajena(fabrica_reservas, estudiante, docente):
    """Spec: consulta-cancelacion-reservas / Cancelación de una reserva / Cancelar una reserva ajena sin ser administrador."""
    reserva = fabrica_reservas(usuario=docente, fecha=date(2035, 3, 15))
    ahora = timezone.make_aware(datetime(2035, 3, 14, 9, 0))
    with pytest.raises(ErrorDominio) as exc:
        cancelar_reserva(estudiante, reserva.pk, ahora=ahora)
    assert exc.value.codigo == "SIN_PERMISO"
    reserva.refresh_from_db()
    assert reserva.estado == EstadoReserva.ACTIVA


def test_no_se_puede_cancelar_reserva_que_ya_comenzo(fabrica_reservas, estudiante):
    """Spec: consulta-cancelacion-reservas / Cancelación de una reserva / Reserva que ya comenzó."""
    reserva = fabrica_reservas(fecha=date(2030, 3, 15), inicio=time(10), fin=time(12))
    ahora = timezone.make_aware(datetime(2030, 3, 15, 10, 1))
    with pytest.raises(ErrorDominio) as exc:
        cancelar_reserva(estudiante, reserva.pk, ahora=ahora)
    assert exc.value.codigo == "RESERVA_NO_CANCELABLE"
    reserva.refresh_from_db()
    assert reserva.estado == EstadoReserva.ACTIVA


def test_horario_cancelado_se_puede_reservar_de_nuevo(fabrica_reservas, estudiante, docente, espacio):
    """Spec: consulta-cancelacion-reservas / La cancelación libera el horario / Reutilizar un horario cancelado."""
    from reservas.services.reservas import crear_reserva
    reserva = fabrica_reservas(usuario=estudiante, fecha=date(2035, 3, 15), inicio=time(10), fin=time(12))
    ahora = timezone.make_aware(datetime(2035, 3, 14, 9, 0))
    cancelar_reserva(estudiante, reserva.pk, ahora=ahora)
    nueva = crear_reserva(docente, espacio.pk, "2035-03-15", "10:00", "12:00", ahora=ahora)
    assert nueva.pk is not None
    assert nueva.estado == EstadoReserva.ACTIVA


def test_usuario_consulta_detalle_de_reserva_propia(fabrica_reservas, estudiante):
    """Spec: consulta-cancelacion-reservas / Consulta de una reserva / Reserva propia."""
    reserva = fabrica_reservas(usuario=estudiante)
    assert consultar_reserva(estudiante, reserva.pk) == reserva


def test_usuario_no_puede_cancelar_reserva_ya_cancelada(fabrica_reservas, estudiante):
    """Spec: consulta-cancelacion-reservas / Cancelación de una reserva / Reserva ya cancelada."""
    reserva = fabrica_reservas(usuario=estudiante, estado=EstadoReserva.CANCELADA)
    with pytest.raises(ErrorDominio) as exc:
        cancelar_reserva(estudiante, reserva.pk, ahora=timezone.make_aware(datetime(2030, 3, 1, 8, 0)))
    assert exc.value.codigo == "RESERVA_YA_CANCELADA"
