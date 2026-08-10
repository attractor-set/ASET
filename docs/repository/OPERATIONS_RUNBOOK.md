# Specification repository operations

Run `python tools/repository_release_gate.py`. Regenerate derived views with `python tools/generate_repository_views.py`, rebuild the canon package with `python tools/build_canon_package.py`, and verify the exact Git source identity with `python tools/check_repository_source_identity.py`. The active integrity model is documented in [`INTEGRITY_MODEL.md`](INTEGRITY_MODEL.md). No runtime deployment operation is defined by this repository.
