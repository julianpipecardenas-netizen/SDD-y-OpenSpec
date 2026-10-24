"""Vistas de espacios (capa de presentación). Sin reglas de negocio."""

from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from reservas import errores
from reservas.errores import ErrorDominio
from reservas.models import TipoEspacio
from reservas.presentacion import ESTADO_HTTP, sesion_obligatoria
from reservas.services import espacios as servicio
from reservas.services.acceso import ROLES_ADMINISTRADOR, es_administrador, exigir_rol

# Errores que se muestran dentro del formulario; el resto usa la página de error.
ERRORES_DE_FORMULARIO = {errores.DATOS_INVALIDOS, errores.ESPACIO_DUPLICADO}


def _datos_del_formulario(request):
    return {
        "nombre": request.POST.get("nombre", ""),
        "tipo": request.POST.get("tipo", ""),
        "capacidad": request.POST.get("capacidad", ""),
    }


def _mostrar_formulario(request, espacio, datos, error=None):
    return render(
        request,
        "reservas/espacio_form.html",
        {"espacio": espacio, "datos": datos, "error": error, "tipos": TipoEspacio.choices},
        status=ESTADO_HTTP[error.codigo] if error else 200,
    )


@sesion_obligatoria
def lista(request):
    contexto = {
        "espacios": servicio.listar_espacios(request.user),
        "es_admin": es_administrador(request.user),
    }
    return render(request, "reservas/espacios_lista.html", contexto)


@sesion_obligatoria
def detalle(request, espacio_id):
    contexto = {
        "espacio": servicio.obtener_espacio(request.user, espacio_id),
        "es_admin": es_administrador(request.user),
    }
    return render(request, "reservas/espacio_detalle.html", contexto)


@sesion_obligatoria
@require_http_methods(["GET", "POST"])
def crear(request):
    exigir_rol(request.user, *ROLES_ADMINISTRADOR)
    if request.method == "POST":
        datos = _datos_del_formulario(request)
        try:
            espacio = servicio.crear_espacio(request.user, **datos)
        except ErrorDominio as error:
            if error.codigo not in ERRORES_DE_FORMULARIO:
                raise
            return _mostrar_formulario(request, None, datos, error)
        return redirect("espacio_detalle", espacio_id=espacio.pk)
    return _mostrar_formulario(request, None, {})


@sesion_obligatoria
@require_http_methods(["GET", "POST"])
def editar(request, espacio_id):
    exigir_rol(request.user, *ROLES_ADMINISTRADOR)
    espacio = servicio.obtener_espacio(request.user, espacio_id)
    if request.method == "POST":
        datos = _datos_del_formulario(request)
        try:
            servicio.editar_espacio(request.user, espacio_id, **datos)
        except ErrorDominio as error:
            if error.codigo not in ERRORES_DE_FORMULARIO:
                raise
            return _mostrar_formulario(request, espacio, datos, error)
        return redirect("espacio_detalle", espacio_id=espacio_id)
    datos = {"nombre": espacio.nombre, "tipo": espacio.tipo, "capacidad": espacio.capacidad}
    return _mostrar_formulario(request, espacio, datos)


@sesion_obligatoria
@require_POST
def activar(request, espacio_id):
    servicio.activar_espacio(request.user, espacio_id)
    return redirect("espacio_detalle", espacio_id=espacio_id)


@sesion_obligatoria
@require_POST
def desactivar(request, espacio_id):
    servicio.desactivar_espacio(request.user, espacio_id)
    return redirect("espacio_detalle", espacio_id=espacio_id)
