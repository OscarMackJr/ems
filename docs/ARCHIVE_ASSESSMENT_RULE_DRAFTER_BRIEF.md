# Drafter brief

Your task: for each control in the catalog extract below, propose either a not-applicable rule or "no rule" for an archived repository snapshot target. An archived repository snapshot is an archived copy of a repository taken at one point in time. Use only the text in this brief. Use no tools, files or outside information about any particular target. Return a single JSON document and nothing else.

## What each outcome means

A "no rule" proposal means no not-applicable rule is published for that control. No rule resolves to APPLICABLE for every target whatever the facts. That is a real claim that the control applies to every archived repository snapshot, not a neutral default.

A rule resolves as follows.

- decision state NOT_YET_DECIDED, condition ALWAYS: result APPLICABILITY_UNRESOLVED
- decision state NO_RULE_WILL_BE_PUBLISHED, condition ALWAYS: result APPLICABLE
- decision state RULE_PUBLISHED, condition ALL_NAMED_FIELDS_KNOWN_AND_ALL_CONDITIONS_MET: result NOT_APPLICABLE
- decision state RULE_PUBLISHED, condition ALL_NAMED_FIELDS_KNOWN_AND_NOT_ALL_CONDITIONS_MET: result APPLICABLE
- decision state RULE_PUBLISHED, condition ANY_NAMED_FIELD_UNKNOWN: result APPLICABILITY_UNRESOLVED

In plain terms: a rule resolves NOT_APPLICABLE only when every field it names is known and every condition is met. It resolves APPLICABLE when every named field is known and not every condition is met. It resolves APPLICABILITY_UNRESOLVED when any named field is UNKNOWN. UNKNOWN never yields NOT_APPLICABLE. Absence of evidence is not not-applicable.

Fixed statements of the semantics:

- A not_applicable_rule is a flat list of conditions and all conditions must match.
- When every field named by a published rule is known and every condition is met, the result is NOT_APPLICABLE.
- When every field named by a published rule is known and not every condition is met, the result is APPLICABLE.
- NO_RULE_WILL_BE_PUBLISHED resolves to APPLICABLE for every target whatever the facts.
- NOT_YET_DECIDED resolves to APPLICABILITY_UNRESOLVED.
- When any field named by a published rule is UNKNOWN the result is APPLICABILITY_UNRESOLVED, even when another named field already fails its condition.
- UNKNOWN never yields NOT_APPLICABLE.
- The not_applicable_decision_state governs the resolved result; default_applicability_result describes the result absent a decision.

## Rule shape

A rule has combination ALL_CONDITIONS_MUST_MATCH and a list of 1 to 4 conditions. Every condition must match. Each condition has a field and a state. The state is KNOWN_TRUE or KNOWN_FALSE only. Each field may appear at most once in a rule.

The usable fields are production, internet_exposed, contains_customer_data, ai_enabled. Their definitions:

- production: KNOWN_TRUE asserts that the target is used as, or supports, a production system, so production-data, recovery and release controls are in play.
- internet_exposed: KNOWN_TRUE asserts that the target, or a service it provides, is reachable from the public internet.
- contains_customer_data: KNOWN_TRUE asserts that the target holds or processes customer data.
- ai_enabled: KNOWN_TRUE asserts that the target includes or uses AI capabilities, so AI-specific controls apply to it.

owner, tier, service_criticality and data_classification are declared classification fields that are not usable in rules in this version.

## Drafting posture

- Lean to no rule. Propose a rule only when the control name itself points at one of the four usable fields.
- Never propose a control as switchable-off on a guess.
- Use the fewest conditions that justify the rule, normally one, because each added field is one more that can be UNKNOWN.
- A control that would need an "or" is drafted as a narrower single condition list or as no rule.
- Six entries in the extract are not REPOSITORY scoped. Where scope is the real reason a control might not apply and the four fields cannot say so, record a shape_limitation note.
- There is no third outcome. Every entry is either a rule or no rule.
- Give every entry a confidence of HIGH, MEDIUM or LOW, and an alternative_considered: the outcome you rejected and why, or null.

## Interpretation and rationale

None of the catalog entries has a description. The seed rationale field in the entries is boilerplate and not a definition.

You may read the control name using general engineering knowledge. That reading goes in the separate interpretation object with the label DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE, as your own assumption.

Each rationale is two to four sentences. End each sentence with a period and avoid abbreviations that contain periods. Each rationale must stand alone and name its own control's practice. Use no cross-references and no shared reason codes between entries. Each rationale covers: why the outcome follows from the interpretation; for a rule, why the named field and state mark the control as not applying in terms of the approved field definition; for no rule, why none of the four fields gives a sound exemption.

## Catalog extract

The 21 entries below are verbatim. Draft one proposal for each, in this order.

```json
[
  {
    "control_id": "EMS-CTRL-009",
    "control_name": "Branch Protection Required",
    "scope": "REPOSITORY",
    "scope_owner": "Software Development",
    "inheritance_allowed": false,
    "evidence_authority": "Repository evidence",
    "rationale": "Wave 2A seed classification: REPOSITORY-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-010",
    "control_name": "Pull Request Review",
    "scope": "REPOSITORY",
    "scope_owner": "Software Development",
    "inheritance_allowed": false,
    "evidence_authority": "Repository evidence",
    "rationale": "Wave 2A seed classification: REPOSITORY-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-011",
    "control_name": "CODEOWNERS Enforcement",
    "scope": "REPOSITORY",
    "scope_owner": "Software Development",
    "inheritance_allowed": false,
    "evidence_authority": "Repository evidence",
    "rationale": "Wave 2A seed classification: REPOSITORY-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-012",
    "control_name": "Signed Commits",
    "scope": "REPOSITORY",
    "scope_owner": "Software Development",
    "inheritance_allowed": false,
    "evidence_authority": "Repository evidence",
    "rationale": "Wave 2A seed classification: REPOSITORY-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-013",
    "control_name": "Protected Release Tags",
    "scope": "REPOSITORY",
    "scope_owner": "Software Development",
    "inheritance_allowed": false,
    "evidence_authority": "Repository evidence",
    "rationale": "Wave 2A seed classification: REPOSITORY-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-014",
    "control_name": "Mandatory Issue Linkage",
    "scope": "REPOSITORY",
    "scope_owner": "Software Development",
    "inheritance_allowed": false,
    "evidence_authority": "Repository evidence",
    "rationale": "Wave 2A seed classification: REPOSITORY-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-015",
    "control_name": "Repository Template Compliance",
    "scope": "REPOSITORY",
    "scope_owner": "Software Development",
    "inheritance_allowed": false,
    "evidence_authority": "Repository evidence",
    "rationale": "Wave 2A seed classification: REPOSITORY-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-017",
    "control_name": "Secure Coding Standard",
    "scope": "REPOSITORY",
    "scope_owner": "Software Development",
    "inheritance_allowed": false,
    "evidence_authority": "Repository evidence",
    "rationale": "Wave 2A seed classification: REPOSITORY-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-018",
    "control_name": "Secret Scanning",
    "scope": "REPOSITORY",
    "scope_owner": "Software Development",
    "inheritance_allowed": false,
    "evidence_authority": "Repository evidence",
    "rationale": "Wave 2A seed classification: REPOSITORY-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-019",
    "control_name": "Dependency Vulnerability Scanning",
    "scope": "REPOSITORY",
    "scope_owner": "Software Development",
    "inheritance_allowed": false,
    "evidence_authority": "Repository evidence",
    "rationale": "Wave 2A seed classification: REPOSITORY-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-020",
    "control_name": "License Compliance",
    "scope": "REPOSITORY",
    "scope_owner": "Software Development",
    "inheritance_allowed": false,
    "evidence_authority": "Repository evidence",
    "rationale": "Wave 2A seed classification: REPOSITORY-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-021",
    "control_name": "SBOM Generation",
    "scope": "REPOSITORY",
    "scope_owner": "Software Development",
    "inheritance_allowed": false,
    "evidence_authority": "Repository evidence",
    "rationale": "Wave 2A seed classification: REPOSITORY-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-022",
    "control_name": "Security Advisory Monitoring",
    "scope": "PLATFORM",
    "scope_owner": "Software Development / Platform",
    "inheritance_allowed": true,
    "evidence_authority": "Platform evidence",
    "rationale": "Wave 2A seed classification: PLATFORM-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-030",
    "control_name": "Disaster Recovery Testing",
    "scope": "SERVICE",
    "scope_owner": "Software Development",
    "inheritance_allowed": true,
    "evidence_authority": "Service evidence",
    "rationale": "Wave 2A seed classification: SERVICE-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-033",
    "control_name": "Reproducible Builds",
    "scope": "REPOSITORY",
    "scope_owner": "Software Development",
    "inheritance_allowed": false,
    "evidence_authority": "Repository evidence",
    "rationale": "Wave 2A seed classification: REPOSITORY-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-039",
    "control_name": "Release Approval Workflow",
    "scope": "REPOSITORY",
    "scope_owner": "Software Development",
    "inheritance_allowed": false,
    "evidence_authority": "Repository evidence",
    "rationale": "Wave 2A seed classification: REPOSITORY-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-042",
    "control_name": "IaC Security Scanning",
    "scope": "PLATFORM",
    "scope_owner": "Software Development / Platform",
    "inheritance_allowed": true,
    "evidence_authority": "Platform evidence",
    "rationale": "Wave 2A seed classification: PLATFORM-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-052",
    "control_name": "AI Attribution",
    "scope": "ORGANIZATION",
    "scope_owner": "Engineering Leadership",
    "inheritance_allowed": true,
    "evidence_authority": "Organizational evidence",
    "rationale": "Wave 2A seed classification: ORGANIZATION-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-062",
    "control_name": "Schema Version Control",
    "scope": "APPLICATION",
    "scope_owner": "Software Development",
    "inheritance_allowed": true,
    "evidence_authority": "Application evidence",
    "rationale": "Wave 2A seed classification: APPLICATION-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-075",
    "control_name": "Continuous Compliance Scan",
    "scope": "EMS",
    "scope_owner": "EMS Governance",
    "inheritance_allowed": true,
    "evidence_authority": "EMS evidence",
    "rationale": "Wave 2A seed classification: EMS-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  },
  {
    "control_id": "EMS-CTRL-079",
    "control_name": "Repository Health Review",
    "scope": "REPOSITORY",
    "scope_owner": "Software Development",
    "inheritance_allowed": false,
    "evidence_authority": "Repository evidence",
    "rationale": "Wave 2A seed classification: REPOSITORY-scoped based on the control's primary operating boundary.",
    "classification_status": "PROVISIONAL"
  }
]
```

## Header to copy

The output document is the object below copied verbatim, plus one added top-level key `proposals` holding the list of 21 proposals.

```json
{
  "status": "DRAFT_NO_AUTHORITY",
  "non_authority_statement": "This file is a set of drafts. It is not an authority, it binds nothing and it must not be cited as a decision.",
  "drafting_frame": {
    "requires_explicit_controlled_rule": true,
    "absence_of_evidence_is_not_not_applicable": true,
    "unknown_is_not_not_applicable": true,
    "decision_states": [
      "RULE_PUBLISHED",
      "NO_RULE_WILL_BE_PUBLISHED",
      "NOT_YET_DECIDED"
    ],
    "condition_states": [
      "KNOWN_TRUE",
      "KNOWN_FALSE"
    ],
    "condition_combination": "ALL_CONDITIONS_MUST_MATCH",
    "min_conditions": 1,
    "field_may_appear_once": true,
    "rule_condition_fields": [
      "production",
      "internet_exposed",
      "contains_customer_data",
      "ai_enabled"
    ],
    "fields_not_usable_in_rules": [
      "owner",
      "tier",
      "service_criticality",
      "data_classification"
    ],
    "fields_not_usable_in_rules_statement": "owner, tier, service_criticality and data_classification are declared classification fields that are not usable in rules in this version.",
    "field_definitions": {
      "production": "KNOWN_TRUE asserts that the target is used as, or supports, a production system, so production-data, recovery and release controls are in play.",
      "internet_exposed": "KNOWN_TRUE asserts that the target, or a service it provides, is reachable from the public internet.",
      "contains_customer_data": "KNOWN_TRUE asserts that the target holds or processes customer data.",
      "ai_enabled": "KNOWN_TRUE asserts that the target includes or uses AI capabilities, so AI-specific controls apply to it."
    },
    "resolution": [
      {
        "decision_state": "NOT_YET_DECIDED",
        "condition": "ALWAYS",
        "result": "APPLICABILITY_UNRESOLVED"
      },
      {
        "decision_state": "NO_RULE_WILL_BE_PUBLISHED",
        "condition": "ALWAYS",
        "result": "APPLICABLE"
      },
      {
        "decision_state": "RULE_PUBLISHED",
        "condition": "ALL_NAMED_FIELDS_KNOWN_AND_ALL_CONDITIONS_MET",
        "result": "NOT_APPLICABLE"
      },
      {
        "decision_state": "RULE_PUBLISHED",
        "condition": "ALL_NAMED_FIELDS_KNOWN_AND_NOT_ALL_CONDITIONS_MET",
        "result": "APPLICABLE"
      },
      {
        "decision_state": "RULE_PUBLISHED",
        "condition": "ANY_NAMED_FIELD_UNKNOWN",
        "result": "APPLICABILITY_UNRESOLVED"
      }
    ],
    "no_short_circuit": true,
    "decision_state_governs_resolved_result": true,
    "per_control_default_describes_result_absent_a_decision": true,
    "unknown_is_never_not_applicable": true,
    "statements": [
      "A not_applicable_rule is a flat list of conditions and all conditions must match.",
      "When every field named by a published rule is known and every condition is met, the result is NOT_APPLICABLE.",
      "When every field named by a published rule is known and not every condition is met, the result is APPLICABLE.",
      "NO_RULE_WILL_BE_PUBLISHED resolves to APPLICABLE for every target whatever the facts.",
      "NOT_YET_DECIDED resolves to APPLICABILITY_UNRESOLVED.",
      "When any field named by a published rule is UNKNOWN the result is APPLICABILITY_UNRESOLVED, even when another named field already fails its condition.",
      "UNKNOWN never yields NOT_APPLICABLE.",
      "The not_applicable_decision_state governs the resolved result; default_applicability_result describes the result absent a decision."
    ]
  },
  "catalog_source": {
    "relative_path": "registry/control_catalog.yaml",
    "git_blob_id": "03c9faa44af37860fe268a74bcb4468e8bfd34c4",
    "sha256": "12bb1a9d2476e4b0208ff51f9296f51462395f01af8d0543ad3c7eae9f039477",
    "entries_have_description": false,
    "note": "None of the 21 requested catalog entries carries a description, and the catalog seed rationale field is boilerplate, not a definition."
  }
}
```

## Output format

Return bare JSON with no code fence and no commentary. The document is the header object plus the key `proposals`, a list with exactly one proposal per entry of the catalog extract, in the same order. A proposal has exactly these keys and no others.

- control_id: the id of the entry.
- proposed_outcome: PROPOSE_RULE or PROPOSE_NO_RULE.
- proposed_rule: the rule object when PROPOSE_RULE, otherwise null.
- catalog_inputs: copies control_name, scope, scope_owner and evidence_authority exactly from the entry. inheritance_allowed and classification_status may also be copied.
- interpretation: an object with label and text.
- rationale: as described above.
- confidence: HIGH, MEDIUM or LOW.
- alternative_considered: null, or an object with outcome and why.
- shape_limitation: null, or an object with scope and note, where scope is the entry's scope.

Do not add an authority field or a decision id anywhere.

Proposal skeleton (placeholders only):

```json
{
  "control_id": "<ID from the extract>",
  "proposed_outcome": "<PROPOSE_RULE or PROPOSE_NO_RULE>",
  "proposed_rule": "<rule object with combination and conditions when PROPOSE_RULE, otherwise null>",
  "catalog_inputs": {
    "control_name": "<copied exactly from the entry>",
    "scope": "<copied exactly from the entry>",
    "scope_owner": "<copied exactly from the entry>",
    "evidence_authority": "<copied exactly from the entry>"
  },
  "interpretation": {
    "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
    "text": "<your reading of what the control name means>"
  },
  "rationale": "<two to four sentences>",
  "confidence": "<HIGH, MEDIUM or LOW>",
  "alternative_considered": "<null, or an object with outcome and why>",
  "shape_limitation": "<null, or an object with scope and note>"
}
```

Rule object skeleton:

```json
{
  "combination": "ALL_CONDITIONS_MUST_MATCH",
  "conditions": [
    {
      "field": "<one of the four usable fields>",
      "state": "<KNOWN_TRUE or KNOWN_FALSE>"
    }
  ]
}
```

alternative_considered object skeleton:

```json
{
  "outcome": "<the outcome you rejected>",
  "why": "<why it was rejected>"
}
```

shape_limitation object skeleton:

```json
{
  "scope": "<the entry scope, copied exactly>",
  "note": "<why the four fields cannot express the real reason>"
}
```
