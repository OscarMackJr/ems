---
phase: 01-rule-shape-and-decision-states
reviewed: 2026-10-13T17:29:56Z
depth: standard
files_reviewed: 3
files_reviewed_list:
  - schemas/archive_assessment_applicability_authority_v2.schema.json
  - scripts/publish_archive_assessment_applicability_authority_v2.py
  - tests/test_archive_assessment_applicability_authority_v2.py
findings:
  critical: 1
  warning: 9
  info: 6
  total: 16
status: issues_found
---

# Phase 01: Code Review Report

**Reviewed:** 2026-10-13T17:29:56Z
**Depth:** standard
**Files Reviewed:** 3
**Status:** issues_found

## Narrative Findings (AI reviewer)

## Summary

Reviewed the v2 publisher, its committed schema and its pytest file, with the tracked v1 publisher as a read-only reference. The 71 tests pass and `ruff check` is clean, and the committed schema equals `schema()`. Neither fact says much about the defects below, all of which were reproduced by running a probe script against `build_authority()`, `validate_authority()`, `schema()` and `resolve_applicability()` (no source file was modified).

The rule-shape and three-way state/rule/authority checks are sound for the cases the tests exercise. The problems are elsewhere:

- The lineage hashes that `build_authority()` embeds are computed over CRLF working-tree bytes and do not match the content of the commit they name. This was measured, not inferred (CR-01).
- `resolve_applicability()` returns `NOT_APPLICABLE` for controls that `validate_authority()` would reject (no authority, extra `negate`/`NOT` keys, wrong combination).
- The check that a named `AA4-GOV-NNN` authority actually exists is opt-in and is not used by `--validate`.
- The JSON Schema is materially weaker than the Python validator, including for contradictory rules, and several semantic fields are pinned by neither.
- The validator raises `AttributeError`/`TypeError` instead of `AuthorityError` on structurally malformed input.

Not verified: no v2 registry file exists yet (by design in this phase), so `--validate` could only be confirmed to fail closed with "v2 registry authority file is not published"; nothing was checked against Hayes's actual resolver.

## Critical Issues

### CR-01: Lineage SHA-256 values are computed over CRLF working-tree bytes and do not match the commit they cite

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:44,130-131`
**Issue:** `digest()` hashes `p.read_bytes()`. This repository has `core.autocrlf=true` and no `.gitattributes`; `git ls-files --eol` reports `i/lf w/crlf` for `registry/control_catalog.yaml` and `registry/archive_assessment_applicability_authority.json`. The hashes `build_authority()` embeds are therefore hashes of the Windows working copy, not of the committed blobs:

| File | `digest()` on this working tree | sha256 of committed blob |
|------|-------------------------------|--------------------------|
| `registry/archive_assessment_applicability_authority.json` | `782bcc74fd72...af1f88a4` | `f084607c28e5...62b192aa` (`git show 62a8955:...`) |
| `registry/control_catalog.yaml` | `edd9b7c34615...9ccdaa7` | `12bb1a9d2476...9f039477` (`git show HEAD:...`) |

Consequences:

1. `source_lineage.supersedes` asserts `commit: '62a8955'` together with `sha256: digest(V1_AUTHORITY)`. The pair is false: the file at commit `62a8955` hashes to `f084607c...`, not `782bcc74...`. Hayes reads EMS at a pinned commit (LF blobs) and cannot reproduce either lineage hash.
2. `build_authority()` is not deterministic across platforms. On the `ubuntu-latest` CI runner the same commit yields different `sha256` values, so a registry published on Windows cannot be rebuilt byte-identically in CI, which breaks hash-based certification.
3. Nothing detects this. `validate_authority()` checks only `supersedes.commit` and `supersedes.version` (line 170); replacing either `sha256` with `deadbeef` is accepted by both the validator and the schema (reproduced).

The catalog-hash half of this exists in v1 as well (the v1 registry already records `edd9b7c3...`), but v2 adds a new commit-bound claim and is the artifact Hayes re-pins to, so it must be fixed before Phase 4 publishes with this builder.

**Fix:** Hash canonical content rather than checkout bytes, and verify what is claimed:

```python
def digest(p: Path) -> str: return hashlib.sha256(p.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
```

Alternatively add a `.gitattributes` entry (`registry/** text eol=lf`, `schemas/** text eol=lf`) in a coordinated change, noting that this changes the recorded v1 catalog hash. Then make `validate_authority()` recompute and compare:

```python
lin = a.get('source_lineage') if isinstance(a.get('source_lineage'), dict) else {}
if (lin.get('catalog_reference') or {}).get('sha256') != digest(CATALOG): errors.append('catalog_reference sha256 does not match the controlled catalog')
if not isinstance(sup, dict) or sup.get('sha256') != digest(V1_AUTHORITY) or sup.get('authority_id') != 'EMS-AA3-ARCHIVE-APPLICABILITY-AUTHORITY-1.0.0': errors.append('source_lineage supersedes v1 entry does not match the v1 registry')
```

Add a test asserting `build_authority()['source_lineage']['supersedes']['sha256']` equals the sha256 of `git show 62a8955:registry/archive_assessment_applicability_authority.json` (or a pinned literal).

## Warnings

### WR-01: `resolve_applicability()` returns NOT_APPLICABLE for controls the validator rejects

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:217-231`
**Issue:** The resolver defends against some malformed input (unknown state, non-list conditions, bad field/state) but not the rest, and the undefended cases resolve to the one dangerous result. Reproduced with facts `production=KNOWN_FALSE, internet_exposed=KNOWN_FALSE`:

- `RULE_PUBLISHED`, valid rule, `not_applicable_authority: None` -> `NOT_APPLICABLE` (a not-applicable result with no named authority, contrary to the project's core value)
- rule with `combination: 'ANY'`, extra key `NOT: True`, authority `'bogus'` -> `NOT_APPLICABLE`
- condition `{'field': 'production', 'state': 'KNOWN_FALSE', 'negate': True}` -> `NOT_APPLICABLE` (the evident intent is the opposite)
- `NO_RULE_WILL_BE_PUBLISHED` with a rule attached and no authority -> `APPLICABLE` rather than unresolved

`facts=None` raises `AttributeError`. The tests use this function as the semantic oracle but cover none of these.

**Fix:** Reuse the validator's shape rules so the resolver cannot disagree with it, and fail closed to `APPLICABILITY_UNRESOLVED`:

```python
def resolve_applicability(control: dict, facts: dict) -> str:
    state = control.get('not_applicable_decision_state')
    if state == 'NOT_YET_DECIDED' or state not in DECISION_STATES or not isinstance(facts, dict): return 'APPLICABILITY_UNRESOLVED'
    auth = control.get('not_applicable_authority'); rule = control.get('not_applicable_rule')
    if not isinstance(auth, str) or not re.fullmatch(AUTHORITY_ID_BODY, auth): return 'APPLICABILITY_UNRESOLVED'
    if state == 'NO_RULE_WILL_BE_PUBLISHED': return 'APPLICABLE' if rule is None else 'APPLICABILITY_UNRESOLVED'
    errors = []; validate_rule('resolver', rule, errors)
    if errors: return 'APPLICABILITY_UNRESOLVED'
    ...
```

### WR-02: The check that a named authority exists is opt-in and unused by `--validate`

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:152,192,237`
**Issue:** `validate_authority(a, known_decision_ids=None)` only checks that the authority matches `AA4-GOV-NNN`. `main()` calls it with no decision-id set, so `--validate` prints `PASS` for a control citing `AA4-GOV-999` when no such decision record exists (reproduced: validator and schema both accept). The default is the unsafe one: any caller that forgets the second argument silently skips the check. This is the gate against "no rule or no-rule decision is published on drafting judgment alone".
**Fix:** Make the default fail closed: when any control is decided and `known_decision_ids` is `None`, raise `AuthorityError('decided controls require the approved AA4 decision id set')`. Have `main()` load the id set from the decision register once it exists (Phase 3/4) and pass it explicitly.

### WR-03: `AA4-GOV-NNN` pattern accepts a trailing newline in both validators

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:26,191`; `schemas/archive_assessment_applicability_authority_v2.schema.json:37,99,157`
**Issue:** `re.match(r'^AA4-GOV-[0-9]{3}$', auth)` accepts `'AA4-GOV-001\n'` because `$` matches before a final newline, and the Python `jsonschema` library evaluates `pattern` with the same engine. Reproduced: both accept `'AA4-GOV-001\n'`. Hayes then receives an authority id that does not string-equal the decision record id. `[0-9]` is ASCII-only, so there is no Unicode-digit variant of this.
**Fix:** In Python use `re.fullmatch(r'AA4-GOV-[0-9]{3}', auth)`. For the schema, add `"minLength": 11, "maxLength": 11` beside the pattern (portable across regex dialects), and add a test for the trailing-newline case. The same applies to the `control_id` pattern, although the catalog set-equality check already covers it in the validator.

### WR-04: Schema accepts contradictory and duplicate-field rules, and is weaker than the validator in several other places

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:198-199,203-204`; `schemas/archive_assessment_applicability_authority_v2.schema.json:46-74,180-208`
**Issue:** A rule `production=KNOWN_FALSE AND production=KNOWN_TRUE` passes the committed schema (reproduced); only the Python validator rejects it. The tests acknowledge this by naming two cases `..._validator_only`. A consumer that validates with the published schema alone, which is what a pinned read-only assessor has, gets no protection, while `field_may_appear_once: true` is advertised in the semantics. Also schema-accepted but validator-rejected: `statements: 42`, a whitespace-only field definition, a missing `attestation_prohibitions`. `statements` and `fields_not_usable_in_rules_statement` are `required` but have no type constraint at all.
**Fix:** Draft 2020-12 can express once-per-field for a four-field vocabulary. Add to the `conditions` schema:

```python
'allOf': [{'not': {'contains': {'properties': {'field': {'const': f}}, 'required': ['field']}, 'minContains': 2}} for f in RULE_FIELDS]
```

Also add `'statements': {'const': semantics()['statements']}`, `'fields_not_usable_in_rules_statement': {'type': 'string', 'minLength': 1}`, and `'pattern': '\\S'` on the field definitions; then convert the two `_validator_only` tests to `both_reject`.

### WR-05: Approved field-definition wording is not pinned; an inverted definition passes both validators

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:164-168`
**Issue:** `field_definitions` is deliberately excluded from the semantics equality check and only tested for "four keys, non-empty text". Setting `production` to `'KNOWN_TRUE asserts that the target is NOT a production system.'` is accepted by the validator and the schema (reproduced). The definitions were approved in `01-FIELD-DEFINITIONS.md` and are what gives each rule condition its meaning, so a hand edit can invert every published rule on that field without failing validation.
**Fix:** Compare against the approved constant: `if sem.get('field_definitions') != FIELD_DEFINITIONS: errors.append('field_definitions do not match the approved wording')`, and pin with `const` in `schema()`. The separate comparison then becomes unnecessary (drop the `pin`/`expected` filtering and compare `sem != semantics()`).

### WR-06: Vocabulary and per-control fields that the semantics depend on are validated by neither validator

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:159-160,179-192,205-215`
**Issue:** All of the following are accepted by both `validate_authority()` and the schema (reproduced):

- `classification_vocabulary.fields = []` (so `rule_condition_fields` can name fields that are no longer declared)
- `applicability_vocabulary = ['NOT_APPLICABLE']`
- `controls[n].classification_prerequisites = []`
- `classification_vocabulary.unknown_is_not_not_applicable = 'no'` (line 160 tests truthiness, not `is True`)
- an extra per-control key such as `not_applicable_override: 'NOT_APPLICABLE'` (no `additionalProperties: false` on control items)

Separately, the validator accepts `unknown_is_never_not_applicable: 1` because the dict comparison at line 166 treats `1 == True`; the schema catches that one. Per-control `target_type`/`assessment_semantics` are checked only by the schema.
**Fix:** In `validate_authority()` add `cv.get('fields') != CLASSIFICATION_FIELDS`, `a.get('applicability_vocabulary') != RESULTS`, `r.get('classification_prerequisites') != CLASSIFICATION_FIELDS`, use `is not True` for the two vocabulary flags, and compare semantics with a type-strict check (for example `json.dumps(pin, sort_keys=True) != json.dumps(expected, sort_keys=True)`). Mirror these as `const` in `schema()` and set `additionalProperties: False` on control items with the full property list.

### WR-07: Structurally malformed authorities crash with `AttributeError`/`TypeError` instead of `AuthorityError`

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:159,172-174,177,180,193`
**Issue:** Reproduced crashes in `validate_authority()`: a non-dict control row (`'str' object has no attribute 'get'`), non-dict `classification_vocabulary`, `evidence_boundary`, `attestation_prohibitions`, a non-dict `dependencies` item, and an unhashable `control_id` (`TypeError: unhashable type: 'list'`). `not_applicable_semantics` and `source_lineage` are guarded with `isinstance`, the others are not. The process still exits non-zero, but the domain-exception contract (`AuthorityError`, on which every `invalid()` test depends) is broken and the aggregated error list is lost. In `main()` the Python validator runs before the schema, so the schema cannot pre-empt these; four of the six shapes also pass the schema.
**Fix:** In `main()` run `jsonschema.Draft202012Validator(load(SCHEMA)).validate(a)` before `validate_authority(a)` and type the affected properties in `schema()` (`classification_vocabulary`, `evidence_boundary`, `attestation_prohibitions` as `object`). In `validate_authority()` add an early guard: `if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows): raise AuthorityError('controls must be a list of objects')`, and coerce the three dict lookups the same way `sem` is coerced at line 162.

### WR-08: Negative tests assert only that some `AuthorityError` is raised, so they can pass for the wrong reason

**File:** `tests/test_archive_assessment_applicability_authority_v2.py:20-24,36-44`
**Issue:** `invalid()` uses a bare `pytest.raises(AuthorityError)` and `schema_rejects()` a bare `pytest.raises(jsonschema.ValidationError)`. Every one of the ~45 negative tests would still pass if the mutated authority were rejected by an unrelated check, or if the unmutated baseline stopped validating (only `test_not_yet_decided_state_passes` would then fail). The validator aggregates all errors into one message, so asserting the specific message is cheap. This is the reason the gaps in WR-02 to WR-07 are invisible to a green run.
**Fix:** Give `invalid` a `match` argument and assert exactly one error:

```python
def invalid(mutator, match):
    value = copy.deepcopy(build_authority()); mutator(value)
    with pytest.raises(AuthorityError, match=match) as e: validate_authority(value)
    assert '; ' not in str(e.value)
```

### WR-09: Missing test coverage for the behaviours most likely to regress

**File:** `tests/test_archive_assessment_applicability_authority_v2.py:140-156`
**Issue:** No test covers: the resolver on a control with no authority or with extra rule keys (WR-01); a trailing-newline authority id (WR-03); the lineage hashes (CR-01); `main()` at all (`--validate` with no file, `--emit-schema` round trip, neither flag); or agreement between `resolve_applicability()` and the five published `RESOLUTION` rows, which are asserted individually but never iterated against the table that Hayes will read. `RP`, `NR`, `NY` are also built at import time (line 142-144), so any failure in `build_authority()` surfaces as a collection error for the whole file rather than a failing test.
**Fix:** Add the cases above; parametrise the resolver tests over `MODULE.RESOLUTION`; build `RP`/`NR`/`NY` in a module-scoped fixture.

## Info

### IN-01: CLAUDE.md states rule conditions may use the eight declared fields; the implementation permits four

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:20-22`
**Issue:** The project constraint reads "Rule conditions use only the eight declared classification fields". The code restricts rules to the first four and rejects `owner`, `tier`, `service_criticality`, `data_classification`. The phase plan records this as a decision, and it is the stricter reading, but the two documents now disagree and `RULE_FIELDS = CLASSIFICATION_FIELDS[:4]` couples the split to list order.
**Fix:** Update the CLAUDE.md constraint wording, and define `RULE_FIELDS` explicitly rather than by slicing.

### IN-02: `supersedes` uses hard-coded literals, including an abbreviated commit hash

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:131,170`
**Issue:** `'version': '1.0.0'` is a literal rather than `v1['version']`, and `'commit': '62a8955'` is a 7-character abbreviation used as a lineage identity (full hash is `62a8955dc28d9458cd1167fad314926e057c31fc`). Abbreviations can become ambiguous as the repository grows.
**Fix:** Use `v1['version']` and the full 40-character hash in a named constant.

### IN-03: Decided controls keep per-control fields that contradict the governing decision state

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:107,110-111,182`
**Issue:** A `NO_RULE_WILL_BE_PUBLISHED` control resolves to `APPLICABLE` "whatever the facts", yet the validator forces it to keep `classification_unknown_treatment: APPLICABILITY_UNRESOLVED`, `default_applicability_result: APPLICABILITY_UNRESOLVED` and `unresolved_reason: CONTROLLED_TARGET_CLASSIFICATION_AND_AUTHORITY_INPUTS_REQUIRED`. The semantics statements say the decision state governs, but a consumer reading one control record sees conflicting signals.
**Fix:** Confirm this is intended with the approver; if so, state it in the document that accompanies publication.

### IN-04: `--validate` together with `--emit-schema` silently ignores `--emit-schema`

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:234-239`
**Issue:** The flags are not mutually exclusive; the `if/elif` drops the second one without a message.
**Fix:** `group = parser.add_mutually_exclusive_group(required=True)`; this also replaces the manual `parser.error`.

### IN-05: Dead and duplicated code carried over from v1

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:44-61,172-173`
**Issue:** `digest`, `dump`, `load`, `contains_absolute` and `catalog_controls` are verbatim copies of v1 (the "Duplicated helper code" anti-pattern named in CLAUDE.md). The `dependencies` loop validates a key that `build_authority()` never emits. `contains_absolute` inspects values only, not dict keys.
**Fix:** Import the helpers from the v1 module or a shared module; drop or justify the `dependencies` loop.

### IN-06: `resolve_applicability` returns a bare string, and one test is a brittle source-text check

**File:** `scripts/publish_archive_assessment_applicability_authority_v2.py:217`; `tests/test_archive_assessment_applicability_authority_v2.py:136-138`
**Issue:** The project convention is that resolvers return a status dict (`{"status","decision","source"}`), which would also let the result carry the authority id. `test_v2_builder_does_not_use_generated_dir` asserts the substring `'generated'` never appears in the script source, so an unrelated identifier or message containing that word fails the test.
**Fix:** Return a dict including the authority and matched row of `RESOLUTION`; replace the substring test with an assertion on module attributes (no `GENERATED`/`AA2` path constants).

---

_Reviewed: 2026-10-13T17:29:56Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
