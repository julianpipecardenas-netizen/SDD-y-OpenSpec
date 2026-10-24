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
from datetime import date, datetime, time, timedelta
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
        reservas_existentes: pares `(hora_inicio, hora_fin)` de las reservas
            activas del mismo espacio y fecha (ámbito de la regla de
            conflicto; lo decide quien arma el contexto, no la regla).
    """

    espacio_id: Any
    fecha: Any
    hora_inicio: Any
    hora_fin: Any
    espacio: Optional[Any]
    ahora: datetime
    reservas_existentes: tuple = ()


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


def validar_duracion_maxima(contexto):
    """La reserva individual no puede superar cuatro horas (cambio fase 4).

    La regla se aplica a cada solicitud por separado. No acumula reservas de
    días anteriores ni suma reservas de otros días. Una duración exactamente
    igual a cuatro horas está permitida.
    """
    _, inicio, fin = interpretar_horario(contexto)
    duracion = datetime.combine(date.min, fin) - datetime.combine(date.min, inicio)
    if duracion > timedelta(hours=4):
        raise ErrorDominio(errores.DURACION_RESERVA_EXCEDIDA)


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


def hay_solapamiento(inicio_a, fin_a, inicio_b, fin_b):
    """Dos rangos semiabiertos se solapan si el inicio de cada uno es anterior al fin del otro.

    Los rangos contiguos (el fin de uno es el inicio del otro) no se solapan
    (design D7, supuesto P11).
    """
    return inicio_a < fin_b and inicio_b < fin_a


def validar_no_solapamiento(contexto):
    """El rango solicitado no se solapa con ninguna reserva existente del contexto.

    Solo necesita las reservas existentes y el rango solicitado: no usa base
    de datos, sesión ni interfaz (spec validacion-conflictos-horario /
    Regla verificable de forma aislada).
    """
    _, inicio, fin = interpretar_horario(contexto)
    for inicio_existente, fin_existente in contexto.reservas_existentes:
        if hay_solapamiento(inicio, fin, inicio_existente, fin_existente):
            raise ErrorDominio(errores.CONFLICTO_HORARIO)


# Orden fijado por la spec creacion-reservas / Orden de validación y atomicidad.
# El conflicto de horario va al final: solo se evalúa si todo lo demás es válido.
VALIDADORES_RESERVA = (
    validar_datos_obligatorios,
    validar_rango_horario,
    validar_espacio_activo,
    validar_no_en_el_pasado,
    validar_duracion_maxima,
    validar_no_solapamiento,
)
