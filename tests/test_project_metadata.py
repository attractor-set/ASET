from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPIC_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EXPECTED_DESCRIPTION = (
    "ASET is an open specification and reference implementation for "
    "Authority-Signed Evidence Trails, enabling verifiable accountability "
    "within heterogeneous sociotechnical systems."
)


def load(relative: str) -> dict[str, object]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_project_metadata_is_the_single_about_source():
    project = load("metadata/project.json")
    codemeta = load("codemeta.json")
    repository_metadata = load(".github/repository-metadata.json")

    about = project["about"]
    assert isinstance(about, dict)
    assert project["description"] == EXPECTED_DESCRIPTION
    assert about["description"] == EXPECTED_DESCRIPTION
    assert codemeta["description"] == EXPECTED_DESCRIPTION
    assert repository_metadata["description"] == EXPECTED_DESCRIPTION
    assert codemeta["alternateName"] == "Authority-Signed Evidence Trail"


def test_github_topics_are_exact_and_valid():
    project = load("metadata/project.json")
    codemeta = load("codemeta.json")
    repository_metadata = load(".github/repository-metadata.json")

    about = project["about"]
    assert isinstance(about, dict)
    topics = about["topics"]
    assert isinstance(topics, list)
    assert 1 <= len(topics) <= 20
    assert len(topics) == len(set(topics))
    assert all(
        isinstance(topic, str)
        and len(topic) <= 50
        and TOPIC_PATTERN.fullmatch(topic)
        for topic in topics
    )
    assert codemeta["keywords"] == topics
    assert repository_metadata["topics"] == topics


def test_codemeta_uses_released_context_and_repository_identity():
    project = load("metadata/project.json")
    codemeta = load("codemeta.json")

    repository = project["repository"]
    assert isinstance(repository, dict)
    assert codemeta["@context"] == "https://w3id.org/codemeta/3.1"
    assert codemeta["@type"] == "SoftwareSourceCode"
    assert codemeta["codeRepository"] == repository["url"]
    assert codemeta["issueTracker"] == repository["issues"]


def test_all_generated_repository_views_have_committed_parity():
    result = subprocess.run(
        [sys.executable, "tools/generate_repository_views.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "REPOSITORY_VIEWS_PARITY=PASS" in result.stdout
