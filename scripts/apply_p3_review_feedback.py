"""Apply P3 review-feedback clarifications without authorizing evidence writes."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    authority_path = root / "registry/external_evidence_retention_authority.json"
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    authority["evidence_retention_state_transition"] = {
        "from": "STAGED_LOCAL",
        "to": "CSO_APPROVED_STORAGE",
        "transition_authority": "CSO",
        "required_preconditions": [
            "all package artifacts have matching SHA-256 values",
            "authorized write access and approved operational mechanism are confirmed",
            "destination exists or its creation is approved",
            "hold and deletion authority are recorded",
            "immutable or versioned storage layout is used",
        ],
        "required_transition_evidence": [
            "retained object logical path",
            "source and retained SHA-256 equality",
            "retention timestamp",
            "CSO authorization reference",
        ],
        "current_state": "STAGED_LOCAL",
        "transition_authorized": False,
    }
    authority["supersession_history_retention"] = {
        "scope": "onboarding certifications, supersession records, immutable machine results, and append-only human-review supplements",
        "retention_period": "3 years; longer legal or management hold overrides deletion",
        "successor_behavior": "a successor supplements the prior record and never rewrites or deletes the prior record during the retention period",
        "storage_requirement": "all retained lineage records must use the CSO-approved retention authority once the transition is authorized",
    }
    authority_path.write_text(json.dumps(authority, indent=2) + "\n", encoding="utf-8", newline="\n")
    doc = root / "docs/EXTERNAL_EVIDENCE_RETENTION_AUTHORITY.md"
    text = doc.read_text(encoding="utf-8")
    text += "\n## State transition and supersession retention\n\nThe package is initially `STAGED_LOCAL`; it may transition only to `CSO_APPROVED_STORAGE` after CSO authorization, approved access, destination readiness, recorded hold/deletion authority, immutable or versioned storage layout, and per-artifact SHA-256 equality. The transition records the logical path, source/retained hash equality, timestamp, and authorization reference.\n\nOnboarding certifications, supersession records, immutable machine results, and append-only human-review supplements are retained for the same three-year-or-longer-hold period. A successor supplements rather than rewrites or deletes a prior record.\n"
    doc.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
