"""Comprueba la presencia de cada escenario OpenSpec en las pruebas.

Busca escenarios tanto en las especificaciones estables como en los cambios
activos. Para cada escenario exige que su título aparezca en un archivo de
pruebas que también cite la capacidad mediante una referencia ``Spec:``.

Uso: python scripts_verificar_trazabilidad.py
Esta comprobación estática no sustituye la ejecución de pytest ni la revisión
humana de que las aserciones prueben todo el comportamiento descrito.
"""
from pathlib import Path
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parent
SPEC_ROOTS = (ROOT / "openspec" / "specs", ROOT / "openspec" / "changes")
TESTS_ROOT = ROOT / "tests"


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.casefold())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", texto).strip()


def archivos_spec():
    encontrados = []
    for base in SPEC_ROOTS:
        if base == ROOT / "openspec" / "specs":
            encontrados.extend(base.glob("*/spec.md"))
        else:
            encontrados.extend(base.glob("*/specs/*/spec.md"))
    return sorted(set(encontrados))


def main() -> int:
    test_files = sorted(TESTS_ROOT.glob("test_*.py"))
    test_contents = {p: p.read_text(encoding="utf-8") for p in test_files}
    normalized = {p: normalizar(content) for p, content in test_contents.items()}
    total = 0
    failures = []
    spec_files = archivos_spec()

    for spec_path in spec_files:
        capability = spec_path.parent.name
        content = spec_path.read_text(encoding="utf-8")
        scenarios = re.findall(r"^#### Scenario: (.+)$", content, re.MULTILINE)
        for scenario in scenarios:
            total += 1
            title = normalizar(scenario)
            found = any(
                title in normalized[path]
                and re.search(r"Spec:\s*" + re.escape(capability), test_contents[path], re.IGNORECASE)
                for path in test_files
            )
            if not found:
                failures.append((capability, scenario, spec_path.relative_to(ROOT)))

    print(f"Archivos de especificación revisados: {len(spec_files)}")
    print(f"Escenarios identificados: {total}")
    if failures:
        print(f"Escenarios sin referencia de prueba detectable: {len(failures)}")
        for capability, scenario, path in failures:
            print(f"- {capability} / {scenario} ({path})")
        return 1

    print("OK: todos los títulos de escenarios aparecen en archivos de pruebas con referencias Spec de su capacidad.")
    print("Nota: esta verificación es estática; pytest y la revisión humana siguen siendo necesarios.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
