from datetime import date, time
import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_vista_disponibilidad_no_expone_usuario(client, estudiante, fabrica_reservas, espacio):
    """Spec: consulta-disponibilidad / Privacidad de las reservas ajenas / Estudiante consulta disponibilidad"""
    client.force_login(estudiante)
    fabrica_reservas(inicio=time(10), fin=time(12))
    response = client.get(reverse('disponibilidad'), {'espacio': espacio.pk, 'fecha': '2030-03-15'})
    assert response.status_code == 200
    assert b'10:00' in response.content and b'estudiante@uni.edu' not in response.content

@pytest.mark.django_db
def test_flujo_lista_detalle_cancelacion(client, estudiante, fabrica_reservas):
    """Spec: consulta-cancelacion-reservas / Cancelación de una reserva / Usuario cancela su reserva"""
    client.force_login(estudiante)
    r = fabrica_reservas(fecha=date(2035, 3, 15), inicio=time(10), fin=time(12))
    assert client.get(reverse('reservas_lista')).status_code == 200
    assert client.get(reverse('reserva_detalle', args=[r.pk])).status_code == 200
    response = client.post(reverse('reserva_cancelar', args=[r.pk]))
    assert response.status_code == 302
