---
layout: default
title: Evidence quality release gate
description: Fail-closed publication criteria for the proposed v1.4.0 evidence-quality release.
permalink: /evidence-quality-release-gate/
---

## Evidence quality release gate

**Candidate:** `v1.4.0`  
**Status:** `blocked`

The release is intentionally blocked. Phases 52–55 improve the research system and narrow three contradictions, but they do not yet justify any canonical claim promotion or coverage increase.

| Gate | Current | Required | Result |
|---|---:|---:|---|
| Evidence coverage | 54.6 | ≥ 70.0 | FAIL |
| Official or confirmed claims | 5 | ≥ 8 | FAIL |
| Claims below confirmed | 8 | ≤ 5 | FAIL |
| Open contradictions | 6 | ≤ 3 | FAIL |
| Operational health | evaluated on merged `main` | 100 | PENDING |

## Publication rule

Do not create the v1.4.0 tag or GitHub Release until every evidence and operational gate passes from the merged main branch.

## Machine-readable data

See [`/api/release-readiness.json`](../api/release-readiness.json).
