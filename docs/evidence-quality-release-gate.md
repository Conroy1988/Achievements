---
layout: default
title: v1.4.0 evidence release baseline
description: Immutable evidence and operational publication baseline for the published v1.4.0 release.
permalink: /evidence-quality-release-gate/
---

## v1.4.0 evidence release baseline

**Release:** `v1.4.0`  
**Status:** `published`

This gate is a historical published baseline. It is not the active release candidate.

| Gate | Final | Required | Result |
|---|---:|---:|---|
| Evidence coverage | 91.2 | ≥ 70.0 | PASS |
| Official or confirmed claims | 12 | ≥ 8 | PASS |
| Claims below confirmed | 1 | ≤ 5 | PASS |
| Open contradictions | 3 | ≤ 3 | PASS |
| Operational health | 100 | 100 | PASS |

## Immutable release record

- Published: `2026-07-20T00:16:51Z`
- Release commit: `98d478c7b73cff9c6e8fa5235640f12597544b67`
- Baseline record: `c2dc2f43bd860b4ae6282daf066359fdd9a94e22`
- [GitHub Release](https://github.com/Conroy1988/Achievements/releases/tag/v1.4.0)

## Historical publication rule

Historical v1.4.0 evidence gate. The release was published only after the evidence snapshot passed and merged-main operational health was verified at 100/100. Live campaign state is published separately at /Achievements/api/campaign-status.json.

## Active campaign

The live campaign is published at [`/api/campaign-status.json`](../api/campaign-status.json) and [Research campaign status](research-campaign-status.md).

## Machine-readable data

See [`/api/release-readiness.json`](../api/release-readiness.json).
