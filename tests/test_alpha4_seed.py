from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from tools.alpha4_manifest import ManifestError, parse_seed_manifest
from tools.alpha4_causal_expression import (
    CausalExpressionError,
    check_causal_invariant,
    derive_causal_graphs,
)
from tools.alpha4_congruence import (
    CongruenceError,
    check_release_congruence,
    check_source_congruence,
)
from tools.alpha4_operational_expression import derive_operational_graphs
from tools.alpha4_paired_expression import (
    PairedExpressionError,
    check_paired_expression,
)
from tools.alpha4_relational_expression import derive_relational_graphs
from tools.alpha4_triangulated_expression import (
    TriangulatedExpressionError,
    check_triangulated_expression,
)
from tools.alpha4_release_profile_congruence import (
    ReleaseProfileCongruenceError,
    check_release_profile_congruence,
)
from tools.alpha4_proof_witness_materializer import (
    materialize_witnesses,
    write_witnesses,
)
from tools.build_alpha4_release import build_profiles_tree, build_tree, tree_digest

ROOT = Path(__file__).resolve().parents[1]


def materialized_proof_witnesses(tmp_path: Path) -> Path:
    target = tmp_path / "proof-derived-recognition-witnesses.json"
    write_witnesses(target, materialize_witnesses(ROOT))
    return target


def materialized_release_proof_evidence(release: Path, tmp_path: Path) -> Path:
    assembled = release / "formal/AssembledSeed.tla"
    target = tmp_path / "release-assembled-tlaps-evidence.json"
    target.write_text(
        json.dumps(
            {
                "document_type": "aset-release-assembled-tlaps-evidence",
                "schema_version": 1,
                "scope": "POST_BUILD_DEDUCTIVE_ASSURANCE",
                "semantic_delta": "NONE",
                "semantic_precedence": "NONE",
                "semantic_source_runtime_dependency": "NONE",
                "release_binding": {
                    "tree_digest": tree_digest(release),
                    "assembled_formal": {
                        "path": "formal/AssembledSeed.tla",
                        "sha256": (
                            "sha256:"
                            + hashlib.sha256(assembled.read_bytes()).hexdigest()
                        ),
                    },
                },
                "proof": {
                    "module": "AssembledSeedReleaseProofs",
                    "module_materialization": "EPHEMERAL_VERIFIER_ONLY",
                    "module_sha256": "sha256:test",
                    "final_theorem": "AssembledNextPreservesExactSubjectAndAuthority",
                    "obligations_proved": 1,
                },
                "status": "PASS",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return target


def test_seed_subject_identity_is_04alpha() -> None:
    bindings = parse_seed_manifest(ROOT)
    assert bindings.subject_id == "ASET-SEED-0.4-ALPHA"
    assert bindings.version == "0.4alpha"
    assert bindings.compatibility_base == "0.3"
    assert bindings.compatibility == "NONE"


def test_recognition_foundation_is_theory_local() -> None:
    bindings = parse_seed_manifest(ROOT)
    assert (
        bindings.foundation_model
        == "theory/local-recognition/formal/RecognitionCardinality.tla"
    )
    assert (
        bindings.foundation_proof.module
        == "theory/local-recognition/formal/RecognitionCardinalityProofs.tla"
    )
    assert not (ROOT / "assurance").exists()


def test_seed_tree_has_no_human_or_json_documents() -> None:
    unexpected_documents = [
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "seed/alpha4").rglob("*")
        if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt"}
    ]
    assert unexpected_documents == []
    assert not (ROOT / "docs/alpha4").exists()


def test_binding_source_is_relational_not_semantic_component_declaration() -> None:
    lines = (ROOT / "seed/alpha4/SEED.aset").read_text(encoding="utf-8").splitlines()
    pairs = [line.split() for line in lines if line.startswith("PAIR ")]
    assert len(pairs) == 6
    assert all(len(tokens) == 5 for tokens in pairs)
    assert not any(
        "recognition_in" in line or "recognition_out" in line for line in lines
    )


def test_binding_plan_is_deterministic_and_ephemeral() -> None:
    first = parse_seed_manifest(ROOT)
    second = parse_seed_manifest(ROOT)
    assert first == second
    assert first.semantic_precedence == "NONE"
    assert not (ROOT / "seed/alpha4/binding/graph.cddl").exists()


def test_binding_plan_contains_only_composition_metadata() -> None:
    plan = parse_seed_manifest(ROOT)
    fields = set(plan.__dataclass_fields__)
    assert fields == {
        "schema_version",
        "subject_id",
        "version",
        "compatibility_base",
        "compatibility",
        "digest_role",
        "semantic_precedence",
        "theory_algebra",
        "theory_coding",
        "abstract_machine",
        "formal_reflection",
        "correctness_model",
        "causal_model",
        "pairs",
        "causal_bindings",
        "foundation_model",
        "foundation_proof",
        "proofs",
        "checks",
        "derivers",
        "relations",
    }
    assert "recognition_in" not in fields
    assert "recognition_out" not in fields


def test_local_recognition_theory_precedes_seed_implementation() -> None:
    bindings = parse_seed_manifest(ROOT)
    theory = (ROOT / bindings.theory_algebra).read_text(encoding="utf-8")
    assert bindings.theory_algebra.startswith("theory/local-recognition/")
    assert "EXTENDS RecognitionCardinality" in theory
    assert "ComponentRelations" not in theory
    assert "RestrictedOperationalSemantics" not in theory
    assert "components.forth" not in theory
    assert "components.petri" not in theory
    assert bindings.theory_coding == ("U", "UNKNOWN", "A", "ALLOW", "B", "BLOCK")
    assert bindings.abstract_machine == "seed/alpha4/operational/components.forth"
    assert bindings.formal_reflection.endswith("RestrictedOperationalSemantics.tla")
    assert bindings.correctness_model.endswith("ComponentRelations.tla")
    assert bindings.causal_model == "seed/alpha4/causal/components.petri"


def test_correctness_model_is_explicitly_theory_constrained() -> None:
    bindings = parse_seed_manifest(ROOT)
    text = (ROOT / bindings.correctness_model).read_text(encoding="utf-8")
    assert "EXTENDS FiniteSets, LocalRecognitionAlgebra" in text
    assert "ToTheoryRecognition" in text
    for operator in (
        "TheoryObserveUnknown",
        "TheoryRecognizeAllow",
        "TheoryRecognizeBlock",
        "TheoryPreserveUnknown",
        "TheoryPreserveAllow",
        "TheoryPreserveBlock",
    ):
        assert operator in text
    theory_evidence = check_source_congruence(ROOT)["theory"]
    assert theory_evidence["status"] == "PASS"
    assert theory_evidence["relation"] == "THEORY_ALGEBRA_IMPLEMENTATION_CONGRUENCE"


def test_operational_source_has_no_explanatory_or_component_annotation_comments() -> (
    None
):
    text = (ROOT / "seed/alpha4/operational/components.forth").read_text(
        encoding="utf-8"
    )
    assert "\\ @component" not in text
    assert "semantic source representation" not in text
    assert text.count(": ") == 6


def test_operational_relational_and_causal_sources_derive_same_six_components() -> None:
    operational = derive_operational_graphs(ROOT)
    relational = derive_relational_graphs(ROOT)
    causal = derive_causal_graphs(ROOT)
    assert len(operational["components"]) == 6
    assert len(relational["components"]) == 6
    assert len(causal["components"]) == 6
    evidence = check_source_congruence(ROOT)
    assert evidence["source_pairing"]["components_checked"] == 6
    assert evidence["source_triangulation"]["components_checked"] == 6
    assert evidence["source_triangulation"]["semantic_delta"] == "NONE"


def test_preserve_actions_do_not_require_unused_evidence_argument() -> None:
    text = (ROOT / "seed/alpha4/formal/ComponentRelations.tla").read_text(
        encoding="utf-8"
    )
    for operator in ("PreserveUnknown", "PreserveAllow", "PreserveBlock"):
        body = text.split(f"{operator}(s, t, e) ==", 1)[1].split("\n\n", 1)[0]
        assert "e \\in EvidenceItems" not in body
        assert "t = s" in body


def test_observe_preserve_abstraction_boundary_is_explicitly_proved() -> None:
    bindings = parse_seed_manifest(ROOT)
    component = next(
        item for item in bindings.proofs if item.proof_id == "COMPONENT_COMPOSITION"
    )
    assert component.expected_obligations == 22
    text = (ROOT / component.module).read_text(encoding="utf-8")
    for theorem in (
        "ObserveAndPreserveUnknownShareRecognitionProjection",
        "FreshObserveUnknownIsNotPreserveUnknown",
        "ReobserveUnknownIsPreserveUnknown",
    ):
        assert f"THEOREM {theorem}" in text


def test_pairing_proof_binds_all_six_pairs_and_final_theorem() -> None:
    bindings = parse_seed_manifest(ROOT)
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


def test_formal_assurance_total_is_49_obligations() -> None:
    bindings = parse_seed_manifest(ROOT)
    assert [item.expected_obligations for item in bindings.all_proofs] == [14, 22, 13]
    assert sum(item.expected_obligations for item in bindings.all_proofs) == 49


def test_derivation_paths_are_physically_independent() -> None:
    operational = (ROOT / "tools/alpha4_operational_expression.py").read_text(
        encoding="utf-8"
    )
    relational = (ROOT / "tools/alpha4_relational_expression.py").read_text(
        encoding="utf-8"
    )
    causal = (ROOT / "tools/alpha4_causal_expression.py").read_text(encoding="utf-8")
    assert "alpha4_relational_expression" not in operational
    assert "alpha4_causal_expression" not in operational
    assert "alpha4_operational_expression" not in relational
    assert "alpha4_causal_expression" not in relational
    assert "alpha4_operational_expression" not in causal
    assert "alpha4_relational_expression" not in causal


def test_paired_expression_remains_congruent() -> None:
    evidence = check_paired_expression(ROOT)
    assert evidence["components_checked"] == 6
    assert evidence["cases_checked"] == 1824
    assert (
        evidence["runtime_relation"]
        == "THEORY_PREDICTION_BOUNDED_OBSERVATIONAL_CONGRUENCE"
    )
    assert (
        evidence["prediction_source"]
        == "THEORY_CONSTRAINED_RELATIONAL_CORRECTNESS_MODEL"
    )
    assert evidence["observation_source"] == "ABSTRACT_FORTH_MACHINE_EPHEMERAL_JIT"
    assert evidence["status"] == "PASS"


def test_causal_representation_is_one_safe_and_semantically_neutral() -> None:
    causal = derive_causal_graphs(ROOT)
    invariant = check_causal_invariant(causal)
    assert causal["semantic_precedence"] == "NONE"
    assert invariant["invariant_id"] == "RECOGNITION-ONEHOT"
    assert invariant["transitions_checked"] == 6
    assert invariant["one_safe"] is True
    assert invariant["total"] == 1
    assert invariant["status"] == "PASS"


def test_triangulated_expression_remains_congruent() -> None:
    evidence = check_triangulated_expression(ROOT)
    assert evidence["components_checked"] == 6
    assert evidence["cases_checked"] == 1824
    assert evidence["semantic_delta"] == "NONE"
    assert evidence["pairwise_relations"] == {
        "operational_relational": "PASS",
        "operational_causal": "PASS",
        "relational_causal": "PASS",
    }
    assert evidence["causal_invariant"]["status"] == "PASS"
    assert evidence["status"] == "PASS"


def test_causal_arc_drift_is_rejected(tmp_path: Path) -> None:
    copied = tmp_path / "root"
    shutil.copytree(ROOT / "seed", copied / "seed")
    shutil.copytree(ROOT / "theory", copied / "theory")
    shutil.copytree(ROOT / "tools", copied / "tools")
    causal = copied / "seed/alpha4/causal/components.petri"
    text = causal.read_text(encoding="utf-8")
    causal.write_text(
        text.replace(
            "TRANSITION RECOGNIZE-ALLOW ASET-COMPONENT-RECOGNIZE-ALLOW\n"
            "FROM U\n"
            "REQUIRE EVIDENCE_ARGUMENT\n"
            "REQUIRE OBSERVED_EVIDENCE\n"
            "REQUIRE LOCAL_AUTHORITY_ALLOW\n"
            "TO A",
            "TRANSITION RECOGNIZE-ALLOW ASET-COMPONENT-RECOGNIZE-ALLOW\n"
            "FROM U\n"
            "REQUIRE EVIDENCE_ARGUMENT\n"
            "REQUIRE OBSERVED_EVIDENCE\n"
            "REQUIRE LOCAL_AUTHORITY_ALLOW\n"
            "TO B",
            1,
        ),
        encoding="utf-8",
    )
    with pytest.raises(
        (
            TriangulatedExpressionError,
            CausalExpressionError,
            CongruenceError,
            ValueError,
        )
    ):
        check_triangulated_expression(copied)


def test_causal_invariant_drift_is_rejected(tmp_path: Path) -> None:
    copied = tmp_path / "root"
    shutil.copytree(ROOT / "seed", copied / "seed")
    shutil.copytree(ROOT / "theory", copied / "theory")
    shutil.copytree(ROOT / "tools", copied / "tools")
    causal = copied / "seed/alpha4/causal/components.petri"
    causal.write_text(
        causal.read_text(encoding="utf-8").replace(
            "INVARIANT RECOGNITION-ONEHOT U A B TOTAL 1",
            "INVARIANT RECOGNITION-ONEHOT U A B TOTAL 2",
            1,
        ),
        encoding="utf-8",
    )
    with pytest.raises(
        (CausalExpressionError, TriangulatedExpressionError, ValueError)
    ):
        check_triangulated_expression(copied)


def test_operational_semantic_drift_is_rejected(tmp_path: Path) -> None:
    copied = tmp_path / "root"
    shutil.copytree(ROOT / "seed", copied / "seed")
    shutil.copytree(ROOT / "theory", copied / "theory")
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
    shutil.copytree(ROOT / "theory", copied / "theory")
    shutil.copytree(ROOT / "tools", copied / "tools")
    proof = copied / "theory/local-recognition/formal/RecognitionCardinalityProofs.tla"
    before = hashlib.sha256(proof.read_bytes()).hexdigest()
    proof.write_text(proof.read_text(encoding="utf-8") + "\n\n", encoding="utf-8")
    after = hashlib.sha256(proof.read_bytes()).hexdigest()
    assert before != after
    assert check_source_congruence(copied)["status"] == "PASS"


def test_seed_release_uses_manifest_directly_and_has_no_human_profiles(
    tmp_path: Path,
) -> None:
    release = tmp_path / "release"
    manifest = build_tree(release)
    assert (release / "LICENSE").is_file()
    assert (release / "NOTICE").is_file()
    assert (release / "source/SEED.aset").is_file()
    assert (release / "operational/components.forth").is_file()
    assert (release / "formal/LocalRecognitionAlgebra.tla").is_file()
    assert (release / "causal/components.petri").is_file()
    assert (release / "expression/causal/causal-graph.json").is_file()
    assert not (release / "binding").exists()
    assert not (release / "en").exists()
    assert not (release / "python").exists()
    assert not (release / "expression/en").exists()
    assert not (release / "expression/python").exists()
    assert manifest["version"] == "0.4alpha"
    assert manifest["semantic_algebra"] == {
        "id": "ASET_ALPHA",
        "name": "Local Recognition Algebra",
    }
    assert (
        manifest["architecture"]["abstract_machine"] == "operational/components.forth"
    )
    assert manifest["architecture"]["prediction_observation_relation"] == (
        "THEORY_PREDICTION_BOUNDED_OBSERVATIONAL_CONGRUENCE"
    )
    assert manifest["composition_manifest"] == {
        "path": "source/SEED.aset",
        "role": "NON_SEMANTIC_COMPOSITION_AND_IDENTITY_BINDING",
        "materialization": "DIRECT_SOURCE_COPY",
        "semantic_precedence": "NONE",
    }
    assert manifest["causal_expression"]["semantic_delta"] == "NONE"
    assert manifest["causal_expression"]["semantic_precedence"] == "NONE"
    assert manifest["triangulated_assurance"]["semantic_delta"] == "NONE"
    assert (
        manifest["congruence_assurance"]["triangulated_expression"]["status"] == "PASS"
    )


def test_ci_profiles_are_separate_and_bound_to_seed_release(tmp_path: Path) -> None:
    release = tmp_path / "release"
    build_tree(release)
    digest = tree_digest(release)
    profiles = tmp_path / "profiles"
    manifest = build_profiles_tree(
        profiles, digest, materialized_proof_witnesses(tmp_path)
    )
    evidence = check_release_profile_congruence(ROOT, profiles)
    assert evidence["english"]["components_checked"] == 6
    assert evidence["python_expression_assurance"] == (
        "EXTERNAL_AIRGAP_VERIFIER_REQUIRED"
    )
    assert manifest["seed_membership"] == "EXTERNAL_RELEASE_COMPANION"
    assert manifest["semantic_precedence"] == "NONE"
    assert manifest["seed_release_tree_digest"] == digest
    assert manifest["proof_witness_artifact"]["role"] == (
        "INDEPENDENT_PROOF_DERIVED_EXPRESSION_ORACLE"
    )
    build_source = (ROOT / "tools/build_alpha4_release.py").read_text(encoding="utf-8")
    assert "alpha4_proof_witness_materializer" not in build_source


def test_corrupt_python_companion_is_rejected(tmp_path: Path) -> None:
    from tools.alpha4_expression_airgap_verifier import (
        ExpressionAirgapError,
        check_airgapped_expression,
    )

    release = tmp_path / "release"
    build_tree(release)
    profiles = tmp_path / "profiles"
    witnesses = materialized_proof_witnesses(tmp_path)
    build_profiles_tree(profiles, tree_digest(release), witnesses)
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
    with pytest.raises(ExpressionAirgapError):
        check_airgapped_expression(witnesses, python_path)


def test_corrupt_english_companion_is_rejected(tmp_path: Path) -> None:
    release = tmp_path / "release"
    build_tree(release)
    profiles = tmp_path / "profiles"
    build_profiles_tree(
        profiles, tree_digest(release), materialized_proof_witnesses(tmp_path)
    )
    english = profiles / "en/Seed.md"
    text = english.read_text(encoding="utf-8")
    english.write_text(
        text.replace("UNKNOWN -> ALLOW", "UNKNOWN -> BLOCK", 1), encoding="utf-8"
    )
    with pytest.raises(ReleaseProfileCongruenceError):
        check_release_profile_congruence(ROOT, profiles)


def test_release_content_congruence_is_independent_from_companion_profiles(
    tmp_path: Path,
) -> None:
    release = tmp_path / "release"
    build_tree(release)
    evidence = check_release_congruence(ROOT, release)
    assert evidence["status"] == "PASS"
    assert "english" not in evidence
    assert "python" not in evidence


def test_verify_workflow_uses_single_alpha4_gate() -> None:
    workflows = sorted(path.name for path in (ROOT / ".github/workflows").glob("*.yml"))
    assert workflows == ["verify.yml"]
    workflow = (ROOT / ".github/workflows/verify.yml").read_text(encoding="utf-8")
    assert "python tools/alpha4_seed_gate.py" in workflow
    assert "dist/inpi/**" in workflow


def test_old_semantic_json_sources_are_absent() -> None:
    assert not (ROOT / "seed/alpha4/BOOTSTRAP.json").exists()
    assert not (ROOT / "seed/alpha4/source").exists()


def test_manifest_parser_rejects_semantic_precedence(tmp_path: Path) -> None:
    copied = tmp_path / "root"
    shutil.copytree(ROOT / "seed", copied / "seed")
    shutil.copytree(ROOT / "theory", copied / "theory")
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
    with pytest.raises(ManifestError):
        parse_seed_manifest(copied)


def test_release_manifest_uses_hash_only_as_byte_identity(tmp_path: Path) -> None:
    release = tmp_path / "release"
    manifest = build_tree(release)
    assert (
        manifest["integrity_policy"]["primary_relation"]
        == "DECLARED_CONTENT_CONGRUENCE"
    )
    assert manifest["integrity_policy"]["digest_role"] == "BYTE_IDENTITY_AND_CACHE_ONLY"
    assert manifest["source_byte_identity_digest"].startswith("sha256:")
    assert "semantic_source_digest" not in manifest


def test_public_identity_and_aset_alpha_are_bound() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    assert "ASET — Authority-Seeded Evidence Trail" in readme
    assert 'title: "ASET — Authority-Seeded Evidence Trail"' in citation
    assert "ASET Alpha" in readme
    assert "Local Recognition Algebra" in readme


def test_repository_locator_is_aset_seed_only() -> None:
    repository_url = "https://github.com/attractor-set/aset-seed"
    old_repository_url = "https://github.com/attractor-set/" + "ASET"
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    history = (ROOT / "history/REFERENCES.aset").read_text(encoding="utf-8")
    assert f'repository-code: "{repository_url}"' in citation
    assert f"REPOSITORY {repository_url}" in history

    for relative in (
        "pyproject.toml",
        "CITATION.cff",
        "README.md",
        "history/REFERENCES.aset",
        ".github/workflows/verify.yml",
    ):
        assert old_repository_url not in (ROOT / relative).read_text(encoding="utf-8")


def test_python_sqlite_is_exact_base_expression_persistence_extension(
    tmp_path: Path,
) -> None:
    release = tmp_path / "release"
    build_tree(release)
    profiles = tmp_path / "profiles"
    manifest = build_profiles_tree(
        profiles,
        tree_digest(release),
        materialized_proof_witnesses(tmp_path),
    )
    evidence = check_release_profile_congruence(ROOT, profiles)
    persistence = evidence["python_sqlite_persistence_extension"]
    assert persistence["relation"] == "PERSISTENCE_EXTENSION_OF_EXACT_PYTHON_EXPRESSION"
    assert persistence["semantic_delta"] == "NONE"
    assert manifest["project"] == "Authority-Seeded Evidence Trail (ASET)"
    assert manifest["semantic_algebra"] == {
        "id": "ASET_ALPHA",
        "name": "Local Recognition Algebra",
    }
    python_sqlite = manifest["profiles"]["python_sqlite"]
    assert python_sqlite["role"] == "PERSISTENCE_EXTENSION"
    assert python_sqlite["base_expression"] == "python"
    assert python_sqlite["semantic_delta"] == "NONE"
    assert python_sqlite["assurance"] == "EXTERNAL_PERSISTENCE_PROFILE_GATE_REQUIRED"

    binding = json.loads(
        (profiles / "python-sqlite/PERSISTENCE_EXTENSION.json").read_text(
            encoding="utf-8"
        )
    )
    base_expression = profiles / binding["base_expression"]["path"]
    extension = profiles / binding["extension"]["path"]
    assert binding["relation"] == "PERSISTENCE_EXTENSION"
    assert binding["semantic_delta"] == "NONE"
    assert binding["semantic_precedence"] == "NONE"
    assert binding["base_expression"]["profile"] == "python"
    assert binding["extension"]["profile"] == "python-sqlite"
    assert binding["base_expression"]["sha256"] == (
        "sha256:" + hashlib.sha256(base_expression.read_bytes()).hexdigest()
    )
    source = extension.read_text(encoding="utf-8")
    assert "_base_expression.apply_component" in source
    assert "ASET-COMPONENT-" not in source
    assert '"UNKNOWN"' not in source
    assert '"ALLOW"' not in source
    assert '"BLOCK"' not in source


def test_python_sqlite_persistence_gate_preserves_exact_base_expression(
    tmp_path: Path,
) -> None:
    from tools.alpha4_python_sqlite_persistence_gate import (
        check_python_sqlite_persistence,
    )

    release = tmp_path / "release"
    build_tree(release)
    profiles = tmp_path / "profiles"
    build_profiles_tree(
        profiles,
        tree_digest(release),
        materialized_proof_witnesses(tmp_path),
    )
    evidence = check_python_sqlite_persistence(profiles)
    runtime = evidence["runtime"]
    assert evidence["relation"] == "PERSISTENCE_EXTENSION"
    assert evidence["semantic_delta"] == "NONE"
    assert runtime["base_expression_congruence_cases"] == 1824
    assert runtime["restart_round_trip_components"] == 6
    assert runtime["rollback_checks"] > 0
    assert runtime["status"] == "PASS"
    boundary = evidence["materialization_boundary"]
    assert boundary["profile_tree_unchanged"] is True
    assert boundary["python_bytecode_written"] is False
    assert (
        boundary["profile_tree_digest_before"] == boundary["profile_tree_digest_after"]
    )


def test_python_sqlite_rejects_semantic_logic_in_persistence_layer(
    tmp_path: Path,
) -> None:
    from tools.alpha4_python_sqlite_persistence_gate import (
        PythonSQLitePersistenceError,
        check_python_sqlite_persistence,
    )

    release = tmp_path / "release"
    build_tree(release)
    profiles = tmp_path / "profiles"
    build_profiles_tree(
        profiles,
        tree_digest(release),
        materialized_proof_witnesses(tmp_path),
    )
    binding_path = profiles / "python-sqlite/PERSISTENCE_EXTENSION.json"
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    extension = profiles / binding["extension"]["path"]
    extension.write_text(
        extension.read_text(encoding="utf-8") + '\nSEMANTIC_DRIFT = "ALLOW"\n',
        encoding="utf-8",
    )
    binding["extension"]["sha256"] = (
        "sha256:" + hashlib.sha256(extension.read_bytes()).hexdigest()
    )
    binding_path.write_text(
        json.dumps(binding, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(PythonSQLitePersistenceError):
        check_python_sqlite_persistence(profiles)


def test_python_sqlite_rejects_base_expression_byte_drift(tmp_path: Path) -> None:
    from tools.alpha4_python_sqlite_persistence_gate import (
        PythonSQLitePersistenceError,
        check_python_sqlite_persistence,
    )

    release = tmp_path / "release"
    build_tree(release)
    profiles = tmp_path / "profiles"
    build_profiles_tree(
        profiles,
        tree_digest(release),
        materialized_proof_witnesses(tmp_path),
    )
    base_expression = profiles / "python/aset_seed_alpha4.py"
    base_expression.write_text(
        base_expression.read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )
    with pytest.raises(PythonSQLitePersistenceError):
        check_python_sqlite_persistence(profiles)


def test_verify_workflow_uploads_expression_and_persistence_evidence() -> None:
    workflow = (ROOT / ".github/workflows/verify.yml").read_text(encoding="utf-8")
    assert "dist/airgap-expression-evidence.json" in workflow
    assert "dist/python-sqlite-persistence-evidence.json" in workflow
    assert "dist/release-admission-certificate.json" in workflow
    assert "dist/public-release-audit.json" in workflow


def test_release_admission_certificate_binds_independent_evidence(
    tmp_path: Path,
) -> None:
    from tools.alpha4_expression_airgap_verifier import check_airgapped_expression
    from tools.alpha4_python_sqlite_persistence_gate import (
        check_python_sqlite_persistence,
    )
    from tools.alpha4_release_admission_certificate import check_release_admission
    from tools.build_alpha4_release import zip_tree

    release = tmp_path / "release"
    build_tree(release)
    witnesses = materialized_proof_witnesses(tmp_path)
    profiles = tmp_path / "profiles"
    build_profiles_tree(profiles, tree_digest(release), witnesses)

    expression_evidence = tmp_path / "airgap.json"
    expression_evidence.write_text(
        json.dumps(
            check_airgapped_expression(
                witnesses,
                profiles / "python/aset_seed_alpha4.py",
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    persistence_evidence = tmp_path / "persistence.json"
    persistence_evidence.write_text(
        json.dumps(
            check_python_sqlite_persistence(profiles),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    release_proof_evidence = materialized_release_proof_evidence(release, tmp_path)

    release_archive = tmp_path / "release.zip"
    profiles_archive = tmp_path / "profiles.zip"
    zip_tree(release, release_archive, "ASET-Seed-0.4alpha")
    zip_tree(profiles, profiles_archive, "ASET-Seed-0.4alpha-profiles")

    certificate = check_release_admission(
        witnesses,
        expression_evidence,
        persistence_evidence,
        release_proof_evidence,
        release,
        profiles,
        release_archive,
        profiles_archive,
    )
    assert certificate["project"] == "Authority-Seeded Evidence Trail (ASET)"
    assert certificate["semantic_algebra"] == {
        "id": "ASET_ALPHA",
        "name": "Local Recognition Algebra",
    }
    post_build = certificate["evidence"]["post_build_formal_assurance"]
    assert post_build["status"] == "PASS"
    assert post_build["final_theorem"] == (
        "AssembledNextPreservesExactSubjectAndAuthority"
    )
    assert post_build["semantic_delta"] == "NONE"
    triangulated = certificate["evidence"]["triangulated_assurance"]
    assert triangulated["representations"] == ["OPERATIONAL", "RELATIONAL", "CAUSAL"]
    assert triangulated["components_checked"] == 6
    assert triangulated["cases_checked"] == 1824
    assert triangulated["causal_invariant"] == "PASS"
    assert triangulated["semantic_delta"] == "NONE"
    assert certificate["evidence"]["python_airgap"]["cases_checked"] == 1824
    sqlite = certificate["evidence"]["python_sqlite_persistence"]
    assert sqlite["base_expression_congruence_cases"] == 1824
    assert sqlite["semantic_delta"] == "NONE"
    assert certificate["status"] == "PASS"


def test_release_admission_rejects_expression_base_mismatch(tmp_path: Path) -> None:
    from tools.alpha4_expression_airgap_verifier import check_airgapped_expression
    from tools.alpha4_python_sqlite_persistence_gate import (
        check_python_sqlite_persistence,
    )
    from tools.alpha4_release_admission_certificate import (
        ReleaseAdmissionError,
        check_release_admission,
    )
    from tools.build_alpha4_release import zip_tree

    release = tmp_path / "release"
    build_tree(release)
    witnesses = materialized_proof_witnesses(tmp_path)
    profiles = tmp_path / "profiles"
    build_profiles_tree(profiles, tree_digest(release), witnesses)

    expression_evidence = tmp_path / "airgap.json"
    expression = check_airgapped_expression(
        witnesses,
        profiles / "python/aset_seed_alpha4.py",
    )
    expression["verifier_inputs"]["expression_artifact"]["sha256"] = "sha256:00"
    expression_evidence.write_text(
        json.dumps(expression, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    persistence_evidence = tmp_path / "persistence.json"
    persistence_evidence.write_text(
        json.dumps(
            check_python_sqlite_persistence(profiles),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    release_proof_evidence = materialized_release_proof_evidence(release, tmp_path)

    release_archive = tmp_path / "release.zip"
    profiles_archive = tmp_path / "profiles.zip"
    zip_tree(release, release_archive, "ASET-Seed-0.4alpha")
    zip_tree(profiles, profiles_archive, "ASET-Seed-0.4alpha-profiles")

    with pytest.raises(ReleaseAdmissionError):
        check_release_admission(
            witnesses,
            expression_evidence,
            persistence_evidence,
            release_proof_evidence,
            release,
            profiles,
            release_archive,
            profiles_archive,
        )


def test_public_release_audit_binds_neutral_public_identity(tmp_path: Path) -> None:
    from tools.alpha4_expression_airgap_verifier import check_airgapped_expression
    from tools.alpha4_public_release_audit import check_public_release
    from tools.alpha4_python_sqlite_persistence_gate import (
        check_python_sqlite_persistence,
    )
    from tools.alpha4_release_admission_certificate import check_release_admission
    from tools.build_alpha4_release import zip_tree

    release = tmp_path / "release"
    build_tree(release)
    witnesses = materialized_proof_witnesses(tmp_path)
    profiles = tmp_path / "profiles"
    build_profiles_tree(profiles, tree_digest(release), witnesses)

    expression_evidence = tmp_path / "airgap.json"
    expression_evidence.write_text(
        json.dumps(
            check_airgapped_expression(
                witnesses,
                profiles / "python/aset_seed_alpha4.py",
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    persistence_evidence = tmp_path / "persistence.json"
    persistence_evidence.write_text(
        json.dumps(
            check_python_sqlite_persistence(profiles),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    release_proof_evidence = materialized_release_proof_evidence(release, tmp_path)

    release_archive = tmp_path / "release.zip"
    profiles_archive = tmp_path / "profiles.zip"
    zip_tree(release, release_archive, "ASET-Seed-0.4alpha")
    zip_tree(profiles, profiles_archive, "ASET-Seed-0.4alpha-profiles")

    certificate_path = tmp_path / "certificate.json"
    certificate_path.write_text(
        json.dumps(
            check_release_admission(
                witnesses,
                expression_evidence,
                persistence_evidence,
                release_proof_evidence,
                release,
                profiles,
                release_archive,
                profiles_archive,
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    evidence = check_public_release(ROOT, release, profiles, certificate_path)
    assert evidence["project"] == "Authority-Seeded Evidence Trail (ASET)"
    assert evidence["semantic_algebra"] == {
        "id": "ASET_ALPHA",
        "name": "Local Recognition Algebra",
    }
    assert evidence["post_build_formal_assurance"] == "PASS"
    assert evidence["representation_id"] == "0.4alpha"
    assert evidence["assurance_representations"] == [
        "OPERATIONAL",
        "RELATIONAL",
        "CAUSAL",
    ]
    assert evidence["assurance_semantic_delta"] == "NONE"
    assert evidence["python_sqlite_role"] == "PERSISTENCE_EXTENSION"
    assert evidence["python_sqlite_semantic_delta"] == "NONE"
    assert evidence["status"] == "PASS"


def test_post_build_tlaps_verifier_binds_materialized_release(tmp_path: Path) -> None:
    from tools.run_alpha4_release_tlaps import FINAL_THEOREM, check_release_tlaps

    release = tmp_path / "release"
    build_tree(release)
    fake_tlapm = tmp_path / "tlapm"
    fake_tlapm.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "import sys\n"
        "verifier = Path(sys.argv[-1]).read_text(encoding='utf-8')\n"
        "cache = Path('.tlacache')\n"
        "cache.mkdir(parents=True, exist_ok=True)\n"
        "(cache / 'probe').write_text('cache', encoding='utf-8')\n"
        "assert 'EXTENDS AssembledSeed, TLAPS' in verifier\n"
        "assert 'AssembledNextPreservesExactSubjectAndAuthority' in verifier\n"
        "print('All 1 obligation proved.')\n",
        encoding="utf-8",
    )
    fake_tlapm.chmod(0o755)

    release_tree_before = tree_digest(release)
    evidence = check_release_tlaps(release, str(fake_tlapm))
    assembled = release / "formal/AssembledSeed.tla"
    assert evidence["scope"] == "POST_BUILD_DEDUCTIVE_ASSURANCE"
    assert evidence["semantic_delta"] == "NONE"
    assert evidence["semantic_source_runtime_dependency"] == "NONE"
    assert evidence["release_binding"]["tree_digest"] == release_tree_before
    assert tree_digest(release) == release_tree_before
    assert not (release / ".tlacache").exists()
    assert evidence["release_binding"]["assembled_formal"]["sha256"] == (
        "sha256:" + hashlib.sha256(assembled.read_bytes()).hexdigest()
    )
    assert evidence["proof"]["final_theorem"] == FINAL_THEOREM
    assert evidence["proof"]["obligations_proved"] == 1
    assert evidence["status"] == "PASS"


def test_release_admission_rejects_post_build_proof_byte_mismatch(
    tmp_path: Path,
) -> None:
    from tools.alpha4_expression_airgap_verifier import check_airgapped_expression
    from tools.alpha4_python_sqlite_persistence_gate import (
        check_python_sqlite_persistence,
    )
    from tools.alpha4_release_admission_certificate import (
        ReleaseAdmissionError,
        check_release_admission,
    )
    from tools.build_alpha4_release import zip_tree

    release = tmp_path / "release"
    build_tree(release)
    witnesses = materialized_proof_witnesses(tmp_path)
    profiles = tmp_path / "profiles"
    build_profiles_tree(profiles, tree_digest(release), witnesses)

    expression_evidence = tmp_path / "airgap.json"
    expression_evidence.write_text(
        json.dumps(
            check_airgapped_expression(
                witnesses,
                profiles / "python/aset_seed_alpha4.py",
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    persistence_evidence = tmp_path / "persistence.json"
    persistence_evidence.write_text(
        json.dumps(
            check_python_sqlite_persistence(profiles),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    release_proof_evidence = materialized_release_proof_evidence(release, tmp_path)
    proof = json.loads(release_proof_evidence.read_text(encoding="utf-8"))
    proof["release_binding"]["assembled_formal"]["sha256"] = "sha256:00"
    release_proof_evidence.write_text(
        json.dumps(proof, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    release_archive = tmp_path / "release.zip"
    profiles_archive = tmp_path / "profiles.zip"
    zip_tree(release, release_archive, "ASET-Seed-0.4alpha")
    zip_tree(profiles, profiles_archive, "ASET-Seed-0.4alpha-profiles")

    with pytest.raises(ReleaseAdmissionError):
        check_release_admission(
            witnesses,
            expression_evidence,
            persistence_evidence,
            release_proof_evidence,
            release,
            profiles,
            release_archive,
            profiles_archive,
        )
