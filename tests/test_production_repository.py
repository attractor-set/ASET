import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_repository_role_is_specification_only():
    status=json.loads((ROOT/"REPOSITORY_STATUS.json").read_text())
    assert status["repository_role"]=="OPEN_IMPLEMENTATION_NEUTRAL_SPECIFICATION"
    assert status["implementation_precedence"]=="NONE"
    assert status["architectural_role"]=="MACHINE_INTERPRETABLE_EVOLUTION_CAPABLE_SEMANTIC_VESSEL"
    assert status["operational_nucleus"]=="LOCAL_EXACT_BINDING_RESOLUTION_RECOGNITION"
    assert status["evolution_search_boundary"]=="OUTSIDE_SEED_UNSPECIFIED_NO_RECOGNITION_AUTHORITY"
def test_language_switch_is_first_line():
    for path in ("README.md","README.ru.md","README.pt-BR.md"):
        assert (ROOT/path).read_text(encoding="utf-8").splitlines()[0].startswith("[English]")
