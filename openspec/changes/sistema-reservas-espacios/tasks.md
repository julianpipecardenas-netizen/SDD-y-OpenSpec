# Tasks

> Regla de trabajo (PLAN 10): una tarea a la vez. Al terminar cada una se revisa el diff, se descarta lo que no esté en la spec, se ejecuta `pytest` y se hace un commit (`feat:`, `test:` o `docs:`). Cada prueba cita en su docstring `Spec: <capacidad> / <requisito> / <escenario>` (design D10).

## 1. Preparación del proyecto

- [x] 1.1 Crear el entorno virtual y `requirements.txt` con Django y pytest-django, y verificar que `pip install -r requirements.txt` termina sin errores
- [x] 1.2 Crear el proyecto Django en `src/config/` y la aplicación `src/reservas/` con zona horaria America/Bogota, y verificar que `python src/manage.py check` no reporta problemas
- [x] 1.3 Configurar pytest (`pytest.ini` con la ruta de `src` y los ajustes de Django) con una prueba mínima, y verificar que `pytest` se ejecuta y pasa
- [x] 1.4 Redactar la sección inicial del `README.md` (instalación y ejecución de servidor y pruebas, RNF-03) y verificar que los comandos documentados funcionan tal como están escritos

## 2. Autenticación y roles (`autenticacion-roles`)

- [x] 2.1 Implementar el error de dominio con `codigo` y `mensaje` y la lista de códigos de design D5, y verificar con pruebas unitarias que cada código existe y que el error expone ambos campos
- [x] 2.2 Crear el modelo de usuario propio (correo único, nombre y `rol` con los tres valores) con su migración, y verificar con pruebas los escenarios «Usuario con un único rol» y «Contraseña no recuperable» (requisitos «Roles reconocidos» y «Contraseñas protegidas»)
- [x] 2.3 Implementar el servicio de inicio y cierre de sesión, y verificar con pruebas los escenarios de credenciales válidas, contraseña incorrecta y correo no registrado (mismo código y mismo mensaje en los dos últimos)
- [x] 2.4 Implementar la exigencia de autenticación y la comprobación de rol en los servicios (design D6), y verificar con pruebas los escenarios `NO_AUTENTICADO` y «Estudiante y docente tienen los mismos permisos»
- [x] 2.5 Crear las vistas y plantillas de inicio y cierre de sesión, y verificar con pruebas de integración que tras cerrar sesión la siguiente petición protegida responde `NO_AUTENTICADO` y que ninguna respuesta incluye la contraseña
- [x] 2.6 Añadir la orden de gestión para crear el primer administrador (design D11), documentarla en el `README.md` y verificar que, siguiendo el README, se puede iniciar sesión como administrador

## 3. Gestión de espacios (`gestion-espacios`)

- [ ] 3.1 Crear el modelo `Espacio` con sus restricciones (nombre único sin distinguir mayúsculas, capacidad mayor que cero, tipos permitidos), y verificar con pruebas que la base de datos rechaza duplicados y capacidades inválidas
- [ ] 3.2 Implementar el servicio para crear y editar espacios restringido al administrador, y verificar con pruebas los escenarios de espacio válido, `ESPACIO_DUPLICADO`, capacidad inválida, tipo no permitido y `SIN_PERMISO`
- [ ] 3.3 Implementar la activación y desactivación de espacios, y verificar con pruebas los escenarios «Desactivar un espacio» y «Reactivar un espacio»
- [ ] 3.4 Implementar el listado y la consulta de espacios según el rol, y verificar con pruebas los escenarios de estudiante, administrador, `ESPACIO_NO_ENCONTRADO` y `ESPACIO_INACTIVO`
- [ ] 3.5 Crear las vistas y plantillas de espacios, y verificar con pruebas de integración que el administrador gestiona espacios y que un docente recibe `SIN_PERMISO`

## 4. Creación de reservas (`creacion-reservas`)

- [ ] 4.1 Crear el modelo `Reserva` con estado, fechas de auditoría, restricción `hora_fin > hora_inicio` e índice sobre espacio, fecha y estado, y verificar con una prueba que la base de datos rechaza un rango invertido
- [ ] 4.2 Implementar la eliminación de espacios bloqueada cuando tienen reservas, y verificar con pruebas los escenarios `ESPACIO_CON_RESERVAS` y «Reservas existentes se conservan» al desactivar
- [ ] 4.3 Implementar el marco de validadores (contexto, lista ordenada, reloj inyectable, design D4 y D9), y verificar con una prueba unitaria que se ejecutan en orden y que se detiene en la primera falla
- [ ] 4.4 Implementar los validadores de datos obligatorios y de rango horario, y verificar con pruebas unitarias los escenarios `DATOS_INVALIDOS` (dato ausente, fecha inexistente, hora fuera de rango) y `HORARIO_INVALIDO` (fin igual, fin anterior, cruce de medianoche, reserva de un minuto)
- [ ] 4.5 Implementar el validador de espacio existente y activo, y verificar con pruebas los escenarios `ESPACIO_NO_ENCONTRADO` y `ESPACIO_INACTIVO`
- [ ] 4.6 Implementar el validador de reserva en el pasado, y verificar con pruebas, usando un reloj fijo, los escenarios `RESERVA_EN_PASADO` e inicio en el futuro
- [ ] 4.7 Implementar el servicio de creación de reservas (propietario, estado `activa`, fecha de creación, rechazo sin efectos), y verificar con pruebas los escenarios «Reserva válida», «Reserva a nombre de quien la crea», «Rechazo sin efectos» y «Se informa el primer error en orden»
- [ ] 4.8 Crear la vista y plantilla de creación de reservas, y verificar con una prueba de integración que un estudiante crea una reserva válida y que un dato inválido muestra el código y el mensaje

## 5. Validación de conflictos de horario (`validacion-conflictos-horario`)

- [ ] 5.1 Implementar el validador de no solapamiento como función independiente, y verificar con pruebas unitarias sin base de datos los escenarios de solapamiento parcial por ambos extremos, rango contenido, rango que contiene e idéntico, y que las reservas contiguas no son conflicto
- [ ] 5.2 Aplicar el ámbito de la regla (solo reservas `activa` del mismo espacio y fecha), y verificar con pruebas de base de datos los escenarios de reserva cancelada, otro espacio, otra fecha y conflicto con el mismo usuario
- [ ] 5.3 Registrar el validador como último de la lista del servicio, y verificar con una prueba que `HORARIO_INVALIDO` se informa antes que `CONFLICTO_HORARIO`
- [ ] 5.4 Hacer atómica la comprobación y la inserción de la reserva (design D7), y verificar con una prueba de concurrencia con hilos que solo una de dos solicitudes simultáneas queda activa y la otra recibe `CONFLICTO_HORARIO`
- [ ] 5.5 Mostrar el conflicto en la vista de creación con el mensaje «El espacio ya está reservado en ese horario», y verificar con una prueba de integración que se muestra el código y ese mensaje

## 6. Consulta de disponibilidad (`consulta-disponibilidad`)

- [ ] 6.1 Implementar el cálculo de intervalos ocupados y libres entre las 00:00 y las 23:59 (design D8), y verificar con pruebas unitarias los escenarios de día con reservas, día sin reservas y reservas contiguas
- [ ] 6.2 Implementar el servicio de disponibilidad con validación de entrada, exclusión de reservas canceladas y privacidad por rol, y verificar con pruebas los escenarios de fecha inválida, espacio inexistente, espacio inactivo, fecha pasada, reserva cancelada y datos visibles para estudiante frente a administrador
- [ ] 6.3 Crear la vista y plantilla de disponibilidad, y verificar con una prueba de integración que un estudiante ve los intervalos sin datos de otros usuarios
- [ ] 6.4 Verificar la consistencia entre disponibilidad y creación, con pruebas de los escenarios «Reservar un intervalo libre informado» y «Reservar sobre un intervalo ocupado informado»
- [ ] 6.5 Verificar el rendimiento con una prueba que carga 1000 reservas activas en un espacio y comprueba que la consulta responde en menos de 2 segundos (RNF-05)

## 7. Consulta y cancelación de reservas (`consulta-cancelacion-reservas`)

- [ ] 7.1 Implementar el listado de reservas propias y el listado total del administrador, y verificar con pruebas los escenarios de usuario con reservas, aislamiento entre usuarios, usuario sin reservas y administrador que lista todo
- [ ] 7.2 Implementar la consulta de una reserva por identificador, y verificar con pruebas los escenarios de reserva propia, reserva ajena (`SIN_PERMISO`), reserva inexistente y consulta del administrador
- [ ] 7.3 Añadir los campos `cancelada_en` y `cancelada_por` con su migración e implementar la cancelación en el orden de validación de la spec, y verificar con pruebas los escenarios de cancelación propia, de administrador, `SIN_PERMISO`, `RESERVA_YA_CANCELADA`, `RESERVA_NO_CANCELABLE`, `RESERVA_NO_ENCONTRADA` y «Reserva ajena y ya cancelada»
- [ ] 7.4 Verificar que la cancelación libera el horario, con una prueba que cancela una reserva, la reserva de nuevo y comprueba que el intervalo aparece libre
- [ ] 7.5 Crear las vistas y plantillas de listado, detalle y cancelación, y verificar con pruebas de integración el flujo completo de un estudiante y de un administrador

## 8. Verificación de integración

- [ ] 8.1 Ejecutar la suite completa con `pytest` y verificar que todas las pruebas pasan
- [ ] 8.2 Crear un script que lea los escenarios de `specs/` y las referencias `Spec:` de las pruebas, y verificar que no queda ningún escenario sin prueba asociada
- [ ] 8.3 Ejecutar `openspec validate sistema-reservas-espacios --strict` y verificar que no reporta errores

## Workflow follow-up

- Archivar el cambio con OpenSpec (`/opsx:archive`) una vez aprobado, para que las specs queden en `openspec/specs/` y los cambios posteriores puedan modificarlas.
- Verificar el resultado archivado y registrar el commit correspondiente.
