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
| `EVD-2026-001` | [Pull Shark](../docs/achievements/pull-shark.md) | official | github-owned-live-product-fragment | accepted-with-limitations | 2026-07-19 |
| `EVD-2026-002` | [Quickdraw](../docs/quickdraw.md) | official | github-owned-live-product-fragment | accepted-with-limitations | 2026-07-19 |
| `EVD-2026-003` | [YOLO](../docs/achievements/yolo.md) | official | github-owned-live-product-fragment | accepted-with-limitations | 2026-07-19 |
| `EVD-2026-004` | [Pair Extraordinaire](../achievements/pair-extraordinaire.md) | official | github-owned-live-product-fragment | accepted-with-limitations | 2026-07-19 |
| `EVD-2026-005` | [Galaxy Brain](../docs/achievements/galaxy-brain.md) | official | github-owned-live-product-fragment | accepted-with-limitations | 2026-07-19 |
| `EVD-2026-006` | [Starstruck](../docs/achievements/starstruck.md) | official | github-owned-live-product-fragment | accepted-with-limitations | 2026-07-19 |
| `EVD-2026-007` | [Public Sponsor](../docs/achievements/public-sponsor.md) | official | officially-documented-trigger | accepted-with-limitations | 2026-07-19 |
| `EVD-2026-008` | [Arctic Code Vault Contributor](../docs/arctic-code-vault-contributor.md) | official | historical-official-documentation | accepted | 2026-07-19 |
| `EVD-2026-009` | [Mars 2020 Contributor](../docs/mars-2020-contributor.md) | official | historical-official-documentation | accepted | 2026-07-19 |

## Record details

### EVD-2026-001 — Pull Shark

**Claim:** GitHub's live product fragment explicitly documents the material Pull Shark contract.

**Guide location:** `docs/achievements/pull-shark.md` — Trigger and attribution

**Privacy:** `public-no-personal-data`  
**Sources:** 1 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

GitHub's live x4 detail fragment states the merged-pull-request trigger and the 2nd, 16th, 128th, and 1024th milestones.

### EVD-2026-002 — Quickdraw

**Claim:** GitHub's live product fragment explicitly documents the material Quickdraw contract.

**Guide location:** `docs/quickdraw.md` — Qualifying time window

**Privacy:** `public-no-personal-data`  
**Sources:** 5 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

GitHub's live detail fragment links a qualifying pull request and states that it was closed within five minutes of opening.

### EVD-2026-003 — YOLO

**Claim:** GitHub's live product fragment explicitly documents the material YOLO contract.

**Guide location:** `docs/achievements/yolo.md` — Review-state requirement

**Privacy:** `public-no-personal-data`  
**Sources:** 5 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

GitHub's live detail fragment links a qualifying pull request and states that it was merged without a review.

### EVD-2026-004 — Pair Extraordinaire

**Claim:** GitHub's live product fragment explicitly documents the material Pair Extraordinaire contract.

**Guide location:** `achievements/pair-extraordinaire.md` — Co-author attribution

**Privacy:** `public-no-personal-data`  
**Sources:** 8 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

GitHub's live detail fragment states that Pair Extraordinaire recognises coauthored commits on merged pull requests; numerical tier counts remain unpublished.

### EVD-2026-005 — Galaxy Brain

**Claim:** GitHub's live product fragment explicitly documents the material Galaxy Brain contract.

**Guide location:** `docs/achievements/galaxy-brain.md` — Accepted answers

**Privacy:** `public-no-personal-data`  
**Sources:** 3 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

GitHub's live x4 detail fragment publishes accepted-answer milestones at 2, 8, 16, and 32.

### EVD-2026-006 — Starstruck

**Claim:** GitHub's live product fragment explicitly documents the material Starstruck contract.

**Guide location:** `docs/achievements/starstruck.md` — Repository ownership and star thresholds

**Privacy:** `public-no-personal-data`  
**Sources:** 1 public source(s), 0 archive source(s)  
**Contradictory evidence:** 0 item(s)

GitHub's live x4 detail fragment states the repository-creation trigger and star milestones at 16, 128, 512, and 4096.

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
