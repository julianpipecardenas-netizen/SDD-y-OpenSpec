"""Modelos de datos (PLAN 7.3, design D3)."""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class Rol(models.TextChoices):
    """Los tres roles del sistema (spec autenticacion-roles / Roles reconocidos)."""

    ESTUDIANTE = "estudiante", "Estudiante"
    DOCENTE = "docente", "Docente"
    ADMINISTRADOR = "administrador", "Administrador"


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def get_by_natural_key(self, correo):
        # El correo no distingue mayúsculas al iniciar sesión.
        return self.get(email__iexact=correo)

    def _crear(self, email, nombre, password, **extra):
        if not email:
            raise ValueError("El correo es obligatorio.")
        usuario = self.model(email=email, nombre=nombre, **extra)
        usuario.set_password(password)  # siempre con hash (RNF-04)
        usuario.save(using=self._db)
        return usuario

    def create_user(self, email, nombre, password=None, *, rol, **extra):
        """Crea un usuario. El rol es obligatorio: no hay rol por defecto."""
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._crear(email, nombre, password, rol=rol, **extra)

    def create_superuser(self, email, nombre, password=None, **extra):
        """Crea un administrador con acceso al panel de administración."""
        extra.update(is_staff=True, is_superuser=True, rol=Rol.ADMINISTRADOR)
        return self._crear(email, nombre, password, **extra)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Persona que usa el sistema. Se identifica con su correo."""

    email = models.EmailField("correo", unique=True)
    nombre = models.CharField(max_length=150)
    rol = models.CharField(max_length=20, choices=Rol.choices)
    is_active = models.BooleanField("activo", default=True)
    is_staff = models.BooleanField(
        "acceso al panel de administración",
        default=False,
        help_text="Permite entrar al panel de administración de Django.",
    )

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre"]

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rol__in=Rol.values),
                name="usuario_rol_valido",
            ),
        ]

    def save(self, *args, **kwargs):
        # Un solo formato de correo: sin espacios y en minúsculas.
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} <{self.email}>"
