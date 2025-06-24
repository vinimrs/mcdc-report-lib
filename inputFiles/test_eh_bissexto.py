import pytest
from eh_bissexto import eh_bissexto  # ajuste para o nome correto do módulo

@pytest.mark.parametrize("ano, expected_exception, expected_result", [
    # anos inválidos geram ValueError
    (0,     ValueError, None),
    (10000, ValueError, None),

    # # regra antiga (ano ≤ 1752): múltiplo de 4
    # (4,     None, True),
    # (100,   None, True),
    # (1752,  None, True),
    (1751,  None, False),

    # regra moderna
    (1600,  None, True),   # %400 == 0
    (2000,  None, True),   # %400 == 0
    (1900,  None, False),  # %100 == 0, mas não %400
    (2004,  None, True),   # %4 == 0, não múltiplo de 100
    (2001,  None, False),  # não múltiplo de 4
])
def test_eh_bissexto(ano, expected_exception, expected_result):
    if expected_exception:
        with pytest.raises(expected_exception) as excinfo:
            eh_bissexto(ano)
        # Opcional: garantir mensagem
        assert "entre 1 e 9999" in str(excinfo.value)
    else:
        assert eh_bissexto(ano) is expected_result

if __name__ == "__main__":
    pytest.main([__file__])