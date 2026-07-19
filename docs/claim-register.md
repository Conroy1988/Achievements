---
layout: default
title: Claim-level evidence register
description: Atomic GitHub achievement claims linked to evidence, research tasks, and lifecycle state.
permalink: /claim-register/
---

## Claim-level evidence register

The register separates broad achievement guides into atomic claims that can be evidenced, disputed, and reviewed independently.

**Claims:** 13  
**Weak claims without research ownership:** 0  
**Schema version:** `1.1.0`

| Claim | Achievement | Type | Evidence | Research | Status |
|---|---|---|---|---|---|
| `CLM-001` | pull-shark | trigger | confirmed | Not required | maintained |
| `CLM-002` | pull-shark | tiers | community-reported | `RSH-003` | provisional |
| `CLM-003` | quickdraw | trigger | community-reported | `RSH-001` | provisional |
| `CLM-004` | yolo | trigger | community-reported | `RSH-002` | provisional |
| `CLM-005` | pair-extraordinaire | trigger | community-reported | `RSH-009` | provisional |
| `CLM-006` | pair-extraordinaire | tiers | community-reported | `RSH-010` | provisional |
| `CLM-007` | galaxy-brain | trigger | observed | `RSH-011` | maintained-with-limitations |
| `CLM-008` | galaxy-brain | tiers | community-reported | `RSH-004` | provisional |
| `CLM-009` | starstruck | trigger | observed | `RSH-005` | maintained-with-limitations |
| `CLM-010` | starstruck | tiers | community-reported | `RSH-005` | provisional |
| `CLM-011` | public-sponsor | trigger | community-reported | `RSH-012` | provisional |
| `CLM-012` | arctic-code-vault-contributor | historical-trigger | confirmed | `RSH-006` | historical |
| `CLM-013` | mars-2020-contributor | historical-trigger | confirmed | `RSH-007` | historical |

All claims below confirmed strength must have at least one assigned research task. The research-intelligence validator fails when a weak claim is orphaned.

Machine-readable claims are published at [`/api/claims.json`](../api/claims.json).
