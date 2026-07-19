---
layout: default
title: Mission evidence promotion planner
description: Fail-closed canonical change plans generated from accepted mission packet reviews.
permalink: /promotion-planner/
---

## Mission evidence promotion planner

The planner converts accepted mission-review promotion proposals into isolated impact previews. It never edits canonical evidence, claims, contradictions, missions, thresholds, release gates, tags, or releases.

**Plans:** 0  
**Ready for maintainer review:** 0  
**Blocked:** 0  
**Automatic applications:** 0  
**Current release status:** `blocked`

## Planning rules

- A generated plan is an impact preview and implementation checklist, not an executable patch.
- The planner must never write canonical claims, evidence, contradictions, missions, thresholds, release gates, tags, or releases.
- Every plan requires a separate maintainer-reviewed pull request before canonical changes may occur.
- Contradiction resolution is never implied by claim promotion and requires its own published criteria to pass.
- Release readiness must be regenerated after the canonical change; the plan may not declare v1.4.0 publishable in advance.
- Blocked plans remain public and may not be silently discarded.

## Promotion plans

No accepted mission-review promotion proposal currently qualifies for a canonical change plan. This is the expected launch state.

## Implementation boundary

A ready plan still requires a separate maintainer-reviewed pull request. The implementation PR must assign the canonical evidence ID, edit the named source files, regenerate every output, run the complete validation suite, and remain isolated for clean rollback.

The machine-readable planner output is published at [`/api/promotion-plans.json`](../api/promotion-plans.json).
