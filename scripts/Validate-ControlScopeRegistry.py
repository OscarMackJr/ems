import argparse,json,re,sys
from pathlib import Path
import yaml

ALLOWED={"REPOSITORY","SERVICE","APPLICATION","PLATFORM","ORGANIZATION","EMS"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--registry",required=True)
    ap.add_argument("--taxonomy",required=True)
    ap.add_argument("--report",required=True)
    a=ap.parse_args()

    reg=yaml.safe_load(Path(a.registry).read_text(encoding="utf-8")) or {}
    tax=yaml.safe_load(Path(a.taxonomy).read_text(encoding="utf-8")) or {}
    controls=reg.get("controls",[])
    errors=[];warnings=[]

    if len(controls)!=80:
        errors.append(f"Expected 80 controls, found {len(controls)}")

    ids=[c.get("control_id") for c in controls]
    expected=[f"EMS-CTRL-{i:03d}" for i in range(1,81)]
    missing=[x for x in expected if x not in ids]
    dup=sorted({x for x in ids if ids.count(x)>1})
    if missing: errors.append("Missing controls: "+", ".join(missing))
    if dup: errors.append("Duplicate controls: "+", ".join(dup))

    taxonomy_scopes=set((tax.get("scopes") or {}).keys())
    if taxonomy_scopes != ALLOWED:
        errors.append(f"Taxonomy scopes differ from expected: {sorted(taxonomy_scopes)}")

    for c in controls:
        cid=c.get("control_id","")
        scope=c.get("scope")
        if scope not in ALLOWED: errors.append(f"{cid}: invalid scope {scope}")
        if not c.get("rationale"): errors.append(f"{cid}: rationale required")
        if c.get("classification_status")=="PROVISIONAL":
            warnings.append(f"{cid}: scope classification remains PROVISIONAL")
        expected_inherit=(tax.get("scopes") or {}).get(scope,{}).get("inheritance_allowed")
        if expected_inherit is not None and c.get("inheritance_allowed") != expected_inherit:
            errors.append(f"{cid}: inheritance_allowed disagrees with taxonomy")

    result={
        "status":"PASS" if not errors else "FAIL",
        "control_count":len(controls),
        "errors":errors,
        "warnings":warnings,
        "scope_counts":{}
    }
    for c in controls:
        s=c.get("scope","UNKNOWN")
        result["scope_counts"][s]=result["scope_counts"].get(s,0)+1

    Path(a.report).parent.mkdir(parents=True,exist_ok=True)
    Path(a.report).write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))
    sys.exit(1 if errors else 0)

if __name__=="__main__": main()
