from datetime import time
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from reservas.presentacion import sesion_obligatoria, con_errores_de_dominio
from reservas.services.disponibilidad import consultar_disponibilidad

@sesion_obligatoria
@con_errores_de_dominio
@require_http_methods(["GET", "POST"])
def consultar(request):
    datos = request.POST if request.method == "POST" else request.GET
    contexto = {"espacio_id": datos.get("espacio", ""), "fecha": datos.get("fecha", "")}
    resultado = None
    if contexto["espacio_id"] or contexto["fecha"]:
        resultado = consultar_disponibilidad(request.user, contexto["espacio_id"], contexto["fecha"])
    from reservas.services.espacios import listar_espacios
    return render(request, "reservas/disponibilidad.html", {"datos": contexto, "resultado": resultado,
                   "espacios": listar_espacios(request.user)})
