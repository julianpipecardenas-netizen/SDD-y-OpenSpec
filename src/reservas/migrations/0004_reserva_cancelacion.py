from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('reservas', '0003_reserva'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField(
            model_name='reserva', name='cancelada_en',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reserva', name='cancelada_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='reservas_canceladas', to=settings.AUTH_USER_MODEL),
        ),
    ]
