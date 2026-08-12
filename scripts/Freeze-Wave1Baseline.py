import argparse,hashlib,json,shutil,zipfile
from pathlib import Path

def sha256(p):
    h=hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pass45",required=True)
    ap.add_argument("--config",required=True)
    ap.add_argument("--outdir",required=True)
    a=ap.parse_args()

    root=Path(a.pass45)
    cfg=json.loads(Path(a.config).read_text(encoding="utf-8"))
    out=Path(a.outdir)
    if out.exists():shutil.rmtree(out)
    out.mkdir(parents=True)

    manifest=[]
    missing=[]
    for rel in cfg["freeze_required_outputs"]:
        src=root/rel
        if not src.exists():
            missing.append(rel)
            continue
        dest=out/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dest)
        manifest.append({"path":rel,"sha256":sha256(src)})

    if missing:
        raise SystemExit("Missing freeze inputs:\n"+"\n".join(missing))

    (out/"WAVE1_BASELINE_MANIFEST.json").write_text(
        json.dumps({"version":"Pass4.5-Wave1","files":manifest},indent=2),
        encoding="utf-8"
    )

    zip_path=out.parent/"EMS_Pass4_5_Wave1_Baseline.zip"
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
        for p in out.rglob("*"):
            if p.is_file():z.write(p,p.relative_to(out))
    print(zip_path)

if __name__=="__main__":main()
