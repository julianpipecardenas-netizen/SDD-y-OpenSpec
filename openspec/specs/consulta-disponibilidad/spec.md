# Spec

## Purpose

Define cómo un usuario consulta qué partes de un día están ocupadas y cuáles libres en un espacio, para decidir dónde y cuándo reservar.

## Requirements

### Requirement: Consulta de disponibilidad por espacio y fecha
El sistema SHALL permitir a todo usuario autenticado consultar la disponibilidad de un espacio en una fecha. La respuesta MUST incluir los intervalos ocupados por reservas `activa` de ese espacio y fecha, ordenados por hora de inicio, y los intervalos libres que complementan a los ocupados entre las 00:00 y las 23:59. (RF-05)

#### Scenario: Día con reservas
- **WHEN** un usuario consulta un espacio que tiene reservas activas de 08:00 a 10:00 y de 14:00 a 16:00 en la fecha consultada
- **THEN** la respuesta lista como ocupados 08:00-10:00 y 14:00-16:00, y como libres 00:00-08:00, 10:00-14:00 y 16:00-23:59

#### Scenario: Día sin reservas
- **WHEN** un usuario consulta un espacio sin reservas activas en la fecha consultada
- **THEN** la respuesta no lista intervalos ocupados y lista como libre 00:00-23:59

#### Scenario: Reservas contiguas
- **WHEN** el espacio tiene reservas activas de 08:00 a 10:00 y de 10:00 a 12:00 en la fecha consultada
- **THEN** la respuesta lista como libres 00:00-08:00 y 12:00-23:59, sin un intervalo libre de duración cero entre las dos reservas

### Requirement: Solo las reservas activas ocupan
Los intervalos ocupados MUST derivarse únicamente de reservas en estado `activa`. Una reserva cancelada MUST NOT aparecer como ocupada y su horario MUST contarse como libre. (RF-05)

#### Scenario: Reserva cancelada
- **WHEN** el espacio tiene una reserva `cancelada` de 10:00 a 12:00 y ninguna otra en la fecha consultada
- **THEN** el intervalo 10:00-12:00 aparece como libre

### Requirement: Disponibilidad consistente con la creación
La disponibilidad devuelta MUST coincidir con lo que el sistema acepta al crear reservas: un horario completamente contenido en un intervalo libre MUST poder reservarse, y un horario que se solape con un intervalo ocupado MUST ser rechazado. (RF-05, RF-04)

#### Scenario: Reservar un intervalo libre informado
- **WHEN** un usuario reserva un horario completamente contenido en un intervalo que la consulta informó como libre, en una fecha futura
- **THEN** el sistema crea la reserva

#### Scenario: Reservar sobre un intervalo ocupado informado
- **WHEN** un usuario reserva un horario que se solapa con un intervalo que la consulta informó como ocupado
- **THEN** el sistema responde `CONFLICTO_HORARIO`

### Requirement: Privacidad de las reservas ajenas
Para estudiantes y docentes, los intervalos ocupados MUST mostrar solo hora de inicio y hora de fin, sin identificar a quién pertenece cada reserva. Para el administrador, cada intervalo ocupado MUST incluir además el identificador de la reserva y el usuario que la hizo (supuesto P13). (RF-05)

#### Scenario: Estudiante consulta disponibilidad
- **WHEN** un estudiante consulta la disponibilidad de un espacio con reservas de otros usuarios
- **THEN** los intervalos ocupados no incluyen identificador de reserva ni datos del usuario

#### Scenario: Administrador consulta disponibilidad
- **WHEN** el administrador consulta la disponibilidad de un espacio con reservas activas
- **THEN** cada intervalo ocupado incluye el identificador de la reserva y el usuario que la hizo

### Requirement: Validación de la consulta
La consulta MUST rechazarse si la fecha falta o no es un día calendario válido (`DATOS_INVALIDOS`), si el espacio no existe (`ESPACIO_NO_ENCONTRADO`) o si el espacio está inactivo para un estudiante o docente (`ESPACIO_INACTIVO`). La consulta de fechas pasadas SHALL estar permitida. (RF-05)

#### Scenario: Fecha inválida
- **WHEN** un usuario consulta con la fecha 2030-13-01
- **THEN** el sistema responde `DATOS_INVALIDOS`

#### Scenario: Espacio inexistente
- **WHEN** un usuario consulta la disponibilidad de un identificador de espacio que no existe
- **THEN** el sistema responde `ESPACIO_NO_ENCONTRADO`

#### Scenario: Espacio inactivo para un estudiante
- **WHEN** un estudiante consulta la disponibilidad de un espacio inactivo
- **THEN** el sistema responde `ESPACIO_INACTIVO`

#### Scenario: Fecha pasada
- **WHEN** un usuario consulta la disponibilidad de una fecha anterior a hoy
- **THEN** el sistema devuelve los intervalos ocupados y libres de esa fecha

### Requirement: Tiempo de respuesta
En uso normal, con hasta 1000 reservas activas en el espacio consultado, la consulta de disponibilidad MUST responder en menos de 2 segundos. (RNF-05)

#### Scenario: Espacio con muchas reservas
- **WHEN** se consulta la disponibilidad de un espacio que tiene 1000 reservas activas repartidas en distintas fechas
- **THEN** la respuesta se obtiene en menos de 2 segundos
