# Proposal

## Why

La institución asigna hoy los espacios académicos de forma manual o informal, lo que produce dobles reservas, poca visibilidad de la disponibilidad y ninguna trazabilidad de quién reservó qué. Esta propuesta formaliza, como especificaciones verificables, el alcance de la versión 1 definido en `PLAN_INGENIERIA.md` (objetivos 1 a 5, requisitos RF-01 a RF-07), antes de escribir cualquier código.

## What Changes

- Se introduce un sistema de reserva de espacios académicos con autenticación y tres roles: estudiante, docente y administrador.
- El administrador gestiona el catálogo de espacios (crear, consultar, editar, activar y desactivar).
- Los usuarios autenticados crean reservas con fecha, hora de inicio y hora de fin sobre un espacio activo.
- El sistema rechaza reservas que se solapen con otra reserva activa del mismo espacio; las reservas contiguas (el fin de una es el inicio de otra) están permitidas.
- Los usuarios consultan la disponibilidad de un espacio por fecha.
- Los usuarios consultan y cancelan sus propias reservas; el administrador consulta y cancela cualquiera. La cancelación es lógica y conserva el registro.
- Las reglas de negocio fallidas devuelven errores de dominio con código y mensaje claros (PLAN 7.5).
- Fuera de alcance, según el plan: pagos, notificaciones, integraciones externas, app móvil nativa y reservas recurrentes.

## Capabilities

### New Capabilities
- `autenticacion-roles`: inicio y cierre de sesión, identificación del rol y control de acceso por rol (RF-01, RNF-04).
- `gestion-espacios`: catálogo de espacios académicos administrado solo por el administrador (RF-02).
- `creacion-reservas`: creación de reservas con validación de datos de entrada y estado inicial (RF-03).
- `validacion-conflictos-horario`: regla de no solapamiento de reservas sobre un mismo espacio (RF-04, RNF-01, RNF-02).
- `consulta-disponibilidad`: consulta de los intervalos ocupados y libres de un espacio en una fecha (RF-05, RNF-05).
- `consulta-cancelacion-reservas`: listado y cancelación lógica de reservas propias, y de cualquiera para el administrador (RF-06, RF-07).

### Modified Capabilities

Ninguna. Es el primer cambio del proyecto y `openspec/specs/` está vacío.

## Trazabilidad con el plan

| Requisito del plan | Capacidad (spec) |
|---|---|
| RF-01 | `autenticacion-roles` |
| RF-02 | `gestion-espacios` |
| RF-03 | `creacion-reservas` |
| RF-04 | `validacion-conflictos-horario` |
| RF-05 | `consulta-disponibilidad` |
| RF-06, RF-07 | `consulta-cancelacion-reservas` |
| RNF-01, RNF-02 | `validacion-conflictos-horario` (reglas aisladas y verificables) y `design.md` |
| RNF-03 | tareas de documentación en `tasks.md` (README) |
| RNF-04 | `autenticacion-roles` |
| RNF-05 | `consulta-disponibilidad` |

## Preguntas abiertas (para la Fase 2)

Cada punto es una ambigüedad que el plan no resuelve. Las specs usan el **supuesto provisional** indicado; el estudiante debe confirmarlo o cambiarlo durante la revisión, antes de implementar.

| # | Pregunta | Supuesto provisional en las specs |
|---|---|---|
| P1 | ¿En qué se diferencian estudiante y docente? El plan dice "igual que estudiante". | Permisos idénticos. |
| P2 | ¿Se puede reservar en el pasado? | No: el inicio debe ser posterior al instante actual. |
| P3 | ¿Hay granularidad mínima de horario (bloques de 30 min, 1 h)? | No hay restricción; se acepta precisión de minutos. |
| P4 | ¿Qué pasa con las reservas futuras de un espacio que se desactiva? | Se conservan activas; solo se bloquean reservas nuevas. |
| P5 | ¿Se puede cancelar una reserva que ya empezó o terminó? | No: solo reservas activas que aún no han comenzado. |
| P6 | ¿Hay un horario de funcionamiento (por ejemplo 06:00 a 22:00)? | No; solo se exige que la reserva no cruce la medianoche (S2). |
| P7 | ¿Cómo se crean los usuarios? El plan no incluye registro. | Los crea el administrador; el auto-registro queda fuera de alcance. |
| P8 | ¿La capacidad del espacio restringe algo en la reserva? | No; es un dato informativo del espacio. |
| P9 | ¿Hay un tope de reservas activas por usuario? | No hay tope. |
| P10 | ¿Puede el administrador reservar en nombre de otro usuario? | No; cada reserva pertenece a quien la crea. |
| P11 | ¿Las reservas contiguas (fin = inicio) cuentan como conflicto? | No: se permiten (intervalos semiabiertos). |
| P12 | ¿Un mismo usuario puede tener reservas simultáneas en espacios distintos? | Sí; solo se prohíbe el solapamiento dentro de un mismo espacio. |
| P13 | ¿Qué información de las reservas ajenas ve un estudiante o docente en la disponibilidad? | Solo el intervalo; el administrador ve además reserva y usuario. |

## Impact

- **Código:** aplicación nueva (greenfield); no existe código previo.
- **Datos:** entidades Usuario, Espacio y Reserva (PLAN 7.3); la cancelación es lógica.
- **Documentos:** `README.md` (RNF-03) e `INFORME_FINAL.md` en fases posteriores.
- **Dependencias:** las definidas en el plan (7.2); las specs no las nombran para mantenerse independientes de la implementación.
