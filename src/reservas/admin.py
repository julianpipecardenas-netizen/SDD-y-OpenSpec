"""Panel de administración: alta de usuarios por el administrador (design D11).

No hay pantalla de registro (supuesto P7): los usuarios los crea el
administrador desde el panel de Django, indicando su rol.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm

from reservas.models import Usuario


class FormularioCrearUsuario(BaseUserCreationForm):
    class Meta:
        model = Usuario
        fields = ("email", "nombre", "rol")


class FormularioEditarUsuario(UserChangeForm):
    class Meta:
        model = Usuario
        fields = "__all__"


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    form = FormularioEditarUsuario
    add_form = FormularioCrearUsuario

    list_display = ("email", "nombre", "rol", "is_active")
    list_filter = ("rol", "is_active")
    search_fields = ("email", "nombre")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Datos", {"fields": ("nombre", "rol")}),
        (
            "Permisos",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Fechas", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "nombre", "rol", "password1", "password2"),
            },
        ),
    )
