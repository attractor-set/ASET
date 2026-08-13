#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPOSITORY_URL = "https://github.com/attractor-set/aset-seed"
OLD_REPOSITORY_URL = "https://github.com/attractor-set/" + "ASET"
REPOSITORY_LOCATOR_SURFACES = (
    "pyproject.toml",
    "CITATION.cff",
    "README.md",
    "history/REFERENCES.aset",
    ".github/workflows/verify.yml",
)

ALLOWED_ROOT_FILES = {
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
    "CITATION.cff",
    "LICENSE",
    "NOTICE",
    "README.md",
    "pyproject.toml",
    "requirements-ci.txt",
}
ALLOWED_ROOT_DIRS = {
    ".github",
    "history",
    "seed",
    "tests",
    "theory",
    "tools",
}
IGNORED_ROOT_DIRS = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".tlacache",
    ".tooling",
    ".venv",
    "__pycache__",
    "dist",
}
ALLOWED_ACTIVE_PATHS = {
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
    ".github/workflows/verify.yml",
    "CITATION.cff",
    "LICENSE",
    "NOTICE",
    "README.md",
    "history/REFERENCES.aset",
    "pyproject.toml",
    "requirements-ci.txt",
    "seed/alpha4/SEED.aset",
    "seed/alpha4/causal/components.petri",
    "seed/alpha4/formal/ComponentCompositionProofs.tla",
    "seed/alpha4/formal/ComponentRelations.tla",
    "seed/alpha4/formal/OperationalRelationalPairingProofs.tla",
    "seed/alpha4/formal/RestrictedOperationalSemantics.tla",
    "seed/alpha4/operational/components.forth",
    "tests/test_alpha4_seed.py",
    "theory/local-recognition/formal/LocalRecognitionAlgebra.tla",
    "theory/local-recognition/formal/RecognitionCardinality.tla",
    "theory/local-recognition/formal/RecognitionCardinalityProofs.tla",
    "tools/alpha4_manifest.py",
    "tools/alpha4_assurance.py",
    "tools/alpha4_causal_expression.py",
    "tools/alpha4_congruence.py",
    "tools/alpha4_expression_airgap_verifier.py",
    "tools/alpha4_operational_expression.py",
    "tools/alpha4_paired_expression.py",
    "tools/alpha4_proof_witness_materializer.py",
    "tools/alpha4_public_release_audit.py",
    "tools/alpha4_python_sqlite_persistence_gate.py",
    "tools/alpha4_release_admission_certificate.py",
    "tools/alpha4_relational_expression.py",
    "tools/alpha4_release_profile_congruence.py",
    "tools/alpha4_release_profiles.py",
    "tools/alpha4_seed_gate.py",
    "tools/alpha4_triangulated_expression.py",
    "tools/build_alpha4_release.py",
    "tools/run_alpha4_tlaps.py",
    "tools/run_alpha4_release_tlaps.py",
    "tools/validate_alpha4_seed.py",
    "tools/validate_repository_minimal.py",
}


def version_control_visible_files() -> set[str]:
    """Return the prospective version-controlled worktree surface.

    This includes existing tracked files plus non-ignored untracked files, while
    excluding tracked paths deleted in the worktree.  Local generated artifacts
    covered by .gitignore therefore do not become repository semantics, but any
    non-ignored file that could enter the next commit is still audited.
    """
    import subprocess

    result = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(
            "git ls-files failed while resolving active repository surface"
        )

    visible: set[str] = set()
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        relative = raw.decode("utf-8")
        path = ROOT / relative
        if path.is_file() or path.is_symlink():
            visible.add(relative)
    return visible


def main() -> int:
    errors: list[str] = []

    try:
        active_files = version_control_visible_files()
    except (OSError, RuntimeError, UnicodeError) as error:
        print(f"REPOSITORY_MINIMALITY_ERROR={error}")
        print("REPOSITORY_ACTIVE_SURFACE=FAIL")
        return 1

    root_files = {path for path in active_files if "/" not in path}
    extra_files = sorted(root_files - ALLOWED_ROOT_FILES)
    missing_files = sorted(ALLOWED_ROOT_FILES - root_files)
    if extra_files:
        errors.append("unexpected root files: " + ", ".join(extra_files))
    if missing_files:
        errors.append("required root files missing: " + ", ".join(missing_files))

    root_dirs = {path.split("/", 1)[0] for path in active_files if "/" in path}
    extra_dirs = sorted(root_dirs - ALLOWED_ROOT_DIRS)
    missing_dirs = sorted(ALLOWED_ROOT_DIRS - root_dirs)
    if extra_dirs:
        errors.append("unexpected active root directories: " + ", ".join(extra_dirs))
    if missing_dirs:
        errors.append(
            "required active root directories missing: " + ", ".join(missing_dirs)
        )

    unexpected_active = sorted(active_files - ALLOWED_ACTIVE_PATHS)
    missing_active = sorted(ALLOWED_ACTIVE_PATHS - active_files)
    if unexpected_active:
        errors.append("unexpected active files: " + ", ".join(unexpected_active))
    if missing_active:
        errors.append("required active files missing: " + ", ".join(missing_active))

    seed_paths = {path for path in active_files if path.startswith("seed/")}
    if any(not path.startswith("seed/alpha4/") for path in seed_paths):
        errors.append(
            "seed/ must contain only alpha4/ in the version-controlled surface"
        )

    notice = (ROOT / "NOTICE").read_text(encoding="utf-8")
    if "Copyright 2026 Dzmitry Prychyna" not in notice:
        errors.append("copyright holder missing from NOTICE")
    if "Attractor Set" not in notice:
        errors.append("project identity missing from NOTICE")

    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    for required in (
        'version: "0.4alpha"',
        'family-names: "Prychyna"',
        'given-names: "Dzmitry"',
        f'repository-code: "{REPOSITORY_URL}"',
    ):
        if required not in citation:
            errors.append(f"citation attribution missing: {required}")

    history = (ROOT / "history/REFERENCES.aset").read_text(encoding="utf-8")
    for required in (
        f"REPOSITORY {REPOSITORY_URL}",
        "COMMIT 633c130187b2a2bb42f24cfd66662d475de385d2",
        "COMMIT e89d984203a126f8bc62467224cdf6c5374dada7",
        "COMPATIBILITY ASET-SEED-0.4-ALPHA SEED-0.3.0-ALPHA.3 NONE",
    ):
        if required not in history:
            errors.append(f"historical reference missing: {required}")

    for relative in REPOSITORY_LOCATOR_SURFACES:
        surface = (ROOT / relative).read_text(encoding="utf-8")
        if OLD_REPOSITORY_URL in surface:
            errors.append(f"legacy repository locator present: {relative}")

    workflows = sorted(
        path.rsplit("/", 1)[-1]
        for path in active_files
        if path.startswith(".github/workflows/") and path.endswith(".yml")
    )
    if workflows != ["verify.yml"]:
        errors.append("CI surface must contain only .github/workflows/verify.yml")

    if errors:
        for error in errors:
            print(f"REPOSITORY_MINIMALITY_ERROR={error}")
        print("REPOSITORY_ACTIVE_SURFACE=FAIL")
        return 1

    print("REPOSITORY_ACTIVE_SURFACE=MINIMAL")
    print("REPOSITORY_LEGACY_SEMANTIC_SURFACE=ABSENT")
    print("REPOSITORY_HISTORY_REFERENCES=PASS")
    print("REPOSITORY_COPYRIGHT_NOTICE=PASS")
    print("REPOSITORY_SINGLE_ACTIVE_SEED_LINE=0.4alpha")
    print("REPOSITORY_SINGLE_THEORY_FOUNDATION=PASS")
    print("REPOSITORY_SINGLE_VERIFICATION_WORKFLOW=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
