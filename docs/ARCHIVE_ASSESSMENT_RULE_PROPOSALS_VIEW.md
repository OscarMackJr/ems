# Archive Assessment Rule Proposals View

This view is derived from the frozen proposals file by scripts/build_archive_assessment_governance_decisions.py and is read-only.

## Drafting frame

```json
{
  "absence_of_evidence_is_not_not_applicable": true,
  "condition_combination": "ALL_CONDITIONS_MUST_MATCH",
  "condition_states": [
    "KNOWN_TRUE",
    "KNOWN_FALSE"
  ],
  "decision_state_governs_resolved_result": true,
  "decision_states": [
    "RULE_PUBLISHED",
    "NO_RULE_WILL_BE_PUBLISHED",
    "NOT_YET_DECIDED"
  ],
  "field_definitions": {
    "ai_enabled": "KNOWN_TRUE asserts that the target includes or uses AI capabilities, so AI-specific controls apply to it.",
    "contains_customer_data": "KNOWN_TRUE asserts that the target holds or processes customer data.",
    "internet_exposed": "KNOWN_TRUE asserts that the target, or a service it provides, is reachable from the public internet.",
    "production": "KNOWN_TRUE asserts that the target is used as, or supports, a production system, so production-data, recovery and release controls are in play."
  },
  "field_may_appear_once": true,
  "fields_not_usable_in_rules": [
    "owner",
    "tier",
    "service_criticality",
    "data_classification"
  ],
  "fields_not_usable_in_rules_statement": "owner, tier, service_criticality and data_classification are declared classification fields that are not usable in rules in this version.",
  "min_conditions": 1,
  "no_short_circuit": true,
  "per_control_default_describes_result_absent_a_decision": true,
  "requires_explicit_controlled_rule": true,
  "resolution": [
    {
      "condition": "ALWAYS",
      "decision_state": "NOT_YET_DECIDED",
      "result": "APPLICABILITY_UNRESOLVED"
    },
    {
      "condition": "ALWAYS",
      "decision_state": "NO_RULE_WILL_BE_PUBLISHED",
      "result": "APPLICABLE"
    },
    {
      "condition": "ALL_NAMED_FIELDS_KNOWN_AND_ALL_CONDITIONS_MET",
      "decision_state": "RULE_PUBLISHED",
      "result": "NOT_APPLICABLE"
    },
    {
      "condition": "ALL_NAMED_FIELDS_KNOWN_AND_NOT_ALL_CONDITIONS_MET",
      "decision_state": "RULE_PUBLISHED",
      "result": "APPLICABLE"
    },
    {
      "condition": "ANY_NAMED_FIELD_UNKNOWN",
      "decision_state": "RULE_PUBLISHED",
      "result": "APPLICABILITY_UNRESOLVED"
    }
  ],
  "rule_condition_fields": [
    "production",
    "internet_exposed",
    "contains_customer_data",
    "ai_enabled"
  ],
  "statements": [
    "A not_applicable_rule is a flat list of conditions and all conditions must match.",
    "When every field named by a published rule is known and every condition is met, the result is NOT_APPLICABLE.",
    "When every field named by a published rule is known and not every condition is met, the result is APPLICABLE.",
    "NO_RULE_WILL_BE_PUBLISHED resolves to APPLICABLE for every target whatever the facts.",
    "NOT_YET_DECIDED resolves to APPLICABILITY_UNRESOLVED.",
    "When any field named by a published rule is UNKNOWN the result is APPLICABILITY_UNRESOLVED, even when another named field already fails its condition.",
    "UNKNOWN never yields NOT_APPLICABLE.",
    "The not_applicable_decision_state governs the resolved result; default_applicability_result describes the result absent a decision."
  ],
  "unknown_is_never_not_applicable": true,
  "unknown_is_not_not_applicable": true
}
```

## EMS-CTRL-009

### catalog_inputs

```json
{
  "control_name": "Branch Protection Required",
  "evidence_authority": "Repository evidence",
  "scope": "REPOSITORY",
  "scope_owner": "Software Development"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "The important branches of the repository are configured so that direct pushes, forced pushes and deletion are blocked and changes must pass defined gates before they land."
}
```

### proposed_outcome

PROPOSE_NO_RULE

### proposed_rule

```json
null
```

### rationale

Branch protection is a configuration of the repository itself that guards branch history against direct or forced changes, so it follows the repository and not any deployment fact. None of production, internet_exposed, contains_customer_data or ai_enabled says whether a repository has branch history worth protecting, so none of them gives a sound exemption. Proposing no rule claims that branch protection applies to every archived repository snapshot, and the frozen nature of a snapshot cannot be expressed with the four usable fields.

### confidence

HIGH

### alternative_considered

```json
{
  "outcome": "PROPOSE_RULE",
  "why": "A rule on production KNOWN_FALSE was rejected because the control name does not point at production and a repository that supports no production system still needs its branch history guarded."
}
```

### shape_limitation

```json
null
```

## EMS-CTRL-010

### catalog_inputs

```json
{
  "control_name": "Pull Request Review",
  "evidence_authority": "Repository evidence",
  "scope": "REPOSITORY",
  "scope_owner": "Software Development"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "Changes enter the repository through pull requests that are approved by at least one reviewer other than the author before merge."
}
```

### proposed_outcome

PROPOSE_NO_RULE

### proposed_rule

```json
null
```

### rationale

Pull request review is a practice about how changes are accepted into a repository, and the evidence for it lives in the merge history that a snapshot still carries. Whether the target is production, internet exposed, holds customer data or is AI enabled does not change whether its changes should have been reviewed, so none of the four fields gives a sound exemption. Proposing no rule therefore claims that pull request review applies to every archived repository snapshot.

### confidence

HIGH

### alternative_considered

```json
{
  "outcome": "PROPOSE_RULE",
  "why": "A rule on production KNOWN_FALSE was rejected because it would be a guess that review only matters for production code, and the control name does not point at any usable field."
}
```

### shape_limitation

```json
null
```

## EMS-CTRL-011

### catalog_inputs

```json
{
  "control_name": "CODEOWNERS Enforcement",
  "evidence_authority": "Repository evidence",
  "scope": "REPOSITORY",
  "scope_owner": "Software Development"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "The repository carries a CODEOWNERS file that assigns owners to paths, and review by those owners is enforced for changes to the paths they own."
}
```

### proposed_outcome

PROPOSE_NO_RULE

### proposed_rule

```json
null
```

### rationale

CODEOWNERS enforcement is a repository practice that ties paths to accountable reviewers, and it is evidenced by a file and settings that belong to the repository. None of production, internet_exposed, contains_customer_data or ai_enabled describes whether a repository needs accountable path owners, so none of them gives a sound exemption. Proposing no rule claims that CODEOWNERS enforcement applies to every archived repository snapshot.

### confidence

HIGH

### alternative_considered

```json
{
  "outcome": "PROPOSE_RULE",
  "why": "The only field that sounds related is owner, which is a classification field that is not usable in rules in this version and does not describe code ownership of paths in any case."
}
```

### shape_limitation

```json
null
```

## EMS-CTRL-012

### catalog_inputs

```json
{
  "control_name": "Signed Commits",
  "evidence_authority": "Repository evidence",
  "scope": "REPOSITORY",
  "scope_owner": "Software Development"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "Commits in the repository are cryptographically signed by their authors and the signatures can be verified."
}
```

### proposed_outcome

PROPOSE_NO_RULE

### proposed_rule

```json
null
```

### rationale

Signed commits are a property of the commit history, and that history is exactly what an archived snapshot preserves and what a reader of the snapshot relies on for authorship. None of production, internet_exposed, contains_customer_data or ai_enabled bears on whether authorship of commits should be verifiable, so none of them gives a sound exemption. Proposing no rule claims that signed commits apply to every archived repository snapshot.

### confidence

HIGH

### alternative_considered

```json
null
```

### shape_limitation

```json
null
```

## EMS-CTRL-013

### catalog_inputs

```json
{
  "control_name": "Protected Release Tags",
  "evidence_authority": "Repository evidence",
  "scope": "REPOSITORY",
  "scope_owner": "Software Development"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "Tags that mark released versions are protected so that they cannot be moved, overwritten or deleted by ordinary contributors."
}
```

### proposed_outcome

PROPOSE_NO_RULE

### proposed_rule

```json
null
```

### rationale

Protected release tags keep the mapping between a version label and a commit from being altered, which is an integrity property of the repository history and not of a deployment. A repository that supports no production system can still publish tagged versions that others consume, so production KNOWN_FALSE is not a sound exemption, and internet_exposed, contains_customer_data and ai_enabled do not relate to tags at all. Proposing no rule claims that protected release tags apply to every archived repository snapshot.

### confidence

MEDIUM

### alternative_considered

```json
{
  "outcome": "PROPOSE_RULE",
  "why": "A rule on production KNOWN_FALSE was considered because the production definition mentions release controls, but it was rejected because tag protection guards history integrity for any tagged version and exempting it would rest on a guess about what the tags are used for."
}
```

### shape_limitation

```json
null
```

## EMS-CTRL-014

### catalog_inputs

```json
{
  "control_name": "Mandatory Issue Linkage",
  "evidence_authority": "Repository evidence",
  "scope": "REPOSITORY",
  "scope_owner": "Software Development"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "Every change merged into the repository references a tracked issue or work item so that the reason for the change can be traced."
}
```

### proposed_outcome

PROPOSE_NO_RULE

### proposed_rule

```json
null
```

### rationale

Mandatory issue linkage is a traceability practice recorded in commits and pull requests, and that record remains in a snapshot of the repository. None of production, internet_exposed, contains_customer_data or ai_enabled describes whether changes need a traceable reason, so none of them gives a sound exemption. Proposing no rule claims that mandatory issue linkage applies to every archived repository snapshot.

### confidence

HIGH

### alternative_considered

```json
null
```

### shape_limitation

```json
null
```

## EMS-CTRL-015

### catalog_inputs

```json
{
  "control_name": "Repository Template Compliance",
  "evidence_authority": "Repository evidence",
  "scope": "REPOSITORY",
  "scope_owner": "Software Development"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "The repository conforms to the standard repository template of the organisation, including its required files, layout and baseline settings."
}
```

### proposed_outcome

PROPOSE_NO_RULE

### proposed_rule

```json
null
```

### rationale

Repository template compliance checks the structure and required files of the repository itself, which can be assessed on a snapshot as readily as on a live repository. None of production, internet_exposed, contains_customer_data or ai_enabled describes whether a repository should follow the standard template, so none of them gives a sound exemption. Proposing no rule claims that repository template compliance applies to every archived repository snapshot.

### confidence

HIGH

### alternative_considered

```json
null
```

### shape_limitation

```json
null
```

## EMS-CTRL-017

### catalog_inputs

```json
{
  "control_name": "Secure Coding Standard",
  "evidence_authority": "Repository evidence",
  "scope": "REPOSITORY",
  "scope_owner": "Software Development"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "The code in the repository is written and checked against a defined secure coding standard."
}
```

### proposed_outcome

PROPOSE_NO_RULE

### proposed_rule

```json
null
```

### rationale

A secure coding standard governs how the code in the repository is written, and the code is the content that a snapshot preserves and that may later be reused. Code that is not internet exposed or not in production can still be copied, restored or deployed later, so neither internet_exposed nor production gives a sound exemption, and contains_customer_data and ai_enabled do not relate to coding practice. Proposing no rule claims that the secure coding standard applies to every archived repository snapshot.

### confidence

HIGH

### alternative_considered

```json
{
  "outcome": "PROPOSE_RULE",
  "why": "A rule on internet_exposed KNOWN_FALSE was rejected because the control name does not point at exposure and insecure code is a risk on internal systems as well."
}
```

### shape_limitation

```json
null
```

## EMS-CTRL-018

### catalog_inputs

```json
{
  "control_name": "Secret Scanning",
  "evidence_authority": "Repository evidence",
  "scope": "REPOSITORY",
  "scope_owner": "Software Development"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "The repository content and history are scanned for committed credentials, keys and tokens, and findings are handled."
}
```

### proposed_outcome

PROPOSE_NO_RULE

### proposed_rule

```json
null
```

### rationale

Secret scanning looks for credentials committed to repository content and history, and an archived snapshot retains any such credentials for as long as the copy exists. Secrets are not customer data, and a leaked key is harmful whether or not the target is production, internet exposed or AI enabled, so none of the four fields gives a sound exemption. Proposing no rule claims that secret scanning applies to every archived repository snapshot.

### confidence

HIGH

### alternative_considered

```json
{
  "outcome": "PROPOSE_RULE",
  "why": "A rule on contains_customer_data KNOWN_FALSE was rejected because credentials are a different class of content from customer data and the control name does not point at that field."
}
```

### shape_limitation

```json
null
```

## EMS-CTRL-019

### catalog_inputs

```json
{
  "control_name": "Dependency Vulnerability Scanning",
  "evidence_authority": "Repository evidence",
  "scope": "REPOSITORY",
  "scope_owner": "Software Development"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "The third party dependencies declared by the repository are scanned for known vulnerabilities and the findings are tracked."
}
```

### proposed_outcome

PROPOSE_NO_RULE

### proposed_rule

```json
null
```

### rationale

Dependency vulnerability scanning examines the dependency declarations held in the repository, and those declarations are present in a snapshot and become riskier as new vulnerabilities are disclosed over time. A vulnerable dependency matters when the code is restored or reused whatever the exposure or production status at the time of the snapshot, and contains_customer_data and ai_enabled do not relate to dependencies. Proposing no rule claims that dependency vulnerability scanning applies to every archived repository snapshot.

### confidence

HIGH

### alternative_considered

```json
{
  "outcome": "PROPOSE_RULE",
  "why": "A rule on internet_exposed KNOWN_FALSE was rejected because the control name does not point at exposure and vulnerable dependencies are exploitable on internal systems too."
}
```

### shape_limitation

```json
null
```

## EMS-CTRL-020

### catalog_inputs

```json
{
  "control_name": "License Compliance",
  "evidence_authority": "Repository evidence",
  "scope": "REPOSITORY",
  "scope_owner": "Software Development"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "The licences of the code and dependencies in the repository are identified and checked against the licences the organisation permits."
}
```

### proposed_outcome

PROPOSE_NO_RULE

### proposed_rule

```json
null
```

### rationale

License compliance concerns the legal terms attached to the code and dependencies that the repository holds, and holding a copy in an archive does not remove those terms. None of production, internet_exposed, contains_customer_data or ai_enabled describes licence obligations, so none of them gives a sound exemption. Proposing no rule claims that license compliance applies to every archived repository snapshot.

### confidence

HIGH

### alternative_considered

```json
null
```

### shape_limitation

```json
null
```

## EMS-CTRL-021

### catalog_inputs

```json
{
  "control_name": "SBOM Generation",
  "evidence_authority": "Repository evidence",
  "scope": "REPOSITORY",
  "scope_owner": "Software Development"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "A software bill of materials listing the components and dependencies of the repository is generated and kept with it."
}
```

### proposed_outcome

PROPOSE_NO_RULE

### proposed_rule

```json
null
```

### rationale

SBOM generation produces an inventory of the components in the repository, and that inventory is useful for an archived copy because it lets later vulnerability and licence questions be answered without rebuilding. The control name does not point at production, internet_exposed, contains_customer_data or ai_enabled, and a component inventory is meaningful whatever those facts are. Proposing no rule claims that SBOM generation applies to every archived repository snapshot.

### confidence

MEDIUM

### alternative_considered

```json
{
  "outcome": "PROPOSE_RULE",
  "why": "A rule on production KNOWN_FALSE was rejected because it assumes a bill of materials is only needed for shipped production artefacts, which is a guess the control name does not support."
}
```

### shape_limitation

```json
null
```

## EMS-CTRL-022

### catalog_inputs

```json
{
  "control_name": "Security Advisory Monitoring",
  "evidence_authority": "Platform evidence",
  "scope": "PLATFORM",
  "scope_owner": "Software Development / Platform"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "Published security advisories that affect the components in use are monitored at platform level and routed to the teams that must act on them."
}
```

### proposed_outcome

PROPOSE_NO_RULE

### proposed_rule

```json
null
```

### rationale

Security advisory monitoring watches for newly published advisories against components in use, and advisories keep appearing after a snapshot is taken. None of production, internet_exposed, contains_customer_data or ai_enabled says whether advisories are relevant to the components a target holds, so none of them gives a sound exemption. Proposing no rule claims that security advisory monitoring applies to every archived repository snapshot, although the real doubt is about platform scope and not about any of the four fields.

### confidence

MEDIUM

### alternative_considered

```json
{
  "outcome": "PROPOSE_RULE",
  "why": "A rule on internet_exposed KNOWN_FALSE was rejected because the control name does not point at exposure and advisories matter for internal components as well."
}
```

### shape_limitation

```json
{
  "note": "The control is scoped to the platform and its evidence is platform evidence, so the real reason it might not apply to an archived repository snapshot is that the snapshot is not the platform that operates the monitoring. None of the four usable fields can express a mismatch between control scope and target type.",
  "scope": "PLATFORM"
}
```

## EMS-CTRL-030

### catalog_inputs

```json
{
  "control_name": "Disaster Recovery Testing",
  "evidence_authority": "Service evidence",
  "scope": "SERVICE",
  "scope_owner": "Software Development"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "The ability to recover a service after a major outage or loss is exercised on a schedule and the results are recorded."
}
```

### proposed_outcome

PROPOSE_RULE

### proposed_rule

```json
{
  "combination": "ALL_CONDITIONS_MUST_MATCH",
  "conditions": [
    {
      "field": "production",
      "state": "KNOWN_FALSE"
    }
  ]
}
```

### rationale

Disaster recovery testing exercises the recovery of a running service, and the approved definition of production states that recovery controls are in play when the target is used as, or supports, a production system. When production is KNOWN_FALSE the target neither is nor supports a production system, so there is no production recovery to test and the control does not apply. A snapshot that serves as a recovery source for a production system would be production KNOWN_TRUE and the control would then resolve as applicable, and an UNKNOWN value leaves applicability unresolved.

### confidence

HIGH

### alternative_considered

```json
{
  "outcome": "PROPOSE_NO_RULE",
  "why": "No rule was rejected because it would claim that disaster recovery testing applies to every archived repository snapshot, including those that support no production system, while the production definition names recovery controls directly."
}
```

### shape_limitation

```json
{
  "note": "The control is scoped to a service and an archived repository snapshot is not itself a service. The production field is used as the nearest expressible condition, but the four usable fields cannot state that the target type falls outside service scope.",
  "scope": "SERVICE"
}
```

## EMS-CTRL-033

### catalog_inputs

```json
{
  "control_name": "Reproducible Builds",
  "evidence_authority": "Repository evidence",
  "scope": "REPOSITORY",
  "scope_owner": "Software Development"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "Building the same source revision with the pinned toolchain and dependencies yields the same output each time."
}
```

### proposed_outcome

PROPOSE_NO_RULE

### proposed_rule

```json
null
```

### rationale

Reproducible builds depend on pinned inputs and build definitions held in the repository, and an archived copy is valuable largely because it can be rebuilt faithfully later. The control name does not point at production, internet_exposed, contains_customer_data or ai_enabled, and build determinism is a property of the source and its build definition whatever those facts are. Proposing no rule claims that reproducible builds apply to every archived repository snapshot.

### confidence

MEDIUM

### alternative_considered

```json
{
  "outcome": "PROPOSE_RULE",
  "why": "A rule on production KNOWN_FALSE was rejected because the control name does not point at production and treating reproducibility as a production only concern would be a guess."
}
```

### shape_limitation

```json
null
```

## EMS-CTRL-039

### catalog_inputs

```json
{
  "control_name": "Release Approval Workflow",
  "evidence_authority": "Repository evidence",
  "scope": "REPOSITORY",
  "scope_owner": "Software Development"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "A release from the repository must pass a recorded approval step by an authorised person before it is promoted to production use."
}
```

### proposed_outcome

PROPOSE_RULE

### proposed_rule

```json
{
  "combination": "ALL_CONDITIONS_MUST_MATCH",
  "conditions": [
    {
      "field": "production",
      "state": "KNOWN_FALSE"
    }
  ]
}
```

### rationale

A release approval workflow gates the promotion of a release into production use, and the approved definition of production states that release controls are in play when the target is used as, or supports, a production system. When production is KNOWN_FALSE the target feeds no production system, so there is no production release for the workflow to approve and the control does not apply. A single condition is used so that only one field can be UNKNOWN, and an UNKNOWN value leaves applicability unresolved.

### confidence

MEDIUM

### alternative_considered

```json
{
  "outcome": "PROPOSE_NO_RULE",
  "why": "No rule was considered because a repository that supports no production system might still publish releases to other consumers, but it was rejected because the production definition names release controls directly and no rule would assert the workflow for every snapshot whatever the facts."
}
```

### shape_limitation

```json
null
```

## EMS-CTRL-042

### catalog_inputs

```json
{
  "control_name": "IaC Security Scanning",
  "evidence_authority": "Platform evidence",
  "scope": "PLATFORM",
  "scope_owner": "Software Development / Platform"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "Infrastructure as code definitions are scanned for insecure configuration before they are applied."
}
```

### proposed_outcome

PROPOSE_NO_RULE

### proposed_rule

```json
null
```

### rationale

IaC security scanning checks infrastructure definitions for insecure configuration, and whether it is relevant turns on whether the target holds such definitions. None of production, internet_exposed, contains_customer_data or ai_enabled says whether infrastructure definitions are present, and exposure or production status of the snapshot does not show that its definitions are safe to reuse. Proposing no rule claims that IaC security scanning applies to every archived repository snapshot, because no usable field gives a sound exemption.

### confidence

MEDIUM

### alternative_considered

```json
{
  "outcome": "PROPOSE_RULE",
  "why": "A rule on production KNOWN_FALSE or internet_exposed KNOWN_FALSE was rejected because the control name points at neither field and infrastructure definitions in a non-production or internal target can still be applied later."
}
```

### shape_limitation

```json
{
  "note": "The control is scoped to the platform, and the real reasons it might not apply are that the target is not the platform and that the snapshot may hold no infrastructure as code. None of the four usable fields can express control scope or the presence of infrastructure definitions.",
  "scope": "PLATFORM"
}
```

## EMS-CTRL-052

### catalog_inputs

```json
{
  "control_name": "AI Attribution",
  "evidence_authority": "Organizational evidence",
  "scope": "ORGANIZATION",
  "scope_owner": "Engineering Leadership"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "Content or output that was produced with AI capabilities is identified and attributed as such. This reading assumes that AI assisted authoring of the target content counts as the target using AI capabilities."
}
```

### proposed_outcome

PROPOSE_RULE

### proposed_rule

```json
{
  "combination": "ALL_CONDITIONS_MUST_MATCH",
  "conditions": [
    {
      "field": "ai_enabled",
      "state": "KNOWN_FALSE"
    }
  ]
}
```

### rationale

AI attribution is an AI-specific practice of marking what was produced with AI capabilities, and the approved definition of ai_enabled states that AI-specific controls apply when the target includes or uses AI capabilities. When ai_enabled is KNOWN_FALSE the target neither includes nor uses AI capabilities, so there is nothing produced by AI to attribute and the control does not apply. An UNKNOWN value leaves applicability unresolved, which keeps a target with unexamined AI involvement from being exempted.

### confidence

MEDIUM

### alternative_considered

```json
{
  "outcome": "PROPOSE_NO_RULE",
  "why": "No rule was considered because ai_enabled might be read as covering only AI features in the target and not AI assisted authoring of its content, which would exempt AI written code from attribution. It was rejected because the control name points directly at the ai_enabled field, but the reviewer should confirm that the field covers AI assisted authoring before this rule is accepted."
}
```

### shape_limitation

```json
{
  "note": "The control is scoped to the organisation and its evidence is organisational evidence, so an archived repository snapshot may not be the level at which attribution is operated. The ai_enabled field expresses AI involvement of the target but none of the four usable fields can express that the control is operated at organisation level.",
  "scope": "ORGANIZATION"
}
```

## EMS-CTRL-062

### catalog_inputs

```json
{
  "control_name": "Schema Version Control",
  "evidence_authority": "Application evidence",
  "scope": "APPLICATION",
  "scope_owner": "Software Development"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "Data and interface schemas of the application, and the migrations between their versions, are kept under version control."
}
```

### proposed_outcome

PROPOSE_NO_RULE

### proposed_rule

```json
null
```

### rationale

Schema version control keeps schema definitions and migrations under tracked revision, and whether it is relevant turns on whether the target defines any schema. None of production, internet_exposed, contains_customer_data or ai_enabled says whether a schema exists, and a schema can exist without customer data or production use. Proposing no rule claims that schema version control applies to every archived repository snapshot, because no usable field gives a sound exemption.

### confidence

MEDIUM

### alternative_considered

```json
{
  "outcome": "PROPOSE_RULE",
  "why": "A rule on contains_customer_data KNOWN_FALSE was rejected because schemas describe data structures of any kind and the control name does not point at customer data."
}
```

### shape_limitation

```json
{
  "note": "The control is scoped to an application, and the real reasons it might not apply are that the target is a repository snapshot and not an application, or that it defines no schema. None of the four usable fields can express control scope or the presence of a schema.",
  "scope": "APPLICATION"
}
```

## EMS-CTRL-075

### catalog_inputs

```json
{
  "control_name": "Continuous Compliance Scan",
  "evidence_authority": "EMS evidence",
  "scope": "EMS",
  "scope_owner": "EMS Governance"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "Targets registered in the EMS are scanned on a recurring basis to check that they still meet the controls that apply to them."
}
```

### proposed_outcome

PROPOSE_NO_RULE

### proposed_rule

```json
null
```

### rationale

A continuous compliance scan is the recurring check that registered targets still meet their controls, and it is operated by the EMS across targets. Exempting a target from the continuous compliance scan on production, internet_exposed, contains_customer_data or ai_enabled would remove the mechanism that detects drift in every other control, so none of the four fields gives a sound exemption. Proposing no rule claims that the continuous compliance scan applies to every archived repository snapshot.

### confidence

HIGH

### alternative_considered

```json
{
  "outcome": "PROPOSE_RULE",
  "why": "A rule on production KNOWN_FALSE was rejected because the control name does not point at production and a compliance scan is not limited to production targets."
}
```

### shape_limitation

```json
{
  "note": "The control is scoped to the EMS itself and its evidence is EMS evidence, so the real question is whether it is assessed per target at all or once for the EMS. None of the four usable fields can express that the control is operated at EMS level.",
  "scope": "EMS"
}
```

## EMS-CTRL-079

### catalog_inputs

```json
{
  "control_name": "Repository Health Review",
  "evidence_authority": "Repository evidence",
  "scope": "REPOSITORY",
  "scope_owner": "Software Development"
}
```

### interpretation

```json
{
  "label": "DRAFTER_ASSUMPTION_NOT_AN_EMS_SOURCE",
  "text": "The repository is reviewed periodically for upkeep matters such as ownership, stale content, documentation and whether it should still be retained."
}
```

### proposed_outcome

PROPOSE_NO_RULE

### proposed_rule

```json
null
```

### rationale

A repository health review is a periodic check on the upkeep and continued need for a repository, and an archived copy is a natural subject for the question of whether it is still owned and still needed. None of production, internet_exposed, contains_customer_data or ai_enabled describes whether a repository deserves periodic review, so none of them gives a sound exemption. Proposing no rule claims that the repository health review applies to every archived repository snapshot.

### confidence

HIGH

### alternative_considered

```json
{
  "outcome": "PROPOSE_RULE",
  "why": "A rule on production KNOWN_FALSE was rejected because the control name does not point at production and unreviewed non-production copies are exactly where neglected content accumulates."
}
```

### shape_limitation

```json
null
```
