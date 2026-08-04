
# Dependency and workflow policy

- CI dependencies are explicitly versioned in `requirements-ci.txt`.
- Dependabot monitors Python and GitHub Actions dependencies.
- Workflows use least-privilege permissions.
- Third-party workflow actions are restricted to GitHub-owned actions in the current baseline.
- Dependency updates require the same production gate as normative documentation changes.
- A dependency alert does not automatically establish exploitability, but unresolved critical alerts block a release candidate.
