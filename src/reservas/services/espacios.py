"""Gestión de espacios académicos (spec gestion-espacios).

Las operaciones de escritura son exclusivas del administrador (design D6).
"""

from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from reservas import errores
from reservas.errores import ErrorDominio
from reservas.models import Espacio, Reserva, TipoEspacio
from reservas.services.acceso import (
    ROLES_ADMINISTRADOR,
    ROLES_TODOS,
    es_administrador,
    exigir_rol,
)

LARGO_MAXIMO_NOMBRE = 100


def _datos_validos(nombre, tipo, capacidad):
    """Valida y normaliza los datos de un espacio; lanza `DATOS_INVALIDOS`."""
    if not isinstance(nombre, str) or not nombre.strip():
        raise ErrorDominio(errores.DATOS_INVALIDOS, "El nombre del espacio es obligatorio.")
    nombre = nombre.strip()
    if len(nombre) > LARGO_MAXIMO_NOMBRE:
        raise ErrorDominio(
            errores.DATOS_INVALIDOS,
            f"El nombre no puede superar {LARGO_MAXIMO_NOMBRE} caracteres.",
        )

    if tipo not in TipoEspacio.values:
        raise ErrorDominio(
            errores.DATOS_INVALIDOS,
            "El tipo debe ser uno de: " + ", ".join(TipoEspacio.values) + ".",
        )

    # Un booleano es un entero en Python, pero no es una capacidad válida.
    if isinstance(capacidad, str) and capacidad.strip().isdigit():
        capacidad = int(capacidad.strip())
    if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
        raise ErrorDominio(
            errores.DATOS_INVALIDOS, "La capacidad debe ser un número entero mayor que cero."
        )
    return nombre, tipo, capacidad


def _exigir_nombre_libre(nombre, excluir_pk=None):
    otros = Espacio.objects.filter(nombre__iexact=nombre)
    if excluir_pk is not None:
        otros = otros.exclude(pk=excluir_pk)
    if otros.exists():
        raise ErrorDominio(errores.ESPACIO_DUPLICADO)


def obtener_o_fallar(espacio_id):
    """Devuelve el espacio o lanza `ESPACIO_NO_ENCONTRADO` (sin reglas de rol)."""
    try:
        return Espacio.objects.get(pk=espacio_id)
    except (Espacio.DoesNotExist, ValueError, TypeError):
        raise ErrorDominio(errores.ESPACIO_NO_ENCONTRADO)


def crear_espacio(actor, nombre, tipo, capacidad):
    """Crea un espacio activo. Solo el administrador."""
    exigir_rol(actor, *ROLES_ADMINISTRADOR)
    nombre, tipo, capacidad = _datos_validos(nombre, tipo, capacidad)
    _exigir_nombre_libre(nombre)
    try:
        with transaction.atomic():
            return Espacio.objects.create(
                nombre=nombre, tipo=tipo, capacidad=capacidad, activo=True
            )
    except IntegrityError:  # otra petición creó el mismo nombre un instante antes
        raise ErrorDominio(errores.ESPACIO_DUPLICADO)


def editar_espacio(actor, espacio_id, *, nombre=None, tipo=None, capacidad=None):
    """Cambia nombre, tipo o capacidad. Lo que no se indique no cambia."""
    exigir_rol(actor, *ROLES_ADMINISTRADOR)
    espacio = obtener_o_fallar(espacio_id)

    nombre, tipo, capacidad = _datos_validos(
        espacio.nombre if nombre is None else nombre,
        espacio.tipo if tipo is None else tipo,
        espacio.capacidad if capacidad is None else capacidad,
    )
    _exigir_nombre_libre(nombre, excluir_pk=espacio.pk)

    espacio.nombre, espacio.tipo, espacio.capacidad = nombre, tipo, capacidad
    try:
        with transaction.atomic():
            espacio.save(update_fields=["nombre", "tipo", "capacidad"])
    except IntegrityError:
        raise ErrorDominio(errores.ESPACIO_DUPLICADO)
    return espacio


def _cambiar_estado(actor, espacio_id, activo):
    exigir_rol(actor, *ROLES_ADMINISTRADOR)
    espacio = obtener_o_fallar(espacio_id)
    if espacio.activo != activo:
        espacio.activo = activo
        espacio.save(update_fields=["activo"])
    return espacio


def desactivar_espacio(actor, espacio_id):
    """Deja de aceptar reservas nuevas; las reservas existentes se conservan (P4)."""
    return _cambiar_estado(actor, espacio_id, False)


def activar_espacio(actor, espacio_id):
    """El espacio vuelve a aceptar reservas nuevas."""
    return _cambiar_estado(actor, espacio_id, True)


def eliminar_espacio(actor, espacio_id):
    """Elimina un espacio. Se bloquea si tiene reservas, de cualquier estado.

    Spec gestion-espacios / Activación y desactivación: los espacios no se
    eliminan físicamente mientras tengan reservas asociadas. Para dejar de
    ofrecer un espacio con reservas, se desactiva.
    """
    exigir_rol(actor, *ROLES_ADMINISTRADOR)
    espacio = obtener_o_fallar(espacio_id)
    if Reserva.objects.filter(espacio=espacio).exists():
        raise ErrorDominio(errores.ESPACIO_CON_RESERVAS)
    try:
        with transaction.atomic():
            espacio.delete()
    except ProtectedError:  # una reserva se creó justo antes (clave foránea protegida)
        raise ErrorDominio(errores.ESPACIO_CON_RESERVAS)


def listar_espacios(actor):
    """Estudiantes y docentes ven solo los activos; el administrador, todos."""
    exigir_rol(actor, *ROLES_TODOS)
    espacios = Espacio.objects.all()  # ordenados por nombre (Meta)
    if not es_administrador(actor):
        espacios = espacios.filter(activo=True)
    return list(espacios)


def obtener_espacio(actor, espacio_id):
    """Un espacio por identificador. Un inactivo solo lo ve el administrador."""
    exigir_rol(actor, *ROLES_TODOS)
    espacio = obtener_o_fallar(espacio_id)
    if not espacio.activo and not es_administrador(actor):
        raise ErrorDominio(errores.ESPACIO_INACTIVO)
    return espacio
