"""Pruebas de integración de la vista de creación de reservas (tarea 4.8).

Specs: creacion-reservas (Creación de una reserva, Datos obligatorios y bien
formados, Rango horario válido, Espacio existente y activo, No se reserva en
el pasado). Se entra con `force_login`; el inicio de sesión ya se prueba en
test_vistas_autenticacion.py.
"""

from datetime import date, timedelta

from django.urls import reverse

from reservas import errores
from reservas.models import EstadoReserva, Reserva


def futuro():
    """Una fecha segura hacia adelante, para no depender del reloj."""
    return (date.today() + timedelta(days=30)).isoformat()


def entrar(client, usuario):
    client.force_login(usuario)
    return client


def pagina(respuesta):
    return respuesta.content.decode()


def datos_de_reserva(un_espacio, **cambios):
    datos = {"espacio": str(un_espacio.pk), "fecha": futuro(), "hora_inicio": "10:00", "hora_fin": "12:00"}
    datos.update(cambios)
    return datos


def test_el_formulario_se_muestra_con_los_espacios_activos(client, estudiante, espacio):
    entrar(client, estudiante)
    respuesta = client.get(reverse("reserva_nueva"))
    assert respuesta.status_code == 200
    assert "Nueva reserva" in pagina(respuesta)
    assert espacio.nombre in pagina(respuesta)


def test_un_estudiante_crea_una_reserva_valida(client, estudiante, espacio):
    """Spec: creacion-reservas / Creación de una reserva / Reserva válida."""
    entrar(client, estudiante)
    respuesta = client.post(reverse("reserva_nueva"), datos_de_reserva(espacio), follow=True)
    reserva = Reserva.objects.get()
    assert reserva.usuario == estudiante
    assert reserva.estado == EstadoReserva.ACTIVA
    assert respuesta.status_code == 200
    assert "Reserva creada" in pagina(respuesta)


def test_un_dato_invalido_muestra_el_codigo_y_el_mensaje(client, estudiante, espacio):
    """Spec: creacion-reservas / Datos obligatorios y bien formados / Falta un dato."""
    entrar(client, estudiante)
    respuesta = client.post(reverse("reserva_nueva"), datos_de_reserva(espacio, hora_fin=""))
    assert respuesta.status_code == 422
    assert errores.DATOS_INVALIDOS in pagina(respuesta)
    assert "La hora de fin es obligatoria" in pagina(respuesta)
    assert Reserva.objects.count() == 0


def test_un_horario_invalido_muestra_su_codigo(client, estudiante, espacio):
    """Spec: creacion-reservas / Rango horario válido / Fin anterior al inicio."""
    entrar(client, estudiante)
    respuesta = client.post(
        reverse("reserva_nueva"), datos_de_reserva(espacio, hora_inicio="12:00", hora_fin="10:00")
    )
    assert respuesta.status_code == 422
    assert errores.HORARIO_INVALIDO in pagina(respuesta)
    assert Reserva.objects.count() == 0


def test_el_formulario_conserva_lo_escrito_tras_un_error(client, estudiante, espacio):
    entrar(client, estudiante)
    respuesta = client.post(
        reverse("reserva_nueva"), datos_de_reserva(espacio, hora_inicio="12:00", hora_fin="10:00")
    )
    assert 'value="12:00"' in pagina(respuesta)
    assert 'value="10:00"' in pagina(respuesta)


def test_reservar_en_el_pasado_muestra_su_codigo(client, estudiante, espacio):
    """Spec: creacion-reservas / No se reserva en el pasado / Inicio ya transcurrido."""
    entrar(client, estudiante)
    respuesta = client.post(reverse("reserva_nueva"), datos_de_reserva(espacio, fecha="2000-01-01"))
    assert respuesta.status_code == 422
    assert errores.RESERVA_EN_PASADO in pagina(respuesta)


def test_un_espacio_inactivo_muestra_su_codigo(client, estudiante, espacio):
    """Spec: creacion-reservas / Espacio existente y activo / Espacio inactivo."""
    espacio.activo = False
    espacio.save()
    entrar(client, estudiante)
    respuesta = client.post(reverse("reserva_nueva"), datos_de_reserva(espacio))
    assert respuesta.status_code == 409
    assert errores.ESPACIO_INACTIVO in pagina(respuesta)


def test_un_espacio_inexistente_muestra_su_codigo(client, estudiante, espacio):
    """Spec: creacion-reservas / Espacio existente y activo / Espacio inexistente."""
    entrar(client, estudiante)
    respuesta = client.post(reverse("reserva_nueva"), datos_de_reserva(espacio, espacio="9999"))
    assert respuesta.status_code == 404
    assert errores.ESPACIO_NO_ENCONTRADO in pagina(respuesta)


def test_sin_sesion_responde_no_autenticado(client, espacio):
    """Spec: autenticacion-roles / Operaciones protegidas exigen autenticación / Creación de reserva sin sesión."""
    respuesta = client.post(reverse("reserva_nueva"), datos_de_reserva(espacio))
    assert respuesta.status_code == 401
    assert errores.NO_AUTENTICADO in pagina(respuesta)
    assert Reserva.objects.count() == 0
