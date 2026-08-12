import argparse,yaml,json,csv
from pathlib import Path
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--controls",required=True); ap.add_argument("--repositories",required=True); ap.add_argument("--profiles",required=True); ap.add_argument("--outdir",required=True); a=ap.parse_args()
 controls=yaml.safe_load(Path(a.controls).read_text())["controls"]; repos=yaml.safe_load(Path(a.repositories).read_text())["repositories"]; cfg=yaml.safe_load(Path(a.profiles).read_text()); out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True)
 for r in repos:
  if r["tier"] not in cfg["profiles"]: continue
  p=cfg["profiles"][r["tier"]]; fam=set(p["required_families"]); ids=set(p["always_required_controls"])
  for rule in cfg["conditional_rules"]:
   hit=("when" in rule and all(r.get(k)==v for k,v in rule["when"].items())) or ("when_any_technology" in rule and any(t in r.get("technologies",[]) for t in rule["when_any_technology"]))
   if hit: fam.update(rule.get("add_families",[]))
  for c in controls:
   if c["family"] in fam and r["tier"] in c.get("repository_tiers",[]): ids.add(c["id"])
  by={c["id"]:c for c in controls}; rows=[{"repository_id":r["id"],"repository_name":r["name"],"tier":r["tier"],"control_id":i,"control_name":by[i]["name"],"family":by[i]["family"],"applicability_reason":"EMS profile","compliance_status":"NOT_EVALUATED"} for i in sorted(ids)]
  if rows:
   with (out/f'{r["id"]}_applicable_controls.csv').open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(f"Evaluated applicability for {len(repos)} repositories.")
if __name__=="__main__":main()
