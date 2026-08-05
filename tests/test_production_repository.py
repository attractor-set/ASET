import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_repository_role_is_specification_only():
    s=json.loads((ROOT/"REPOSITORY_STATUS.json").read_text()); assert s["repository_role"]=="NORMATIVE_SPECIFICATION_CONFORMANCE_AND_FORMAL_MODELS"; assert s["implementation_precedence"]=="NONE"
def test_language_switch_is_first_line():
    for p in ("README.md","README.ru.md","README.pt-BR.md"):
        assert (ROOT/p).read_text(encoding="utf-8").splitlines()[0].startswith("[English]")
