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
| `ADJ-D001` | `CLM-003` | defer | official |
| `ADJ-D002` | `CLM-004` | defer | official |
| `ADJ-D003` | `CLM-002` | defer | official |
| `ADJ-D004` | `CLM-006` | defer | observed |
| `ADJ-D005` | `CLM-008` | defer | official |
| `ADJ-D006` | `CLM-010` | defer | official |
| `ADJ-D007` | `CLM-005` | defer | official |

Decisions record remaining research after maintainer-reviewed canonical reconciliation. Generated observations never change claims automatically.

### ADJ-D001 — CLM-003

GitHub's live Quickdraw fragment now states the five-minute contract. Further work is limited to issue equivalence and processing-delay edge cases.

### ADJ-D002 — CLM-004

GitHub's live YOLO fragment states 'Merged without a review'. Alternate review-state and merger-identity edge cases remain separate research.

### ADJ-D003 — CLM-002

GitHub's live Pull Shark x4 fragment publishes the complete merged-pull-request milestone table.

### ADJ-D004 — CLM-006

The x4 sighting lacks final-history co-author counts and merge-method controls.

### ADJ-D005 — CLM-008

GitHub's live Galaxy Brain x4 fragment publishes the complete accepted-answer milestone table.

### ADJ-D006 — CLM-010

GitHub's live Starstruck x4 fragment publishes the complete star milestone table; ownership-transfer persistence remains open.

### ADJ-D007 — CLM-005

GitHub's live Pair Extraordinaire fragment states the broad coauthored-commit trigger; numerical tiers and merge-rewrite edge cases remain open.

## Machine-readable data

See [`/api/adjudication.json`](../api/adjudication.json).
