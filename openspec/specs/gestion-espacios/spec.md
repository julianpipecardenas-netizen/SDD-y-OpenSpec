# Spec

## Purpose

Define el catálogo de espacios académicos (aulas, laboratorios, salas de estudio y auditorios) y quién puede administrarlo.

## Requirements

### Requirement: Datos de un espacio
Cada espacio SHALL tener nombre, tipo, capacidad y estado activo o inactivo. El nombre MUST ser único sin distinguir mayúsculas, el tipo MUST ser uno de `aula`, `laboratorio`, `sala_estudio` o `auditorio`, y la capacidad MUST ser un entero mayor que cero. Un espacio nuevo MUST quedar activo. (RF-02)

#### Scenario: Espacio creado con datos válidos
- **WHEN** el administrador crea un espacio con nombre "Lab 301", tipo `laboratorio` y capacidad 30
- **THEN** el sistema registra el espacio como activo y lo devuelve con un identificador

#### Scenario: Nombre duplicado
- **WHEN** el administrador crea un espacio con un nombre que ya existe, sin distinguir mayúsculas
- **THEN** el sistema responde `ESPACIO_DUPLICADO` y no crea el espacio

#### Scenario: Capacidad inválida
- **WHEN** el administrador crea un espacio con capacidad 0 o negativa
- **THEN** el sistema responde `DATOS_INVALIDOS` y no crea el espacio

#### Scenario: Tipo no permitido
- **WHEN** el administrador crea un espacio con un tipo fuera de la lista permitida
- **THEN** el sistema responde `DATOS_INVALIDOS` y no crea el espacio

### Requirement: Solo el administrador gestiona espacios
Solo un usuario con rol `administrador` SHALL poder crear, editar, activar y desactivar espacios. Cualquier otro usuario autenticado MUST recibir `SIN_PERMISO` y el espacio no debe cambiar. (RF-02)

#### Scenario: Docente intenta editar un espacio
- **WHEN** un docente intenta cambiar la capacidad de un espacio
- **THEN** el sistema responde `SIN_PERMISO` y la capacidad no cambia

#### Scenario: Administrador edita un espacio
- **WHEN** el administrador cambia la capacidad de un espacio a un entero mayor que cero
- **THEN** el sistema guarda el cambio y devuelve el espacio actualizado

### Requirement: Consulta de espacios
Todo usuario autenticado SHALL poder listar los espacios y consultar uno por identificador. En el listado, los estudiantes y docentes MUST ver solo espacios activos y el administrador MUST ver activos e inactivos. Si un estudiante o docente consulta por identificador un espacio inactivo, MUST recibir `ESPACIO_INACTIVO`. (RF-02)

#### Scenario: Estudiante lista espacios
- **WHEN** un estudiante lista los espacios y existe un espacio inactivo
- **THEN** el listado incluye solo los espacios activos

#### Scenario: Administrador lista espacios
- **WHEN** el administrador lista los espacios y existe un espacio inactivo
- **THEN** el listado incluye los espacios activos y los inactivos, indicando el estado de cada uno

#### Scenario: Espacio inexistente
- **WHEN** un usuario consulta un identificador de espacio que no existe
- **THEN** el sistema responde `ESPACIO_NO_ENCONTRADO`

#### Scenario: Estudiante consulta un espacio inactivo
- **WHEN** un estudiante consulta por identificador un espacio inactivo
- **THEN** el sistema responde `ESPACIO_INACTIVO` y no devuelve sus datos

### Requirement: Activación y desactivación
El administrador SHALL poder desactivar y reactivar un espacio. Un espacio inactivo MUST NOT aceptar reservas nuevas. Las reservas activas que ya tuviera se conservan sin cambios (supuesto P4). Los espacios MUST NOT eliminarse físicamente mientras tengan reservas asociadas. (RF-02)

#### Scenario: Desactivar un espacio
- **WHEN** el administrador desactiva un espacio activo
- **THEN** el espacio queda inactivo y deja de aceptar reservas nuevas

#### Scenario: Reservas existentes se conservan
- **WHEN** el administrador desactiva un espacio que tiene una reserva futura activa
- **THEN** esa reserva sigue en estado activo

#### Scenario: Reactivar un espacio
- **WHEN** el administrador reactiva un espacio inactivo
- **THEN** el espacio vuelve a aceptar reservas nuevas

#### Scenario: Eliminación bloqueada con reservas
- **WHEN** el administrador intenta eliminar un espacio que tiene reservas asociadas
- **THEN** el sistema responde `ESPACIO_CON_RESERVAS` y el espacio permanece
