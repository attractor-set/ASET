import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MODEL = (
    ROOT
    / "seed"
    / "canonical"
    / "source"
    / "seed-model.json"
)


def test_languages_are_exact():
    model = json.loads(
        MODEL.read_text(encoding="utf-8")
    )

    assert model["languages"] == [
        "ru",
        "en",
        "pt-BR",
    ]


def test_all_concepts_have_all_languages():
    model = json.loads(
        MODEL.read_text(encoding="utf-8")
    )

    expected = {"ru", "en", "pt-BR"}

    for concept in model["concepts"]:
        assert set(concept["labels"]) == expected
        assert set(concept["definitions"]) == expected


def test_all_requirements_have_all_languages():
    model = json.loads(
        MODEL.read_text(encoding="utf-8")
    )

    expected = {"ru", "en", "pt-BR"}

    for requirement in model["requirements"]:
        assert set(requirement["texts"]) == expected



def test_all_invariants_have_all_languages():
    model = json.loads(
        MODEL.read_text(encoding="utf-8")
    )

    expected = {"ru", "en", "pt-BR"}

    for invariant in model["invariants"]:
        assert set(invariant["texts"]) == expected
