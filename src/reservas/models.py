"""Modelos de datos (PLAN 7.3, design D3)."""

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone


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


class TipoEspacio(models.TextChoices):
    """Tipos de espacio permitidos (spec gestion-espacios / Datos de un espacio)."""

    AULA = "aula", "Aula"
    LABORATORIO = "laboratorio", "Laboratorio"
    SALA_ESTUDIO = "sala_estudio", "Sala de estudio"
    AUDITORIO = "auditorio", "Auditorio"


class Espacio(models.Model):
    """Espacio académico que se puede reservar."""

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TipoEspacio.choices)
    capacidad = models.IntegerField(help_text="Dato informativo; no restringe reservas.")
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "espacio"
        verbose_name_plural = "espacios"
        ordering = ["nombre"]
        constraints = [
            # Nombre único sin distinguir mayúsculas.
            models.UniqueConstraint(Lower("nombre"), name="espacio_nombre_unico"),
            models.CheckConstraint(
                condition=models.Q(capacidad__gt=0), name="espacio_capacidad_positiva"
            ),
            models.CheckConstraint(
                condition=models.Q(tipo__in=TipoEspacio.values), name="espacio_tipo_valido"
            ),
        ]

    def __str__(self):
        return self.nombre


class EstadoReserva(models.TextChoices):
    """Estados de una reserva (spec creacion-reservas / Creación de una reserva)."""

    ACTIVA = "activa", "Activa"
    CANCELADA = "cancelada", "Cancelada"


class Reserva(models.Model):
    """Reserva de un espacio en una fecha y un rango horario (design D3).

    Fecha y horas son locales (America/Bogota), sin conversión (S4). Las claves
    foráneas están protegidas: no se borran espacios ni usuarios con reservas.
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reservas"
    )
    espacio = models.ForeignKey(Espacio, on_delete=models.PROTECT, related_name="reservas")
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(
        max_length=10, choices=EstadoReserva.choices, default=EstadoReserva.ACTIVA
    )
    creada_en = models.DateTimeField(default=timezone.now)
    cancelada_en = models.DateTimeField(null=True, blank=True)
    cancelada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        related_name="reservas_canceladas",
    )

    class Meta:
        verbose_name = "reserva"
        verbose_name_plural = "reservas"
        ordering = ["fecha", "hora_inicio", "id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(hora_fin__gt=models.F("hora_inicio")),
                name="reserva_rango_horario_valido",
            ),
            models.CheckConstraint(
                condition=models.Q(estado__in=EstadoReserva.values),
                name="reserva_estado_valido",
            ),
        ]
        indexes = [
            models.Index(fields=["espacio", "fecha", "estado"], name="reserva_espacio_fecha_estado"),
        ]

    def __str__(self):
        return f"{self.espacio} {self.fecha} {self.hora_inicio:%H:%M}-{self.hora_fin:%H:%M}"
