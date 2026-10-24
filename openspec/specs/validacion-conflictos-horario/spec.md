# Spec

## Purpose

Define la regla que impide que dos reservas activas ocupen el mismo espacio en horarios que se solapan, incluyendo sus casos límite y su comportamiento ante peticiones simultáneas.

## Requirements

### Requirement: No solapamiento de reservas activas
El sistema MUST rechazar una reserva nueva si existe otra reserva en estado `activa` sobre el mismo espacio y la misma fecha cuyo rango se solape con el rango solicitado. Dos rangos se solapan si y solo si el inicio de cada uno es anterior al fin del otro. El rechazo MUST usar el código `CONFLICTO_HORARIO` con el mensaje "El espacio ya está reservado en ese horario". (RF-04)

#### Scenario: Solapamiento parcial por el final
- **WHEN** existe una reserva activa de 10:00 a 12:00 y un usuario solicita 11:00 a 13:00 en el mismo espacio y fecha
- **THEN** el sistema responde `CONFLICTO_HORARIO` y no crea la reserva

#### Scenario: Solapamiento parcial por el inicio
- **WHEN** existe una reserva activa de 10:00 a 12:00 y un usuario solicita 09:00 a 11:00 en el mismo espacio y fecha
- **THEN** el sistema responde `CONFLICTO_HORARIO` y no crea la reserva

#### Scenario: Rango contenido en otro
- **WHEN** existe una reserva activa de 10:00 a 14:00 y un usuario solicita 11:00 a 12:00 en el mismo espacio y fecha
- **THEN** el sistema responde `CONFLICTO_HORARIO` y no crea la reserva

#### Scenario: Rango que contiene a otro
- **WHEN** existe una reserva activa de 11:00 a 12:00 y un usuario solicita 10:00 a 14:00 en el mismo espacio y fecha
- **THEN** el sistema responde `CONFLICTO_HORARIO` y no crea la reserva

#### Scenario: Horario idéntico
- **WHEN** existe una reserva activa de 10:00 a 12:00 y un usuario solicita exactamente 10:00 a 12:00 en el mismo espacio y fecha
- **THEN** el sistema responde `CONFLICTO_HORARIO` y no crea la reserva

#### Scenario: Conflicto con una reserva del mismo usuario
- **WHEN** un usuario ya tiene una reserva activa de 10:00 a 12:00 en un espacio y solicita 11:00 a 13:00 en ese mismo espacio y fecha
- **THEN** el sistema responde `CONFLICTO_HORARIO` y no crea la reserva

### Requirement: Reservas contiguas permitidas
El sistema SHALL aceptar una reserva cuyo inicio coincida con el fin de otra reserva activa del mismo espacio y fecha, o cuyo fin coincida con el inicio de otra. Estos casos MUST NOT considerarse conflicto (supuesto P11). (RF-04)

#### Scenario: Inicio igual al fin de otra reserva
- **WHEN** existe una reserva activa de 10:00 a 12:00 y un usuario solicita 12:00 a 14:00 en el mismo espacio y fecha
- **THEN** el sistema crea la reserva

#### Scenario: Fin igual al inicio de otra reserva
- **WHEN** existe una reserva activa de 10:00 a 12:00 y un usuario solicita 08:00 a 10:00 en el mismo espacio y fecha
- **THEN** el sistema crea la reserva

### Requirement: Ámbito del conflicto
Solo MUST considerarse conflicto el solapamiento con reservas `activa` del mismo espacio y de la misma fecha. Las reservas canceladas, las de otros espacios y las de otras fechas MUST NOT bloquear una reserva nueva. Un mismo usuario puede tener reservas simultáneas en espacios distintos. (RF-04)

#### Scenario: Reserva cancelada no bloquea
- **WHEN** existe una reserva `cancelada` de 10:00 a 12:00 y un usuario solicita 10:00 a 12:00 en el mismo espacio y fecha
- **THEN** el sistema crea la reserva

#### Scenario: Otro espacio, mismo horario
- **WHEN** existe una reserva activa de 10:00 a 12:00 en el espacio A y un usuario solicita 10:00 a 12:00 en el espacio B
- **THEN** el sistema crea la reserva

#### Scenario: Otra fecha, mismo horario
- **WHEN** existe una reserva activa el 2030-03-15 de 10:00 a 12:00 y un usuario solicita 10:00 a 12:00 el 2030-03-16 en el mismo espacio
- **THEN** el sistema crea la reserva

### Requirement: Solicitudes simultáneas
Cuando dos solicitudes simultáneas pidan horarios que se solapan sobre el mismo espacio y fecha, el sistema MUST aceptar como máximo una de ellas. La otra MUST recibir `CONFLICTO_HORARIO`. En ningún caso MUST quedar almacenado un par de reservas activas solapadas. (RF-04)

#### Scenario: Dos usuarios piden el mismo horario a la vez
- **WHEN** dos usuarios envían al mismo tiempo una solicitud para el mismo espacio, fecha y horario libre
- **THEN** exactamente una reserva queda activa y la otra solicitud recibe `CONFLICTO_HORARIO`

### Requirement: Regla verificable de forma aislada
La regla de no solapamiento SHALL poder evaluarse y comprobarse de manera automatizada con solo un conjunto de reservas existentes y un rango solicitado, sin necesidad de una sesión de usuario ni de la interfaz. (RNF-01, RNF-02)

#### Scenario: Evaluación sin interfaz
- **WHEN** se evalúa la regla con un conjunto de reservas y un rango solicitado
- **THEN** la regla indica si hay conflicto sin depender de la interfaz ni de una sesión
