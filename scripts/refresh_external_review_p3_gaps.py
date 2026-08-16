"""Build the P3 external-review gap register without dropping inherited review gaps."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    p2_path = root / "generated/external-review/p2/external_review_open_gap_register.json"
    p2 = json.loads(p2_path.read_text(encoding="utf-8"))
    inherited = {gap["gap_id"]: gap for gap in p2["gaps"]}
    gaps = [
        {
            "gap_id": "P3-GAP-01",
            "title": "Retention role terminology",
            "state": "RESOLVED_BY_TERMINOLOGY_CLARIFICATION",
            "details": {
                "former_ambiguous_value": "retention_owner = Software Development",
                "evidence_producer_and_business_owner": "Software Development",
                "storage_authority": "CSO",
                "authority_model": "registry/external_evidence_retention_authority.json",
            },
        },
        {
            "gap_id": "P3-GAP-02",
            "title": "CSO retention write access and operational mapping",
            "state": "OPEN/BLOCKED",
            "details": {
                "replaces": ["P2-GAP-01", "P2-GAP-04"],
                "logical_authority": "Egnyte / TWG/TechAudits",
                "operational_access": "BLOCKED / INACCESSIBLE",
                "required_action": "CSO must authorize an operator and operational access mechanism, confirm destination readiness, and record hold/deletion authority.",
            },
        },
        {
            "gap_id": "P3-GAP-03",
            "title": inherited["P2-GAP-02"]["title"],
            "state": inherited["P2-GAP-02"]["state"],
            "category": inherited["P2-GAP-02"]["category"],
            "details": inherited["P2-GAP-02"]["details"],
        },
        {
            "gap_id": "P3-GAP-04",
            "title": inherited["P2-GAP-03"]["title"],
            "state": inherited["P2-GAP-03"]["state"],
            "category": inherited["P2-GAP-03"]["category"],
            "details": inherited["P2-GAP-03"]["details"],
        },
        {
            "gap_id": "P3-GAP-05",
            "title": "Final external-review baseline certification",
            "state": "OPEN",
            "details": {"replaces": "P2-GAP-05", "blocked_by": "P3-GAP-02"},
        },
        {
            "gap_id": "P3-GAP-06",
            "title": inherited["P2-GAP-06"]["title"],
            "state": "INTENTIONALLY_NOT_AUTHORIZED",
            "details": inherited["P2-GAP-06"]["details"],
        },
    ]
    result = {
        "component": "P3 External Evidence Retention Finalization",
        "p2_open_gap_register_reference": str(p2_path.relative_to(root)).replace("\\", "/"),
        "gaps": gaps,
    }
    output = root / "generated/external-review/p3/external_review_open_gap_register.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
