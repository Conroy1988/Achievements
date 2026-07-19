---
layout: default
title: Research intelligence system
description: Claim-level traceability, contradictions, coverage, priorities, and official-document change impact.
permalink: /research-intelligence/
---

## Research intelligence system

The research intelligence layer converts the encyclopedia's evidence into an explicit decision system. It does not manufacture certainty. It identifies exactly what is known, what is disputed, what should be researched next, and what must be reviewed when an official GitHub source changes.

## Phase 40 — Claim-level evidence registry

The [claim register](claim-register.md) decomposes the nine achievement guides into stable, atomic claims. Each claim links to evidence records, contributor research tasks, an evidence level, a lifecycle state, and a review date.

## Phase 41 — Contradiction and dispute ledger

The [contradiction ledger](contradiction-ledger.md) records competing interpretations without silently choosing one. Every entry includes severity, affected claims, mapped evidence, research tasks, and measurable resolution criteria.

## Phase 42 — Evidence-coverage matrix

The [coverage matrix](evidence-coverage.md) scores documentation strength at claim and achievement level. The score exposes weak evidence, open disputes, and claims that lack an assigned research task.

## Phase 43 — Research priority scoring

The [priority board](research-priorities.md) ranks open tasks from declared urgency, evidence weakness, contradiction severity, active-achievement scope, task state, and good-first-research value.

## Phase 44 — Official-document change-impact map

The [change-impact map](change-impact-map.md) connects each monitored GitHub documentation page to the claims, disputes, achievements, and research tasks that require review when its fingerprint changes.

## Machine-readable outputs

| Endpoint | Purpose |
|---|---|
| [`claims.json`](../api/claims.json) | Atomic canonical claims and evidence links |
| [`contradictions.json`](../api/contradictions.json) | Disputes, positions, and resolution criteria |
| [`coverage.json`](../api/coverage.json) | Coverage scoring and unassigned gaps |
| [`priorities.json`](../api/priorities.json) | Ranked research queue with exposed score components |
| [`change-impact.json`](../api/change-impact.json) | Official-document impact relationships and review actions |

## Validation

Run the complete intelligence contract locally with:

```bash
python scripts/build_research_intelligence.py --check
```

The dedicated GitHub Actions workflow runs on relevant pushes and pull requests, every Monday, and on manual dispatch.
