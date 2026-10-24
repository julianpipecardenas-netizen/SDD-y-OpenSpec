from datetime import date, time
import pytest
from reservas.errores import ErrorDominio
from reservas.models import EstadoReserva, Rol
from reservas.services.disponibilidad import calcular_intervalos, consultar_disponibilidad


def test_calculo_con_reservas_y_huecos():
    """Spec: consulta-disponibilidad / Consulta de disponibilidad por espacio y fecha / Día con reservas"""
    ocupados, libres = calcular_intervalos([(time(8), time(10)), (time(14), time(16))])
    assert ocupados == ((time(8), time(10)), (time(14), time(16)))
    assert libres == ((time(0), time(8)), (time(10), time(14)), (time(16), time(23, 59)))


def test_dia_vacio_y_reservas_contiguas():
    """Spec: consulta-disponibilidad / Consulta de disponibilidad por espacio y fecha / Día sin reservas y Reservas contiguas"""
    assert calcular_intervalos([])[1] == ((time(0), time(23, 59)),)
    assert calcular_intervalos([(time(8), time(10)), (time(10), time(12))])[1] == ((time(0), time(8)), (time(12), time(23, 59)))


def test_consulta_privada_y_admin(fabrica_reservas, estudiante, administrador, espacio):
    """Spec: consulta-disponibilidad / Privacidad de las reservas ajenas / Estudiante consulta disponibilidad y Administrador consulta disponibilidad"""
    fabrica_reservas(inicio=time(10), fin=time(12))
    privado = consultar_disponibilidad(estudiante, espacio.pk, '2030-03-15')
    assert 'reserva_id' not in privado['ocupados'][0] and 'usuario' not in privado['ocupados'][0]
    admin = consultar_disponibilidad(administrador, espacio.pk, '2030-03-15')
    assert admin['ocupados'][0]['reserva_id']


def test_fecha_invalida_y_cancelada(fabrica_reservas, estudiante, espacio):
    """Spec: consulta-disponibilidad / Validación de la consulta / Fecha inválida y Reserva cancelada"""
    with pytest.raises(ErrorDominio) as exc:
        consultar_disponibilidad(estudiante, espacio.pk, '2030-13-01')
    assert exc.value.codigo == 'DATOS_INVALIDOS'
    fabrica_reservas(inicio=time(10), fin=time(12), estado=EstadoReserva.CANCELADA)
    result = consultar_disponibilidad(estudiante, espacio.pk, '2030-03-15')
    assert not result['ocupados'] and result['libres'] == ({'inicio': time(0), 'fin': time(23, 59)},)


def test_consistencia_disponibilidad_con_creacion(fabrica_reservas, estudiante, espacio):
    """Spec: consulta-disponibilidad / Disponibilidad consistente con la creación / Reservar un intervalo libre informado y Reservar sobre un intervalo ocupado informado"""
    from datetime import datetime
    from django.utils import timezone
    from reservas.errores import ErrorDominio
    from reservas.services.reservas import crear_reserva
    fabrica_reservas(fecha=date(2035, 3, 15), inicio=time(10), fin=time(12))
    libre = consultar_disponibilidad(estudiante, espacio.pk, '2035-03-15')
    ahora = timezone.make_aware(datetime(2035, 3, 14, 8, 0))
    creada = crear_reserva(estudiante, espacio.pk, '2035-03-15', '12:00', '13:00', ahora=ahora)
    assert creada.hora_inicio == time(12)
    with pytest.raises(ErrorDominio) as exc:
        crear_reserva(estudiante, espacio.pk, '2035-03-15', '11:00', '12:30', ahora=ahora)
    assert exc.value.codigo == 'CONFLICTO_HORARIO'
