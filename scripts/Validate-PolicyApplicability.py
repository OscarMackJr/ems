import argparse,json,sys
from pathlib import Path
TARGET={"EMS-CTRL-034","EMS-CTRL-036","EMS-CTRL-038","EMS-CTRL-039"}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--input",required=True);a=ap.parse_args()
    d=json.loads(Path(a.input).read_text(encoding="utf-8"))
    errs=[]
    for x in d:
        if x.get("control_id") not in TARGET: errs.append(f"Unexpected control {x.get('control_id')}")
        if x.get("applicability") not in {"APPLICABLE","NOT_APPLICABLE"}: errs.append(f"Invalid applicability {x}")
        if not x.get("applicability_reason"): errs.append(f"Missing reason {x.get('repository_name')} {x.get('control_id')}")
    print(json.dumps({"status":"PASS" if not errs else "FAIL","row_count":len(d),"errors":errs},indent=2))
    sys.exit(1 if errs else 0)
if __name__=="__main__":main()
