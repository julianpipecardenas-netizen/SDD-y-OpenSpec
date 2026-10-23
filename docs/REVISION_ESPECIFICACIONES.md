# Revisión de especificaciones (Fase 2)

**Cambio revisado:** `sistema-reservas-espacios` (OpenSpec)
**Fecha de la revisión:** 2026-10-23
**Documento de referencia:** `PLAN_INGENIERIA.md`
**Alcance:** `proposal.md`, 6 specs (32 requisitos, 82 escenarios), `design.md` y `tasks.md` (41 tareas)

> Las especificaciones se redactaron con ayuda de un agente de IA a partir del plan. Esta revisión registra lo que se comprobó, lo que se corrigió y las decisiones tomadas por el estudiante antes de implementar.

## 1. Comprobaciones realizadas

| Comprobación | Resultado |
|---|---|
| Formato válido según OpenSpec (`openspec validate --strict`) | Correcto |
| Cada RF (01 a 07) y RNF (01 a 05) del plan tiene al menos una capacidad que lo cubre | Correcto (ver tabla en `proposal.md`) |
| Cada requisito tiene al menos un escenario verificable | Correcto |
| Los códigos de error de las specs coinciden con los de `design.md` (D5) | Correcto, sin diferencias |
| El diseño respeta las decisiones del plan (monolito en capas, Django, SQLite, pytest, validadores independientes) | Correcto, sin contradicciones |
| Las specs no incluyen funcionalidades fuera del alcance del plan | Correcto |
| Cada tarea de `tasks.md` indica su verificación y trae sus propias pruebas | Correcto |

## 2. Inconsistencias y problemas encontrados

| # | Hallazgo | Dónde | Corrección |
|---|---|---|---|
| H1 | Un espacio inactivo se trataba distinto al consultarlo por identificador (`gestion-espacios`) y al consultar su disponibilidad (`consulta-disponibilidad`); el primero lo ocultaba y el segundo devolvía `ESPACIO_INACTIVO` | `gestion-espacios`, `consulta-disponibilidad` | Se unificó: estudiantes y docentes reciben `ESPACIO_INACTIVO` en ambos casos; se añadió el escenario «Estudiante consulta un espacio inactivo» |
| H2 | Varias validaciones podían fallar a la vez y el código devuelto no estaba definido | `creacion-reservas`, `consulta-cancelacion-reservas` | Se fijó un orden de validación en ambas capacidades, con un escenario que lo verifica |
| H3 | El plan no define el límite del día para los intervalos libres | `consulta-disponibilidad` | Se fijó el rango 00:00 a 23:59, coherente con que una reserva no cruza la medianoche (S2) |
| H4 | «Solapamiento» no estaba definido para los extremos | `validacion-conflictos-horario` | Se definió con intervalos semiabiertos: fin = inicio no es conflicto (P11) |
| H5 | El plan no cubre las peticiones simultáneas para el mismo horario | `validacion-conflictos-horario`, `design.md` D7 | Se añadió un requisito y una decisión de diseño con prueba de concurrencia |
| H6 | RNF-05 («tiempo razonable») no era verificable | `consulta-disponibilidad` | Se concretó: 1000 reservas activas, respuesta en menos de 2 segundos |
| H7 | No estaba claro qué le pasa a una reserva cuando su espacio se desactiva | `gestion-espacios` | Se definió: las reservas activas se conservan, solo se bloquean las nuevas (P4) |

## 3. Preguntas abiertas y decisiones

Las 13 preguntas de `proposal.md` quedaron resueltas. El estudiante **confirmó todos los supuestos provisionales** sin cambios.

| # | Pregunta | Decisión | Justificación |
|---|---|---|---|
| P1 | ¿Diferencia entre estudiante y docente? | Permisos idénticos | El plan (sección 5) dice «igual que estudiante»; evita reglas no pedidas |
| P2 | ¿Reservar en el pasado? | No | Una reserva en el pasado no tiene utilidad y rompe la consistencia de la disponibilidad |
| P3 | ¿Granularidad mínima del horario? | Sin restricción (minutos) | El plan no la exige; simplifica la validación |
| P4 | ¿Reservas de un espacio que se desactiva? | Se conservan activas | Evita cancelaciones masivas no pedidas |
| P5 | ¿Cancelar una reserva que ya empezó? | No | Una reserva iniciada ya consumió su horario; conserva la trazabilidad |
| P6 | ¿Horario de funcionamiento? | No hay | Fuera del alcance del plan; solo aplica S2 |
| P7 | ¿Cómo se crean los usuarios? | Los crea el administrador | El plan no incluye registro |
| P8 | ¿La capacidad restringe la reserva? | No, es informativa | No hay número de asistentes en el modelo |
| P9 | ¿Tope de reservas por usuario? | Sin tope | No está en el plan |
| P10 | ¿Reservar en nombre de otro? | No | Mantiene la reserva ligada a quien la crea (S1) |
| P11 | ¿Reservas contiguas como conflicto? | No hay conflicto | Permite aprovechar el espacio sin huecos artificiales |
| P12 | ¿Reservas simultáneas del mismo usuario en espacios distintos? | Permitidas | Solo se prohíbe el solapamiento dentro de un mismo espacio (RF-04) |
| P13 | ¿Qué ven los estudiantes de las reservas ajenas? | Solo el intervalo | Protege la privacidad; el administrador ve más |

## 4. Resultado

- Las especificaciones son consistentes entre sí y con `PLAN_INGENIERIA.md`.
- No quedan ambigüedades sin resolver ni contradicciones conocidas.
- Las tareas de implementación están definidas en `tasks.md`, ordenadas por dependencia.
- **Se autoriza la implementación (Fase 3)**, empezando por la tarea 1.1.

## 5. Limitaciones conocidas de esta revisión

- Se comprobó la consistencia por lectura y con comprobaciones automáticas de formato y de códigos; ninguna spec se ha ejecutado todavía contra código.
- La prueba de concurrencia sobre SQLite puede resultar frágil; se evaluará en la tarea 5.4 y, si no es estable, se documentará en `INFORME_FINAL.md`.
- Las decisiones de código HTTP (design D2) son una convención de presentación y pueden ajustarse sin cambiar las specs.
