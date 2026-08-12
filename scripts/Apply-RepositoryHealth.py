import argparse,csv,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--compliance",required=True)
    ap.add_argument("--health",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    with Path(a.compliance).open(encoding="utf-8-sig",newline="") as fh:
        rows=list(csv.DictReader(fh))
    health=json.loads(Path(a.health).read_text(encoding="utf-8"))
    by={x["repository_name"]:x for x in health}

    for r in rows:
        if r["control_id"]=="EMS-CTRL-079" and r["repository_name"] in by:
            x=by[r["repository_name"]]
            r["pre_health_recompute_status"]=r["compliance_status"]
            r["compliance_status"]=x["status"]
            r["collector_version"]="v2-rollup"
            r["collector_assertions_json"]=json.dumps(x["assertions"],separators=(",",":"))
        else:
            r.setdefault("pre_health_recompute_status","")

    fields=list(rows[0].keys())
    with Path(a.out).open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields);w.writeheader();w.writerows(rows)

if __name__=="__main__":main()
