---
layout: default
title: Mission packet review queue
description: Human review and adjudication queue for privacy-screened mission evidence packets.
permalink: /mission-review-queue/
---

## Mission packet review queue

This queue begins after automated mission intake. A packet appears here only after structural, relationship, timing, safeguard, and privacy screening has passed.

**Packets:** 0  
**Pending review:** 0  
**Promotion proposals:** 0  
**Automatic canonical mutations:** 0

## Review dispositions

| Disposition | Queue result | Promotion proposal |
|---|---|---|
| `accept-evidence` | `accepted` | allowed |
| `defer` | `deferred` | not allowed |
| `retain-inconclusive` | `retained-inconclusive` | not allowed |
| `request-correction` | `needs-correction` | not allowed |
| `reject` | `rejected` | not allowed |

## Current queue

No mission packet has passed intake yet. The empty queue is the correct launch state.

## Promotion controls

- Promotion proposals require the mission to publish that exact claim and target level.
- The applicable adjudication rule must be named explicitly.
- At least two reviewers and one unconflicted reviewer are required.
- Every checklist item must pass.
- A proposal cannot edit canonical claims, contradictions, thresholds, missions, or releases automatically.

## Machine-readable contracts

- [Review queue](../api/mission-review-queue.json)
- [Review record schema](../api/mission-review-schema.json)
- [Review policy](../data/mission-review-policy.json)
