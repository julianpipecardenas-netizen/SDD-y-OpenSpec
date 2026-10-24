from django.urls import path

from reservas import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("login/", views.iniciar_sesion, name="login"),
    path("logout/", views.cerrar_sesion, name="logout"),
]
