---
layout: default
title: Public data API
description: Static JSON endpoints for achievements, evidence, research operations, profile auditing, public observations, schema, and repository health.
permalink: /api/
---

## Public data API

The encyclopedia publishes a read-only static JSON API through GitHub Pages.

Base path:

```text
https://conroy1988.github.io/Achievements/api/
```

## Core discovery endpoints

| Endpoint | Purpose |
|---|---|
| [`index.json`](../api/index.json) | Core API version, endpoint discovery, and achievement slugs |
| [`achievements.json`](../api/achievements.json) | Complete nine-record achievement catalogue |
| `achievements/{slug}.json` | One achievement record |
| [`schema.json`](../api/schema.json) | JSON Schema draft 2020-12 achievement contract |
| [`status.json`](../api/status.json) | Generated repository health and workflow state |

## Evidence and research endpoints

| Endpoint | Purpose |
|---|---|
| [`evidence.json`](../api/evidence.json) | Privacy-safe evidence records and review state |
| [`timelines.json`](../api/timelines.json) | Verification timelines and page-level review dates |
| [`research-queue.json`](../api/research-queue.json) | Twelve bounded contributor research tasks |
| [`claims.json`](../api/claims.json) | Atomic claims with evidence and task relationships |
| [`contradictions.json`](../api/contradictions.json) | Competing interpretations and resolution criteria |
| [`coverage.json`](../api/coverage.json) | Claim and achievement coverage scores and ownership gaps |
| [`priorities.json`](../api/priorities.json) | Deterministically ranked research tasks with score components |
| [`change-impact.json`](../api/change-impact.json) | Official-document changes mapped to claims, disputes, and tasks |
| [`public-observations.json`](../api/public-observations.json) | Dated GitHub-owned profile, tier, and repository observations with explicit limitations |

## Evidence-operations endpoints

| Endpoint | Purpose |
|---|---|
| [`lab-protocols.json`](../api/lab-protocols.json) | Ethical, privacy-safe reproduction protocols |
| [`auditor-rules.json`](../api/auditor-rules.json) | Read-only public-signal rules and explicit limitations |
| [`submission-schema.json`](../api/submission-schema.json) | Structured evidence-observation contract |
| [`command-centre.json`](../api/command-centre.json) | Static research metrics, targets, and public routes |

The discovery index now exposes **26 public JSON files**: the aggregate catalogue, nine individual achievement records, schema, discovery, status, and thirteen auxiliary endpoints.

## Response obligations

Consumers must preserve uncertainty. Evidence level, reproduction state, reviewer decision, task state, dispute status, coverage score, observation scope, privacy status, and limitations are separate fields and must not be flattened into one confidence label.

Public observations establish only the platform state visible at the cited URL and date. They do not automatically prove causality, an exact threshold, a qualifying event, or an immutable historical count.

The profile-auditor rules are expressly non-authoritative. They describe public signals, not badge detection.

## Generation and drift control

```bash
python scripts/build_public_api.py
python scripts/build_evidence_register.py
python scripts/build_verification_timelines.py
python scripts/build_research_hub.py
python scripts/build_research_intelligence.py
python scripts/build_evidence_operations.py
python scripts/build_public_observations.py
```

Generated endpoints must not be edited independently. Update the canonical source, run its builder, then commit the source and output together.

## Versioning

- The core catalogue envelope remains `1.1.0`.
- Research, observation, and evidence-operations endpoints carry independent schema and API versions.
- A breaking envelope change increments the relevant major version.
- Release tags describe encyclopedia releases rather than GitHub's achievement system.

## Release baselines

- [`v1.1.0`](releases/v1.1.0.md) introduced the initial achievement and health API.
- [`v1.2.0`](releases/v1.2.0.md) introduced evidence, timeline, and contributor-research discovery.
- [`v1.3.0`](releases/v1.3.0.md) introduced research intelligence, reproduction protocols, automated triage, the profile auditor, and the command centre.

The immutable `v1.3.0` source baseline is commit `4869e71b392fc8a8f6d20835cdabe123c0c95e6f`. The tag resolves exactly to that commit.

## Related material

- [Public observation corpus](public-observation-corpus.md)
- [Evidence road to 100](evidence-road-to-100.md)
- [Research command centre](../research-command-centre.md)
- [GitHub achievement profile auditor](../profile-auditor.md)
- [Achievement reproduction laboratory](reproduction-lab.md)
- [Submit achievement evidence](../evidence-submission.md)
- [Research intelligence system](research-intelligence.md)
- [Repository health dashboard](health-dashboard.md)
- [Unified repository audit](repository-audit.md)
