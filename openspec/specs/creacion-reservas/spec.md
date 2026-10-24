# Spec

## Purpose

Define cómo un usuario autenticado crea una reserva sobre un espacio, qué datos debe aportar y qué validaciones de entrada se aplican antes de evaluar conflictos de horario.

## Requirements

### Requirement: Creación de una reserva
El sistema SHALL permitir a todo usuario autenticado crear una reserva indicando espacio, fecha, hora de inicio y hora de fin. Una reserva creada MUST quedar en estado `activa`, pertenecer al usuario que la creó y registrar su fecha y hora de creación. (RF-03)

#### Scenario: Reserva válida
- **WHEN** un estudiante reserva un espacio activo el 2030-03-15 de 10:00 a 12:00 y ese horario está libre
- **THEN** el sistema crea la reserva en estado `activa`, a nombre del estudiante, con identificador y fecha de creación

#### Scenario: Reserva a nombre de quien la crea
- **WHEN** el administrador crea una reserva
- **THEN** la reserva pertenece al administrador y no a otro usuario (supuesto P10)

### Requirement: Rango horario válido
La hora de fin MUST ser estrictamente posterior a la hora de inicio, y ambas MUST estar en la misma fecha, sin cruzar la medianoche. Si no se cumple, el sistema MUST rechazar la reserva con el código `HORARIO_INVALIDO`. (RF-03)

#### Scenario: Fin igual al inicio
- **WHEN** un usuario crea una reserva con hora de inicio 10:00 y hora de fin 10:00
- **THEN** el sistema responde `HORARIO_INVALIDO` y no crea la reserva

#### Scenario: Fin anterior al inicio
- **WHEN** un usuario crea una reserva con hora de inicio 12:00 y hora de fin 10:00
- **THEN** el sistema responde `HORARIO_INVALIDO` y no crea la reserva

#### Scenario: Reserva que cruza la medianoche
- **WHEN** un usuario intenta reservar de las 23:00 de un día a la 01:00 del día siguiente
- **THEN** el sistema responde `HORARIO_INVALIDO` y no crea la reserva

#### Scenario: Reserva mínima de un minuto
- **WHEN** un usuario reserva de 10:00 a 10:01 en un horario libre
- **THEN** el sistema crea la reserva (supuesto P3: no hay granularidad mínima)

### Requirement: Datos obligatorios y bien formados
La fecha, la hora de inicio, la hora de fin y el espacio SHALL ser obligatorios. La fecha MUST ser un día calendario válido y las horas MUST ser horas del día válidas. Si falta un dato o está mal formado, el sistema MUST responder `DATOS_INVALIDOS` y no crear la reserva. (RF-03)

#### Scenario: Falta un dato
- **WHEN** un usuario envía una reserva sin hora de fin
- **THEN** el sistema responde `DATOS_INVALIDOS` y no crea la reserva

#### Scenario: Fecha inexistente
- **WHEN** un usuario envía la fecha 2030-02-30
- **THEN** el sistema responde `DATOS_INVALIDOS` y no crea la reserva

#### Scenario: Hora fuera de rango
- **WHEN** un usuario envía la hora de inicio 25:00
- **THEN** el sistema responde `DATOS_INVALIDOS` y no crea la reserva

### Requirement: Espacio existente y activo
La reserva MUST referirse a un espacio que exista y esté activo. Si el espacio no existe, el sistema MUST responder `ESPACIO_NO_ENCONTRADO`; si está inactivo, MUST responder `ESPACIO_INACTIVO`. En ambos casos no se crea la reserva. (RF-03)

#### Scenario: Espacio inexistente
- **WHEN** un usuario reserva un identificador de espacio que no existe
- **THEN** el sistema responde `ESPACIO_NO_ENCONTRADO` y no crea la reserva

#### Scenario: Espacio inactivo
- **WHEN** un usuario reserva un espacio inactivo
- **THEN** el sistema responde `ESPACIO_INACTIVO` y no crea la reserva

### Requirement: No se reserva en el pasado
La hora de inicio de una reserva MUST ser posterior al instante actual, medido en la zona horaria America/Bogota. Si no lo es, el sistema MUST responder `RESERVA_EN_PASADO` y no crear la reserva (supuesto P2). (RF-03)

#### Scenario: Inicio ya transcurrido
- **WHEN** un usuario reserva un horario cuyo inicio ya pasó
- **THEN** el sistema responde `RESERVA_EN_PASADO` y no crea la reserva

#### Scenario: Inicio en el futuro
- **WHEN** un usuario reserva un horario cuyo inicio es posterior al instante actual
- **THEN** esta validación no rechaza la reserva

### Requirement: Orden de validación y atomicidad
El sistema SHALL evaluar las condiciones en este orden y detenerse en la primera que falle: autenticación, datos obligatorios y bien formados, rango horario, espacio existente y activo, reserva en el pasado y, por último, conflictos de horario. Una reserva rechazada MUST NOT dejar ningún registro.

#### Scenario: Se informa el primer error en orden
- **WHEN** un usuario envía una reserva con hora de fin anterior al inicio sobre un espacio inactivo
- **THEN** el sistema responde `HORARIO_INVALIDO`, que es la primera condición del orden que falla

#### Scenario: Rechazo sin efectos
- **WHEN** el sistema rechaza una reserva por cualquier motivo
- **THEN** el número de reservas almacenadas no cambia
