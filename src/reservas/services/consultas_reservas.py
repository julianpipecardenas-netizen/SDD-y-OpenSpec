"""Listado, detalle y cancelación lógica (spec consulta-cancelacion-reservas)."""
from datetime import datetime
from django.utils import timezone
from reservas import errores
from reservas.errores import ErrorDominio
from reservas.models import EstadoReserva, Reserva, Rol
from reservas.services.acceso import ROLES_TODOS, exigir_rol


def listar_reservas(actor):
    exigir_rol(actor, *ROLES_TODOS)
    qs = Reserva.objects.select_related("espacio", "usuario").all()
    if actor.rol != Rol.ADMINISTRADOR:
        qs = qs.filter(usuario=actor)
    return qs.order_by("fecha", "hora_inicio", "id")


def consultar_reserva(actor, reserva_id):
    exigir_rol(actor, *ROLES_TODOS)
    try:
        reserva = Reserva.objects.select_related("espacio", "usuario").get(pk=int(reserva_id))
    except (Reserva.DoesNotExist, TypeError, ValueError):
        raise ErrorDominio(errores.RESERVA_NO_ENCONTRADA)
    if actor.rol != Rol.ADMINISTRADOR and reserva.usuario_id != actor.pk:
        raise ErrorDominio(errores.SIN_PERMISO)
    return reserva


def cancelar_reserva(actor, reserva_id, *, ahora=None):
    exigir_rol(actor, *ROLES_TODOS)
    # Orden exigido por la spec: existencia, permiso, estado, inicio.
    try:
        reserva = Reserva.objects.select_related("usuario").get(pk=int(reserva_id))
    except (Reserva.DoesNotExist, TypeError, ValueError):
        raise ErrorDominio(errores.RESERVA_NO_ENCONTRADA)
    if actor.rol != Rol.ADMINISTRADOR and reserva.usuario_id != actor.pk:
        raise ErrorDominio(errores.SIN_PERMISO)
    if reserva.estado == EstadoReserva.CANCELADA:
        raise ErrorDominio(errores.RESERVA_YA_CANCELADA)
    ahora = ahora if ahora is not None else timezone.localtime()
    inicio = datetime.combine(reserva.fecha, reserva.hora_inicio)
    if timezone.is_aware(ahora):
        inicio = timezone.make_aware(inicio, timezone.get_current_timezone())
    if inicio <= ahora:
        raise ErrorDominio(errores.RESERVA_NO_CANCELABLE)
    reserva.estado = EstadoReserva.CANCELADA
    reserva.cancelada_en = ahora
    reserva.cancelada_por = actor
    reserva.save(update_fields=["estado", "cancelada_en", "cancelada_por"])
    return reserva
