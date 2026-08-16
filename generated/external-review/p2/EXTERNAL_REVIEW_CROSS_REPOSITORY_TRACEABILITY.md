# External Review Cross-Repository Traceability

This package maps EMS governance authority to Hayes WS1–WS10 implementation and to hash-indexed synthetic evidence. Policy authority, implementation, and execution evidence are separate layers. See `external_review_cross_repo_traceability.json` for the machine-readable map.

The orchestrator accepts `AuthoritySource(root, source_identity, source_class)`. The root is execution-local and never persists; identity/class and authority-file hashes provide provenance. Hayes consumes authority and does not define EMS policy.
