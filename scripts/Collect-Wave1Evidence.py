import argparse
import csv
import datetime
import json
import re
import subprocess
from pathlib import Path

import yaml


def run_gh(args):
    """Run gh CLI and always decode as UTF-8 on Windows."""
    p = subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return p.returncode, p.stdout, p.stderr


def gh_api(path):
    code, out, err = run_gh(["api", path])
    if code != 0:
        return None, err.strip()
    if not out.strip():
        return {}, None
    try:
        return json.loads(out), None
    except Exception as exc:
        return None, f"JSON parse failure: {exc}"


def observation(repo, control_id, status, assertions, note=None):
    item = {
        "repository_id": repo["id"],
        "repository_name": repo["name"],
        "control_id": control_id,
        "status": status,
        "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": "GitHub API / repository evidence",
        "assertions": assertions,
    }
    if note:
        item["note"] = note
    return item


def workflows(repo):
    d, e = gh_api(f"repos/{repo}/actions/workflows")
    if d is None:
        return [], e
    return d.get("workflows", []), None


def root_items(repo):
    d, e = gh_api(f"repos/{repo}/contents")
    return d if isinstance(d, list) else [], e


def tags(repo):
    d, e = gh_api(f"repos/{repo}/tags?per_page=100")
    return d if isinstance(d, list) else [], e


def releases(repo):
    d, e = gh_api(f"repos/{repo}/releases?per_page=20")
    return d if isinstance(d, list) else [], e


def recent_commits(repo, branch, count=20):
    d, e = gh_api(f"repos/{repo}/commits?sha={branch}&per_page={count}")
    return d if isinstance(d, list) else [], e


def recent_prs(repo, count=20):
    d, e = gh_api(
        f"repos/{repo}/pulls?state=closed&per_page={count}&sort=updated&direction=desc"
    )
    return d if isinstance(d, list) else [], e


def evaluate(repo, cid, strategy):
    full = repo["github"]
    branch = repo.get("default_branch")
    collector = strategy["collector"]

    if collector == "branch_protection":
        d, e = gh_api(f"repos/{full}/branches/{branch}/protection")
        if d:
            return observation(repo, cid, "PASS", {"branch_protected": True})
        if e and ("Upgrade to GitHub Pro" in e or "HTTP 403" in e or "403" in e):
            return observation(
                repo, cid, "EXCEPTION",
                {"branch_protected": False, "platform_capability": False}, e
            )
        return observation(repo, cid, "WARNING", {"branch_protected": False}, e)

    if collector == "pull_request_reviews":
        d, e = gh_api(f"repos/{full}/branches/{branch}/protection")
        if not d:
            if e and ("Upgrade to GitHub Pro" in e or "HTTP 403" in e or "403" in e):
                return observation(repo, cid, "EXCEPTION", {"pull_request_required": False}, e)
            return observation(repo, cid, "WARNING", {"pull_request_required": False}, e)
        review = d.get("required_pull_request_reviews")
        approvals = int((review or {}).get("required_approving_review_count", 0))
        return observation(
            repo, cid,
            "PASS" if review and approvals >= 1 else "WARNING",
            {"pull_request_required": bool(review), "required_approvals": approvals},
        )

    if collector == "signed_commits":
        commits, e = recent_commits(full, branch, int(strategy.get("sample_size", 20)))
        if not commits:
            return observation(repo, cid, "NOT_EVALUATED", {}, e or "No commits sampled.")
        verified = 0
        for c in commits:
            detail, _ = gh_api(f"repos/{full}/commits/{c['sha']}")
            if detail and detail.get("commit", {}).get("verification", {}).get("verified"):
                verified += 1
        ratio = verified / len(commits)
        status = "PASS" if ratio == 1 else ("WARNING" if verified else "FAIL")
        return observation(
            repo, cid, status,
            {"sampled_commits": len(commits), "verified_commits": verified, "verified_ratio": ratio},
        )

    if collector == "protected_release_tags":
        tag_rows, _ = tags(full)
        rules, _ = gh_api(f"repos/{full}/rulesets")
        active = []
        if isinstance(rules, list):
            active = [r for r in rules if r.get("target") == "tag" and r.get("enforcement") == "active"]
        if active:
            return observation(repo, cid, "PASS", {"active_tag_rulesets": len(active)})
        if not tag_rows:
            return observation(repo, cid, "NOT_APPLICABLE", {"tag_count": 0}, "No release tags detected.")
        return observation(repo, cid, "WARNING", {"tag_count": len(tag_rows), "active_tag_rulesets": 0})

    if collector == "issue_linkage":
        prs, e = recent_prs(full, int(strategy.get("sample_size", 20)))
        if not prs:
            return observation(repo, cid, "NOT_EVALUATED", {}, e or "No closed PRs sampled.")
        pattern = re.compile(r"(close[sd]?|fix(e[sd])?|resolve[sd]?)\s+#\d+|#\d+", re.I)
        linked = sum(1 for pr in prs if pattern.search(pr.get("body") or ""))
        ratio = linked / len(prs)
        status = "PASS" if ratio == 1 else ("WARNING" if linked else "FAIL")
        return observation(
            repo, cid, status,
            {"sampled_prs": len(prs), "linked_prs": linked, "linked_ratio": ratio},
        )

    if collector == "secret_scanning":
        d, e = gh_api(f"repos/{full}/secret-scanning/alerts?state=open&per_page=1")
        if d is not None:
            return observation(repo, cid, "PASS", {"secret_scanning_api_accessible": True})
        return observation(repo, cid, "NOT_EVALUATED", {"secret_scanning_api_accessible": False}, e)

    if collector == "dependency_scanning":
        d, e = gh_api(f"repos/{full}/dependabot/alerts?state=open&per_page=1")
        if d is not None:
            return observation(repo, cid, "PASS", {"dependabot_api_accessible": True})
        return observation(repo, cid, "NOT_EVALUATED", {"dependabot_api_accessible": False}, e)

    if collector == "license_compliance":
        items, _ = root_items(full)
        names = {x.get("name", "").lower() for x in items}
        license_present = any(n.startswith("license") or n.startswith("licence") for n in names)
        wfs, _ = workflows(full)
        text = " ".join(((w.get("name") or "") + " " + (w.get("path") or "")).lower() for w in wfs)
        scan = any(k in text for k in ["license", "dependency review", "fossa", "scancode"])
        status = "PASS" if scan else ("WARNING" if license_present else "FAIL")
        return observation(repo, cid, status, {
            "license_file_present": license_present,
            "license_scan_workflow_detected": scan
        })

    if collector == "sbom":
        d, e = gh_api(f"repos/{full}/dependency-graph/sbom")
        return observation(
            repo, cid, "PASS" if d else "NOT_EVALUATED",
            {"sbom_api_available": bool(d)}, e
        )

    if collector == "security_advisories":
        d, e = gh_api(f"repos/{full}/dependabot/alerts?per_page=1")
        return observation(
            repo, cid, "PASS" if d is not None else "NOT_EVALUATED",
            {"security_advisory_api_accessible": d is not None}, e
        )

    if collector in {
        "unit_testing", "integration_testing", "regression_testing",
        "contract_testing", "performance_testing"
    }:
        wfs, _ = workflows(full)
        text = " ".join(((w.get("name") or "") + " " + (w.get("path") or "")).lower() for w in wfs)
        patterns = {
            "unit_testing": ["unit", "pytest", "dotnet test", "cargo test", "jest", "test"],
            "integration_testing": ["integration"],
            "regression_testing": ["regression"],
            "contract_testing": ["contract", "pact", "api test"],
            "performance_testing": ["performance", "load test", "k6", "jmeter", "locust"],
        }[collector]
        found = any(p in text for p in patterns)
        status = ("PASS" if found else "WARNING") if collector == "unit_testing" else (
            "PASS" if found else "NOT_EVALUATED"
        )
        return observation(repo, cid, status, {
            "workflow_count": len(wfs),
            "matching_test_workflow_detected": found
        })

    if collector == "test_evidence_retention":
        d, e = gh_api(f"repos/{full}/actions/artifacts?per_page=10")
        if d is None:
            return observation(repo, cid, "NOT_EVALUATED", {}, e)
        artifacts = d.get("artifacts", [])
        return observation(repo, cid, "PASS" if artifacts else "WARNING", {
            "artifact_sample_count": len(artifacts)
        })

    if collector == "reproducible_builds":
        items, _ = root_items(full)
        names = {x.get("name", "") for x in items}
        lock_files = {
            "package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml",
            "poetry.lock", "Pipfile.lock", "requirements.txt", "Cargo.lock", "packages.lock.json"
        }
        pinned = bool(names & lock_files)
        wfs, _ = workflows(full)
        build = bool(wfs)
        status = "PASS" if pinned and build else ("WARNING" if pinned or build else "FAIL")
        return observation(repo, cid, status, {
            "dependency_lock_or_pin_file": pinned,
            "workflow_present": build
        })

    if collector == "release_manifest":
        items, _ = root_items(full)
        names = {x.get("name", "").lower() for x in items}
        found = any("manifest" in n for n in names)
        wfs, _ = workflows(full)
        wf = any("manifest" in (((w.get("name") or "") + " " + (w.get("path") or "")).lower()) for w in wfs)
        return observation(repo, cid, "PASS" if found or wf else "WARNING", {
            "manifest_file_detected": found,
            "manifest_workflow_detected": wf
        })

    if collector == "sha256_integrity":
        rels, _ = releases(full)
        if not rels:
            return observation(repo, cid, "NOT_APPLICABLE", {"release_count_sampled": 0}, "No releases detected.")
        assets = [a.get("name", "").lower() for r in rels for a in r.get("assets", [])]
        found = any("sha256" in a or a.endswith(".sha256") or "checksums" in a for a in assets)
        return observation(repo, cid, "PASS" if found else "WARNING", {
            "release_count_sampled": len(rels),
            "checksum_asset_detected": found
        })

    if collector == "release_signing":
        rels, _ = releases(full)
        if not rels:
            return observation(repo, cid, "NOT_APPLICABLE", {"release_count_sampled": 0}, "No releases detected.")
        assets = [a.get("name", "").lower() for r in rels for a in r.get("assets", [])]
        found = any(a.endswith((".sig", ".asc", ".pem", ".crt")) or "cosign" in a or "attestation" in a for a in assets)
        return observation(repo, cid, "PASS" if found else "WARNING", {
            "signature_or_attestation_asset_detected": found
        })

    if collector == "artifact_retention":
        d, e = gh_api(f"repos/{full}/actions/artifacts?per_page=10")
        if d is None:
            return observation(repo, cid, "NOT_EVALUATED", {}, e)
        arts = d.get("artifacts", [])
        return observation(repo, cid, "PASS" if arts else "WARNING", {
            "artifact_sample_count": len(arts)
        })

    if collector == "version_governance":
        tag_rows, _ = tags(full)
        if not tag_rows:
            return observation(repo, cid, "NOT_APPLICABLE", {"tag_count": 0}, "No release tags detected.")

        # Correct SemVer regex. Hyphen is first in the character class, so it is literal.
        semver_re = re.compile(r"^v?\d+\.\d+\.\d+(?:[-+].*)?$")
        semver_rows = [x for x in tag_rows if semver_re.match(x.get("name", ""))]
        ratio = len(semver_rows) / len(tag_rows)
        status = "PASS" if ratio == 1 else ("WARNING" if semver_rows else "FAIL")
        return observation(repo, cid, status, {
            "tag_count": len(tag_rows),
            "semver_tag_count": len(semver_rows),
            "semver_ratio": ratio
        })

    if collector == "release_workflow":
        wfs, _ = workflows(full)
        found = any(
            any(k in (((w.get("name") or "") + " " + (w.get("path") or "")).lower())
                for k in ["release", "deploy", "publish"])
            for w in wfs
        )
        return observation(repo, cid, "PASS" if found else "WARNING", {
            "release_or_deploy_workflow_detected": found,
            "workflow_count": len(wfs)
        })

    if collector == "repository_health":
        profile, _ = gh_api(f"repos/{full}/community/profile")
        health = (profile or {}).get("health_percentage")
        codeowners, _ = gh_api(f"repos/{full}/contents/.github/CODEOWNERS")
        wfs, _ = workflows(full)
        protection, _ = gh_api(f"repos/{full}/branches/{branch}/protection")
        score = sum([
            bool(codeowners),
            bool(wfs),
            bool(protection),
            isinstance(health, int) and health >= 70
        ])
        status = "PASS" if score >= 3 else ("WARNING" if score >= 1 else "FAIL")
        return observation(repo, cid, status, {
            "community_health_percentage": health,
            "codeowners": bool(codeowners),
            "workflows": bool(wfs),
            "branch_protection": bool(protection),
            "composite_score": score
        })

    return observation(repo, cid, "NOT_EVALUATED", {}, "No Wave 1 evaluator implemented.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repositories", required=True)
    ap.add_argument("--strategies", required=True)
    ap.add_argument("--applicability-csv", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    repos = yaml.safe_load(Path(args.repositories).read_text(encoding="utf-8"))["repositories"]
    strategies = yaml.safe_load(Path(args.strategies).read_text(encoding="utf-8"))["strategies"]

    applicable = set()
    with Path(args.applicability_csv).open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            applicable.add((row["repository_id"], row["control_id"]))

    out = []
    for repo in repos:
        for cid, strategy in strategies.items():
            if (repo["id"], cid) in applicable:
                out.append(evaluate(repo, cid, strategy))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Generated {len(out)} Wave 1 observations.")


if __name__ == "__main__":
    main()
