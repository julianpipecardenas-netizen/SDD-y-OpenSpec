"""Prueba de concurrencia de la creación de reservas (tarea 5.4).

Spec: validacion-conflictos-horario / Solicitudes simultáneas. Varios hilos
piden a la vez el mismo espacio, fecha y horario; cada hilo usa su propia
conexión a una base de datos SQLite en archivo (ver `DATABASES["default"]["TEST"]`
en la configuración). Exactamente una solicitud debe aceptarse y las demás
recibir `CONFLICTO_HORARIO` (design D7).
"""

import threading
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from django.db import connection, connections

from reservas import errores
from reservas.errores import ErrorDominio
from reservas.models import EstadoReserva, Reserva, Rol, Usuario
from reservas.services import reservas as servicio

AHORA = datetime(2030, 3, 1, 8, 0, tzinfo=ZoneInfo("America/Bogota"))


def test_la_transaccion_inmediata_esta_configurada():
    """Spec: validacion-conflictos-horario / Solicitudes simultáneas / Dos usuarios piden el mismo horario a la vez (configuración)."""
    assert connection.settings_dict["OPTIONS"]["transaction_mode"] == "IMMEDIATE"


def _solicitar(actor, espacio_id, barrera, resultados):
    try:
        barrera.wait(timeout=15)  # todos los hilos arrancan juntos
        reserva = servicio.crear_reserva(
            actor, espacio_id, "2030-03-15", "10:00", "12:00", ahora=AHORA
        )
        resultados.append(("aceptada", reserva.pk))
    except ErrorDominio as error:
        resultados.append(("rechazada", error.codigo))
    except Exception as error:  # cualquier otra cosa es un fallo de la prueba
        resultados.append(("excepcion", repr(error)))
    finally:
        connections.close_all()  # cada hilo cierra su propia conexión


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("solicitudes", [2, 5])
def test_solo_una_de_varias_solicitudes_simultaneas_queda_activa(espacio, solicitudes):
    """Spec: validacion-conflictos-horario / Solicitudes simultáneas / Dos usuarios piden el mismo horario a la vez."""
    usuarios = [
        Usuario.objects.create_user(
            f"usuario{n}@uni.edu", f"Usuario {n}", "clave-de-prueba-123", rol=Rol.ESTUDIANTE
        )
        for n in range(solicitudes)
    ]
    barrera = threading.Barrier(solicitudes)
    resultados = []
    hilos = [
        threading.Thread(target=_solicitar, args=(usuario, espacio.pk, barrera, resultados))
        for usuario in usuarios
    ]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join(timeout=60)

    assert len(resultados) == solicitudes, resultados
    aceptadas = [r for r in resultados if r[0] == "aceptada"]
    rechazadas = [r for r in resultados if r[0] == "rechazada"]
    assert len(aceptadas) == 1, resultados
    assert [codigo for _, codigo in rechazadas] == [errores.CONFLICTO_HORARIO] * (solicitudes - 1)
    assert Reserva.objects.filter(estado=EstadoReserva.ACTIVA).count() == 1
