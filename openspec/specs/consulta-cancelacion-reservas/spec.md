# Spec

## Purpose

Define cómo los usuarios consultan y cancelan sus reservas, cómo el administrador opera sobre las de cualquier usuario y cómo se conserva la trazabilidad de lo cancelado.

## Requirements

### Requirement: Listado de reservas propias
Todo usuario autenticado SHALL poder listar sus reservas, tanto `activa` como `cancelada`. El listado MUST estar ordenado por fecha y hora de inicio, e indicar para cada reserva el espacio, la fecha, el rango horario y el estado. Un estudiante o docente MUST NOT ver reservas de otros usuarios. (RF-06)

#### Scenario: Usuario con reservas
- **WHEN** un estudiante con una reserva activa y una cancelada lista sus reservas
- **THEN** el listado incluye ambas, cada una con su estado, ordenadas por fecha y hora de inicio

#### Scenario: Aislamiento entre usuarios
- **WHEN** un estudiante lista sus reservas y existen reservas de otros usuarios
- **THEN** el listado contiene únicamente las reservas del estudiante

#### Scenario: Usuario sin reservas
- **WHEN** un usuario sin reservas lista las suyas
- **THEN** el sistema devuelve un listado vacío sin error

### Requirement: Consulta de una reserva
Todo usuario autenticado SHALL poder consultar el detalle de una reserva propia por su identificador. Un estudiante o docente que consulte una reserva ajena MUST recibir `SIN_PERMISO`; si la reserva no existe, MUST recibir `RESERVA_NO_ENCONTRADA`. (RF-06)

#### Scenario: Reserva propia
- **WHEN** un docente consulta una reserva suya por identificador
- **THEN** el sistema devuelve su espacio, fecha, rango horario, estado y fecha de creación

#### Scenario: Reserva ajena
- **WHEN** un estudiante consulta por identificador una reserva de otro usuario
- **THEN** el sistema responde `SIN_PERMISO` y no devuelve sus datos

#### Scenario: Reserva inexistente
- **WHEN** un usuario consulta un identificador de reserva que no existe
- **THEN** el sistema responde `RESERVA_NO_ENCONTRADA`

### Requirement: Consulta total para el administrador
El administrador SHALL poder listar todas las reservas del sistema y consultar cualquiera por identificador. Cada reserva MUST indicar el usuario que la hizo. (RF-07)

#### Scenario: Administrador lista todo
- **WHEN** el administrador lista las reservas y existen reservas de varios usuarios
- **THEN** el listado incluye las reservas de todos, cada una con el usuario que la hizo

#### Scenario: Administrador consulta una reserva ajena
- **WHEN** el administrador consulta por identificador una reserva de un estudiante
- **THEN** el sistema devuelve el detalle de la reserva

### Requirement: Cancelación de una reserva
El sistema SHALL permitir a un usuario cancelar sus propias reservas y al administrador cancelar cualquiera. Solo MUST poder cancelarse una reserva `activa` cuyo inicio aún no haya llegado (supuesto P5). Cancelar MUST cambiar el estado a `cancelada` y registrar la fecha y hora de cancelación y quién la canceló; la reserva MUST NOT borrarse. (RF-06, RF-07)

#### Scenario: Usuario cancela su reserva
- **WHEN** un estudiante cancela una reserva activa suya que comienza en el futuro
- **THEN** la reserva queda en estado `cancelada` con fecha de cancelación y el usuario que canceló, y sigue apareciendo en su listado

#### Scenario: Administrador cancela una reserva ajena
- **WHEN** el administrador cancela una reserva activa futura de un estudiante
- **THEN** la reserva queda `cancelada` y se registra al administrador como quien canceló

#### Scenario: Cancelar una reserva ajena sin ser administrador
- **WHEN** un estudiante intenta cancelar una reserva de otro usuario
- **THEN** el sistema responde `SIN_PERMISO` y la reserva sigue `activa`

#### Scenario: Reserva ya cancelada
- **WHEN** un usuario cancela una reserva que ya está `cancelada`
- **THEN** el sistema responde `RESERVA_YA_CANCELADA` y no modifica el registro

#### Scenario: Reserva que ya comenzó
- **WHEN** un usuario intenta cancelar una reserva cuyo inicio ya pasó
- **THEN** el sistema responde `RESERVA_NO_CANCELABLE` y la reserva sigue `activa`

#### Scenario: Reserva inexistente
- **WHEN** un usuario intenta cancelar un identificador de reserva que no existe
- **THEN** el sistema responde `RESERVA_NO_ENCONTRADA`

### Requirement: Orden de validación al cancelar
El sistema SHALL evaluar la cancelación en este orden y detenerse en la primera condición que falle: autenticación, existencia de la reserva, permiso sobre la reserva, estado `activa` y, por último, que el inicio no haya llegado.

#### Scenario: Reserva ajena y ya cancelada
- **WHEN** un estudiante intenta cancelar una reserva cancelada que pertenece a otro usuario
- **THEN** el sistema responde `SIN_PERMISO`, que es la primera condición del orden que falla

### Requirement: La cancelación libera el horario
Una reserva cancelada MUST dejar de ocupar su horario: el mismo espacio y rango MUST poder reservarse de nuevo y MUST aparecer como libre en la disponibilidad. (RF-04, RF-05)

#### Scenario: Reutilizar un horario cancelado
- **WHEN** se cancela una reserva activa de 10:00 a 12:00 y luego otro usuario solicita ese mismo espacio, fecha y horario
- **THEN** el sistema crea la nueva reserva
