"""Verificación estática de trazabilidad entre escenarios OpenSpec y pruebas.

Uso: python scripts_verificar_trazabilidad.py
La comprobación exige que cada capacidad con escenarios tenga al menos una
referencia Spec en los docstrings de pruebas. El informe muestra escenarios y
referencias para facilitar la revisión manual de correspondencia uno a uno.
"""
from pathlib import Path
import re

ROOT = Path(__file__).parent
SPECS = ROOT / "openspec" / "changes" / "sistema-reservas-espacios" / "specs"
TESTS = ROOT / "tests"

def main():
    docstrings = "\n".join(p.read_text(encoding="utf-8") for p in TESTS.glob("test_*.py"))
    failed = []
    total = 0
    for spec in sorted(SPECS.glob("*/spec.md")):
        content = spec.read_text(encoding="utf-8")
        scenarios = re.findall(r"^#### Scenario: (.+)$", content, re.M)
        total += len(scenarios)
        capability = spec.parent.name
        refs = len(re.findall(r"Spec:\s*" + re.escape(capability), docstrings))
        print(f"{capability}: {len(scenarios)} escenarios; {refs} referencias de pruebas")
        if scenarios and refs == 0:
            failed.append(capability)
    print(f"Total: {total} escenarios identificados en specs")
    if failed:
        print("Capacidades sin pruebas referenciadas: " + ", ".join(failed))
        return 1
    print("Todas las capacidades tienen referencias Spec; revisar correspondencia escenario-prueba en el informe.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
