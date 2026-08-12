import argparse,json,sys
from pathlib import Path
V={'PASS','WARNING','FAIL','EXCEPTION','NOT_APPLICABLE','NOT_EVALUATED'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--observations',required=True);ap.add_argument('--report',required=True);a=ap.parse_args();o=json.loads(Path(a.observations).read_text());err=[]
 for i,x in enumerate(o):
  if x.get('status') not in V:err.append(f'{i}: invalid status')
  for f in ['repository_id','control_id','status','observed_at','source','assertions']:
   if f not in x:err.append(f'{i}: missing {f}')
 r={'status':'PASS' if not err else 'FAIL','observation_count':len(o),'errors':err};Path(a.report).parent.mkdir(parents=True,exist_ok=True);Path(a.report).write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));sys.exit(0 if not err else 1)
if __name__=='__main__':main()
