"""Autenticación obligatoria y control de acceso por rol (design D6).

La autorización se aplica en los servicios, no solo en las vistas, para que
la regla no dependa de la interfaz. Cada servicio recibe al usuario que actúa.
"""

from reservas import errores
from reservas.errores import ErrorDominio
from reservas.models import Rol

# Estudiante y docente tienen los mismos permisos (supuesto P1).
ROLES_TODOS = (Rol.ESTUDIANTE, Rol.DOCENTE, Rol.ADMINISTRADOR)
ROLES_ADMINISTRADOR = (Rol.ADMINISTRADOR,)


def exigir_autenticado(actor):
    """Devuelve al actor si tiene sesión válida; si no, `NO_AUTENTICADO`."""
    if actor is None or not getattr(actor, "is_authenticated", False):
        raise ErrorDominio(errores.NO_AUTENTICADO)
    return actor


def exigir_rol(actor, *roles):
    """Exige sesión válida y que el rol del actor esté entre `roles`.

    Sin sesión lanza `NO_AUTENTICADO`; con un rol no permitido, `SIN_PERMISO`.
    """
    exigir_autenticado(actor)
    if actor.rol not in roles:
        raise ErrorDominio(errores.SIN_PERMISO)
    return actor


def es_administrador(actor):
    return bool(
        actor is not None
        and getattr(actor, "is_authenticated", False)
        and actor.rol == Rol.ADMINISTRADOR
    )
