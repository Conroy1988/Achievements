---
layout: default
title: Contradiction and dispute ledger
description: Open evidence conflicts, behavioural ambiguities, and explicit resolution criteria.
permalink: /contradictions/
---

## Contradiction and dispute ledger

This ledger prevents unresolved interpretations from being silently flattened into certainty.

| Record | Type | Severity | Status | Claims | Research |
|---|---|---|---|---|---|
| `CTR-001` | threshold-dispute | critical | open | `CLM-003` | `RSH-001` |
| `CTR-002` | behavioural-ambiguity | critical | open | `CLM-004` | `RSH-002` |
| `CTR-003` | threshold-dispute | high | open | `CLM-002` | `RSH-003` |
| `CTR-004` | attribution-ambiguity | medium | open | `CLM-005`, `CLM-006` | — |
| `CTR-005` | threshold-dispute | high | open | `CLM-008` | `RSH-004` |
| `CTR-006` | ownership-ambiguity | high | open | `CLM-009`, `CLM-010` | `RSH-005` |

## Resolution criteria

### CTR-001 — Quickdraw qualifying-window uncertainty

- Community references frequently report a very short qualifying window.
- GitHub publishes no exact threshold and independent timing evidence remains incomplete.

**Resolution:** Independent, dated reproduction across at least two accounts with creation, closure, and award timestamps.

### CTR-002 — YOLO review-state interpretation

- The relevant condition is absence of an approving review.
- Any formal review object, including comments or requested changes, may alter qualification.

**Resolution:** Controlled tests covering no review, comment-only, changes-requested, and approved review states.

### CTR-003 — Pull Shark tier thresholds

- The 2, 16, 128, and 1024 sequence is consistently community-reported.
- GitHub does not publish the complete tier contract and attribution edge cases can change observed counts.

**Resolution:** Independently attributed observations at each boundary with processing-delay controls.

### CTR-004 — Pair Extraordinaire attribution after merge rewriting

- A valid Co-authored-by trailer should preserve attribution.
- Squash merges, rewritten commits, and email matching can prevent the final merged history from retaining qualifying attribution.

**Resolution:** Controlled merge-method tests that inspect final commit attribution and subsequent award visibility.

### CTR-005 — Galaxy Brain tier thresholds

- The 2, 8, 16, and 32 sequence is consistently community-reported.
- GitHub does not publish the complete tier table and accepted-answer state can be confused with other moderation labels.

**Resolution:** Dated accepted-answer counts observed immediately around each award boundary on independent accounts.

### CTR-006 — Starstruck ownership and transfer attribution

- Stars on a repository owned by the account contribute to the achievement.
- Organization ownership, repository transfer, forks, archival, and falling star counts may change attribution or persistence.

**Resolution:** Documented public edge cases covering ownership state before and after award or transfer.

Machine-readable records are published at [`/api/contradictions.json`](../api/contradictions.json).
