# Design

## Context

La creación de reservas ejecuta validadores independientes en orden. La nueva regla debe limitar la duración de una sola reserva sin alterar la lógica de conflicto ni sumar reservas de días distintos.

## Goals / Non-Goals

- Goal: rechazar una reserva individual cuya duración sea superior a cuatro horas.
- Goal: permitir una duración exactamente igual a cuatro horas.
- Goal: usar un error de dominio estable y probar la regla sin base de datos.
- Non-Goal: acumular reservas de varios días o limitar el total semanal de un usuario.

## Decisions

1. La duración se calcula como `hora_fin - hora_inicio` después de validar que ambas horas están bien formadas y que la hora final es posterior a la inicial.
2. Se compara contra `timedelta(hours=4)`; solo una duración estrictamente superior se rechaza.
3. Se añade `validar_duracion_maxima` como función independiente y se registra después de la validación de espacio y de pasado, pero antes del conflicto de horario. Así se conserva el orden relativo de los validadores existentes.
4. El código de error es `DURACION_RESERVA_EXCEDIDA`, con el mensaje «La duración máxima de una reserva es de cuatro horas.»
5. La regla se aplica a cada solicitud individual. No consulta ni suma reservas anteriores.

## Risks / Trade-offs

- La regla es de duración, no de horario de apertura; una reserva de cuatro horas puede empezar a cualquier hora futura válida si no entra en conflicto con otra.
- La duración se mide con precisión de minutos, conforme a las especificaciones existentes.

## Verification

- Pruebas unitarias para duración menor, exacta y superior a cuatro horas.
- Pruebas de servicio para comprobar que cuatro horas se aceptan y que una duración superior se rechaza sin crear registros.
- Ejecutar `pytest`, `python src/manage.py check`, `python src/manage.py makemigrations --check --dry-run` y `openspec validate --strict`.
