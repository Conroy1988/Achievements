---
layout: default
title: Evidence intelligence dashboard
description: Deterministic analytics across coverage, event evidence, boundary investigations, adjudication, contradictions, and release readiness.
permalink: /evidence-intelligence/
---

## Evidence intelligence dashboard

This dashboard combines the public evidence-operation endpoints into one read-only decision surface. It does not promote claims, resolve contradictions, or override the formal release gate.

**Evidence coverage:** 54.6/100  
**Event-linked records:** 5  
**Boundary investigations:** 5  
**Deferred adjudications:** 6  
**Release status:** `blocked`

## Distance to the evidence-quality release

| Gate | Remaining gap |
|---|---:|
| Coverage | 15.4 points |
| Official or confirmed claims | 3 claims |
| Claims below confirmed | 3 promotions |
| Open contradictions | 3 resolutions |

## Research pressure ranking

| Rank | Achievement | Pressure | Coverage | Events | Boundaries | Deferred | Contradiction |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | Pair Extraordinaire | 72 | 25.0 | 0 | 1 | 1 | still-disputed |
| 2 | Pull Shark | 67 | 55.0 | 3 | 1 | 1 | still-disputed |
| 3 | Quickdraw | 64 | 25.0 | 1 | 1 | 1 | narrowed |
| 4 | Starstruck | 58 | 37.5 | 0 | 1 | 1 | narrowed |
| 5 | Galaxy Brain | 55 | 62.5 | 0 | 1 | 1 | still-disputed |
| 6 | YOLO | 54 | 25.0 | 1 | 0 | 1 | narrowed |
| 7 | Arctic Code Vault Contributor | 0 | 100.0 | 0 | 0 | 0 | none |
| 8 | Mars 2020 Contributor | 0 | 100.0 | 0 | 0 | 0 | none |
| 9 | Public Sponsor | 0 | 100.0 | 0 | 0 | 0 | none |

## Immediate evidence requirements

### Pair Extraordinaire

- Capture final-history co-author attribution and visible tier state around each merge-method boundary.

### Pull Shark

- Capture independently attributed exact counts immediately below and at each visible tier transition.

### Quickdraw

- Run independent positive and negative controls immediately around the proposed five-minute boundary.

### Starstruck

- Obtain exact unrounded star totals immediately below and above the x4 transition with ownership and timing controls.

### Galaxy Brain

- Capture exact accepted-answer totals and public tier states around each proposed transition.

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
