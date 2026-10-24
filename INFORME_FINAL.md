# Informe final — Sistema de reserva de espacios académicos

## 1. Objetivo y alcance

El proyecto implementa un sistema web de reserva de espacios académicos con Django 5.2, SQLite y zona horaria `America/Bogota`. El proceso se organizó mediante Spec-Driven Development (SDD): plan de ingeniería, especificaciones OpenSpec revisadas, implementación incremental, pruebas y gestión de cambios.

El sistema incluye autenticación con roles de estudiante, docente y administrador; gestión de espacios; creación de reservas; validación de conflictos; consulta de disponibilidad; listado, consulta y cancelación lógica de reservas. La cancelación conserva la reserva y registra quién y cuándo la canceló.

## 2. Regla incorporada en la fase 4

Se añadió el cambio OpenSpec `limite-duracion-reserva`: **cada reserva individual puede durar como máximo cuatro horas**. Una reserva de cuatro horas exactas se permite; una de cuatro horas y un minuto se rechaza con `DURACION_RESERVA_EXCEDIDA`. El límite no acumula las horas de reservas de otros días ni de la semana anterior. La regla tiene un validador independiente y pruebas unitarias y de servicio.

## 3. Organización de OpenSpec

- `openspec/specs/` contiene las seis capacidades estables de la implementación inicial.
- `openspec/changes/archive/2026-10-24-sistema-reservas-espacios/` conserva la propuesta, diseño, tareas y deltas originales de la primera implementación.
- `openspec/changes/limite-duracion-reserva/` conserva la propuesta, diseño, tareas y delta de la regla nueva. Tras verificarla en el entorno local, debe archivarse mediante OpenSpec.

## 4. Trazabilidad

| Capacidad | Código principal | Pruebas principales |
|---|---|---|
| `autenticacion-roles` | `services/autenticacion.py`, `services/acceso.py`, vistas de autenticación | `test_autenticacion.py`, `test_usuarios.py`, `test_vistas_autenticacion.py` |
| `gestion-espacios` | `services/espacios.py`, vistas y modelos de espacio | `test_servicio_espacios.py`, `test_modelo_espacio.py`, `test_vistas_espacios.py` |
| `creacion-reservas` | `services/reservas.py`, `services/validadores.py` | `test_servicio_reservas.py`, `test_validadores_datos_horario.py` |
| `validacion-conflictos-horario` | `services/validadores.py`, transacción de creación | `test_validador_solapamiento.py`, `test_concurrencia_reservas.py`, `test_vistas_conflictos.py` |
| `consulta-disponibilidad` | `services/disponibilidad.py` | `test_disponibilidad.py`, `test_rendimiento_disponibilidad.py` |
| `consulta-cancelacion-reservas` | `services/consultas_reservas.py` | `test_consultas_reservas.py`, `test_vistas_disponibilidad_consultas.py` |
| `limite-duracion-reserva` | `validadores.validar_duracion_maxima` y `errores.DURACION_RESERVA_EXCEDIDA` | `test_validadores_datos_horario.py`, `test_servicio_reservas.py` |

El script `scripts_verificar_trazabilidad.py` comprueba que los títulos de los escenarios OpenSpec aparecen en archivos de prueba que citan la capacidad correspondiente. Esta verificación es estática y no prueba por sí sola la validez de cada aserción.

## 5. Verificación y resultados

Durante la verificación de la implementación inicial, el usuario ejecutó `pytest` y obtuvo **280 pruebas aprobadas**. También ejecutó `openspec validate --strict`, que finalizó con un resultado correcto para el cambio inicial. Después se añadieron pruebas de cobertura para escenarios previamente no referenciados y para el nuevo límite de duración.

**Pendiente de confirmar en la copia final:** el entorno en el que se preparó este ZIP no tiene Django/pytest instalados y no tiene acceso al índice de paquetes. Por eso no se declara como ejecutada aquí la suite final que incluye los cambios recientes. Antes de presentar el proyecto, ejecutar en Windows los comandos del apartado siguiente y registrar sus resultados reales. No se deben copiar resultados antiguos como si correspondieran a la última versión.

## 6. Comandos de verificación en Windows PowerShell

Desde la raíz del proyecto, crea y activa un entorno virtual limpio:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/manage.py check
python src/manage.py makemigrations --check --dry-run
python src/manage.py migrate
pytest
python scripts_verificar_trazabilidad.py
openspec validate --strict
```

Resultados esperados: `manage.py check` sin problemas; migraciones sincronizadas; suite `pytest` completamente aprobada; script de trazabilidad sin escenarios pendientes; y OpenSpec sin errores. El comando `migrate` crea la base SQLite local; no se incluye la base de datos del usuario en el ZIP.

## 7. Decisiones técnicas y dificultades

- La lógica de negocio está separada de las vistas mediante servicios y validadores independientes.
- Los intervalos se tratan como semiabiertos, por lo que dos reservas contiguas no se consideran conflicto.
- La comprobación de conflicto y la inserción se realizan dentro de una transacción.
- La disponibilidad muestra solo intervalos a estudiantes y docentes; los datos de identidad quedan reservados al administrador.
- La duración máxima es una regla independiente de cada reserva, no un acumulado diario o semanal.
- Una dificultad importante del proceso es mantener sincronizados los requisitos, el diseño, las tareas, las pruebas y la implementación. Un resultado de validación estructural de OpenSpec no reemplaza las pruebas funcionales.

## 8. Conclusiones sobre SDD

SDD obliga a definir y revisar el comportamiento antes de implementarlo y permite relacionar requisitos, escenarios y pruebas. OpenSpec ayuda a gestionar cambios sin modificar silenciosamente el alcance original. El coste es mantener los artefactos sincronizados y verificar que los escenarios estén cubiertos de verdad. La calidad de la entrega depende tanto del historial de Git como de ejecutar la suite completa y documentar resultados verificables.
