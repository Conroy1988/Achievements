---
layout: default
title: Research campaign status
description: Live Phase 65 campaign lifecycle, evidence gates, task buckets, primary mission, and immutable release history.
permalink: /research-campaign-status/
---

## Research campaign status

This is the authoritative live campaign control plane. Published release gates remain historical and are never reused as active candidates.

**Campaign:** `v1.5.0` — Post-v1.4 Research Operations  
**Phase:** 65  
**Lifecycle:** `collecting-evidence`  
**Evidence gate:** `blocked`  
**Primary mission:** `MSN-006` — Run the active YOLO submitted-review-state matrix

## Campaign gate

| Gate | Current | Required | Remaining |
|---|---:|---:|---:|
| Coverage | 91.2 | ≥ 92.0 | 0.8 points |
| Official or confirmed claims | 12 | ≥ 12 | 0 claims |
| Claims below confirmed | 1 | ≤ 1 | 0 promotions |
| Open contradictions | 3 | ≤ 2 | 1 resolutions |
| Operational health | 100 | 100 | 0 points |

## Task buckets

| Bucket | Tasks |
|---|---|
| active | `RSH-002`, `RSH-008`, `RSH-009` |
| blocked | `RSH-010` |
| monitoring | `RSH-005` |
| queued | `RSH-011`, `RSH-012` |

## Lifecycle rule

The v1.5.0 campaign may advance to release-candidate only after its evidence gate passes, all generated outputs are current, and a maintainer explicitly changes the lifecycle. Release-ready additionally requires a fully passing merged-main operational audit.

## Archived campaigns

### v1.4.0 — published

Published: `2026-07-20T00:16:51Z`  
Release commit: `98d478c7b73cff9c6e8fa5235640f12597544b67`  
Baseline record: `c2dc2f43bd860b4ae6282daf066359fdd9a94e22`  
[GitHub Release](https://github.com/Conroy1988/Achievements/releases/tag/v1.4.0)

## Operating rules

- An archived release snapshot is immutable and cannot be reused as the active campaign.
- Campaign lifecycle changes require a maintainer-reviewed source change; builders only validate and publish state.
- Blocked evidence remains blocked until the published evidence requirement is met without artificial activity.
- Active missions must preserve repository safeguards, independent usefulness, privacy, and fail-closed adjudication.

## Machine-readable data

See [`/api/campaign-status.json`](../api/campaign-status.json).
