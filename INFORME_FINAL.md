# Informe final — Sistema de reserva de espacios académicos

## Alcance y estado de verificación

El proyecto aplica Spec-Driven Development (SDD) con OpenSpec y Django. El orden esperado del proceso es plan de ingeniería, especificaciones revisadas, implementación por tareas, gestión de cambios y verificación. El historial de Git debe conservar ese orden.

Se implementaron las funcionalidades de disponibilidad, consulta de reservas y cancelación lógica en las capas de servicios y presentación. La cancelación conserva el registro y guarda quién y cuándo la realizó. La disponibilidad consulta solo reservas activas, calcula intervalos libres y aplica privacidad según el rol.

**Limitación de esta entrega:** el entorno de generación no tiene Django ni pytest instalados y no dispone de acceso a Internet para instalar las dependencias. Por eso no se declara que la suite esté verde ni que las migraciones y las vistas se hayan ejecutado satisfactoriamente. Sí se realizó una comprobación sintáctica de los archivos Python mediante `compileall`. Antes de entregar académicamente, ejecutar todos los comandos de verificación indicados en el README desde el entorno Windows del proyecto y corregir cualquier fallo.

## Trazabilidad de las funcionalidades añadidas

| Requisito | Especificación | Implementación | Pruebas añadidas |
|---|---|---|---|
| Calcular ocupados y libres del día | `consulta-disponibilidad` | `services/disponibilidad.py` | `test_disponibilidad.py` |
| Ocultar identidad a estudiantes y docentes | `consulta-disponibilidad` | Servicio de disponibilidad y plantilla | `test_disponibilidad.py`, `test_vistas_disponibilidad_consultas.py` |
| Validar espacio y fecha de consulta | `consulta-disponibilidad` | `consultar_disponibilidad` | `test_disponibilidad.py` |
| Respetar consistencia con creación de reservas | `consulta-disponibilidad` y `creacion-reservas` | Servicios de disponibilidad y reservas | `test_disponibilidad.py` |
| Listar reservas propias y todas para administrador | `consulta-cancelacion-reservas` | `services/consultas_reservas.py` | `test_consultas_reservas.py` |
| Consultar detalle con autorización | `consulta-cancelacion-reservas` | `consultar_reserva` | `test_consultas_reservas.py` |
| Cancelar sin borrar y registrar auditoría | `consulta-cancelacion-reservas` | Modelo, migración 0004 y `cancelar_reserva` | `test_consultas_reservas.py`, `test_vistas_disponibilidad_consultas.py` |
| Rendimiento con 1000 reservas | `consulta-disponibilidad` | Índice existente sobre espacio/fecha/estado y consulta filtrada | `test_rendimiento_disponibilidad.py` |

## Decisiones técnicas

- La lógica de negocio se mantiene en servicios y no en las vistas.
- La consulta de disponibilidad devuelve únicamente franjas horarias para estudiantes y docentes; los datos de identificación se añaden solo para el administrador.
- La cancelación es lógica: cambia el estado y registra `cancelada_en` y `cancelada_por`, conservando la reserva para auditoría.
- Los servicios reciben el actor como argumento y aplican autorización independientemente de la interfaz.

## Dificultades y limitaciones

La verificación automatizada completa no pudo ejecutarse en el entorno de construcción por ausencia de dependencias instaladas y falta de conexión al índice de paquetes. Por tanto, la revisión sintáctica no equivale a validar el comportamiento de Django, el esquema de base de datos, el rendimiento real o la concurrencia.

## Conclusiones sobre SDD

SDD ayuda a mantener visibles los requisitos y a convertir escenarios en pruebas verificables. OpenSpec ofrece una estructura para revisar cambios antes de programarlos y reduce el riesgo de que una IA añada comportamientos no solicitados. Su coste es mantener sincronizados propuesta, diseño, especificaciones, tareas, código y pruebas; además, una referencia `Spec:` por sí sola no demuestra que el escenario esté cubierto correctamente. Se necesita ejecutar la suite, revisar la trazabilidad y conservar un historial de Git coherente para demostrar el proceso.

## Verificación pendiente en Windows

Desde PowerShell, en la raíz del repositorio y con el entorno virtual activado:

```powershell
pip install -r requirements.txt
python src/manage.py check
python src/manage.py makemigrations --check --dry-run
python src/manage.py migrate
pytest
python scripts_verificar_trazabilidad.py
openspec validate sistema-reservas-espacios --strict
```

No se debe considerar la entrega completamente verificada hasta resolver cualquier error de estos comandos y actualizar este informe con resultados reales.
