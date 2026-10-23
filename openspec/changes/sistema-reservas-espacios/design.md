# Design

## Context

Proyecto nuevo, sin código previo. Las decisiones de arquitectura y stack ya están justificadas en `PLAN_INGENIERIA.md` (secciones 7.1 a 7.5) y este diseño no las reabre: monolito modular en capas, Python con Django, SQLite, pytest y validadores de reglas independientes. Aquí se define **cómo** se aplican a las specs de este cambio. La motivación está en `proposal.md`; los requisitos, en `specs/`.

Restricciones heredadas del plan: zona horaria única America/Bogota (S4), reservas dentro de un mismo día (S2), reglas de negocio extensibles (S5, RNF-01), cada regla probable de forma aislada (RNF-02).

## Goals / Non-Goals

**Goals:**
- Que cada regla de negocio de las specs viva en un único lugar, separada de la interfaz y de la base de datos.
- Que un escenario de las specs se traduzca de forma directa en al menos una prueba automatizada.
- Que una regla nueva (como la de la Fase 4) se agregue sin modificar las reglas existentes.

**Non-Goals:**
- API pública para terceros, interfaz pulida o diseño visual elaborado.
- Despliegue en producción, alta disponibilidad o base de datos distinta de SQLite.
- Auto-registro de usuarios, recuperación de contraseña y reservas recurrentes.

## Decisions

### D1. Capas y estructura del código
Tres capas dentro de la aplicación `reservas`: **presentación** (vistas y plantillas, sin reglas de negocio), **servicios** (casos de uso y reglas) y **acceso a datos** (modelos y consultas). Las vistas solo traducen la petición en una llamada a un servicio y el resultado o el error de dominio en una respuesta.
- *Alternativa descartada:* reglas en las vistas o en los modelos (`save()`); mezclarían capas y harían las reglas difíciles de probar sin interfaz (RNF-01, RNF-02).

Estructura (consistente con PLAN 13): `src/manage.py`, `src/config/` (configuración del proyecto), `src/reservas/` con `models.py`, `services/` y `views.py`, y `tests/` en la raíz.

### D2. Interfaz: vistas de servidor con sesión
Aplicación web con plantillas de Django y autenticación por sesión. Cada error de dominio se muestra con su código y mensaje, y se responde con un estado HTTP coherente (401 `NO_AUTENTICADO`, 403 `SIN_PERMISO`, 404 `*_NO_ENCONTRAD*`, 409 conflictos y estados incompatibles, 422 datos o reglas de entrada). Esto mantiene verificables los códigos de las specs desde las pruebas de integración.
- *Alternativa descartada:* API JSON con frontend separado; añade una segunda aplicación sin que el alcance lo exija.

### D3. Modelo de datos y restricciones en base de datos
Se siguen las entidades del plan (7.3), con los campos que las specs hacen necesarios:
- **Usuario:** modelo de usuario propio con correo único como identificador de acceso, nombre y `rol` (`estudiante`, `docente`, `administrador`). Se define desde el inicio porque cambiarlo después es costoso. Contraseñas con el hash por defecto del framework (RNF-04).
- **Espacio:** nombre (único sin distinguir mayúsculas), tipo, capacidad, `activo`.
- **Reserva:** usuario, espacio, `fecha`, `hora_inicio`, `hora_fin`, `estado` (`activa` o `cancelada`), `creada_en`, `cancelada_en` y `cancelada_por` (nulos hasta cancelar).
- Restricciones en base de datos (PLAN 7.3): `hora_fin > hora_inicio`, `capacidad > 0`, nombre único insensible a mayúsculas y claves foráneas protegidas para que no se borren espacios ni usuarios con reservas (`ESPACIO_CON_RESERVAS`). Un índice sobre espacio, fecha y estado sostiene la consulta de disponibilidad (RNF-05).
- Fecha y horas se guardan como fecha y hora locales, sin conversión, porque hay una sola zona horaria (S4). Los instantes de auditoría (`creada_en`, `cancelada_en`) usan la zona America/Bogota.

### D4. Reglas como validadores independientes (PLAN 7.4)
Cada regla de creación de reserva es una función independiente que recibe un contexto inmutable (datos solicitados, espacio, reservas existentes y hora actual) y no devuelve nada si se cumple o lanza un error de dominio si no. El servicio de reservas las ejecuta en el orden fijado por la spec `creacion-reservas`:
datos obligatorios → rango horario → espacio existente y activo → reserva en el pasado → conflicto de horario.
Agregar una regla significa escribir una función nueva y registrarla en la lista ordenada; las existentes no se modifican. La spec de cada regla se prueba con pruebas unitarias sin base de datos ni sesión (RNF-02).
- *Alternativa descartada:* un único método con condicionales encadenados; cada regla nueva obligaría a editar código ya probado.

### D5. Errores de dominio (PLAN 7.5)
Un único tipo de error de dominio con `codigo` y `mensaje`. Los códigos son exactamente los de las specs: `CREDENCIALES_INVALIDAS`, `NO_AUTENTICADO`, `SIN_PERMISO`, `DATOS_INVALIDOS`, `HORARIO_INVALIDO`, `RESERVA_EN_PASADO`, `CONFLICTO_HORARIO`, `ESPACIO_NO_ENCONTRADO`, `ESPACIO_INACTIVO`, `ESPACIO_DUPLICADO`, `ESPACIO_CON_RESERVAS`, `RESERVA_NO_ENCONTRADA`, `RESERVA_YA_CANCELADA`, `RESERVA_NO_CANCELABLE`. Las pruebas comprueban el código, no el texto, salvo el mensaje de `CONFLICTO_HORARIO` que la spec fija.

### D6. Control de acceso
La autenticación se exige en la capa de presentación; la autorización por rol se aplica en los servicios, no solo en las vistas, para que la regla no dependa de la interfaz. Los servicios reciben al usuario que actúa como parámetro.

### D7. Solapamiento y concurrencia
La regla de solapamiento compara rangos semiabiertos: hay conflicto si `inicio_nuevo < fin_existente` **y** `inicio_existente < fin_nuevo`, solo contra reservas `activa` del mismo espacio y fecha. SQLite no ofrece restricciones de exclusión para rangos, así que la garantía de la spec «solicitudes simultáneas» se obtiene ejecutando la comprobación y la inserción dentro de una misma transacción que tome el bloqueo de escritura antes de comprobar (transacción inmediata). La forma exacta de configurarlo se verifica contra la versión de Django instalada y queda cubierta por una prueba de concurrencia con hilos.
- *Alternativa descartada:* comprobar y luego insertar sin transacción; deja una ventana de carrera en la que dos reservas solapadas quedarían activas.

### D8. Disponibilidad
Se consultan las reservas `activa` del espacio y la fecha ordenadas por inicio y se calcula el complemento recorriendo un cursor desde las 00:00 hasta las 23:59: cada hueco entre el cursor y el inicio de la siguiente reserva es un intervalo libre. Las reservas contiguas no producen intervalos de duración cero. El resultado de privacidad (P13) se decide en el servicio según el rol, no en la plantilla.

### D9. Tiempo como dependencia
Los servicios reciben la hora actual como parámetro, con el reloj real como valor por defecto. Así las pruebas de `RESERVA_EN_PASADO` y de cancelación de reservas que ya comenzaron son deterministas.

### D10. Pruebas y trazabilidad
Estructura de `tests/` por capacidad. Cada prueba lleva en su docstring la referencia `Spec: <capacidad> / <requisito> / <escenario>`, de modo que la tabla requisito → spec → código → prueba de `INFORME_FINAL.md` pueda generarse y revisarse. Niveles: unitarias de validadores sin base de datos, pruebas de servicios con base de datos y pruebas de integración por las vistas. Casos especiales: concurrencia con hilos (D7) y rendimiento con 1000 reservas (RNF-05).

### D11. Usuarios iniciales (P7)
Los usuarios se crean desde el panel de administración del framework y una orden de gestión documentada en el README para el primer administrador. No hay pantalla de registro.

## Risks / Trade-offs

- **Supuestos P1 a P13 sin confirmar** → se resuelven en la Fase 2 antes de implementar; cada cambio de supuesto se refleja en las specs y en este diseño en el mismo commit `spec:`.
- **La verificación de concurrencia en SQLite puede ser frágil** (bloqueos de base de datos entre hilos) → prueba dedicada con un archivo de base de datos real y reintento acotado; si no se logra de forma estable, se documenta la limitación en `INFORME_FINAL.md`.
- **Códigos HTTP elegidos por convención** (D2) pueden no coincidir con lo que espere el docente → son una decisión de presentación; las specs solo exigen el código de dominio.
- **Modelo de usuario propio** no se puede cambiar fácilmente después → se fija en la primera tarea de implementación.
- **Más capas que un CRUD simple** → es el costo aceptado en el plan para poder cambiar reglas sin afectar otras capas (RNF-01).
- **Validadores con contexto compartido** pueden crecer en parámetros → se mantiene el contexto como un objeto único y se revisa cada vez que se añada una regla nueva.

## Open Questions

- Estilo visual y textos exactos de las plantillas: se resuelven durante la implementación sin afectar las specs.
- Versión exacta de Python y de Django: se fija al crear el entorno y se documenta en el README.
