---
layout: default
title: Public evidence register
description: Privacy-safe, reviewable evidence records supporting the encyclopedia's achievement claims.
permalink: /evidence-register/
---

## Public evidence register

This register links each canonical achievement to a dated, privacy-safe evidence record. It exposes uncertainty and limitations instead of converting community reports into official claims.

**Schema version:** `1.0.0`  
**Records:** 9  
**Privacy policy:** [Evidence register policy](evidence-register-policy.md)

| Record | Achievement | Evidence | Reproduction | Decision | Observed |
|---|---|---|---|---|---|
| `EVD-2026-001` | [Pull Shark](../docs/achievements/pull-shark.md) | confirmed | reproduced | accepted-with-limitations | 2026-07-19 |
| `EVD-2026-002` | [Quickdraw](../docs/quickdraw.md) | observed | two-independent-public-reconstructions | accepted-with-limitations | 2026-07-19 |
| `EVD-2026-003` | [YOLO](../docs/achievements/yolo.md) | observed | two-independent-public-reconstructions | accepted-with-limitations | 2026-07-19 |
| `EVD-2026-004` | [Pair Extraordinaire](../achievements/pair-extraordinaire.md) | observed | two-independent-public-reconstructions | accepted-with-limitations | 2026-07-19 |
| `EVD-2026-005` | [Galaxy Brain](../docs/achievements/galaxy-brain.md) | official | official-trigger-description | accepted-with-limitations | 2026-07-19 |
| `EVD-2026-006` | [Starstruck](../docs/achievements/starstruck.md) | observed | observed-not-fully-reproduced | accepted-with-limitations | 2026-07-19 |
| `EVD-2026-007` | [Public Sponsor](../docs/achievements/public-sponsor.md) | official | officially-documented-trigger | accepted-with-limitations | 2026-07-19 |
| `EVD-2026-008` | [Arctic Code Vault Contributor](../docs/arctic-code-vault-contributor.md) | official | historical-official-documentation | accepted | 2026-07-19 |
| `EVD-2026-009` | [Mars 2020 Contributor](../docs/mars-2020-contributor.md) | official | historical-official-documentation | accepted | 2026-07-19 |

## Record details

### EVD-2026-001 — Pull Shark

**Claim:** A substantive pull request attributable to the account is merged.

**Guide location:** `docs/achievements/pull-shark.md` — Trigger and attribution

**Privacy:** `public-no-personal-data`  
**Sources:** 0 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

The trigger is confirmed; the complete tier table remains community-reported.

### EVD-2026-002 — Quickdraw

**Claim:** Closing an issue or pull request very shortly after creation can award Quickdraw.

**Guide location:** `docs/quickdraw.md` — Qualifying time window

**Privacy:** `public-no-personal-data`  
**Sources:** 4 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

Two independent public pull requests were merged within five and nine seconds and both accounts publicly display Quickdraw. The exact maximum interval and direct contributing-event link remain unresolved.

### EVD-2026-003 — YOLO

**Claim:** A pull request authored by the account and merged without a submitted formal review can award YOLO.

**Guide location:** `docs/achievements/yolo.md` — Review-state requirement

**Privacy:** `public-no-personal-data`  
**Sources:** 4 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

Two independent authored pull requests were merged with zero submitted formal reviews and both accounts publicly display YOLO. Merger identity and alternate review-state controls remain unresolved.

### EVD-2026-004 — Pair Extraordinaire

**Claim:** A correctly attributed co-authored commit incorporated into a merged pull request can qualify for Pair Extraordinaire.

**Guide location:** `achievements/pair-extraordinaire.md` — Co-author attribution

**Privacy:** `public-no-personal-data`  
**Sources:** 7 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

Two independent public accounts have account-linked co-author attribution preserved in merged pull-request history and publicly display Pair Extraordinaire. Exact counts and rewrite edge cases remain unresolved.

### EVD-2026-005 — Galaxy Brain

**Claim:** A GitHub Discussion answer authored by the account is deemed helpful by another user.

**Guide location:** `docs/achievements/galaxy-brain.md` — Accepted answers

**Privacy:** `public-no-personal-data`  
**Sources:** 2 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

GitHub’s launch material directly ties Galaxy Brain to Discussion answers another user deems helpful. Exact current accepted-state semantics, processing delay, and tiers remain separate research questions.

### EVD-2026-006 — Starstruck

**Claim:** A repository associated with the account reaches a community-reported star threshold.

**Guide location:** `docs/achievements/starstruck.md` — Repository ownership and star thresholds

**Privacy:** `public-no-personal-data`  
**Sources:** 0 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

Ownership-transfer edge cases and the complete tier table are not officially documented.

### EVD-2026-007 — Public Sponsor

**Claim:** Sponsoring an open-source contributor through GitHub Sponsors can award Public Sponsor.

**Guide location:** `docs/achievements/public-sponsor.md` — Public sponsorship visibility

**Privacy:** `public-no-financial-data`  
**Sources:** 2 public source(s), 1 archive source(s)  
**Contradictory evidence:** 0 item(s)

Archived GitHub documentation directly states the sponsor-badge trigger. Visibility, cancellation, eligibility, and processing behaviour remain limitations rather than changes to the broad trigger.

### EVD-2026-008 — Arctic Code Vault Contributor

**Claim:** The account authored a commit on the default branch of a repository archived in the 2020 GitHub Arctic Code Vault program.

**Guide location:** `docs/arctic-code-vault-contributor.md` — 2020 archive qualification

**Privacy:** `public-no-personal-data`  
**Sources:** 1 public source(s), 1 archive source(s)  
**Contradictory evidence:** 0 item(s)

GitHub’s archived profile documentation states the default-branch commit criterion, while GitHub’s Archive Program publication documents the badge and 2020 vault.

### EVD-2026-009 — Mars 2020 Contributor

**Claim:** The account authored or co-authored a commit present in the listed qualifying tag of a repository used by the Mars 2020 Helicopter Mission.

**Guide location:** `docs/mars-2020-contributor.md` — Mission-linked qualification

**Privacy:** `public-no-personal-data`  
**Sources:** 2 public source(s), 1 archive source(s)  
**Contradictory evidence:** 0 item(s)

Current GitHub documentation publishes the qualifying repository/version/tag list. Archived documentation records commit authorship, co-authorship, tag, and verified-email attribution conditions.

## Using this register

Evidence classification, reviewer decision, and reproduction status are separate fields. Consumers must preserve all three when presenting a record.

Machine-readable data is available from [`/api/evidence.json`](../api/evidence.json).
