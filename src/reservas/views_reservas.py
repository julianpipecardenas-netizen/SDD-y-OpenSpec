"""Vistas de reservas (capa de presentación). Sin reglas de negocio."""

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from reservas.errores import ErrorDominio
from reservas.presentacion import ESTADO_HTTP, sesion_obligatoria
from reservas.services import espacios as servicio_espacios
from reservas.services import reservas as servicio


def _datos_del_formulario(request):
    return {
        "espacio_id": request.POST.get("espacio", ""),
        "fecha": request.POST.get("fecha", ""),
        "hora_inicio": request.POST.get("hora_inicio", ""),
        "hora_fin": request.POST.get("hora_fin", ""),
    }


def _mostrar_formulario(request, datos, error=None):
    contexto = {
        "espacios": servicio_espacios.listar_espacios(request.user),
        "datos": datos,
        "error": error,
    }
    return render(
        request,
        "reservas/reserva_form.html",
        contexto,
        status=ESTADO_HTTP[error.codigo] if error else 200,
    )


@sesion_obligatoria
@require_http_methods(["GET", "POST"])
def crear(request):
    if request.method == "POST":
        datos = _datos_del_formulario(request)
        try:
            servicio.crear_reserva(request.user, **datos)
        except ErrorDominio as error:
            return _mostrar_formulario(request, datos, error)
        messages.success(request, "Reserva creada.")
        return redirect("inicio")
    return _mostrar_formulario(request, {})
