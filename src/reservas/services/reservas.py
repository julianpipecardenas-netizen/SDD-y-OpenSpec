"""Creación de reservas (spec creacion-reservas).

Orquesta el caso de uso: exige sesión, arma el contexto, ejecuta las reglas
(`validadores.VALIDADORES_RESERVA`, en el orden de la spec) y, solo si todas
se cumplen, guarda la reserva. Una reserva rechazada no deja ningún registro.
"""

import dataclasses

from django.db import transaction
from django.utils import timezone

from reservas.errores import ErrorDominio
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


def intervalos_ocupados(espacio, fecha):
    """Pares `(hora_inicio, hora_fin)` de las reservas que pueden causar conflicto.

    Ámbito de la regla (spec validacion-conflictos-horario / Ámbito del
    conflicto): solo reservas `activa` del mismo espacio y la misma fecha. Las
    canceladas, las de otros espacios y las de otras fechas no cuentan. El
    usuario que reservó no importa: también hay conflicto con las propias.
    """
    consulta = Reserva.objects.filter(
        espacio=espacio, fecha=fecha, estado=EstadoReserva.ACTIVA
    ).order_by("hora_inicio")
    return tuple(consulta.values_list("hora_inicio", "hora_fin"))


def _con_reservas_existentes(contexto):
    """Completa el contexto con las reservas que pueden causar conflicto.

    Si el espacio no existe o la fecha no se puede interpretar, no hay nada que
    consultar: las reglas anteriores en la lista ya rechazan esa solicitud
    antes de que se evalúe el conflicto.
    """
    if contexto.espacio is None:
        return contexto
    try:
        fecha, _, _ = interpretar_horario(contexto)
    except ErrorDominio:
        return contexto
    return dataclasses.replace(
        contexto, reservas_existentes=intervalos_ocupados(contexto.espacio, fecha)
    )


def crear_reserva(actor, espacio_id, fecha, hora_inicio, hora_fin, *, ahora=None):
    """Crea una reserva `activa` a nombre de `actor` (cualquier usuario autenticado).

    `ahora` es el reloj inyectable (design D9): por defecto, la hora real en la
    zona horaria del proyecto. Lanza el `ErrorDominio` de la primera regla que
    falle; en ese caso no se guarda nada.

    La lectura de las reservas existentes, la evaluación de las reglas y la
    inserción ocurren dentro de una misma transacción que toma el bloqueo de
    escritura al empezar (design D7; ver `DATABASES` en la configuración). Así,
    de dos solicitudes simultáneas que se solapan, solo una se acepta y la otra
    recibe `CONFLICTO_HORARIO`.
    """
    exigir_rol(actor, *ROLES_TODOS)
    ahora = ahora if ahora is not None else timezone.localtime()

    with transaction.atomic():
        contexto = ContextoReserva(
            espacio_id=espacio_id,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            espacio=_buscar_espacio(espacio_id),
            ahora=ahora,
        )
        contexto = _con_reservas_existentes(contexto)
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
