"""Inicio y cierre de sesión (spec autenticacion-roles)."""

from django.contrib.auth import authenticate, login, logout

from reservas import errores
from reservas.errores import ErrorDominio


def autenticar(correo, contrasena):
    """Devuelve el usuario si las credenciales son válidas.

    Con cualquier fallo (correo inexistente, contraseña incorrecta, usuario
    inactivo, datos vacíos) lanza el mismo `CREDENCIALES_INVALIDAS` con el
    mismo mensaje, para no revelar cuál dato falló.
    """
    usuario = authenticate(username=correo or "", password=contrasena or "")
    if usuario is None:
        raise ErrorDominio(errores.CREDENCIALES_INVALIDAS)
    return usuario


def abrir_sesion(request, usuario):
    """Asocia la sesión de la petición al usuario ya autenticado."""
    login(request, usuario)


def cerrar_sesion(request):
    """Invalida la sesión de la petición."""
    logout(request)
