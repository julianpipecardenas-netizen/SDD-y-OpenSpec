$ErrorActionPreference = 'Stop'

function Invoke-Check([string]$Description, [scriptblock]$Command) {
    Write-Host "`n=== $Description ===" -ForegroundColor Cyan
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Falló la verificación: $Description (código $LASTEXITCODE)."
    }
}

Invoke-Check 'Django system check' { python src/manage.py check }
Invoke-Check 'Migraciones sincronizadas' { python src/manage.py makemigrations --check --dry-run }
Invoke-Check 'Suite completa de pruebas' { pytest }
Invoke-Check 'Trazabilidad OpenSpec ↔ pruebas' { python scripts_verificar_trazabilidad.py }
Invoke-Check 'Validación estricta de OpenSpec' { openspec validate --strict }

Write-Host "`nTodas las verificaciones terminaron correctamente." -ForegroundColor Green
