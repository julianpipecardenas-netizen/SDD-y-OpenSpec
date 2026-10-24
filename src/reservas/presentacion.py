"""Utilidades de la capa de presentación (design D2).

Traducen los errores de dominio en respuestas HTTP coherentes. Aquí no hay
reglas de negocio: solo la correspondencia código de dominio -> estado HTTP.
"""

from functools import wraps

from django.shortcuts import render

from reservas import errores as e
from reservas.errores import ErrorDominio
from reservas.services.acceso import exigir_autenticado

ESTADO_HTTP = {
    e.NO_AUTENTICADO: 401,
    e.CREDENCIALES_INVALIDAS: 401,
    e.SIN_PERMISO: 403,
    e.ESPACIO_NO_ENCONTRADO: 404,
    e.RESERVA_NO_ENCONTRADA: 404,
    e.CONFLICTO_HORARIO: 409,
    e.ESPACIO_DUPLICADO: 409,
    e.ESPACIO_CON_RESERVAS: 409,
    e.ESPACIO_INACTIVO: 409,
    e.RESERVA_YA_CANCELADA: 409,
    e.RESERVA_NO_CANCELABLE: 409,
    e.DATOS_INVALIDOS: 422,
    e.HORARIO_INVALIDO: 422,
    e.RESERVA_EN_PASADO: 422,
}


def responder_error(request, error):
    """Muestra el código y el mensaje del error con su estado HTTP."""
    return render(
        request, "reservas/error.html", {"error": error}, status=ESTADO_HTTP[error.codigo]
    )


def con_errores_de_dominio(vista):
    """Convierte cualquier `ErrorDominio` de la vista en una página de error."""

    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        try:
            return vista(request, *args, **kwargs)
        except ErrorDominio as error:
            return responder_error(request, error)

    return envoltura


def sesion_obligatoria(vista):
    """Exige sesión válida; sin ella responde `NO_AUTENTICADO` (401)."""

    @con_errores_de_dominio
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        exigir_autenticado(request.user)
        return vista(request, *args, **kwargs)

    return envoltura
