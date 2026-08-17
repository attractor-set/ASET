#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED_MANIFEST = Path("seed/alpha4/SEED.aset")


class ManifestError(RuntimeError):
    pass


@dataclass(frozen=True)
class PairBinding:
    component_id: str
    operational_word: str
    formal_operator: str
    pairing_theorem: str


@dataclass(frozen=True)
class CausalBinding:
    component_id: str
    causal_transition: str


@dataclass(frozen=True)
class ProofBinding:
    proof_id: str
    module: str
    final_theorem: str
    expected_obligations: int


@dataclass(frozen=True)
class BindingPlan:
    schema_version: int
    subject_id: str
    version: str
    compatibility_base: str
    compatibility: str
    digest_role: str
    semantic_precedence: str
    theory_algebra: str
    theory_coding: tuple[str, ...]
    abstract_machine: str
    formal_reflection: str
    correctness_model: str
    causal_model: str
    pairs: tuple[PairBinding, ...]
    causal_bindings: tuple[CausalBinding, ...]
    foundation_model: str
    foundation_proof: ProofBinding
    proofs: tuple[ProofBinding, ...]
    checks: tuple[tuple[str, str], ...]
    derivers: tuple[tuple[str, str], ...]
    relations: tuple[tuple[str, str], ...]

    @property
    def all_proofs(self) -> tuple[ProofBinding, ...]:
        return (self.foundation_proof, *self.proofs)

    def check_map(self) -> dict[str, str]:
        return dict(self.checks)

    def deriver_map(self) -> dict[str, str]:
        return dict(self.derivers)

    def relation_map(self) -> dict[str, str]:
        return dict(self.relations)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ManifestError(message)


def parse_seed_manifest(root: Path = ROOT) -> BindingPlan:
    path = root / SEED_MANIFEST
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if stripped:
            lines.append(stripped.split())
    require(lines, "empty Seed composition manifest")

    head = lines[0]
    require(len(head) == 4 and head[0] == "ASET-SEED", "invalid ASET-SEED header")
    schema_version = int(head[1])
    subject_id = head[2]
    version = head[3]

    compatibility_base = ""
    compatibility = ""
    digest_role = ""
    semantic_precedence = ""
    theory_algebra = ""
    theory_coding: tuple[str, ...] = ()
    abstract_machine = ""
    formal_reflection = ""
    correctness_model = ""
    causal_model = ""
    pairs: list[PairBinding] = []
    causal_bindings: list[CausalBinding] = []
    foundation_model = ""
    foundation_proof: ProofBinding | None = None
    proofs: list[ProofBinding] = []
    checks: list[tuple[str, str]] = []
    derivers: list[tuple[str, str]] = []
    relations: list[tuple[str, str]] = []

    for tokens in lines[1:]:
        kind = tokens[0]
        if kind == "COMPATIBILITY":
            require(len(tokens) == 3, "invalid COMPATIBILITY relation")
            compatibility_base, compatibility = tokens[1], tokens[2]
        elif kind == "DIGEST-ROLE":
            require(len(tokens) == 2, "invalid DIGEST-ROLE relation")
            digest_role = tokens[1]
        elif kind == "SEMANTIC-PRECEDENCE":
            require(len(tokens) == 2, "invalid SEMANTIC-PRECEDENCE relation")
            semantic_precedence = tokens[1]
        elif kind == "THEORY-ALGEBRA":
            require(len(tokens) == 2, "invalid THEORY-ALGEBRA relation")
            theory_algebra = tokens[1]
        elif kind == "THEORY-CODING":
            require(len(tokens) == 7, "invalid THEORY-CODING relation")
            theory_coding = tuple(tokens[1:])
        elif kind == "ABSTRACT-MACHINE":
            require(len(tokens) == 2, "invalid ABSTRACT-MACHINE relation")
            abstract_machine = tokens[1]
        elif kind == "FORMAL-REFLECTION":
            require(len(tokens) == 2, "invalid FORMAL-REFLECTION relation")
            formal_reflection = tokens[1]
        elif kind == "CORRECTNESS-MODEL":
            require(len(tokens) == 2, "invalid CORRECTNESS-MODEL relation")
            correctness_model = tokens[1]
        elif kind == "CAUSAL-MODEL":
            require(len(tokens) == 2, "invalid CAUSAL-MODEL relation")
            causal_model = tokens[1]
        elif kind == "PAIR":
            require(len(tokens) == 5, "invalid PAIR relation")
            pairs.append(PairBinding(*tokens[1:]))
        elif kind == "CAUSAL-BIND":
            require(len(tokens) == 3, "invalid CAUSAL-BIND relation")
            causal_bindings.append(CausalBinding(tokens[1], tokens[2]))
        elif kind == "FOUNDATION-MODEL":
            require(len(tokens) == 2, "invalid FOUNDATION-MODEL relation")
            foundation_model = tokens[1]
        elif kind == "FOUNDATION-PROOF":
            require(len(tokens) == 4, "invalid FOUNDATION-PROOF relation")
            foundation_proof = ProofBinding(
                "RECOGNITION_CARDINALITY_FOUNDATION",
                tokens[1],
                tokens[2],
                int(tokens[3]),
            )
        elif kind == "PROOF":
            require(len(tokens) == 5, "invalid PROOF relation")
            proofs.append(ProofBinding(tokens[1], tokens[2], tokens[3], int(tokens[4])))
        elif kind == "CHECK":
            require(len(tokens) == 3, "invalid CHECK relation")
            checks.append((tokens[1], tokens[2]))
        elif kind == "DERIVER":
            require(len(tokens) == 3, "invalid DERIVER relation")
            derivers.append((tokens[1], tokens[2]))
        elif kind == "RELATION":
            require(len(tokens) == 3, "invalid RELATION relation")
            relations.append((tokens[1], tokens[2]))
        else:
            raise ManifestError(f"unsupported Seed manifest declaration: {kind}")

    require(schema_version == 1, "unsupported Seed manifest schema")
    require(subject_id == "ASET-SEED-0.4-ALPHA", "subject id mismatch")
    require(version == "0.4alpha", "Seed version mismatch")
    require(
        compatibility_base == "0.3" and compatibility == "NONE",
        "compatibility mismatch",
    )
    require(digest_role == "BYTE_IDENTITY_AND_CACHE_ONLY", "digest role mismatch")
    require(
        semantic_precedence == "NONE", "binding layer semantic precedence must be NONE"
    )
    require(
        theory_algebra == "theory/local-recognition/formal/LocalRecognitionAlgebra.tla",
        "local-recognition theory binding mismatch",
    )
    require(
        theory_coding == ("U", "UNKNOWN", "A", "ALLOW", "B", "BLOCK"),
        "theory-to-Seed recognition coding mismatch",
    )
    require(
        abstract_machine == "seed/alpha4/operational/components.forth",
        "abstract machine binding mismatch",
    )
    require(
        formal_reflection == "seed/alpha4/formal/RestrictedOperationalSemantics.tla",
        "formal reflection binding mismatch",
    )
    require(
        correctness_model == "seed/alpha4/formal/ComponentRelations.tla",
        "correctness model binding mismatch",
    )
    require(
        causal_model == "seed/alpha4/causal/components.petri",
        "causal model binding mismatch",
    )
    require(len(pairs) == 6, "expected six component pair bindings")
    require(
        len({item.component_id for item in pairs}) == len(pairs),
        "duplicate component id",
    )
    require(
        len({item.operational_word for item in pairs}) == len(pairs),
        "duplicate operational word",
    )
    require(
        len({item.formal_operator for item in pairs}) == len(pairs),
        "duplicate formal operator",
    )
    require(
        len({item.pairing_theorem for item in pairs}) == len(pairs),
        "duplicate pairing theorem",
    )
    require(len(causal_bindings) == 6, "expected six causal component bindings")
    require(
        {item.component_id for item in causal_bindings}
        == {item.component_id for item in pairs},
        "causal component identity set differs from paired component identity set",
    )
    require(
        len({item.causal_transition for item in causal_bindings})
        == len(causal_bindings),
        "duplicate causal transition",
    )
    require(
        foundation_model
        == "theory/local-recognition/formal/RecognitionCardinality.tla",
        "recognition cardinality foundation model must be theory-local",
    )
    require(foundation_proof is not None, "foundation proof binding missing")
    require(
        foundation_proof.module
        == "theory/local-recognition/formal/RecognitionCardinalityProofs.tla",
        "recognition cardinality proof must be theory-local",
    )
    require(
        dict(checks)
        == {
            "ASSURANCE": "tools/alpha4_assurance.py",
            "RELEASE_CONGRUENCE": "tools/alpha4_congruence.py",
        },
        "checker bindings mismatch",
    )
    require(
        dict(derivers)
        == {
            "OPERATIONAL": "tools/alpha4_operational_expression.py",
            "RELATIONAL": "tools/alpha4_relational_expression.py",
            "CAUSAL": "tools/alpha4_causal_expression.py",
        },
        "deriver bindings mismatch",
    )
    require(
        dict(relations)
        == {
            "FOUNDATION": "NORMALIZED_DECLARATIVE_CLAIM_CONGRUENCE",
            "THEORY": "THEORY_ALGEBRA_IMPLEMENTATION_CONGRUENCE",
            "OPERATIONAL": "TYPED_OPERATIONAL_SOURCE_PROJECTION_CONGRUENCE",
            "RELATIONAL": "DECLARED_RELATION_PROJECTION_CONGRUENCE",
            "CAUSAL": "RESTRICTED_CAUSAL_SOURCE_PROJECTION_CONGRUENCE",
            "ASSEMBLED": "COMPOSITION_PROJECTION_CONGRUENCE",
            "PAIRED_GRAPH": "INDEPENDENT_DERIVATION_CROSS_CONGRUENCE",
            "PAIRED_RUNTIME": "THEORY_PREDICTION_BOUNDED_OBSERVATIONAL_CONGRUENCE",
            "OPERATIONAL_CAUSAL": "OPERATIONAL_CAUSAL_SOURCE_PROJECTION_CONGRUENCE",
            "OPERATIONAL_CAUSAL_INTERFACE": (
                "STACK_EFFECT_EVIDENCE_REQUIREMENT_CONGRUENCE"
            ),
            "RELATIONAL_CAUSAL": "RELATIONAL_CAUSAL_SOURCE_PROJECTION_CONGRUENCE",
            "TRIANGULATED_GRAPH": "THREE_WAY_INDEPENDENT_DERIVATION_CONGRUENCE",
            "TRIANGULATED_RUNTIME": "THREE_WAY_BOUNDED_OBSERVATIONAL_CONGRUENCE",
        },
        "congruence relation bindings mismatch",
    )

    for relative in [
        theory_algebra,
        abstract_machine,
        formal_reflection,
        correctness_model,
        causal_model,
        foundation_model,
        foundation_proof.module,
        *(item.module for item in proofs),
        *(path for _, path in checks),
        *(path for _, path in derivers),
    ]:
        require((root / relative).is_file(), f"bound file absent: {relative}")

    return BindingPlan(
        schema_version=schema_version,
        subject_id=subject_id,
        version=version,
        compatibility_base=compatibility_base,
        compatibility=compatibility,
        digest_role=digest_role,
        semantic_precedence=semantic_precedence,
        theory_algebra=theory_algebra,
        theory_coding=theory_coding,
        abstract_machine=abstract_machine,
        formal_reflection=formal_reflection,
        correctness_model=correctness_model,
        causal_model=causal_model,
        pairs=tuple(pairs),
        causal_bindings=tuple(causal_bindings),
        foundation_model=foundation_model,
        foundation_proof=foundation_proof,
        proofs=tuple(proofs),
        checks=tuple(checks),
        derivers=tuple(derivers),
        relations=tuple(relations),
    )


def main() -> int:
    try:
        plan = parse_seed_manifest(ROOT)
        count = len(plan.pairs)
        print(f"ALPHA4_MANIFEST_COMPONENT_BINDINGS={count}/{count} PASS")
        print(
            "ALPHA4_MANIFEST_CAUSAL_BINDINGS="
            f"{len(plan.causal_bindings)}/{len(plan.causal_bindings)} PASS"
        )
        print(f"ALPHA4_MANIFEST_SEMANTIC_PRECEDENCE={plan.semantic_precedence}")
        print("ALPHA4_BINDING_PLAN=PASS")
        return 0
    except (ManifestError, OSError, UnicodeError, ValueError) as error:
        print(f"ALPHA4_MANIFEST_ERROR={error}")
        print("ALPHA4_BINDING_PLAN=FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
