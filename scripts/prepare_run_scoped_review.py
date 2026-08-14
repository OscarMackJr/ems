import argparse
import json
from pathlib import Path


def load_jsonl(path):
    rows=[]
    with Path(path).open("r",encoding="utf-8-sig") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


ap=argparse.ArgumentParser()
ap.add_argument("--input",required=True)
ap.add_argument("--output",required=True)
args=ap.parse_args()

rows=load_jsonl(args.input)
for row in rows:
    row["human_decision"]=""
    row["decision_owner"]=""
    row["decision_rationale"]=""

out=Path(args.output)
out.parent.mkdir(parents=True,exist_ok=True)
with out.open("w",encoding="utf-8") as f:
    for row in rows:
        f.write(json.dumps(row)+"\n")

print(json.dumps({"status":"PASS","row_count":len(rows),"output":str(out)},indent=2))
