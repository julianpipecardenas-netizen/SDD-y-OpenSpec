# PLAN_INGENIERIA.md

**Proyecto:** Sistema de reserva de espacios académicos
**Metodología:** Spec-Driven Development (SDD) con OpenSpec y agente de programación con IA
**Estado:** Versión inicial, previa a las especificaciones y a la implementación
**Autor:** Julian

> Este documento se escribe y se registra en Git **antes** de crear cualquier especificación o línea de código. Todo ajuste posterior se documenta en `INFORME_FINAL.md`, sin reescribir este plan.

---

## 1. Contexto y problema

La institución necesita gestionar la reserva de espacios académicos (aulas, laboratorios, salas de estudio, auditorios). Hoy la asignación suele hacerse de forma manual o informal, lo que produce:

- Dobles reservas del mismo espacio y horario.
- Falta de visibilidad sobre la disponibilidad.
- Ausencia de trazabilidad: quién reservó, cuándo y por qué.

## 2. Objetivo

Construir un sistema web que permita consultar disponibilidad y reservar espacios académicos sin conflictos de horario, con trazabilidad y reglas de negocio verificables.

### Objetivos específicos
1. Registrar y administrar espacios académicos.
2. Permitir crear, consultar y cancelar reservas.
3. Impedir solapamientos de reservas sobre un mismo espacio.
4. Aplicar el control de acceso según el rol del usuario.
5. Dejar el sistema preparado para incorporar nuevas reglas de negocio sin reestructurarlo.

## 3. Alcance

### Dentro del alcance (versión 1)
- Autenticación de usuarios y roles (estudiante, docente, administrador).
- CRUD de espacios (solo administrador).
- Creación de reservas con fecha, hora de inicio y hora de fin.
- Validación de conflictos de horario.
- Consulta de disponibilidad por espacio y fecha.
- Consulta y cancelación de reservas propias.
- Pruebas automatizadas de las reglas de negocio.

### Fuera del alcance
- Pagos o cobros.
- Notificaciones por correo o SMS.
- Integración con sistemas académicos externos.
- Aplicación móvil nativa.
- Reservas recurrentes.

## 4. Supuestos y restricciones

| # | Supuesto o restricción | Impacto |
|---|---|---|
| S1 | Una reserva pertenece a un único usuario y a un único espacio | Simplifica el modelo de datos |
| S2 | Una reserva no cruza la medianoche (empieza y termina el mismo día) | Simplifica la validación de horarios |
| S3 | Las reservas se hacen en bloques con hora de inicio y de fin explícitas | Define el modelo temporal |
| S4 | Zona horaria única: America/Bogota | Evita conversiones |
| S5 | La institución puede añadir reglas de negocio durante el desarrollo | Exige diseño extensible |
| S6 | Plazo académico limitado y trabajo individual | Condiciona el alcance |
| S7 | Todo el código se desarrolla con un agente de IA bajo control del estudiante | Exige specs claras y revisión |

## 5. Actores y roles

| Rol | Permisos generales |
|---|---|
| Estudiante | Consultar disponibilidad, reservar, ver y cancelar sus reservas |
| Docente | Igual que estudiante |
| Administrador | Gestionar espacios y consultar o cancelar cualquier reserva |

*Las diferencias finas de permisos entre estudiante y docente se definirán y revisarán en la Fase 2 (posible ambigüedad).*

## 6. Requisitos de alto nivel (previos a la especificación)

Son requisitos de alto nivel, aún no verificables. En la Fase 2 se convertirán en especificaciones con escenarios de aceptación.

### Funcionales
- RF-01: El sistema permite iniciar sesión y distingue roles.
- RF-02: El administrador gestiona los espacios.
- RF-03: El usuario crea una reserva sobre un espacio, con fecha y rango horario.
- RF-04: El sistema rechaza reservas que se solapen con otra existente en el mismo espacio.
- RF-05: El usuario consulta la disponibilidad de un espacio.
- RF-06: El usuario consulta y cancela sus reservas.
- RF-07: El administrador consulta y cancela cualquier reserva.

### No funcionales
- RNF-01: Las reglas de negocio deben estar aisladas de la interfaz y de la base de datos, para poder cambiarlas sin afectar otras capas.
- RNF-02: Cada regla de negocio debe poder probarse de forma automatizada.
- RNF-03: Instalación y ejecución local documentadas en `README.md`.
- RNF-04: Contraseñas almacenadas con hash, nunca en texto plano.
- RNF-05: Tiempo de respuesta razonable para consultas de disponibilidad (objetivo: menos de 2 s en uso normal).

## 7. Decisiones de ingeniería y justificación

### 7.1 Arquitectura: monolito modular en capas

**Decisión:** una sola aplicación web dividida en capas: presentación, lógica de negocio (servicios) y acceso a datos.

**Justificación:**
- El alcance y el equipo (una persona) no justifican microservicios; añadirían complejidad de despliegue sin beneficio.
- La capa de servicios aislada cumple RNF-01 y RNF-02: las reglas de negocio quedan en un único lugar, lo que reduce el impacto de futuros cambios.

**Alternativas descartadas:**
- *Microservicios:* sobrecoste operativo desproporcionado.
- *Lógica en vistas o plantillas:* difícil de probar y de modificar.

### 7.2 Stack tecnológico

| Componente | Decisión | Justificación | Alternativa descartada |
|---|---|---|---|
| Lenguaje | Python 3 | Dominio previo del estudiante; el agente de IA lo genera con alta fiabilidad | Java (mayor verbosidad) |
| Framework | Django | Incluye autenticación, roles, ORM y panel de administración; reduce código propio | Flask (habría que armar auth y ORM aparte) |
| Base de datos | SQLite en desarrollo y pruebas | Cero configuración; reproducible por el evaluador | PostgreSQL (innecesario para esta versión) |
| Pruebas | pytest + pytest-django | Sintaxis simple, buena integración con Django | unittest (más verboso) |
| Control de versiones | Git | Requisito de evaluación | Ninguna |
| Especificaciones | OpenSpec | Requisito de la metodología SDD | Ninguna |

*Si el stack cambia por indicación del docente, esta sección se actualizará antes de crear las especificaciones.*

### 7.3 Modelo de datos preliminar

- **Usuario:** id, nombre, correo, rol.
- **Espacio:** id, nombre, tipo, capacidad, activo.
- **Reserva:** id, usuario, espacio, fecha, hora_inicio, hora_fin, estado (activa o cancelada), creada_en.

**Decisiones:**
- La cancelación es lógica (cambio de estado), no un borrado, para conservar la trazabilidad.
- Las restricciones de integridad (hora_fin posterior a hora_inicio, claves foráneas) se aplican también en base de datos y no solo en la interfaz.

### 7.4 Diseño de reglas de negocio extensible

**Decisión:** cada regla de negocio (por ejemplo, "no solapamiento") se implementa como una función o validador independiente dentro de la capa de servicios, y el servicio de reservas los ejecuta en secuencia.

**Justificación:** la institución puede añadir reglas durante el proyecto (S5). Con validadores independientes, una regla nueva se agrega sin modificar las existentes, y se puede probar de forma aislada.

### 7.5 Política de manejo de errores

Las reglas de negocio fallidas devuelven un error de dominio con mensaje claro (por ejemplo, "El espacio ya está reservado en ese horario"), y no una excepción genérica. Esto permite probar cada regla por su mensaje y código.

## 8. Estrategia de pruebas

| Nivel | Qué cubre | Herramienta |
|---|---|---|
| Unitarias | Validadores y servicios de reglas de negocio | pytest |
| Integración | Flujos completos de reserva (vista + servicio + BD) | pytest-django |
| Regresión | Reejecución completa tras cada cambio, especialmente en la Fase 4 | pytest |

**Criterios:**
- Cada escenario de aceptación de las especificaciones tiene al menos una prueba asociada.
- Se incluyen casos límite: reservas contiguas (el fin de una es el inicio de otra), horarios idénticos, rangos inválidos.

## 9. Estrategia de Git

- Rama principal: `main`. Ramas cortas por funcionalidad: `feature/<nombre>`.
- Commits pequeños, con prefijos: `docs:`, `spec:`, `feat:`, `test:`, `fix:`, `refactor:`.
- **Secuencia obligatoria verificable en el historial:**
  1. `docs: plan de ingeniería inicial` (este documento)
  2. `spec: ...` (especificaciones OpenSpec)
  3. `feat:` y `test:` (implementación)
  4. `spec: propuesta de cambio` antes de `feat:` del cambio de la Fase 4
  5. `docs: informe final`
- Ningún `feat:` se registra sin su `spec:` previo.

## 10. Uso controlado de la IA

La IA es una herramienta; la responsabilidad técnica es del estudiante.

**Reglas de trabajo:**
1. El agente solo recibe como instrucción las especificaciones aprobadas, no ideas sueltas.
2. Se implementa una funcionalidad a la vez, con su commit.
3. Todo el código generado se revisa antes de aceptarlo (lógica, seguridad, correspondencia con la spec).
4. Si el agente añade funcionalidad no especificada, se descarta o se crea primero su especificación.
5. Se registran en una bitácora los casos donde el agente se equivocó o se desvió de la spec, para usarlos en la sustentación.

## 11. Riesgos y mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| La IA implementa funcionalidades no pedidas | Alta | Medio | Instrucciones acotadas a una spec; revisión del diff |
| Especificaciones ambiguas generan código incorrecto | Media | Alto | Revisión en Fase 2; escenarios de aceptación concretos |
| Cambio de regla de negocio rompe lo existente | Media | Alto | Validadores independientes; pruebas de regresión |
| Errores en casos límite de horarios | Alta | Alto | Casos límite explícitos en las specs y pruebas |
| Falta de tiempo | Media | Medio | Alcance acotado; priorizar RF-03, RF-04 y RF-05 |

## 12. Plan de trabajo por fases

| Fase | Actividad | Entregable | Criterio de salida |
|---|---|---|---|
| 1 | Planificación | `PLAN_INGENIERIA.md` | Plan registrado en Git antes de cualquier spec |
| 2 | Revisión de especificaciones | Specs OpenSpec revisadas, lista de ambigüedades y tareas | Specs consistentes y alineadas con este plan |
| 3 | Implementación asistida | Código y pruebas por funcionalidad | Pruebas en verde; cada feature con spec previa |
| 4 | Gestión de cambios | Propuesta OpenSpec, specs actualizadas, código y pruebas | Regla nueva implementada sin regresiones |
| 5 | Verificación y cierre | `INFORME_FINAL.md`, `README.md` final | Trazabilidad requisitos, código y pruebas completa |

## 13. Estructura prevista del repositorio

```
/
├── PLAN_INGENIERIA.md
├── README.md
├── INFORME_FINAL.md
├── openspec/
│   ├── specs/
│   └── changes/
├── src/
│   ├── reservas/        (app Django)
│   │   ├── models.py
│   │   ├── services/    (reglas de negocio)
│   │   └── views.py
│   └── manage.py
└── tests/
```

## 14. Criterios de éxito

- El sistema evita el 100 % de las reservas solapadas en los casos de prueba.
- Todo requisito tiene especificación, código y prueba asociados.
- El historial de Git muestra la secuencia plan, specs, código, cambio y cierre.
- Una regla de negocio nueva se incorpora modificando solo la capa de servicios, sus specs y sus pruebas.
