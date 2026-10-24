"""Vistas (capa de presentación). Sin reglas de negocio: llaman a servicios."""

from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from reservas.errores import ErrorDominio
from reservas.presentacion import ESTADO_HTTP, sesion_obligatoria
from reservas.services import autenticacion as servicio_autenticacion


@sesion_obligatoria
def inicio(request):
    return render(request, "reservas/inicio.html")


@require_http_methods(["GET", "POST"])
def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect("inicio")
    if request.method == "POST":
        correo = request.POST.get("correo", "").strip()
        contrasena = request.POST.get("contrasena", "")
        try:
            usuario = servicio_autenticacion.autenticar(correo, contrasena)
        except ErrorDominio as error:
            return render(
                request,
                "reservas/login.html",
                {"error": error, "correo": correo},
                status=ESTADO_HTTP[error.codigo],
            )
        servicio_autenticacion.abrir_sesion(request, usuario)
        return redirect("inicio")
    return render(request, "reservas/login.html")


@require_POST
def cerrar_sesion(request):
    servicio_autenticacion.cerrar_sesion(request)
    return redirect("login")
