import atexit, json
from pathlib import Path

_observed = []

def record_call(assignments, result):
    _observed.append((assignments.copy(), result))

def get_observed():
    return list(_observed)

@atexit.register
def _dump_observed():
    try:
        # Grava em observed.json no diretório de trabalho atual
        Path('observed.json').write_text(
            json.dumps(_observed), encoding='utf-8'
        )
    except Exception:
        pass