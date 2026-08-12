# Engineering Management System (EMS)

EMS is the controlled engineering governance and evidence system used to define, evaluate, and improve engineering standards.

This repository contains the authoritative EMS source, including:

- engineering controls and registries;
- evidence collectors and evaluators;
- policy applicability logic;
- adjudication and remediation automation;
- schemas, templates, tests, and documentation;
- controlled release manifests.

## Current baseline

Initial GitHub baseline:

`ems-v0.4.5-wave1`

This tag corresponds to the EMS Pass 4.5 Wave 1 Evidence Expansion baseline.

## Governance

EMS governs itself.

Changes to controls, policy decisions, applicability logic, schemas, collectors, or release governance should be treated as control-plane changes and receive heightened review.

## Generated evidence

Transient generated outputs and raw collected evidence are intentionally excluded from source control unless specifically promoted into a controlled release artifact.
