"""Pruebas de integración del conflicto de horario en la vista de reservas (tarea 5.5).

Spec: validacion-conflictos-horario. La vista muestra cualquier error de
dominio con su código y su mensaje; aquí se comprueba para el conflicto.
"""

from datetime import date, time, timedelta

from django.urls import reverse

from reservas import errores
from reservas.models import EstadoReserva, Reserva

MENSAJE_CONFLICTO = "El espacio ya está reservado en ese horario"


def futuro():
    return date.today() + timedelta(days=30)


def datos(espacio, inicio="11:00", fin="13:00"):
    return {
        "espacio": str(espacio.pk),
        "fecha": futuro().isoformat(),
        "hora_inicio": inicio,
        "hora_fin": fin,
    }


def test_el_conflicto_se_muestra_con_su_codigo_y_mensaje(client, estudiante, docente, espacio, fabrica_reservas):
    """Spec: validacion-conflictos-horario / No solapamiento de reservas activas / Solapamiento parcial por el final."""
    fabrica_reservas(usuario=docente, fecha=futuro(), inicio=time(10, 0), fin=time(12, 0))
    client.force_login(estudiante)
    respuesta = client.post(reverse("reserva_nueva"), datos(espacio))
    pagina = respuesta.content.decode()
    assert respuesta.status_code == 409
    assert errores.CONFLICTO_HORARIO in pagina
    assert MENSAJE_CONFLICTO in pagina
    assert Reserva.objects.count() == 1


def test_tras_el_conflicto_el_formulario_conserva_lo_escrito(client, estudiante, espacio, fabrica_reservas):
    fabrica_reservas(fecha=futuro(), inicio=time(10, 0), fin=time(12, 0))
    client.force_login(estudiante)
    pagina = client.post(reverse("reserva_nueva"), datos(espacio)).content.decode()
    assert 'value="11:00"' in pagina
    assert 'value="13:00"' in pagina


def test_una_reserva_contigua_se_crea_desde_la_vista(client, estudiante, espacio, fabrica_reservas):
    """Spec: validacion-conflictos-horario / Reservas contiguas permitidas / Inicio igual al fin de otra reserva."""
    fabrica_reservas(fecha=futuro(), inicio=time(10, 0), fin=time(12, 0))
    client.force_login(estudiante)
    respuesta = client.post(reverse("reserva_nueva"), datos(espacio, inicio="12:00", fin="14:00"))
    assert respuesta.status_code == 302
    assert Reserva.objects.count() == 2


def test_una_reserva_cancelada_no_bloquea_desde_la_vista(client, estudiante, espacio, fabrica_reservas):
    """Spec: validacion-conflictos-horario / Ámbito del conflicto / Reserva cancelada no bloquea."""
    fabrica_reservas(
        fecha=futuro(), inicio=time(10, 0), fin=time(12, 0), estado=EstadoReserva.CANCELADA
    )
    client.force_login(estudiante)
    respuesta = client.post(reverse("reserva_nueva"), datos(espacio, inicio="10:00", fin="12:00"))
    assert respuesta.status_code == 302
    assert Reserva.objects.filter(estado=EstadoReserva.ACTIVA).count() == 1
