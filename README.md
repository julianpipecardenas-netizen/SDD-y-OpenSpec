# Sistema de reserva de espacios académicos

Aplicación web para consultar la disponibilidad y reservar espacios académicos (aulas, laboratorios, salas de estudio y auditorios) sin conflictos de horario. Se desarrolla con **Spec-Driven Development**: primero el plan, luego las especificaciones con OpenSpec y después la implementación asistida por IA.

> **Estado:** implementación completa para la versión académica, con una nueva regla de duración máxima individual en su cambio OpenSpec activo. La suite final debe ejecutarse en el entorno local después de descomprimir el ZIP.

## Documentación del proyecto

| Archivo | Contenido |
|---|---|
| `PLAN_INGENIERIA.md` | Planificación y justificación técnica inicial |
| `openspec/specs/` | Especificaciones estables de la versión inicial |
| `openspec/changes/archive/` | Cambio inicial archivado con propuesta, diseño, tareas y especificaciones originales |
| `openspec/changes/limite-duracion-reserva/` | Cambio de fase 4: máximo de cuatro horas por reserva individual |
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

Para comprobar que cada escenario de las especificaciones aparece en un archivo de pruebas con una referencia `Spec:` de su capacidad, ejecuta `python scripts_verificar_trazabilidad.py`. La comprobación es estática y no sustituye la ejecución de `pytest` ni la revisión humana.


## Verificación rápida en PowerShell

Con el entorno virtual activado y las dependencias instaladas, puedes ejecutar todos los controles en secuencia:

```powershell
.\VERIFICAR_PROYECTO.ps1
```

El script se detiene en el primer comando que falle. Si PowerShell bloquea su ejecución, puedes ejecutar los comandos listados dentro de `VERIFICAR_PROYECTO.ps1` uno por uno.

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

1. Las especificaciones estables viven en `openspec/specs/`.
2. El cambio inicial está archivado en `openspec/changes/archive/2026-10-24-sistema-reservas-espacios/`.
3. El cambio de fase 4 está en `openspec/changes/limite-duracion-reserva/` y define una duración máxima de cuatro horas por solicitud individual. No suma reservas de días anteriores.
4. Después de verificar este cambio con las pruebas, debe archivarse y sincronizarse con `openspec/specs/`.
5. El historial de Git conserva la secuencia plan → especificaciones → implementación → pruebas → documentación.
