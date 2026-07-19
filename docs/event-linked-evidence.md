---
layout: default
title: Event-linked evidence
description: Public GitHub events linked to achievement claims without overstating causality.
permalink: /event-linked-evidence/
---

## Event-linked evidence collector

This register links public GitHub events to achievement claims. A link is not automatically causal: participant reports, processing delay, hidden attribution, and missing controls remain explicit.

**Events:** 5  
**Candidate observations:** 2  
**Negative or inconclusive:** 3

| Event | Achievement | Public object | Result | Elapsed |
|---|---|---|---|---:|
| `EVT-2026-001` | quickdraw | [issue-closure](https://github.com/Conroy1988/Achievements/issues/1) | candidate-observed | 4 seconds |
| `EVT-2026-002` | yolo | [pull-request-merge](https://github.com/Conroy1988/Achievements/pull/2) | candidate-observed | 14 seconds |
| `EVT-2026-003` | pull-shark | [pull-request-merge](https://github.com/Conroy1988/Achievements/pull/231) | negative-inconclusive | 119 seconds |
| `EVT-2026-004` | pull-shark | [pull-request-merge](https://github.com/Team-Killing-Bastards/TKB-Discord-Bot/pull/12) | negative-inconclusive | 68 seconds |
| `EVT-2026-005` | pull-shark | [pull-request-merge](https://github.com/Conroy1988/uk-fire-command/pull/37) | negative-inconclusive | 444 seconds |

## Event records

### EVT-2026-001 — quickdraw

**Claims:** `CLM-003`  
**Account:** `Conroy1988`  
**Award link:** `participant-reported-visible`  
**Adjudication:** `candidate-observed`

**Public facts**

- The issue was opened and closed by the same public account.
- The public timestamps show a four-second creation-to-closure interval.

**Limitations**

- The participant report is not an independently captured public achievement-detail record.
- A four-second result does not establish the maximum qualifying time window.

### EVT-2026-002 — yolo

**Claims:** `CLM-004`  
**Account:** `Conroy1988`  
**Award link:** `participant-reported-visible-within-ten-minutes`  
**Adjudication:** `candidate-observed`

**Public facts**

- The pull request was authored by Conroy1988 and merged into main.
- The public discussion timeline contains no issue comments, inline review comments, or review submissions.

**Limitations**

- The public connector output does not identify the merging actor.
- One no-review event does not resolve comment-only, changes-requested, or approved-review controls.

### EVT-2026-003 — pull-shark

**Claims:** `CLM-001`, `CLM-002`  
**Account:** `Conroy1988`  
**Award link:** `participant-reported-not-visible-as-of-2026-07-19`  
**Adjudication:** `negative-inconclusive`

**Public facts**

- The pull request was authored by Conroy1988 and merged into main.
- The change added ten files and more than one thousand lines of substantive evidence infrastructure.

**Limitations**

- Absence from the visible profile may reflect processing delay rather than non-qualification.
- The event does not expose GitHub's internal attributed Pull Shark count.

### EVT-2026-004 — pull-shark

**Claims:** `CLM-001`, `CLM-002`  
**Account:** `Conroy1988`  
**Award link:** `participant-reported-not-visible-as-of-2026-07-19`  
**Adjudication:** `negative-inconclusive`

**Public facts**

- The pull request was authored by Conroy1988 and merged into the organisation repository's main branch.
- The pull request delivered a substantive HTTPS reverse-proxy security upgrade.

**Limitations**

- The observation does not prove how organisation-owned repositories are counted internally.
- The profile state was reported before a full processing-delay window elapsed.

### EVT-2026-005 — pull-shark

**Claims:** `CLM-001`, `CLM-002`  
**Account:** `Conroy1988`  
**Award link:** `participant-reported-not-visible-as-of-2026-07-19`  
**Adjudication:** `negative-inconclusive`

**Public facts**

- The pull request was authored by Conroy1988 and merged into main.
- The change fixed development LAN access and stale PWA caching.

**Limitations**

- One public merge cannot establish a cumulative tier boundary.
- The profile state was reported before the scheduled 72-hour follow-up.

## Machine-readable data

See [`/api/event-linked-evidence.json`](../api/event-linked-evidence.json).
