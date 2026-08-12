#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SEED_RELATIONS = Path("seed/alpha4/SEED.aset")


class BindingError(RuntimeError):
    pass


@dataclass(frozen=True)
class PairBinding:
    component_id: str
    operational_word: str
    formal_operator: str
    pairing_theorem: str


@dataclass(frozen=True)
class ProofBinding:
    proof_id: str
    module: str
    final_theorem: str
    expected_obligations: int


@dataclass(frozen=True)
class SeedBindings:
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
    pairs: tuple[PairBinding, ...]
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
        raise BindingError(message)


def parse_seed_bindings(root: Path = ROOT) -> SeedBindings:
    path = root / SEED_RELATIONS
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if stripped:
            lines.append(stripped.split())
    require(lines, "empty Seed relation source")

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
    pairs: list[PairBinding] = []
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
        elif kind == "PAIR":
            require(len(tokens) == 5, "invalid PAIR relation")
            pairs.append(PairBinding(*tokens[1:]))
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
            raise BindingError(f"unsupported Seed relation: {kind}")

    require(schema_version == 1, "unsupported Seed relation schema")
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
            "CONTENT": "tools/alpha4_congruence.py",
            "PAIRED_EXPRESSION": "tools/alpha4_paired_expression.py",
        },
        "checker bindings mismatch",
    )
    require(
        dict(derivers)
        == {
            "OPERATIONAL": "tools/alpha4_operational_expression.py",
            "RELATIONAL": "tools/alpha4_relational_expression.py",
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
            "ASSEMBLED": "COMPOSITION_PROJECTION_CONGRUENCE",
            "PAIRED_GRAPH": "INDEPENDENT_DERIVATION_CROSS_CONGRUENCE",
            "PAIRED_RUNTIME": "THEORY_PREDICTION_BOUNDED_OBSERVATIONAL_CONGRUENCE",
        },
        "congruence relation bindings mismatch",
    )

    for relative in [
        theory_algebra,
        abstract_machine,
        formal_reflection,
        correctness_model,
        foundation_model,
        foundation_proof.module,
        *(item.module for item in proofs),
        *(path for _, path in checks),
        *(path for _, path in derivers),
    ]:
        require((root / relative).is_file(), f"bound file absent: {relative}")

    return SeedBindings(
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
        pairs=tuple(pairs),
        foundation_model=foundation_model,
        foundation_proof=foundation_proof,
        proofs=tuple(proofs),
        checks=tuple(checks),
        derivers=tuple(derivers),
        relations=tuple(relations),
    )


def _major_type(major: int, value: int) -> bytes:
    if value < 24:
        return bytes([(major << 5) | value])
    if value < 256:
        return bytes([(major << 5) | 24, value])
    if value < 65536:
        return bytes([(major << 5) | 25]) + value.to_bytes(2, "big")
    if value < 2**32:
        return bytes([(major << 5) | 26]) + value.to_bytes(4, "big")
    return bytes([(major << 5) | 27]) + value.to_bytes(8, "big")


def encode_cbor(value: Any) -> bytes:
    if isinstance(value, bool):
        return b"\xf5" if value else b"\xf4"
    if value is None:
        return b"\xf6"
    if isinstance(value, int) and value >= 0:
        return _major_type(0, value)
    if isinstance(value, str):
        payload = value.encode("utf-8")
        return _major_type(3, len(payload)) + payload
    if isinstance(value, (list, tuple)):
        return _major_type(4, len(value)) + b"".join(
            encode_cbor(item) for item in value
        )
    raise BindingError(f"unsupported deterministic CBOR value: {type(value).__name__}")


def _read_uint(data: bytes, offset: int, additional: int) -> tuple[int, int]:
    if additional < 24:
        return additional, offset
    sizes = {24: 1, 25: 2, 26: 4, 27: 8}
    require(additional in sizes, "unsupported CBOR integer additional info")
    size = sizes[additional]
    end = offset + size
    require(end <= len(data), "truncated CBOR integer")
    return int.from_bytes(data[offset:end], "big"), end


def decode_cbor(data: bytes, offset: int = 0) -> tuple[Any, int]:
    require(offset < len(data), "truncated CBOR value")
    initial = data[offset]
    offset += 1
    major = initial >> 5
    additional = initial & 31
    if major == 0:
        return _read_uint(data, offset, additional)
    if major == 3:
        length, offset = _read_uint(data, offset, additional)
        end = offset + length
        require(end <= len(data), "truncated CBOR text")
        return data[offset:end].decode("utf-8"), end
    if major == 4:
        length, offset = _read_uint(data, offset, additional)
        values = []
        for _ in range(length):
            value, offset = decode_cbor(data, offset)
            values.append(value)
        return values, offset
    if major == 7 and additional in {20, 21, 22}:
        return ({20: False, 21: True, 22: None}[additional], offset)
    raise BindingError(f"unsupported CBOR major type: {major}")


def binding_graph(bindings: SeedBindings) -> list[Any]:
    nodes: set[tuple[str, str]] = {("SUBJECT", bindings.subject_id)}
    edges_raw: list[tuple[tuple[str, str], str, tuple[str, str]]] = []
    subject = ("SUBJECT", bindings.subject_id)

    theory = ("THEORY_ALGEBRA", bindings.theory_algebra)
    coding = ("THEORY_CODING", " ".join(bindings.theory_coding))
    abstract_machine = ("ABSTRACT_MACHINE", bindings.abstract_machine)
    reflection = ("FORMAL_REFLECTION", bindings.formal_reflection)
    correctness = ("CORRECTNESS_MODEL", bindings.correctness_model)
    nodes.update({theory, coding, abstract_machine, reflection, correctness})
    edges_raw += [
        (subject, "GROUNDED_IN", theory),
        (subject, "USES_THEORY_CODING", coding),
        (subject, "IMPLEMENTED_BY", abstract_machine),
        (abstract_machine, "IMPLEMENTS", theory),
        (abstract_machine, "REFLECTED_BY", reflection),
        (reflection, "CHECKED_AGAINST", correctness),
        (correctness, "CONSTRAINED_BY", theory),
    ]

    for pair in bindings.pairs:
        component = ("COMPONENT", pair.component_id)
        word = ("OPERATIONAL_SYMBOL", pair.operational_word)
        operator = ("RELATIONAL_SYMBOL", pair.formal_operator)
        theorem = ("PAIRING_THEOREM", pair.pairing_theorem)
        nodes.update({component, word, operator, theorem})
        edges_raw += [
            (subject, "HAS_COMPONENT", component),
            (component, "BINDS_OPERATIONAL", word),
            (component, "BINDS_RELATIONAL", operator),
            (component, "VERIFIED_BY", theorem),
        ]

    for proof in bindings.all_proofs:
        proof_node = ("PROOF_SUBJECT", proof.proof_id)
        module = ("PROOF_MODULE", proof.module)
        theorem = ("FINAL_THEOREM", proof.final_theorem)
        nodes.update({proof_node, module, theorem})
        edges_raw += [
            (subject, "REQUIRES_PROOF", proof_node),
            (proof_node, "USES_MODULE", module),
            (proof_node, "FINAL_THEOREM", theorem),
        ]
        if proof.proof_id == "RECOGNITION_CARDINALITY_FOUNDATION":
            edges_raw.append((theory, "MINIMALITY_PROVED_BY", proof_node))

    for name, path in bindings.checks:
        checker = ("CHECKER", f"{name}:{path}")
        nodes.add(checker)
        edges_raw.append((subject, "CHECKED_BY", checker))
    for name, path in bindings.derivers:
        deriver = ("DERIVER", f"{name}:{path}")
        nodes.add(deriver)
        edges_raw.append((subject, "DERIVED_BY", deriver))
    for name, relation in bindings.relations:
        relation_node = ("CONGRUENCE_RELATION", f"{name}:{relation}")
        nodes.add(relation_node)
        edges_raw.append((subject, "USES_CONGRUENCE", relation_node))

    ordered_nodes = sorted(nodes)
    node_ids = {node: index for index, node in enumerate(ordered_nodes)}
    node_rows = [
        [index, kind, value] for index, (kind, value) in enumerate(ordered_nodes)
    ]
    edge_rows = sorted(
        [
            [node_ids[source], relation, node_ids[target]]
            for source, relation, target in edges_raw
        ],
        key=lambda row: (row[0], row[1], row[2]),
    )
    return [
        "ASET-BINDING-GRAPH",
        1,
        bindings.subject_id,
        bindings.version,
        node_rows,
        edge_rows,
    ]


def graph_digest(graph: list[Any]) -> str:
    return "sha256:" + hashlib.sha256(encode_cbor(graph)).hexdigest()


def write_binding_graph(root: Path, target: Path) -> dict[str, Any]:
    bindings = parse_seed_bindings(root)
    graph = binding_graph(bindings)
    encoded = encode_cbor(graph)
    decoded, offset = decode_cbor(encoded)
    require(
        offset == len(encoded) and decoded == graph,
        "deterministic CBOR round-trip failed",
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(encoded)
    return {
        "document_type": "aset-derived-binding-graph-evidence",
        "subject_id": bindings.subject_id,
        "version": bindings.version,
        "node_count": len(graph[4]),
        "edge_count": len(graph[5]),
        "encoding": "DETERMINISTIC_CBOR_SUBSET",
        "semantic_precedence": "NONE",
        "sha256": "sha256:" + hashlib.sha256(encoded).hexdigest(),
        "status": "PASS",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        bindings = parse_seed_bindings(ROOT)
        graph = binding_graph(bindings)
        encoded = encode_cbor(graph)
        decoded, offset = decode_cbor(encoded)
        require(
            offset == len(encoded) and decoded == graph,
            "deterministic CBOR round-trip failed",
        )
        print(f"ALPHA4_BINDING_PAIRS={len(bindings.pairs)}/{len(bindings.pairs)} PASS")
        print(f"ALPHA4_BINDING_GRAPH_NODES={len(graph[4])}")
        print(f"ALPHA4_BINDING_GRAPH_EDGES={len(graph[5])}")
        print(f"ALPHA4_BINDING_GRAPH_DIGEST={graph_digest(graph)}")
        print("ALPHA4_BINDING_GRAPH=PASS")
        if args.output is not None:
            target = args.output if args.output.is_absolute() else ROOT / args.output
            write_binding_graph(ROOT, target)
        return 0
    except (BindingError, OSError, UnicodeError, ValueError) as error:
        print(f"ALPHA4_BINDING_GRAPH_ERROR={error}")
        print("ALPHA4_BINDING_GRAPH=FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
