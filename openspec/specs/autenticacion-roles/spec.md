# Spec

## Purpose

Define cómo los usuarios se identifican ante el sistema y cómo el rol asignado (estudiante, docente o administrador) determina lo que cada persona puede hacer.

## Requirements

### Requirement: Inicio de sesión con credenciales
El sistema SHALL permitir iniciar sesión con correo y contraseña. Con credenciales válidas MUST abrir una sesión e identificar el rol del usuario. Con credenciales inválidas MUST rechazar el acceso con el código `CREDENCIALES_INVALIDAS` sin revelar cuál dato falló. (RF-01)

#### Scenario: Credenciales válidas
- **WHEN** un usuario registrado envía su correo y su contraseña correctos
- **THEN** el sistema abre una sesión y responde con el rol del usuario

#### Scenario: Contraseña incorrecta
- **WHEN** un usuario registrado envía una contraseña incorrecta
- **THEN** el sistema rechaza el acceso con el código `CREDENCIALES_INVALIDAS` y no abre sesión

#### Scenario: Correo no registrado
- **WHEN** alguien envía un correo que no existe en el sistema
- **THEN** el sistema responde con el mismo código `CREDENCIALES_INVALIDAS` y el mismo mensaje que en el caso de contraseña incorrecta

### Requirement: Cierre de sesión
El sistema SHALL permitir a un usuario autenticado cerrar su sesión. Después del cierre, la sesión anterior MUST dejar de dar acceso a las operaciones protegidas. (RF-01)

#### Scenario: Cierre de sesión exitoso
- **WHEN** un usuario autenticado cierra su sesión
- **THEN** el sistema invalida la sesión y la siguiente petición protegida con esa sesión responde `NO_AUTENTICADO`

### Requirement: Operaciones protegidas exigen autenticación
El sistema MUST exigir una sesión válida para toda operación sobre espacios, reservas o disponibilidad. Sin sesión válida MUST rechazar la operación con el código `NO_AUTENTICADO` y no ejecutar ningún efecto. (RF-01)

#### Scenario: Consulta sin sesión
- **WHEN** una persona sin sesión intenta consultar la disponibilidad de un espacio
- **THEN** el sistema responde `NO_AUTENTICADO` y no devuelve datos

#### Scenario: Creación de reserva sin sesión
- **WHEN** una persona sin sesión intenta crear una reserva
- **THEN** el sistema responde `NO_AUTENTICADO` y no se crea ninguna reserva

### Requirement: Roles reconocidos
El sistema SHALL reconocer exactamente tres roles: `estudiante`, `docente` y `administrador`. Cada usuario MUST tener un único rol. Los permisos de `estudiante` y de `docente` son idénticos (supuesto P1). Solo `administrador` MUST poder gestionar espacios y operar sobre reservas ajenas. (RF-01)

#### Scenario: Usuario con un único rol
- **WHEN** el sistema identifica a un usuario autenticado
- **THEN** le asocia uno solo de los roles `estudiante`, `docente` o `administrador`

#### Scenario: Estudiante y docente tienen los mismos permisos
- **WHEN** un estudiante y un docente intentan crear una reserva válida sobre el mismo espacio y horario libre
- **THEN** el sistema acepta la operación para ambos con el mismo resultado

#### Scenario: Operación reservada al administrador
- **WHEN** un usuario con rol `estudiante` o `docente` intenta crear un espacio
- **THEN** el sistema responde con el código `SIN_PERMISO` y no crea el espacio

### Requirement: Contraseñas protegidas
El sistema MUST almacenar las contraseñas de forma que no puedan recuperarse en texto plano, y MUST NOT incluirlas en ninguna respuesta, registro o mensaje de error. (RNF-04)

#### Scenario: Contraseña no recuperable
- **WHEN** se inspeccionan los datos almacenados de un usuario
- **THEN** la contraseña no aparece en texto plano

#### Scenario: Contraseña ausente en respuestas
- **WHEN** el sistema devuelve datos de un usuario
- **THEN** la respuesta no contiene la contraseña ni su valor almacenado
