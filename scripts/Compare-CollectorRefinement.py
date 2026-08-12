import argparse, json, csv
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v1",required=True)
    ap.add_argument("--v2",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    v1=json.loads(Path(a.v1).read_text(encoding="utf-8"))
    v2=json.loads(Path(a.v2).read_text(encoding="utf-8"))

    k1={(x["repository_name"],x["control_id"]):x for x in v1}
    rows=[]
    for x in v2:
        key=(x["repository_name"],x["control_id"])
        old=k1.get(key,{})
        rows.append({
            "repository_name":x["repository_name"],
            "control_id":x["control_id"],
            "v1_status":old.get("status",""),
            "v2_status":x["status"],
            "changed":old.get("status","")!=x["status"],
            "v2_stage":x.get("stage",""),
            "v2_assertions_json":json.dumps(x.get("assertions",{}),separators=(",",":"))
        })

    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=list(rows[0].keys()))
        w.writeheader();w.writerows(rows)

    changed=[r for r in rows if r["changed"]]
    print(json.dumps({
        "row_count":len(rows),
        "changed_count":len(changed),
        "changed_rows":[
            {
                "repository":r["repository_name"],
                "control_id":r["control_id"],
                "v1_status":r["v1_status"],
                "v2_status":r["v2_status"]
            } for r in changed
        ]
    },indent=2))

if __name__=="__main__":main()
