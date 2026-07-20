---
layout: default
title: Event-linked evidence
description: Public GitHub events linked to achievement claims without overstating causality.
permalink: /event-linked-evidence/
---

## Event-linked evidence collector

This register links public GitHub events to achievement claims. A link is not automatically causal: participant reports, processing delay, hidden attribution, and missing controls remain explicit.

**Events:** 16  
**Candidate observations:** 2  
**Negative or inconclusive:** 3

| Event | Achievement | Public object | Result | Elapsed |
|---|---|---|---|---:|
| `EVT-2026-001` | quickdraw | [issue-closure](https://github.com/Conroy1988/Achievements/issues/1) | candidate-observed | 4 seconds |
| `EVT-2026-002` | yolo | [pull-request-merge](https://github.com/Conroy1988/Achievements/pull/2) | candidate-observed | 14 seconds |
| `EVT-2026-003` | pull-shark | [pull-request-merge](https://github.com/Conroy1988/Achievements/pull/231) | negative-inconclusive | 119 seconds |
| `EVT-2026-004` | pull-shark | [pull-request-merge](https://github.com/Team-Killing-Bastards/TKB-Discord-Bot/pull/12) | negative-inconclusive | 68 seconds |
| `EVT-2026-005` | pull-shark | [pull-request-merge](https://github.com/Conroy1988/uk-fire-command/pull/37) | negative-inconclusive | 444 seconds |
| `EVT-2026-006` | quickdraw | [pull-request-close-and-merge](https://github.com/Schweinepriester/Fira/pull/1) | accepted | 5 seconds |
| `EVT-2026-007` | quickdraw | [pull-request-close-and-merge](https://github.com/tronicapp/tronic-track/pull/1) | accepted | 9 seconds |
| `EVT-2026-008` | yolo | [pull-request-merge-without-formal-review](https://github.com/Schweinepriester/Fira/pull/1) | accepted | 5 seconds |
| `EVT-2026-009` | yolo | [pull-request-merge-without-formal-review](https://github.com/tronicapp/tronic-track/pull/1) | accepted | 9 seconds |
| `EVT-2026-010` | pair-extraordinaire | [coauthored-commit-in-merged-pull-request](https://github.com/devflash101/POC/pull/11) | accepted | 21 seconds |
| `EVT-2026-011` | pair-extraordinaire | [coauthored-final-merge-commit](https://github.com/Fyrd/caniuse/pull/7466) | accepted | 533698 seconds |
| `EVT-2026-012` | yolo | [merge-with-review-request-but-no-submitted-review](https://github.com/Schweinepriester/achievement-testarea/pull/4) | accepted | 2 seconds |
| `EVT-2026-013` | pair-extraordinaire | [squash-merge-preserving-coauthor-attribution](https://github.com/Fyrd/caniuse/pull/6271) | accepted | 917153 seconds |
| `EVT-2026-014` | pair-extraordinaire | [squash-merge-preserving-coauthor-attribution](https://github.com/Fyrd/caniuse/pull/7306) | accepted | 187715 seconds |
| `EVT-2026-015` | starstruck | [creator-attribution-on-organization-owned-repository](https://github.com/users/balloob/achievements/starstruck/detail?hovercard=1) | accepted | 0 seconds |
| `EVT-2026-016` | starstruck | [creator-attribution-on-organization-owned-repository](https://github.com/users/tiangolo/achievements/starstruck/detail?hovercard=1) | accepted | 0 seconds |

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

### EVT-2026-006 — quickdraw

**Claims:** `CLM-003`  
**Account:** `Schweinepriester`  
**Award link:** `public-profile-visible-no-contributing-fragment`  
**Adjudication:** `accepted`

**Public facts**

- The pull request was authored by Schweinepriester and merged into master five seconds after creation.
- The pull request has no submitted formal reviews and the account publicly displays Quickdraw.

**Limitations**

- The anonymous achievement fragment does not expose the contributing event.
- The event does not establish the maximum qualifying interval.

### EVT-2026-007 — quickdraw

**Claims:** `CLM-003`  
**Account:** `kmcclosk`  
**Award link:** `public-profile-visible-no-contributing-fragment`  
**Adjudication:** `accepted`

**Public facts**

- The pull request was authored by kmcclosk and merged into main nine seconds after creation.
- The pull request has no submitted formal reviews and the account publicly displays Quickdraw.

**Limitations**

- The anonymous achievement fragment does not expose the contributing event.
- The event does not establish issue equivalence or the maximum interval.

### EVT-2026-008 — yolo

**Claims:** `CLM-004`  
**Account:** `Schweinepriester`  
**Award link:** `public-profile-visible-no-contributing-fragment`  
**Adjudication:** `accepted`

**Public facts**

- The account authored the merged pull request and no formal review was submitted.
- The account publicly displays YOLO.

**Limitations**

- The normalized pull-request record does not expose the merging actor.
- Comment-only, changes-requested, dismissed, and approved states are not tested.

### EVT-2026-009 — yolo

**Claims:** `CLM-004`  
**Account:** `kmcclosk`  
**Award link:** `public-profile-visible-no-contributing-fragment`  
**Adjudication:** `accepted`

**Public facts**

- The account authored the merged pull request and no formal review was submitted.
- The account publicly displays YOLO.

**Limitations**

- The normalized pull-request record does not expose the merging actor.
- Alternate formal review states are not tested.

### EVT-2026-010 — pair-extraordinaire

**Claims:** `CLM-005`  
**Account:** `Rongronggg9`  
**Award link:** `public-profile-visible-no-contributing-fragment`  
**Adjudication:** `accepted`

**Public facts**

- The pull request merged into main and retained an account-linked Rongronggg9 co-author trailer in its one-commit history.
- Rongronggg9 publicly displays Pair Extraordinaire x4.

**Limitations**

- The exact attributed qualifying count is not public.
- The merge-commit example does not establish squash or rebase behaviour.

### EVT-2026-011 — pair-extraordinaire

**Claims:** `CLM-005`  
**Account:** `Schweinepriester`  
**Award link:** `public-profile-visible-no-contributing-fragment`  
**Adjudication:** `accepted`

**Public facts**

- The pull request merged into main and the final merge commit contains an account-linked Schweinepriester co-author trailer.
- Schweinepriester publicly displays Pair Extraordinaire x3.

**Limitations**

- The exact attributed qualifying count is not public.
- The example does not resolve every squash, rebase, email-matching, or history-rewrite case.

### EVT-2026-012 — yolo

**Claims:** `CLM-004`  
**Account:** `Schweinepriester`  
**Award link:** `github-owned-achievement-fragment-linked-event`  
**Adjudication:** `accepted`

**Public facts**

- The pull request had a requested reviewer at merge time, but the public reviews endpoint contains no submitted review objects.
- GitHub's achievement-detail fragment links this pull request and states that it was merged without a review.

**Limitations**

- This establishes that requesting a reviewer is not itself a submitted review for this observed award.
- It does not establish how submitted COMMENT, REQUEST_CHANGES, APPROVE, or dismissed reviews affect qualification.

### EVT-2026-013 — pair-extraordinaire

**Claims:** `CLM-005`  
**Account:** `Schweinepriester`  
**Award link:** `github-owned-achievement-fragment-linked-event`  
**Adjudication:** `accepted`

**Public facts**

- The two-commit pull request was squash-merged and its final default-branch commit retained an account-linked Schweinepriester Co-authored-by trailer.
- GitHub's Pair Extraordinaire x3 achievement-detail fragment links this pull request in its contributing history.

**Limitations**

- The fragment does not expose how many qualifying pull requests GitHub attributed to the account.
- One successful squash configuration does not prove that every squash setting preserves attribution.

### EVT-2026-014 — pair-extraordinaire

**Claims:** `CLM-005`  
**Account:** `Schweinepriester`  
**Award link:** `github-owned-achievement-fragment-linked-event`  
**Adjudication:** `accepted`

**Public facts**

- The two-commit pull request was squash-merged and its final default-branch commit retained an account-linked Schweinepriester Co-authored-by trailer.
- GitHub's Pair Extraordinaire x3 achievement-detail fragment independently links this pull request in its contributing history.

**Limitations**

- The fragment does not expose the internal attributed count or the exact tier boundary crossed by this event.
- Rebase, stripped-trailer, mismatched-email, and later history-rewrite cases remain outside this observation.

### EVT-2026-015 — starstruck

**Claims:** `CLM-009`, `CLM-010`  
**Account:** `balloob`  
**Award link:** `github-owned-achievement-fragment`  
**Adjudication:** `accepted`

**Public facts**

- GitHub's Starstruck x4 fragment credits balloob and links home-assistant/core for published star milestones.
- The linked repository is currently owned by the home-assistant organization rather than the credited personal account.

**Limitations**

- The fragment does not publish the repository transfer date or prove whether transfer occurred before or after each milestone.
- Fork, archive, deletion, restoration, falling-count, and award-removal behavior remain unresolved.

### EVT-2026-016 — starstruck

**Claims:** `CLM-009`, `CLM-010`  
**Account:** `tiangolo`  
**Award link:** `github-owned-achievement-fragment`  
**Adjudication:** `accepted`

**Public facts**

- GitHub's Starstruck x4 fragment credits tiangolo and links fastapi/fastapi for the published 4096-star milestone.
- The linked repository is currently owned by the fastapi organization rather than the credited personal account.

**Limitations**

- The fragment does not expose the ownership state at the exact moment the milestone or award was processed.
- It does not resolve forks, archival, falling star counts, deletion, restoration, or revocation behavior.

## Machine-readable data

See [`/api/event-linked-evidence.json`](../api/event-linked-evidence.json).
