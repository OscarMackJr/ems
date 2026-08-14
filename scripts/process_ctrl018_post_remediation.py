import argparse
import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rp(root, rel):
    return root / Path(rel.replace("\\", "/"))


ap = argparse.ArgumentParser()
ap.add_argument("--ems-root", required=True)
ap.add_argument("--hayes-root", required=True)
ap.add_argument("--spec", required=True)
ap.add_argument("--owner", required=True)
ap.add_argument("--source", required=True)
ap.add_argument("--rationale", required=True)
args = ap.parse_args()

if not args.source.startswith("HUMAN_"):
    raise SystemExit("decision_source must begin with HUMAN_")

ems = Path(args.ems_root).resolve()
hayes = Path(args.hayes_root).resolve()
spec = load(Path(args.spec))
errors = []

pre_reg = rp(ems, spec["pre_baseline_registration"])
if not pre_reg.exists():
    errors.append("pre-remediation baseline missing")
elif sha(pre_reg).lower() != spec["pre_baseline_expected_sha256"].lower():
    errors.append("pre-remediation baseline hash mismatch")

post_result_p = rp(hayes, spec["post_hayes_result"])
post_evidence_p = rp(hayes, spec["post_hayes_evidence"])
transition_cert_p = rp(hayes, spec["post_hayes_transition_certification"])

for path in (post_result_p, post_evidence_p, transition_cert_p):
    if not path.exists():
        errors.append(f"missing Hayes post-remediation artifact: {path}")

if errors:
    print(json.dumps({"status": "FAIL", "errors": errors}, indent=2))
    raise SystemExit(1)

post_result = load(post_result_p)
transition = load(transition_cert_p)

if post_result.get("result_state") != "PASS":
    errors.append("post-remediation Hayes result is not PASS")
if post_result.get("evidence_state") != "SUFFICIENT":
    errors.append("post-remediation evidence state is not SUFFICIENT")
if transition.get("status") != "PASS" or transition.get("transition") != "FAIL_TO_PASS":
    errors.append("Hayes FAIL-to-PASS transition certification invalid")

accept = {
    "record_version": "1.0",
    "recorded_at_utc": datetime.now(UTC).isoformat(),
    "wave": "2D",
    "control_id": "EMS-CTRL-018",
    "target_id": "REPO-001",
    "acceptance_state": "ACCEPTED",
    "decision_owner": args.owner,
    "decision_source": args.source,
    "decision_rationale": args.rationale,
    "result_state": "PASS",
    "pre_remediation_baseline_sha256": sha(pre_reg),
    "post_result_sha256": sha(post_result_p),
    "post_evidence_sha256": sha(post_evidence_p),
    "hayes_transition_certification_sha256": sha(transition_cert_p),
    "errors": errors,
}

acceptp = rp(ems, spec["acceptance_output"])
acceptp.parent.mkdir(parents=True, exist_ok=True)
acceptp.write_text(json.dumps(accept, indent=2), encoding="utf-8")

if errors:
    print(json.dumps(accept, indent=2))
    raise SystemExit(1)

dest = rp(ems, spec["promoted_evidence_output"])
dest.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(post_evidence_p, dest)

promotion = {
    "record_version": "1.0",
    "promoted_at_utc": datetime.now(UTC).isoformat(),
    "wave": "2D",
    "control_id": "EMS-CTRL-018",
    "target_id": "REPO-001",
    "promotion_state": "PROMOTED",
    "authoritative_evidence_path": str(dest.relative_to(ems)).replace("\\", "/"),
    "authoritative_evidence_sha256": sha(dest),
    "source_evidence_sha256": sha(post_evidence_p),
    "acceptance_record_sha256": sha(acceptp),
}

promop = rp(ems, spec["promotion_output"])
promop.write_text(json.dumps(promotion, indent=2), encoding="utf-8")

post_baseline = {
    "baseline_version": "1.0",
    "registered_at_utc": datetime.now(UTC).isoformat(),
    "wave": "2D",
    "control_id": "EMS-CTRL-018",
    "target_id": "REPO-001",
    "status": "PASS",
    "baseline_state": "AUTHORITATIVE",
    "result_state": "PASS",
    "acceptance_state": "ACCEPTED",
    "promotion_state": "PROMOTED",
    "pre_remediation_baseline_sha256": sha(pre_reg),
    "post_evidence_sha256": sha(dest),
    "post_acceptance_sha256": sha(acceptp),
    "post_promotion_sha256": sha(promop),
}

post_reg = rp(ems, spec["post_baseline_registration"])
post_reg.parent.mkdir(parents=True, exist_ok=True)
post_reg.write_text(json.dumps(post_baseline, indent=2), encoding="utf-8")

transition_record = {
    "transition_version": "1.0",
    "registered_at_utc": datetime.now(UTC).isoformat(),
    "wave": "2D",
    "control_id": "EMS-CTRL-018",
    "target_id": "REPO-001",
    "status": "PASS",
    "transition": "FAIL_TO_PASS",
    "pre_remediation_baseline": spec["pre_baseline_registration"],
    "pre_remediation_baseline_sha256": sha(pre_reg),
    "post_remediation_baseline": spec["post_baseline_registration"],
    "post_remediation_baseline_sha256": sha(post_reg),
    "hayes_transition_certification_sha256": sha(transition_cert_p),
}

transitionp = rp(ems, spec["transition_record"])
transitionp.write_text(json.dumps(transition_record, indent=2), encoding="utf-8")

out = {
    "status": "PASS",
    "control_id": "EMS-CTRL-018",
    "target_id": "REPO-001",
    "transition": "FAIL_TO_PASS",
    "pre_baseline_sha256": sha(pre_reg),
    "post_baseline_sha256": sha(post_reg),
    "promotion_state": "PROMOTED",
}
print(json.dumps(out, indent=2))
