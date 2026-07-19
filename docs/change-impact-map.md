---
layout: default
title: Official-document change-impact map
description: Monitored GitHub documentation mapped to affected claims, disputes, and research work.
permalink: /change-impact-map/
---

## Official-document change-impact map

A changed official-document fingerprint triggers targeted review; it does not prove an achievement rule changed.

| Document | Risk | Claims | Disputes | Research |
|---|---|---|---|---|
| `github-profile-reference` | critical | `CLM-001`, `CLM-002`, `CLM-003`, `CLM-004`, `CLM-005`, `CLM-006`, `CLM-007`, `CLM-008`, `CLM-009`, `CLM-010`, `CLM-011`, `CLM-013` | `CTR-001`, `CTR-002`, `CTR-003`, `CTR-004`, `CTR-005`, `CTR-006` | `RSH-001`, `RSH-002`, `RSH-003`, `RSH-004`, `RSH-005`, `RSH-007`, `RSH-009`, `RSH-010`, `RSH-011`, `RSH-012` |
| `multiple-authors` | high | `CLM-005`, `CLM-006` | `CTR-004` | `RSH-009`, `RSH-010` |
| `pull-request-reviews` | critical | `CLM-004` | `CTR-002` | `RSH-002` |
| `github-discussions` | high | `CLM-007`, `CLM-008` | `CTR-005` | `RSH-004`, `RSH-011` |
| `repository-stars` | high | `CLM-009`, `CLM-010` | `CTR-006` | `RSH-005` |
| `github-sponsors` | low | `CLM-011` | — | `RSH-012` |

Machine-readable impact data is published at [`/api/change-impact.json`](../api/change-impact.json).
