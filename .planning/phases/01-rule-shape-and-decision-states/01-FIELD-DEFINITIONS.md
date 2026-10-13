# Rule-Condition Field Definitions (D-10)

Status: APPROVED

Definitions state what KNOWN_TRUE asserts about an archived repository snapshot target. Drafted from EMS sources only.

## production
Definition: KNOWN_TRUE asserts that the target is used as, or supports, a production system, so production-data, recovery and release controls are in play.
Source: registry/wave2d/applicability_rules.json
Source: config/repository_overrides.example.yaml
KNOWN_FALSE asserts the negation; UNKNOWN asserts nothing and never yields not-applicable.

## internet_exposed
Definition: KNOWN_TRUE asserts that the target, or a service it provides, is reachable from the public internet.
Source: config/repository_overrides.example.yaml
Source: registry/wave2d/applicability_rules.json
KNOWN_FALSE asserts the negation; UNKNOWN asserts nothing and never yields not-applicable.

## contains_customer_data
Definition: KNOWN_TRUE asserts that the target holds or processes customer data.
Source: config/repository_overrides.example.yaml
Source: registry/wave2d/applicability_rules.json
KNOWN_FALSE asserts the negation; UNKNOWN asserts nothing and never yields not-applicable.

## ai_enabled
Definition: KNOWN_TRUE asserts that the target includes or uses AI capabilities, so AI-specific controls apply to it.
Source: registry/wave2d/applicability_rules.json
Source: config/repository_overrides.example.yaml
KNOWN_FALSE asserts the negation; UNKNOWN asserts nothing and never yields not-applicable.

## Other classification fields
Note: owner, tier, service_criticality and data_classification are declared classification fields not usable in rules in this version.

## Approval
Approver: Oscar Mack
Role: EMS governance authority
Date: 2026-10-13
Approved per D-10 before publisher code carries this wording.
