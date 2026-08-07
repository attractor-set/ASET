# INPI software-deposit generation

`ASET-INPI-SOFTWARE-DEPOSIT-V1` fixes the deterministic procedure used to derive a software-deposit archive from an immutable Git ref.

The profile fixes the source selectors, lexicographic ordering, ZIP storage mode, fixed timestamp, path-prefix rule, Git-mode preservation and SHA-256 algorithm. It does **not** freeze the selected release contents. New or changed files under the selected paths are expected to change the deposit bytes and therefore the resulting SHA-256.

A change to the V1 generation rules requires a new versioned profile. The release gate compares the V1 profile with the approved ref once V1 exists there; ordinary source, test, validator or formal-artifact changes remain permitted.

The generated ZIP, checksum, source manifest and submission worksheet are written under `dist/` and are not committed. They are evidence derived from a release ref, not normative Seed inputs.

The V1 procedure was independently replayed against `seed-0.3.0-alpha.1` and reproduced the previously created deposit SHA-256 `2bee0a57ab8f1e19ed249f3c016fd821ceb7707764451236f517709ca04a845f`. This historical value is informational evidence only and is not a blocking digest for later releases.
