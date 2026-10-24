from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from reservas.presentacion import sesion_obligatoria, con_errores_de_dominio
from reservas.services.consultas_reservas import listar_reservas, consultar_reserva, cancelar_reserva

@sesion_obligatoria
@con_errores_de_dominio
def lista(request):
    return render(request, "reservas/reservas_lista.html", {"reservas": listar_reservas(request.user)})

@sesion_obligatoria
@con_errores_de_dominio
def detalle(request, reserva_id):
    return render(request, "reservas/reserva_detalle.html", {"reserva": consultar_reserva(request.user, reserva_id)})

@sesion_obligatoria
@con_errores_de_dominio
@require_http_methods(["POST"])
def cancelar(request, reserva_id):
    cancelar_reserva(request.user, reserva_id)
    messages.success(request, "Reserva cancelada.")
    return redirect("reservas_lista")
