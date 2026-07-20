---
layout: default
title: Evidence quality release gate
description: Fail-closed publication criteria for the proposed v1.4.0 evidence-quality release.
permalink: /evidence-quality-release-gate/
---

## Evidence quality release gate

**Candidate:** `v1.4.0`  
**Status:** `ready`

All evidence gates pass. Publication still requires merged-main operational verification.

| Gate | Current | Required | Result |
|---|---:|---:|---|
| Evidence coverage | 91.2 | ≥ 70.0 | PASS |
| Official or confirmed claims | 12 | ≥ 8 | PASS |
| Claims below confirmed | 1 | ≤ 5 | PASS |
| Open contradictions | 3 | ≤ 3 | PASS |
| Operational health | evaluated on merged `main` | 100 | PENDING |

## Publication rule

Do not create the v1.4.0 tag or GitHub Release until every evidence and operational gate passes from the merged main branch.

## Machine-readable data

See [`/api/release-readiness.json`](../api/release-readiness.json).
