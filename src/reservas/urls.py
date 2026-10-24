from django.urls import path

from reservas import views, views_espacios, views_reservas, views_disponibilidad, views_consultas_reservas

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("login/", views.iniciar_sesion, name="login"),
    path("logout/", views.cerrar_sesion, name="logout"),
    path("reservas/nueva/", views_reservas.crear, name="reserva_nueva"),
    path("disponibilidad/", views_disponibilidad.consultar, name="disponibilidad"),
    path("reservas/", views_consultas_reservas.lista, name="reservas_lista"),
    path("reservas/<int:reserva_id>/", views_consultas_reservas.detalle, name="reserva_detalle"),
    path("reservas/<int:reserva_id>/cancelar/", views_consultas_reservas.cancelar, name="reserva_cancelar"),
    path("espacios/", views_espacios.lista, name="espacios"),
    path("espacios/nuevo/", views_espacios.crear, name="espacio_nuevo"),
    path("espacios/<int:espacio_id>/", views_espacios.detalle, name="espacio_detalle"),
    path("espacios/<int:espacio_id>/editar/", views_espacios.editar, name="espacio_editar"),
    path("espacios/<int:espacio_id>/activar/", views_espacios.activar, name="espacio_activar"),
    path(
        "espacios/<int:espacio_id>/desactivar/",
        views_espacios.desactivar,
        name="espacio_desactivar",
    ),
]
