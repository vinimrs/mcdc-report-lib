# tests/test_mcdc.py
import subprocess
import filecmp
from pathlib import Path

import pytest

# Ajuste para o comando que inicia sua ferramenta:
MCDC_CMD = ["python", str(Path(__file__).parent.parent / "mcdc_tool.py")]

# Pasta base dos testes
BASE = Path(__file__).parent
INPUT_DIR = BASE / "inputs"
EXPECTED_DIR = BASE / "expected"
GENERATED_DIR = BASE / "generated"

# Garante que exista a pasta de saída
GENERATED_DIR.mkdir(exist_ok=True)

def list_test_cases():
    """
    Encontra todos os arquivos .py em inputs/ e retorna
    tuplas (input_path, expected_path).
    """
    for input_path in sorted(INPUT_DIR.glob("*.py")):
        name = input_path.stem  # ex: "test_1_simple_if"
        expected_path = EXPECTED_DIR / f"{name}.txt"
        if expected_path.exists():
            yield name, input_path, expected_path

@pytest.mark.parametrize("name,input_path,expected_path", list(list_test_cases()))
def test_mcdc_report(name: str, input_path: Path, expected_path: Path):
    """
    Executa o gerador de relatório MC/DC sobre cada input,
    salva em generated/<name>.txt e compara com expected/.
    """
    out_path = GENERATED_DIR / f"{name}.txt"

    # Chama sua ferramenta
    cmd = [*MCDC_CMD, str(input_path), "-o", str(out_path.resolve())]
    subprocess.run(cmd, check=True)

    # Leitura e normalização (trim de espaços e quebra de linhas)
    def normalize(path: Path):
        return "\n".join([line.rstrip() for line in path.read_text().splitlines() if line.strip()])

    gen = normalize(out_path)
    exp = normalize(expected_path)

    assert gen == exp, f"\nRelatório gerado difere do esperado em '{name}':\n--- GERADO ---\n{gen}\n--- ESPERADO ---\n{exp}"