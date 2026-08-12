import argparse,json,csv
from pathlib import Path
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--applicability",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    data=json.loads(Path(a.applicability).read_text(encoding="utf-8"))
    fields=["repository_name","control_id","control_name","applicability",
            "applicability_basis","applicability_reason","decision_source","facts_json"]
    rows=[]
    for x in data:
        rows.append({k:x.get(k,"") for k in fields[:-1]} | {"facts_json":json.dumps(x.get("facts",{}),separators=(",",":"))})
    with Path(a.out).open("w",newline="",encoding="utf-8") as fh:
        w=csv.DictWriter(fh,fieldnames=fields);w.writeheader();w.writerows(rows)
    print(f"Wrote {len(rows)} applicability rows.")
if __name__=="__main__":main()
