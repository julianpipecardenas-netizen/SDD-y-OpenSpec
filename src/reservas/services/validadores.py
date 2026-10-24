"""Marco de validadores de reglas de reserva (design D4 y D9, PLAN 7.4).

Cada regla es una función independiente que recibe un `ContextoReserva`
inmutable. Si la regla se cumple no devuelve nada; si no, lanza un
`ErrorDominio`. El servicio las ejecuta con `ejecutar_validadores` en el orden
de la lista, y se detiene en la primera que falla (spec creacion-reservas /
Orden de validación y atomicidad). Agregar una regla es escribir una función
nueva y registrarla en la lista; las existentes no se modifican.

Este módulo no depende de la base de datos ni de la sesión (RNF-02): el
servicio le entrega ya resueltos el espacio y la hora actual.
"""

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Any, Optional

from reservas import errores
from reservas.errores import ErrorDominio

FORMATO_FECHA = "%Y-%m-%d"
FORMATO_HORA = "%H:%M"


@dataclass(frozen=True)
class ContextoReserva:
    """Todo lo que una regla necesita para decidir (design D4).

    Los datos solicitados llegan tal como los envió el usuario (texto o
    objetos de fecha y hora); la primera regla los valida y las demás los
    interpretan con `interpretar_horario`.

    Atributos:
        espacio_id: identificador del espacio solicitado.
        fecha, hora_inicio, hora_fin: datos solicitados.
        espacio: el `Espacio` ya resuelto, o `None` si no existe.
        ahora: instante actual con zona horaria (reloj inyectable, D9).
    """

    espacio_id: Any
    fecha: Any
    hora_inicio: Any
    hora_fin: Any
    espacio: Optional[Any]
    ahora: datetime


def ejecutar_validadores(contexto, validadores):
    """Ejecuta las reglas en orden; la primera que falla detiene el proceso."""
    for validador in validadores:
        validador(contexto)


# --- Interpretación de los datos solicitados ----------------------------------


def _vacio(valor):
    return valor is None or (isinstance(valor, str) and not valor.strip())


def _a_fecha(valor, nombre):
    if _vacio(valor):
        raise ErrorDominio(errores.DATOS_INVALIDOS, f"{nombre} es obligatoria.")
    if isinstance(valor, datetime):
        raise ErrorDominio(errores.DATOS_INVALIDOS, f"{nombre} no es una fecha válida.")
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        try:
            return datetime.strptime(valor.strip(), FORMATO_FECHA).date()
        except ValueError:
            pass
    raise ErrorDominio(
        errores.DATOS_INVALIDOS, f"{nombre} no es una fecha válida (use AAAA-MM-DD)."
    )


def _a_hora(valor, nombre):
    if _vacio(valor):
        raise ErrorDominio(errores.DATOS_INVALIDOS, f"{nombre} es obligatoria.")
    if isinstance(valor, time):
        return valor.replace(tzinfo=None)
    if isinstance(valor, str):
        try:
            return datetime.strptime(valor.strip(), FORMATO_HORA).time()
        except ValueError:
            pass
    raise ErrorDominio(
        errores.DATOS_INVALIDOS, f"{nombre} no es una hora válida (use HH:MM)."
    )


def interpretar_horario(contexto):
    """Devuelve `(fecha, hora_inicio, hora_fin)` como objetos de fecha y hora.

    Lanza `DATOS_INVALIDOS` si falta un dato o está mal formado.
    """
    return (
        _a_fecha(contexto.fecha, "La fecha"),
        _a_hora(contexto.hora_inicio, "La hora de inicio"),
        _a_hora(contexto.hora_fin, "La hora de fin"),
    )


# --- Reglas -------------------------------------------------------------------


def validar_datos_obligatorios(contexto):
    """Fecha, horas y espacio son obligatorios y están bien formados."""
    if _vacio(contexto.espacio_id):
        raise ErrorDominio(errores.DATOS_INVALIDOS, "El espacio es obligatorio.")
    interpretar_horario(contexto)


def validar_rango_horario(contexto):
    """La hora de fin es estrictamente posterior a la de inicio, en el mismo día.

    Como la reserva tiene una sola fecha, un rango que cruza la medianoche
    (23:00 a 01:00) aparece con la hora de fin anterior a la de inicio.
    """
    _, inicio, fin = interpretar_horario(contexto)
    if not fin > inicio:
        raise ErrorDominio(errores.HORARIO_INVALIDO)


def validar_espacio_activo(contexto):
    """El espacio existe y está activo."""
    if contexto.espacio is None:
        raise ErrorDominio(errores.ESPACIO_NO_ENCONTRADO)
    if not contexto.espacio.activo:
        raise ErrorDominio(errores.ESPACIO_INACTIVO)


def validar_no_en_el_pasado(contexto):
    """El inicio es posterior al instante actual (supuesto P2)."""
    fecha, inicio, _ = interpretar_horario(contexto)
    inicio_completo = datetime.combine(fecha, inicio, tzinfo=contexto.ahora.tzinfo)
    if not inicio_completo > contexto.ahora:
        raise ErrorDominio(errores.RESERVA_EN_PASADO)


# Orden fijado por la spec creacion-reservas / Orden de validación y atomicidad.
# La regla de conflicto de horario se registra al final en la tarea 5.3.
VALIDADORES_RESERVA = (
    validar_datos_obligatorios,
    validar_rango_horario,
    validar_espacio_activo,
    validar_no_en_el_pasado,
)
