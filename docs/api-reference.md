---
layout: default
title: Public data API
description: Static JSON endpoints for achievements, evidence, research missions, intake, review and promotion contracts, analytics, adjudication, campaign lifecycle, release history, schema, and repository health.
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
| [`research-queue.json`](../api/research-queue.json) | Bounded contributor research tasks |
| [`claims.json`](../api/claims.json) | Atomic claims with evidence and task relationships |
| [`contradictions.json`](../api/contradictions.json) | Competing interpretations and resolution criteria |
| [`coverage.json`](../api/coverage.json) | Claim and achievement coverage scores and ownership gaps |
| [`priorities.json`](../api/priorities.json) | Deterministically ranked research tasks with score components |
| [`change-impact.json`](../api/change-impact.json) | Official-document changes mapped to claims, disputes, and tasks |
| [`public-observations.json`](../api/public-observations.json) | Dated GitHub-owned profile, tier, and repository observations with explicit limitations |
| [`public-reconstructions.json`](../api/public-reconstructions.json) | Exact public event/profile pairs used to support broad trigger associations without overstating causality |
| [`official-achievement-fragments.json`](../api/official-achievement-fragments.json) | GitHub-owned live achievement criteria, linked history, fingerprints, and tier milestones |

## Evidence-operations endpoints

| Endpoint | Purpose |
|---|---|
| [`lab-protocols.json`](../api/lab-protocols.json) | Ethical, privacy-safe reproduction protocols |
| [`auditor-rules.json`](../api/auditor-rules.json) | Read-only public-signal rules and explicit limitations |
| [`submission-schema.json`](../api/submission-schema.json) | Structured general evidence-observation contract |
| [`mission-submission-schema.json`](../api/mission-submission-schema.json) | Closed mission-packet contract with relationship, safeguard, and timing requirements |
| [`mission-review-queue.json`](../api/mission-review-queue.json) | Human-review queue and packet disposition state |
| [`mission-review-schema.json`](../api/mission-review-schema.json) | Closed review-record contract with conflict and promotion controls |
| [`promotion-plans.json`](../api/promotion-plans.json) | Fail-closed canonical change plans generated from accepted promotion proposals |
| [`promotion-plan-schema.json`](../api/promotion-plan-schema.json) | Closed promotion-plan contract with impact, validation, approval, and rollback requirements |
| [`command-centre.json`](../api/command-centre.json) | Static research metrics, targets, and public routes |

## Evidence-quality programme endpoints

| Endpoint | Purpose |
|---|---|
| [`event-linked-evidence.json`](../api/event-linked-evidence.json) | Public GitHub events linked to claims, including negative and inconclusive observations |
| [`evidence-intelligence.json`](../api/evidence-intelligence.json) | Deterministic per-achievement pressure scores and remaining release-gate gaps |
| [`acquisition-missions.json`](../api/acquisition-missions.json) | Ranked, ethical evidence missions with controls, stop conditions, and promotion targets |
| [`threshold-boundaries.json`](../api/threshold-boundaries.json) | Proposed boundaries, current brackets, blockers, and required next evidence |
| [`adjudication.json`](../api/adjudication.json) | Fail-closed promotion rules and current human-review decisions |
| [`contradiction-assessments.json`](../api/contradiction-assessments.json) | One current resolution assessment for every open contradiction |
| [`release-readiness.json`](../api/release-readiness.json) | Immutable published v1.4.0 evidence and operational baseline |
| [`campaign-status.json`](../api/campaign-status.json) | Live v1.5.0 campaign lifecycle, task buckets, mission priority, gate distance, and archived release history |

The discovery index now exposes **41 public JSON files**: the aggregate catalogue, nine individual achievement records, schema, discovery, status, and twenty-five auxiliary endpoints.

## Response obligations

Consumers must preserve uncertainty. Evidence level, reproduction state, reviewer decision, task state, dispute status, coverage score, observation scope, privacy status, and limitations are separate fields and must not be flattened into one confidence label.

Public observations establish only the platform state visible at the cited URL and date. They do not automatically prove causality, an exact threshold, a qualifying event, or an immutable historical count.

Event-linked records retain participant reports, negative results, processing-delay uncertainty, and public-event limitations. They do not modify canonical claim levels automatically.

Evidence-intelligence pressure scores prioritise unresolved work. They are not confidence scores and do not predict whether a community-reported claim is true.

Acquisition missions are bounded research instructions. They prohibit artificial activity, spam, false attribution, repository manipulation, and automatic claim promotion.

Mission intake packets must preserve the published mission, task, claim, contradiction, evidence-key, timing, safeguard, privacy, and human-review boundaries. Automated acceptance is not an evidence promotion.

Mission review records classify packets only. Promotion proposals require the mission's published target, the applicable adjudication rule, two reviewers, one unconflicted reviewer, and a fully passing checklist. The queue always reports zero automatic canonical mutations.

Promotion plans are impact previews, not patches. They must preserve the source review, identify every affected source and generated file, require a separate maintainer-reviewed pull request, and report zero automatic applications.

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
python scripts/build_public_reconstructions.py
python scripts/build_official_achievement_fragments.py
python scripts/build_evidence_quality_programme.py
python scripts/build_research_campaign.py
python scripts/build_evidence_intelligence.py
python scripts/build_acquisition_missions.py
python scripts/build_mission_intake.py
python scripts/build_mission_review_queue.py
python scripts/build_promotion_plans.py
```

Generated endpoints must not be edited independently. Update the canonical source, run its builder, then commit the source and output together.

## Versioning

- The core catalogue envelope remains `1.1.0`.
- Research, observation, mission, intake, review, planning, adjudication, analytics, and evidence-operations endpoints carry independent schema and API versions.
- A breaking envelope change increments the relevant major version.
- Release tags describe encyclopedia releases rather than GitHub's achievement system.

## Release baselines

- [`v1.1.0`](releases/v1.1.0.md) introduced the initial achievement and health API.
- [`v1.2.0`](releases/v1.2.0.md) introduced evidence, timeline, and contributor-research discovery.
- [`v1.3.0`](releases/v1.3.0.md) introduced research intelligence, reproduction protocols, automated triage, the profile auditor, and the command centre.
- [`v1.4.0`](releases/v1.4.0.md) introduces GitHub-owned achievement contracts, public reconstructions, controlled evidence missions, review and promotion planning, and release-ready evidence governance.

The immutable `v1.3.0` source baseline is commit `4869e71b392fc8a8f6d20835cdabe123c0c95e6f`. The tag resolves exactly to that commit.

The immutable `v1.4.0` source baseline is commit `98d478c7b73cff9c6e8fa5235640f12597544b67`. The tag resolves exactly to that commit after `release-readiness.json` reported `ready` and merged-main operational health was verified at 100/100.

## Related material

- [Mission evidence promotion planner](promotion-planner.md)
- [Mission packet review queue](mission-review-queue.md)
- [Mission execution intake](mission-execution-intake.md)
- [Targeted evidence acquisition missions](targeted-evidence-missions.md)
- [Evidence intelligence dashboard](evidence-intelligence-dashboard.md)
- [Event-linked evidence](event-linked-evidence.md)
- [Threshold boundary programme](threshold-boundary-programme.md)
- [Evidence adjudication engine](evidence-adjudication-engine.md)
- [Contradiction resolution programme](contradiction-resolution-programme.md)
- [Research campaign status](research-campaign-status.md)
- [Published v1.4.0 release baseline](evidence-quality-release-gate.md)
- [Public observation corpus](public-observation-corpus.md)
- [Public reconstruction corpus](public-reconstruction-corpus.md)
- [Official achievement fragments](official-achievement-fragments.md)
- [Evidence road to 100](evidence-road-to-100.md)
- [Research command centre](../research-command-centre.md)
- [GitHub achievement profile auditor](../profile-auditor.md)
- [Achievement reproduction laboratory](reproduction-lab.md)
- [Submit achievement evidence](../evidence-submission.md)
- [Research intelligence system](research-intelligence.md)
- [Repository health dashboard](health-dashboard.md)
- [Unified repository audit](repository-audit.md)
