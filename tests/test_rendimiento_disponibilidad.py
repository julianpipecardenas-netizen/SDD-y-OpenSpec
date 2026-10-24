from datetime import date, time
from time import perf_counter
import pytest
from reservas.models import EstadoReserva, Reserva
from reservas.services.disponibilidad import consultar_disponibilidad

@pytest.mark.django_db(transaction=True)
def test_disponibilidad_con_mil_reservas_en_menos_de_dos_segundos(estudiante, espacio):
    """Spec: consulta-disponibilidad / Tiempo de respuesta / Espacio con muchas reservas"""
    Reserva.objects.bulk_create([
        Reserva(usuario=estudiante, espacio=espacio, fecha=date(2030, 1, 1 + (i % 28)),
                hora_inicio=time(i % 22, 0), hora_fin=time(i % 22 + 1, 0), estado=EstadoReserva.ACTIVA)
        for i in range(1000)
    ])
    start = perf_counter()
    consultar_disponibilidad(estudiante, espacio.pk, '2030-01-01')
    assert perf_counter() - start < 2.0
