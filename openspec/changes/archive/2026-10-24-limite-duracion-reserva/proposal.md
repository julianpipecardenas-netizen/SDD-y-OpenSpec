# Proposal

## Why

La institución necesita limitar el tiempo que se puede reservar en una sola solicitud para que un estudiante no monopolice un espacio durante una jornada.

## What Changes

- Cada reserva individual tendrá una duración máxima de cuatro horas.
- Una reserva de exactamente cuatro horas será válida; una de más de cuatro horas se rechazará con `DURACION_RESERVA_EXCEDIDA`.
- El límite se aplica a cada reserva y no acumula horas de fechas anteriores ni de otros días.

## Capabilities

### New Capabilities
- `limite-duracion-reserva`: límite de duración para una reserva individual.

### Modified Capabilities
Ninguna. El límite se documenta como una capacidad nueva y se añade como validador independiente al flujo de creación.

## Impact

- Código: se incorpora un validador independiente en `src/reservas/services/validadores.py` y un código de error de dominio.
- Pruebas: se cubren duraciones inferiores, exactamente iguales y superiores a cuatro horas, tanto en el validador como en el servicio.
- Documentación: se conserva la propuesta, el diseño y las tareas de este cambio; el cambio inicial queda archivado con sus seis especificaciones sincronizadas en `openspec/specs/`.
