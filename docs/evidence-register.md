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
| `EVD-2026-002` | [Quickdraw](../docs/quickdraw.md) | community-reported | awaiting-independent-reproduction | provisional | 2026-07-19 |
| `EVD-2026-003` | [YOLO](../docs/achievements/yolo.md) | community-reported | awaiting-independent-reproduction | provisional | 2026-07-19 |
| `EVD-2026-004` | [Pair Extraordinaire](../achievements/pair-extraordinaire.md) | community-reported | partially-reproduced | accepted-with-limitations | 2026-07-19 |
| `EVD-2026-005` | [Galaxy Brain](../docs/achievements/galaxy-brain.md) | observed | observed-not-fully-reproduced | accepted-with-limitations | 2026-07-19 |
| `EVD-2026-006` | [Starstruck](../docs/achievements/starstruck.md) | observed | observed-not-fully-reproduced | accepted-with-limitations | 2026-07-19 |
| `EVD-2026-007` | [Public Sponsor](../docs/achievements/public-sponsor.md) | community-reported | partially-reproduced | accepted-with-limitations | 2026-07-19 |
| `EVD-2026-008` | [Arctic Code Vault Contributor](../docs/arctic-code-vault-contributor.md) | confirmed | historical-confirmation | accepted | 2026-07-19 |
| `EVD-2026-009` | [Mars 2020 Contributor](../docs/mars-2020-contributor.md) | confirmed | historical-confirmation | accepted | 2026-07-19 |

## Record details

### EVD-2026-001 — Pull Shark

**Claim:** A substantive pull request attributable to the account is merged.

**Guide location:** `docs/achievements/pull-shark.md` — Trigger and attribution

**Privacy:** `public-no-personal-data`  
**Sources:** 0 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

The trigger is confirmed; the complete tier table remains community-reported.

### EVD-2026-002 — Quickdraw

**Claim:** An issue or pull request is closed within the short community-observed qualifying window after creation.

**Guide location:** `docs/quickdraw.md` — Qualifying time window

**Privacy:** `public-no-personal-data`  
**Sources:** 0 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

GitHub does not publish the exact qualifying time window.

### EVD-2026-003 — YOLO

**Claim:** The account merges its own pull request without an approving review.

**Guide location:** `docs/achievements/yolo.md` — Review-state requirement

**Privacy:** `public-no-personal-data`  
**Sources:** 0 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

Comments and approving reviews are distinct GitHub objects.

### EVD-2026-004 — Pair Extraordinaire

**Claim:** A correctly attributed co-authored commit is incorporated into a merged pull request.

**Guide location:** `achievements/pair-extraordinaire.md` — Co-author attribution

**Privacy:** `public-no-personal-data`  
**Sources:** 1 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

GitHub documents co-authorship syntax but not the complete achievement contract or tiers.

### EVD-2026-005 — Galaxy Brain

**Claim:** An answer posted by the account in a GitHub Discussion is marked as accepted.

**Guide location:** `docs/achievements/galaxy-brain.md` — Accepted answers

**Privacy:** `public-no-personal-data`  
**Sources:** 0 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

Accepted and verified answers are different moderation states.

### EVD-2026-006 — Starstruck

**Claim:** A repository associated with the account reaches a community-reported star threshold.

**Guide location:** `docs/achievements/starstruck.md` — Repository ownership and star thresholds

**Privacy:** `public-no-personal-data`  
**Sources:** 0 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

Ownership-transfer edge cases and the complete tier table are not officially documented.

### EVD-2026-007 — Public Sponsor

**Claim:** The account creates an active and publicly visible sponsorship through GitHub Sponsors.

**Guide location:** `docs/achievements/public-sponsor.md` — Public sponsorship visibility

**Privacy:** `public-no-financial-data`  
**Sources:** 1 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

The official Sponsors documentation explains the product but not the achievement-award contract.

### EVD-2026-008 — Arctic Code Vault Contributor

**Claim:** The account contributed to a qualifying repository preserved in the 2020 GitHub Arctic Code Vault snapshot.

**Guide location:** `docs/arctic-code-vault-contributor.md` — 2020 archive qualification

**Privacy:** `public-no-personal-data`  
**Sources:** 0 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

The qualifying archival event is complete and cannot be reproduced through new activity.

### EVD-2026-009 — Mars 2020 Contributor

**Claim:** The account contributed to qualifying open-source repositories used by the Mars 2020 mission.

**Guide location:** `docs/mars-2020-contributor.md` — Mission-linked qualification

**Privacy:** `public-no-personal-data`  
**Sources:** 0 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

The mission-linked event is historical and not currently earnable.

## Using this register

Evidence classification, reviewer decision, and reproduction status are separate fields. Consumers must preserve all three when presenting a record.

Machine-readable data is available from [`/api/evidence.json`](../api/evidence.json).
