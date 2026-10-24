import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reservas", "0002_espacio"),
    ]

    operations = [
        migrations.CreateModel(
            name="Reserva",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("fecha", models.DateField()),
                ("hora_inicio", models.TimeField()),
                ("hora_fin", models.TimeField()),
                (
                    "estado",
                    models.CharField(
                        choices=[("activa", "Activa"), ("cancelada", "Cancelada")],
                        default="activa",
                        max_length=10,
                    ),
                ),
                ("creada_en", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "espacio",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="reservas",
                        to="reservas.espacio",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="reservas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "reserva",
                "verbose_name_plural": "reservas",
                "ordering": ["fecha", "hora_inicio", "id"],
                "indexes": [
                    models.Index(
                        fields=["espacio", "fecha", "estado"],
                        name="reserva_espacio_fecha_estado",
                    )
                ],
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("hora_fin__gt", models.F("hora_inicio"))),
                        name="reserva_rango_horario_valido",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(("estado__in", ["activa", "cancelada"])),
                        name="reserva_estado_valido",
                    ),
                ],
            },
        ),
    ]
