"""Prueba mínima de configuración (tarea 1.3).

No corresponde a un escenario de las specs: solo comprueba que pytest
encuentra el proyecto Django y que la configuración base es la del plan.
"""

from django.conf import settings


def test_zona_horaria_es_la_del_plan():
    """PLAN S4: zona horaria única America/Bogota."""
    assert settings.TIME_ZONE == "America/Bogota"


def test_aplicacion_reservas_instalada():
    assert "reservas" in settings.INSTALLED_APPS
