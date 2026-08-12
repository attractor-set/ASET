from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from tools.alpha4_binding_graph import (
    BindingError,
    binding_graph,
    decode_cbor,
    encode_cbor,
    parse_seed_bindings,
)
from tools.alpha4_congruence import (
    CongruenceError,
    check_release_congruence,
    check_source_congruence,
)
from tools.alpha4_operational_expression import derive_operational_graphs
from tools.alpha4_paired_expression import PairedExpressionError, check_paired_expression
from tools.alpha4_relational_expression import derive_relational_graphs
from tools.alpha4_release_profile_congruence import (
    ReleaseProfileCongruenceError,
    check_release_profile_congruence,
)
from tools.build_alpha4_release import build_profiles_tree, build_tree, tree_digest

ROOT = Path(__file__).resolve().parents[1]


def test_seed_line_identity_is_04alpha() -> None:
    bindings = parse_seed_bindings(ROOT)
    assert bindings.subject_id == "ASET-SEED-0.4-ALPHA"
    assert bindings.version == "0.4alpha"
    assert bindings.compatibility_base == "0.3"
    assert bindings.compatibility == "NONE"


def test_seed_tree_has_no_human_or_json_documents() -> None:
    disallowed = [
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "seed/alpha4").rglob("*")
        if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt"}
    ]
    assert disallowed == []
    assert not (ROOT / "docs/alpha4").exists()


def test_binding_source_is_relational_not_semantic_component_declaration() -> None:
    lines = (ROOT / "seed/alpha4/SEED.aset").read_text(encoding="utf-8").splitlines()
    pairs = [line.split() for line in lines if line.startswith("PAIR ")]
    assert len(pairs) == 6
    assert all(len(tokens) == 5 for tokens in pairs)
    assert not any("recognition_in" in line or "recognition_out" in line for line in lines)


def test_binding_graph_is_deterministic_cbor_round_trip() -> None:
    graph = binding_graph(parse_seed_bindings(ROOT))
    encoded_a = encode_cbor(graph)
    encoded_b = encode_cbor(graph)
    assert encoded_a == encoded_b
    decoded, offset = decode_cbor(encoded_a)
    assert offset == len(encoded_a)
    assert decoded == graph
    assert hashlib.sha256(encoded_a).hexdigest() == hashlib.sha256(encoded_b).hexdigest()


def test_binding_graph_contains_only_bindings_and_assurance_edges() -> None:
    graph = binding_graph(parse_seed_bindings(ROOT))
    relations = {row[1] for row in graph[5]}
    assert relations == {
        "BINDS_OPERATIONAL",
        "BINDS_RELATIONAL",
        "CHECKED_BY",
        "DERIVED_BY",
        "FINAL_THEOREM",
        "HAS_COMPONENT",
        "REQUIRES_PROOF",
        "USES_CONGRUENCE",
        "USES_MODULE",
        "VERIFIED_BY",
    }


def test_operational_source_has_no_explanatory_or_component_annotation_comments() -> None:
    text = (ROOT / "seed/alpha4/operational/components.forth").read_text(encoding="utf-8")
    assert "\\ @component" not in text
    assert "semantic source representation" not in text
    assert text.count(": ") == 6


def test_operational_and_relational_sources_derive_same_six_components() -> None:
    operational = derive_operational_graphs(ROOT)
    relational = derive_relational_graphs(ROOT)
    assert len(operational["components"]) == 6
    assert len(relational["components"]) == 6
    assert check_source_congruence(ROOT)["source_pairing"]["components_checked"] == 6


def test_preserve_actions_do_not_require_unused_evidence_argument() -> None:
    text = (ROOT / "seed/alpha4/formal/ComponentRelations.tla").read_text(encoding="utf-8")
    for operator in ("PreserveUnknown", "PreserveAllow", "PreserveBlock"):
        body = text.split(f"{operator}(s, t, e) ==", 1)[1].split("\n\n", 1)[0]
        assert "e \\in EvidenceItems" not in body
        assert "t = s" in body


def test_pairing_proof_binds_all_six_pairs_and_final_theorem() -> None:
    bindings = parse_seed_bindings(ROOT)
    pairing = next(
        item
        for item in bindings.proofs
        if item.proof_id == "OPERATIONAL_RELATIONAL_PAIRING"
    )
    assert pairing.expected_obligations == 13
    assert pairing.final_theorem == "OperationalRelationalPairing"
    text = (ROOT / pairing.module).read_text(encoding="utf-8")
    for pair in bindings.pairs:
        assert f"THEOREM {pair.pairing_theorem}" in text
    assert "THEOREM OperationalRelationalPairing" in text


def test_formal_assurance_total_is_38_obligations() -> None:
    bindings = parse_seed_bindings(ROOT)
    assert [item.expected_obligations for item in bindings.all_proofs] == [14, 11, 13]
    assert sum(item.expected_obligations for item in bindings.all_proofs) == 38


def test_derivation_paths_are_physically_independent() -> None:
    operational = (ROOT / "tools/alpha4_operational_expression.py").read_text(encoding="utf-8")
    relational = (ROOT / "tools/alpha4_relational_expression.py").read_text(encoding="utf-8")
    assert "alpha4_relational_expression" not in operational
    assert "alpha4_operational_expression" not in relational


def test_paired_expression_remains_congruent() -> None:
    evidence = check_paired_expression(ROOT)
    assert evidence["components_checked"] == 6
    assert evidence["cases_checked"] == 1824
    assert evidence["status"] == "PASS"


def test_operational_semantic_drift_is_rejected(tmp_path: Path) -> None:
    copied = tmp_path / "root"
    shutil.copytree(ROOT / "seed", copied / "seed")
    shutil.copytree(ROOT / "assurance", copied / "assurance")
    shutil.copytree(ROOT / "tools", copied / "tools")
    forth = copied / "seed/alpha4/operational/components.forth"
    text = forth.read_text(encoding="utf-8")
    forth.write_text(
        text.replace("UNKNOWN? LOCAL-ALLOW!", "UNKNOWN? LOCAL-BLOCK!", 1),
        encoding="utf-8",
    )
    with pytest.raises((PairedExpressionError, CongruenceError, ValueError)):
        check_paired_expression(copied)


def test_foundation_congruence_survives_nonsemantic_byte_drift(tmp_path: Path) -> None:
    copied = tmp_path / "root"
    shutil.copytree(ROOT / "seed", copied / "seed")
    shutil.copytree(ROOT / "assurance", copied / "assurance")
    shutil.copytree(ROOT / "tools", copied / "tools")
    proof = copied / "assurance/seed-recognition-boundary/formal/RecognitionCardinalityProofs.tla"
    before = hashlib.sha256(proof.read_bytes()).hexdigest()
    proof.write_text(proof.read_text(encoding="utf-8") + "\n\n", encoding="utf-8")
    after = hashlib.sha256(proof.read_bytes()).hexdigest()
    assert before != after
    assert check_source_congruence(copied)["status"] == "PASS"


def test_seed_release_contains_cbor_binding_graph_but_no_human_profiles(tmp_path: Path) -> None:
    release = tmp_path / "release"
    manifest = build_tree(release)
    assert (release / "binding/graph.cbor").is_file()
    assert (release / "binding/graph.cddl").is_file()
    assert not (release / "en").exists()
    assert not (release / "python").exists()
    assert not (release / "expression/en").exists()
    assert not (release / "expression/python").exists()
    assert manifest["version"] == "0.4alpha"
    assert manifest["binding_graph"]["semantic_precedence"] == "NONE"


def test_ci_profiles_are_separate_and_bound_to_seed_release(tmp_path: Path) -> None:
    release = tmp_path / "release"
    build_tree(release)
    digest = tree_digest(release)
    profiles = tmp_path / "profiles"
    manifest = build_profiles_tree(profiles, digest)
    evidence = check_release_profile_congruence(ROOT, profiles)
    assert evidence["english"]["components_checked"] == 6
    assert evidence["python"]["cases_checked"] == 1824
    assert manifest["seed_membership"] == "EXTERNAL_RELEASE_COMPANION"
    assert manifest["semantic_precedence"] == "NONE"
    assert manifest["seed_release_tree_digest"] == digest


def test_corrupt_python_companion_is_rejected(tmp_path: Path) -> None:
    release = tmp_path / "release"
    build_tree(release)
    profiles = tmp_path / "profiles"
    build_profiles_tree(profiles, tree_digest(release))
    python_path = profiles / "python/aset_seed_alpha4.py"
    text = python_path.read_text(encoding="utf-8")
    python_path.write_text(
        text.replace(
            'result["recognition"] = node["value"]',
            'result["recognition"] = "BLOCK"',
            1,
        ),
        encoding="utf-8",
    )
    with pytest.raises(ReleaseProfileCongruenceError):
        check_release_profile_congruence(ROOT, profiles)


def test_corrupt_english_companion_is_rejected(tmp_path: Path) -> None:
    release = tmp_path / "release"
    build_tree(release)
    profiles = tmp_path / "profiles"
    build_profiles_tree(profiles, tree_digest(release))
    english = profiles / "en/Seed.md"
    text = english.read_text(encoding="utf-8")
    english.write_text(text.replace("UNKNOWN -> ALLOW", "UNKNOWN -> BLOCK", 1), encoding="utf-8")
    with pytest.raises(ReleaseProfileCongruenceError):
        check_release_profile_congruence(ROOT, profiles)


def test_release_content_congruence_is_independent_from_companion_profiles(tmp_path: Path) -> None:
    release = tmp_path / "release"
    build_tree(release)
    evidence = check_release_congruence(ROOT, release)
    assert evidence["status"] == "PASS"
    assert "english" not in evidence
    assert "python" not in evidence


def test_release_candidate_workflow_uses_04alpha_names() -> None:
    workflow = (ROOT / ".github/workflows/release-candidate.yml").read_text(encoding="utf-8")
    assert "ASET-Seed-0.4alpha.zip" in workflow
    assert "ASET-Seed-0.4alpha-profiles.zip" in workflow
    assert "0.4.0-alpha.1-bootstrap" not in workflow


def test_old_semantic_json_sources_are_absent() -> None:
    assert not (ROOT / "seed/alpha4/BOOTSTRAP.json").exists()
    assert not (ROOT / "seed/alpha4/source").exists()


def test_binding_parser_rejects_semantic_precedence(tmp_path: Path) -> None:
    copied = tmp_path / "root"
    shutil.copytree(ROOT / "seed", copied / "seed")
    shutil.copytree(ROOT / "assurance", copied / "assurance")
    shutil.copytree(ROOT / "tools", copied / "tools")
    path = copied / "seed/alpha4/SEED.aset"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "SEMANTIC-PRECEDENCE NONE",
            "SEMANTIC-PRECEDENCE BINDING",
            1,
        ),
        encoding="utf-8",
    )
    with pytest.raises(BindingError):
        parse_seed_bindings(copied)


def test_release_manifest_uses_hash_only_as_byte_identity(tmp_path: Path) -> None:
    release = tmp_path / "release"
    manifest = build_tree(release)
    assert manifest["integrity_policy"]["primary_relation"] == "DECLARED_CONTENT_CONGRUENCE"
    assert manifest["integrity_policy"]["digest_role"] == "BYTE_IDENTITY_AND_CACHE_ONLY"
    assert manifest["source_byte_identity_digest"].startswith("sha256:")
    assert "semantic_source_digest" not in manifest
