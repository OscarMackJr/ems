import argparse,csv,json
from pathlib import Path
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--baseline',required=True);ap.add_argument('--observations',required=True);ap.add_argument('--outdir',required=True);a=ap.parse_args()
 with Path(a.baseline).open(encoding='utf-8') as f:rows=list(csv.DictReader(f))
 obs={(o['repository_id'],o['control_id']):o for o in json.loads(Path(a.observations).read_text())};before={};after={};changed=[]
 for r in rows:
  old=r['compliance_status'];before[old]=before.get(old,0)+1;o=obs.get((r['repository_id'],r['control_id']))
  if o:
   r['wave1_previous_status']=old;r['wave1_status']=o['status'];r['wave1_assertions_json']=json.dumps(o.get('assertions',{}),separators=(',',':'));r['compliance_status']=o['status']
   if old!=o['status']:changed.append({'repository':r['repository_name'],'control_id':r['control_id'],'before':old,'after':o['status']})
  else:r['wave1_previous_status']=r['wave1_status']=r['wave1_assertions_json']=''
  after[r['compliance_status']]=after.get(r['compliance_status'],0)+1
 out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True)
 with (out/'repository_control_compliance_wave1.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)
 summary={'baseline_status_counts':before,'wave1_status_counts':after,'changed_row_count':len(changed),'not_evaluated_before':before.get('NOT_EVALUATED',0),'not_evaluated_after':after.get('NOT_EVALUATED',0),'not_evaluated_reduction':before.get('NOT_EVALUATED',0)-after.get('NOT_EVALUATED',0),'changed_rows':changed}
 (out/'wave1_coverage_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
