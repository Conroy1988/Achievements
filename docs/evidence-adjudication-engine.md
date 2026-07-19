---
layout: default
title: Evidence adjudication engine
description: Fail-closed rules and current decisions for evidence-level promotion.
permalink: /evidence-adjudication-engine/
---

## Evidence adjudication engine

The engine separates collection from promotion. Generated observations never modify canonical claim levels automatically.

## Promotion rules

### ADJ-R01 — community-reported-to-observed

- At least two independent public observations, or one public event linked by GitHub to its achievement detail.
- Material timestamps and attribution are retained.
- No unresolved contradiction directly defeats the promoted statement.

### ADJ-R02 — observed-to-confirmed

- Controlled reproduction on at least two independent accounts.
- Positive and relevant negative controls are documented.
- Two reviewers agree and disclose conflicts.
- Processing delay is measured rather than assumed.

### ADJ-R03 — any-to-official

- A maintained or preserved GitHub-owned source explicitly states the material contract.

### ADJ-R04 — attestation-limits

- Participant attestation alone cannot promote a claim.
- A badge sighting alone cannot prove an exact threshold or qualifying event.

### ADJ-R05 — negative-and-inconclusive-evidence

- Negative and inconclusive observations remain visible.
- They may narrow a claim but cannot be silently discarded or treated as proof of non-qualification.

## Current decisions

| Decision | Claim | Outcome | Proposed level |
|---|---|---|---|
| `ADJ-D001` | `CLM-003` | defer | confirmed |
| `ADJ-D002` | `CLM-004` | defer | confirmed |
| `ADJ-D003` | `CLM-002` | defer | observed |
| `ADJ-D004` | `CLM-006` | defer | observed |
| `ADJ-D005` | `CLM-008` | defer | observed |
| `ADJ-D006` | `CLM-010` | defer | observed |
| `ADJ-D007` | `CLM-005` | defer | confirmed |

Every current decision is deferred. No canonical claim level or evidence score changes in this programme.

### ADJ-D001 — CLM-003

Two independent public reconstructions support the broad rapid-close association at observed level; controlled boundary reproduction and measured award timing are still required for confirmed status.

### ADJ-D002 — CLM-004

Two independent authored and unreviewed merged pull requests support the broad YOLO association at observed level; merger identity and alternate review-state controls remain unresolved.

### ADJ-D003 — CLM-002

Visible x3 and x4 tiers lack exact attributed qualifying counts.

### ADJ-D004 — CLM-006

The x4 sighting lacks final-history co-author counts and merge-method controls.

### ADJ-D005 — CLM-008

The x2 and x4 sightings lack exact accepted-answer totals.

### ADJ-D006 — CLM-010

The x3-to-x4 bracket is informative, but rounded star displays and ownership edge cases prevent exact threshold confirmation.

### ADJ-D007 — CLM-005

Two independent account-linked co-author reconstructions support the broad merged-pull-request association at observed level; controlled merge-method and rewrite tests remain required for confirmed status.

## Machine-readable data

See [`/api/adjudication.json`](../api/adjudication.json).
