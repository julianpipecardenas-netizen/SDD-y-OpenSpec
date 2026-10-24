# Spec Delta

## Purpose

Definir el límite de duración para cada reserva individual de un espacio académico.

## ADDED Requirements

### Requirement: Duración máxima individual
El sistema MUST rechazar cualquier reserva individual cuya duración sea superior a cuatro horas, con el código `DURACION_RESERVA_EXCEDIDA`. Una reserva de exactamente cuatro horas o menos MUST ser aceptada si cumple las demás reglas de negocio. El límite MUST aplicarse a cada reserva por separado y MUST NOT acumular las duraciones de reservas de días anteriores.

#### Scenario: Menos de cuatro horas
- **WHEN** un usuario solicita una reserva individual de tres horas y cincuenta y nueve minutos
- **THEN** esta regla no rechaza la reserva por su duración

#### Scenario: Cuatro horas exactas
- **WHEN** un usuario solicita una reserva individual de exactamente cuatro horas
- **THEN** esta regla permite continuar con las demás validaciones

#### Scenario: Más de cuatro horas
- **WHEN** un usuario solicita una reserva individual de cuatro horas y un minuto
- **THEN** el sistema rechaza la solicitud con `DURACION_RESERVA_EXCEDIDA` y no crea ninguna reserva

#### Scenario: Las horas de días anteriores no se acumulan
- **WHEN** un estudiante hizo una reserva de cuatro horas en un día anterior y solicita una reserva válida de cuatro horas para otra fecha
- **THEN** la reserva nueva no se rechaza por la duración de la reserva anterior
