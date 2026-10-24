"""Consulta de disponibilidad y privacidad (spec consulta-disponibilidad)."""
from datetime import date, datetime, time

from reservas import errores
from reservas.errores import ErrorDominio
from reservas.models import EstadoReserva, Espacio, Reserva, Rol
from reservas.services.acceso import ROLES_TODOS, exigir_rol

INICIO_DIA = time(0, 0)
FIN_DIA = time(23, 59)


def calcular_intervalos(ocupados):
    """Calcula el complemento del día sin crear huecos de duración cero."""
    ordenados = sorted((inicio, fin) for inicio, fin in ocupados if inicio < fin)
    libres = []
    cursor = INICIO_DIA
    for inicio, fin in ordenados:
        if inicio > cursor:
            libres.append((cursor, inicio))
        if fin > cursor:
            cursor = fin
    if cursor < FIN_DIA:
        libres.append((cursor, FIN_DIA))
    return tuple(ordenados), tuple(libres)


def consultar_disponibilidad(actor, espacio_id, fecha):
    exigir_rol(actor, *ROLES_TODOS)
    try:
        fecha_valida = fecha if isinstance(fecha, date) and not isinstance(fecha, datetime) else date.fromisoformat(str(fecha))
    except (TypeError, ValueError):
        raise ErrorDominio(errores.DATOS_INVALIDOS)
    try:
        espacio = Espacio.objects.get(pk=int(espacio_id))
    except (Espacio.DoesNotExist, TypeError, ValueError):
        raise ErrorDominio(errores.ESPACIO_NO_ENCONTRADO)
    if not espacio.activo and actor.rol != Rol.ADMINISTRADOR:
        raise ErrorDominio(errores.ESPACIO_INACTIVO)
    filas = list(Reserva.objects.filter(espacio=espacio, fecha=fecha_valida, estado=EstadoReserva.ACTIVA)
                 .order_by("hora_inicio").values("id", "hora_inicio", "hora_fin", "usuario_id", "usuario__nombre", "usuario__email"))
    ocupados, libres = calcular_intervalos((r["hora_inicio"], r["hora_fin"]) for r in filas)
    # La privacidad se decide aquí, no en la plantilla.
    if actor.rol == Rol.ADMINISTRADOR:
        ocupados_detalle = tuple({"inicio": r["hora_inicio"], "fin": r["hora_fin"], "reserva_id": r["id"],
                                  "usuario_id": r["usuario_id"], "usuario": r["usuario__nombre"], "correo": r["usuario__email"]} for r in filas)
    else:
        ocupados_detalle = tuple({"inicio": inicio, "fin": fin} for inicio, fin in ocupados)
    return {"espacio": espacio, "fecha": fecha_valida, "ocupados": ocupados_detalle,
            "libres": tuple({"inicio": a, "fin": b} for a, b in libres)}
