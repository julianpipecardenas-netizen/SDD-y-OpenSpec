"""Creación de reservas (spec creacion-reservas).

Orquesta el caso de uso: exige sesión, arma el contexto, ejecuta las reglas
(`validadores.VALIDADORES_RESERVA`, en el orden de la spec) y, solo si todas
se cumplen, guarda la reserva. Una reserva rechazada no deja ningún registro.
"""

from django.utils import timezone

from reservas.models import Espacio, EstadoReserva, Reserva
from reservas.services.acceso import ROLES_TODOS, exigir_rol
from reservas.services.validadores import (
    VALIDADORES_RESERVA,
    ContextoReserva,
    ejecutar_validadores,
    interpretar_horario,
)


def _buscar_espacio(espacio_id):
    """El espacio solicitado o `None`. Resolverlo no es una regla: la regla es validar_espacio_activo."""
    try:
        return Espacio.objects.filter(pk=int(espacio_id)).first()
    except (TypeError, ValueError):
        return None


def crear_reserva(actor, espacio_id, fecha, hora_inicio, hora_fin, *, ahora=None):
    """Crea una reserva `activa` a nombre de `actor` (cualquier usuario autenticado).

    `ahora` es el reloj inyectable (design D9): por defecto, la hora real en la
    zona horaria del proyecto. Lanza el `ErrorDominio` de la primera regla que
    falle; en ese caso no se guarda nada.
    """
    exigir_rol(actor, *ROLES_TODOS)
    ahora = ahora if ahora is not None else timezone.localtime()

    contexto = ContextoReserva(
        espacio_id=espacio_id,
        fecha=fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        espacio=_buscar_espacio(espacio_id),
        ahora=ahora,
    )
    ejecutar_validadores(contexto, VALIDADORES_RESERVA)

    fecha, inicio, fin = interpretar_horario(contexto)
    return Reserva.objects.create(
        usuario=actor,
        espacio=contexto.espacio,
        fecha=fecha,
        hora_inicio=inicio,
        hora_fin=fin,
        estado=EstadoReserva.ACTIVA,
        creada_en=ahora,
    )
