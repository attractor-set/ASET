from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPIC_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EXPECTED_DESCRIPTION = (
    "ASET is an open, implementation-neutral specification for Authority-Signed "
    "Evidence Trails, with a minimal Seed for verifiable UNKNOWN-to-ACCEPT-or-DENY resolution."
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

def test_creator_and_pseudonym_are_not_modeled_as_an_organization():
    project = load("metadata/project.json")
    codemeta = load("codemeta.json")

    creator = project["creator"]
    publisher = project["publisher"]
    assert isinstance(creator, dict)
    assert isinstance(publisher, dict)
    assert creator == publisher
    assert creator["type"] == "Person"
    assert creator["name"] == "Dzmitry Prychyna"
    assert creator["alternate_name"] == "Attractor Set"

    for field in ("author", "copyrightHolder", "maintainer", "publisher"):
        party = codemeta[field]
        assert isinstance(party, dict)
        assert party["@type"] == "Person"
        assert party["name"] == "Dzmitry Prychyna"
        assert party["alternateName"] == "Attractor Set"
