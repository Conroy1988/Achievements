# Achievement Guide Audit

This audit establishes the Phase 13 upgrade order for the seven active guides listed in the achievement index.

## Audit criteria

A guide is assessed against the required sections in [Achievement Guide Standard](achievement-guide-standard.md): summary, trigger, progression, eligibility, timing, verification, evidence status, edge cases, troubleshooting, responsible participation, history, references, and last-verified date.

## Current audit

| Guide | Published | Tiered | Standardisation priority | Primary gaps to resolve |
|---|---:|---:|---|---|
| Pull Shark | Yes | Yes | Critical | Evidence labels for thresholds, eligibility detail, award timing, troubleshooting, history, references, last-verified date |
| Quickdraw | Yes | No | High | Precise timing evidence, eligibility conditions, edge cases, troubleshooting, references, last-verified date |
| YOLO | Yes | No | High | Review-state definition, merge-method edge cases, evidence status, troubleshooting, references, last-verified date |
| Pair Extraordinaire | Yes | Yes | Critical | Co-author attribution rules, tier evidence, eligibility conditions, timing, troubleshooting, references |
| Galaxy Brain | Yes | Yes | Critical | Accepted-answer mechanics, tier evidence, discussion eligibility, timing, edge cases, references |
| Starstruck | Yes | Yes | Critical | Ownership and transfer conditions, tier evidence, repository visibility, timing, edge cases, references |
| Public Sponsor | Yes | No | High | Public-status requirements, sponsorship lifecycle, privacy limits, timing, references, last-verified date |

## Upgrade sequence

1. Pull Shark
2. Pair Extraordinaire
3. Galaxy Brain
4. Starstruck
5. Quickdraw
6. YOLO
7. Public Sponsor

Tiered guides are prioritised because they carry more numerical claims and therefore require clearer evidence classification.

## Pull request boundaries

Each guide should be upgraded through its own focused pull request. A guide pull request should:

- limit changes to that guide and directly related index links;
- preserve unresolved uncertainty rather than guessing;
- identify which claims are official and which remain community-reported;
- pass repository link validation;
- include a verification date;
- avoid unrelated visual or wording changes.

## Phase 13 completion criteria

Phase 13 is complete when all seven active guides conform to the standard, the achievement index links to every guide, and each guide has a current verification date and explicit evidence classifications.
