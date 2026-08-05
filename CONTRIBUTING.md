# Contributing to ASET

ASET is specification-first. Changes must preserve the distinction between normative canon, generated views, non-normative tooling and external implementation profiles.

Before opening a pull request:

```bash
python -m pip install -r requirements-ci.txt
python tools/generate_repository_views.py
python tools/build_canon_package.py
python tools/rebuild_manifest.py
python tools/repository_release_gate.py
```

Canon changes must be classified as no semantic change, monotonic extension or breaking normative change. No implementation, programming language, checker or storage backend may be granted semantic precedence.

Historical release evidence, protected tags and frozen rc11 bytes must never be rewritten.

## Rights and provenance

Contributions are licensed under `LICENSE`. Existing project Background IP and provenance declarations are recorded in `BACKGROUND_IP_SCHEDULE.md` and `governance/ip/background-ip-schedule.json`; contribution does not transfer ownership of pre-existing material unless a separate written agreement says so.
