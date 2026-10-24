# Sistema de reserva de espacios académicos

Aplicación web para consultar la disponibilidad y reservar espacios académicos (aulas, laboratorios, salas de estudio y auditorios) sin conflictos de horario. Se desarrolla con **Spec-Driven Development**: primero el plan, luego las especificaciones con OpenSpec y después la implementación asistida por IA.

> **Estado:** en construcción. Este README crece junto con el sistema; cada sección se completa cuando la funcionalidad correspondiente se implementa.

## Documentación del proyecto

| Archivo | Contenido |
|---|---|
| `PLAN_INGENIERIA.md` | Planificación y justificación técnica inicial |
| `openspec/` | Especificaciones, propuestas, diseño y tareas (OpenSpec) |
| `docs/REVISION_ESPECIFICACIONES.md` | Registro de la revisión de las especificaciones |
| `INFORME_FINAL.md` | Resultados, trazabilidad y conclusiones del proceso SDD |

## Requisitos previos

- **Python 3.10 o superior** (`python --version`; en Linux o Mac puede ser `python3`).
- **Git**.
- Node.js solo si quieres usar el CLI de OpenSpec (`npm install -g @fission-ai/openspec@latest`).

## Instalación

Desde la carpeta raíz del repositorio:

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Windows (CMD)**
```bat
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

**Linux o Mac**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Si PowerShell bloquea la activación del entorno, ejecuta una vez
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a intentarlo.

## Comprobar la instalación

```
python src/manage.py check
```
Debe responder `System check identified no issues (0 silenced).`

## Primera ejecución: base de datos y primer administrador

Con el entorno virtual activado, desde la raíz del repositorio:

```
python src/manage.py migrate
python src/manage.py createsuperuser
```
`migrate` crea la base de datos SQLite (`src/db.sqlite3`, no se versiona). `createsuperuser` pregunta el **correo**, el **nombre** y la **contraseña** del primer administrador; ese usuario recibe automáticamente el rol `administrador`.

Los demás usuarios (estudiantes y docentes) no se registran solos: los crea el administrador desde el panel de administración, en <http://127.0.0.1:8000/admin/> → *Usuarios* → *Añadir usuario*, eligiendo su rol.

## Ejecutar el servidor

```
python src/manage.py runserver
```
- Sistema: <http://127.0.0.1:8000/> (pide iniciar sesión con correo y contraseña).
- Disponibilidad: <http://127.0.0.1:8000/disponibilidad/>.
- Reservas propias (o todas, para administración): <http://127.0.0.1:8000/reservas/>.
- Panel de administración: <http://127.0.0.1:8000/admin/>.

Para detener el servidor, pulsa `Ctrl + C`.

## Ejecutar las pruebas

```
pytest
```
Ejecuta toda la suite desde la raíz del repositorio con el entorno virtual activado. La prueba de rendimiento comprueba que consultar un día con 1000 reservas repartidas entre fechas tarda menos de 2 segundos.

Para comprobar la trazabilidad básica entre escenarios OpenSpec y docstrings de pruebas: `python scripts_verificar_trazabilidad.py`. La salida debe revisarse como apoyo; no sustituye la comprobación manual escenario por escenario.

## Configuración

- Zona horaria única del sistema: `America/Bogota`.
- Base de datos: SQLite (archivo local, no se versiona).
- Roles: `estudiante`, `docente` y `administrador`. Estudiante y docente tienen los mismos permisos.

## Estructura del repositorio

```
/
├── PLAN_INGENIERIA.md
├── README.md
├── requirements.txt
├── pytest.ini
├── docs/
├── openspec/            especificaciones y cambios
├── src/
│   ├── manage.py
│   ├── config/          configuración del proyecto Django
│   └── reservas/        aplicación principal
└── tests/
```

## Uso de OpenSpec en este repositorio

Toda funcionalidad se define antes de programarse:

1. Las especificaciones viven en `openspec/` (propuesta, specs, diseño y tareas por cambio).
2. Un cambio funcional se propone y se revisa en OpenSpec antes de tocar el código.
3. Cuando un cambio está implementado y verificado, se archiva y sus especificaciones pasan a `openspec/specs/`.
4. El historial de Git conserva la secuencia plan → especificaciones → implementación.
