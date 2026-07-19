---
layout: default
title: Mission execution intake
description: Structured intake, validation, privacy screening, and draft review packets for targeted evidence missions.
permalink: /mission-execution-intake/
---

## Mission execution intake

The mission intake converts a completed or blocked mission observation into a reviewable evidence packet. It does not unlock achievements, create qualifying activity, or promote claims automatically.

[Open the mission evidence form](https://github.com/Conroy1988/Achievements/issues/new?template=mission-evidence.yml)

## Submission matrix

| Mission | Status | Achievement | Claims | Contradiction | Required evidence fields |
|---|---|---|---|---|---:|
| `MSN-001` — Preserve real co-author attribution across merge methods | participant-needed | pair-extraordinaire | CLM-005, CLM-006 | CTR-004 | 8 |
| `MSN-004` — Find exact public observations around the Starstruck x4 boundary | complete | starstruck | CLM-009, CLM-010 | CTR-006 | 9 |
| `MSN-002` — Measure Pull Shark processing and attributed-count behaviour | scheduled | pull-shark | CLM-001, CLM-002 | CTR-003 | 6 |
| `MSN-006` — Separate YOLO review-state and merger-identity conditions | participant-needed | yolo | CLM-004 | CTR-002 | 9 |
| `MSN-005` — Link accepted-answer counts to visible Galaxy Brain tiers | complete | galaxy-brain | CLM-007, CLM-008 | CTR-005 | 8 |
| `MSN-003` — Bracket the Quickdraw timing boundary | complete | quickdraw | CLM-003 | CTR-001 | 9 |
| `MSN-007` — Maintain a passive cross-achievement processing-delay ledger | passive-observation | cross-achievement | none | none | 7 |

## Intake checks

1. The mission, task, claim, contradiction, and achievement relationships must match the published mission queue.
2. Every required evidence key for the selected mission must be supplied using `key: value` lines.
3. Scheduled missions are blocked until their published `no_action_before` timestamp.
4. Public HTTPS sources, timestamps, environment controls, limitations, and result state are validated.
5. Safeguard, privacy, and publication declarations are mandatory.
6. Automated screening blocks credentials, email addresses, secret-like values, payment-card-like numbers, and prohibited material.
7. Passing submissions create a draft packet and draft pull request for human review.

## Required evidence format

Copy each key from the selected mission and provide one value per line:

```text
public_pull_request_url: https://github.com/example/repository/pull/123
final_commit_url: https://github.com/example/repository/commit/abc123
merge_method: squash
```

Unknown keys, duplicated keys, empty values, and missing mission keys are rejected.

## Review boundary

Automated acceptance means only that the packet passed structural, relationship, timing, safeguard, and privacy checks. A maintainer must still inspect the public sources and decide whether the packet affects event evidence, a contradiction assessment, a threshold programme, or a canonical claim.

## Machine-readable contract

The submission schema is published at [`/api/mission-submission-schema.json`](../api/mission-submission-schema.json). The active mission requirements are published at [`/api/acquisition-missions.json`](../api/acquisition-missions.json).
