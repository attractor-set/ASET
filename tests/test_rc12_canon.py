import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def model(): return json.loads((ROOT/"seed/canonical/source/seed-model.json").read_text(encoding="utf-8"))
def test_seed_is_implementation_neutral():
    value=model(); assert "runtime_profile" not in value; assert value["implementation_boundary"]["implementation_precedence"]=="NONE"
def test_implementation_requirements_are_not_seed_requirements():
    assert not any(item["id"].startswith("ASET-SEED-PRT-") for item in model()["requirements"])
