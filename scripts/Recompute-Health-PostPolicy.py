import argparse,csv,json,yaml
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--compliance",required=True)
    ap.add_argument("--rollup",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    roll=yaml.safe_load(Path(a.rollup).read_text(encoding="utf-8"))
    with Path(a.compliance).open(encoding="utf-8-sig",newline="") as fh:
        rows=list(csv.DictReader(fh))
    by={(r["repository_name"],r["control_id"]):r["compliance_status"] for r in rows}
    repos=sorted({r["repository_name"] for r in rows})
    results=[]

    for repo in repos:
        fail=warn=ne=pp=0;domains={}
        for dname,spec in roll["domains"].items():
            states=[]
            for cid in spec["controls"]:
                s=by.get((repo,cid))
                if not s or s=="NOT_APPLICABLE":continue
                states.append(s)
            domains[dname]=states
            fail+=states.count("FAIL")
            warn+=states.count("WARNING")
            ne+=states.count("NOT_EVALUATED")
            pp+=states.count("POLICY_PENDING")

        status="FAIL" if fail else ("WARNING" if pp or ne or warn>2 else "PASS")
        results.append({
            "repository_name":repo,
            "control_id":"EMS-CTRL-079",
            "status":status,
            "assertions":{
                "domains":domains,
                "fail_count":fail,
                "warning_count":warn,
                "not_evaluated_count":ne,
                "policy_pending_count":pp
            }
        })

    Path(a.out).write_text(json.dumps(results,indent=2),encoding="utf-8")
    print(json.dumps(results,indent=2))

if __name__=="__main__":main()
