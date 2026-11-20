from __future__ import annotations

import collections
import json
import sys
from pathlib import Path


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    a = json.loads((root / 'registry/archive_assessment_applicability_authority_v2.json').read_text(encoding='utf-8'))
    controls = a['controls']
    print(f"{a['authority_id']}  (version {a['version']}, status {a['status']})")
    counts = collections.Counter(c['not_applicable_decision_state'] for c in controls)
    print(f"{len(controls)} controls: " + ', '.join(f'{k}={v}' for k, v in sorted(counts.items())))
    print('\nRULE_PUBLISHED (machine-readable not_applicable_rule):')
    for c in controls:
        if c['not_applicable_decision_state'] == 'RULE_PUBLISHED':
            r = c['not_applicable_rule']
            cond = ' AND '.join(f"{x['field']}={x['state']}" for x in r['conditions'])
            print(f"  {c['control_id']}  {c['control_name']}\n      not applicable only when {cond}  [{c['not_applicable_authority']}]")
    print('\nNO_RULE_WILL_BE_PUBLISHED (explicit decision: no rule, so it can never resolve to not-applicable):')
    for c in controls:
        if c['not_applicable_decision_state'] == 'NO_RULE_WILL_BE_PUBLISHED':
            print(f"  {c['control_id']}  {c['control_name']}  [{c['not_applicable_authority']}]")
    print(f"\nNOT_YET_DECIDED: {counts.get('NOT_YET_DECIDED', 0)} controls (EMS has not decided; never read as not applicable)")


if __name__ == '__main__':
    main()
