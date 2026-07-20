---
layout: default
title: Evidence intelligence dashboard
description: Deterministic analytics across coverage, event evidence, boundary investigations, adjudication, contradictions, and release readiness.
permalink: /evidence-intelligence/
---

## Evidence intelligence dashboard

This dashboard combines the public evidence-operation endpoints into one read-only decision surface. It does not promote claims, resolve contradictions, or override the active research campaign lifecycle.

**Evidence coverage:** 91.2/100  
**Event-linked records:** 16  
**Boundary investigations:** 5  
**Deferred adjudications:** 7  
**Campaign lifecycle:** `collecting-evidence`  
**Campaign gate:** `blocked`

## Distance to the active campaign gate

| Gate | Remaining gap |
|---|---:|
| Coverage | 0.8 points |
| Official or confirmed claims | 0 claims |
| Claims below confirmed | 0 promotions |
| Open contradictions | 1 resolutions |

## Research pressure ranking

| Rank | Achievement | Pressure | Coverage | Events | Boundaries | Deferred | Contradiction |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | Pair Extraordinaire | 49 | 57.5 | 4 | 1 | 2 | narrowed |
| 2 | Starstruck | 34 | 90.0 | 2 | 1 | 1 | narrowed |
| 3 | Pull Shark | 27 | 100.0 | 3 | 1 | 1 | none |
| 4 | YOLO | 24 | 90.0 | 4 | 0 | 1 | narrowed |
| 5 | Galaxy Brain | 18 | 100.0 | 0 | 1 | 1 | none |
| 6 | Quickdraw | 18 | 100.0 | 3 | 1 | 1 | none |
| 7 | Arctic Code Vault Contributor | 0 | 100.0 | 0 | 0 | 0 | none |
| 8 | Mars 2020 Contributor | 0 | 100.0 | 0 | 0 | 0 | none |
| 9 | Public Sponsor | 0 | 100.0 | 0 | 0 | 0 | none |

## Immediate evidence requirements

### Pair Extraordinaire

- GitHub-owned x3 and x4 fragments confirm that multiple Pair Extraordinaire tiers exist, and two independent squash-merge cases preserve final-history attribution. Exact 1, 10, 24, and 48 boundaries still require dated below/at/above account counts; a high-tier sighting alone cannot confirm them.

### Starstruck

- Monitor the GitHub-owned achievement fragment for product-contract drift; no additional threshold search is required.

### Pull Shark

- Monitor the GitHub-owned achievement fragment for product-contract drift; no additional threshold search is required.

### Galaxy Brain

- Monitor the GitHub-owned achievement fragment for product-contract drift; no additional threshold search is required.

### Quickdraw

- Monitor the GitHub-owned achievement fragment for product-contract drift; no additional threshold search is required.

## Pressure-score contract

The score is a prioritisation aid, not an evidence-confidence score:

- 45% of the remaining coverage gap contributes to pressure.
- A still-disputed contradiction adds 20 points; a narrowed contradiction adds 12.
- An unresolved boundary programme adds 10 points.
- Any deferred adjudication adds 8 points.
- Each negative or inconclusive event adds 3 points, capped at 9.
- The final score is rounded and capped at 100.

High pressure means the claim area combines weak coverage with unresolved work. It does not mean the underlying community claim is likely to be true.

## Machine-readable data

The generated analytics are published at [`/api/evidence-intelligence.json`](../api/evidence-intelligence.json).
