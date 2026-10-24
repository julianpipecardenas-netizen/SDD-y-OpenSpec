"""Errores de dominio del sistema (PLAN 7.5, design D5).

Toda regla de negocio que falla lanza un `ErrorDominio` con un código estable
y un mensaje legible. Los códigos son exactamente los que definen las specs;
las pruebas comprueban el código, no el texto (salvo `CONFLICTO_HORARIO`,
cuyo mensaje fija la spec `validacion-conflictos-horario`).
"""

CREDENCIALES_INVALIDAS = "CREDENCIALES_INVALIDAS"
NO_AUTENTICADO = "NO_AUTENTICADO"
SIN_PERMISO = "SIN_PERMISO"
DATOS_INVALIDOS = "DATOS_INVALIDOS"
HORARIO_INVALIDO = "HORARIO_INVALIDO"
RESERVA_EN_PASADO = "RESERVA_EN_PASADO"
CONFLICTO_HORARIO = "CONFLICTO_HORARIO"
ESPACIO_NO_ENCONTRADO = "ESPACIO_NO_ENCONTRADO"
ESPACIO_INACTIVO = "ESPACIO_INACTIVO"
ESPACIO_DUPLICADO = "ESPACIO_DUPLICADO"
ESPACIO_CON_RESERVAS = "ESPACIO_CON_RESERVAS"
RESERVA_NO_ENCONTRADA = "RESERVA_NO_ENCONTRADA"
RESERVA_YA_CANCELADA = "RESERVA_YA_CANCELADA"
RESERVA_NO_CANCELABLE = "RESERVA_NO_CANCELABLE"

# Mensaje por defecto de cada código.
MENSAJES = {
    CREDENCIALES_INVALIDAS: "Correo o contraseña incorrectos.",
    NO_AUTENTICADO: "Debes iniciar sesión para realizar esta operación.",
    SIN_PERMISO: "No tienes permiso para realizar esta operación.",
    DATOS_INVALIDOS: "Los datos enviados no son válidos.",
    HORARIO_INVALIDO: (
        "El horario no es válido: la hora de fin debe ser posterior a la de "
        "inicio y ambas deben estar en el mismo día."
    ),
    RESERVA_EN_PASADO: "No se puede reservar en un horario que ya comenzó.",
    CONFLICTO_HORARIO: "El espacio ya está reservado en ese horario",
    ESPACIO_NO_ENCONTRADO: "El espacio no existe.",
    ESPACIO_INACTIVO: "El espacio está inactivo.",
    ESPACIO_DUPLICADO: "Ya existe un espacio con ese nombre.",
    ESPACIO_CON_RESERVAS: "No se puede eliminar un espacio que tiene reservas.",
    RESERVA_NO_ENCONTRADA: "La reserva no existe.",
    RESERVA_YA_CANCELADA: "La reserva ya estaba cancelada.",
    RESERVA_NO_CANCELABLE: "No se puede cancelar una reserva que ya comenzó.",
}

CODIGOS = tuple(MENSAJES)


class ErrorDominio(Exception):
    """Una regla de negocio no se cumple.

    Atributos:
        codigo: uno de `CODIGOS`.
        mensaje: texto para el usuario; si no se indica, el del código.
    """

    def __init__(self, codigo, mensaje=None):
        if codigo not in MENSAJES:
            raise ValueError(f"Código de error de dominio desconocido: {codigo!r}")
        self.codigo = codigo
        self.mensaje = mensaje if mensaje is not None else MENSAJES[codigo]
        super().__init__(f"{codigo}: {self.mensaje}")
