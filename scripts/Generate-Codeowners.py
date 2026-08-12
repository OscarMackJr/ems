from pathlib import Path
import argparse, yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--template", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    gh = cfg["github"]
    co = gh["codeowners"]

    env = Environment(
        loader=FileSystemLoader(str(Path(args.template).parent)),
        undefined=StrictUndefined
    )
    tmpl = env.get_template(Path(args.template).name)

    rendered = tmpl.render(
        organization=gh["organization"],
        team_slug=co["default_team_slug"]
    )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered, encoding="utf-8")

    print(f"Generated {out}")
    print(f"Owner: @{gh['organization']}/{co['default_team_slug']}")
    print(f"Status: {co['status']}")
    print(f"Review due: {co['review_due']}")

if __name__ == "__main__":
    main()
