---
layout: default
title: Contributor research hub
description: Structured, reproducible research tasks for improving GitHub achievement evidence.
permalink: /research-hub/
---

## Contributor research hub

This hub converts known evidence gaps into bounded research tasks. Contributions must follow the evidence register policy and may document failed or contradictory results.

**Open tasks:** 8  
**Good first research tasks:** 3  
**Schema version:** `1.0.0`

| Task | Achievement | Type | Priority | Difficulty | Status |
|---|---|---|---|---|---|
| `RSH-001` | Quickdraw | independent-reproduction | critical | advanced | open |
| `RSH-002` | YOLO | independent-reproduction | critical | advanced | open |
| `RSH-003` | Pull Shark | threshold-verification | high | advanced | open |
| `RSH-004` | Galaxy Brain | threshold-verification | high | advanced | open |
| `RSH-005` | Starstruck | edge-case-research | high | advanced | open |
| `RSH-006` | Arctic Code Vault Contributor | source-replacement — good first issue | medium | beginner | open |
| `RSH-007` | Mars 2020 Contributor | source-replacement — good first issue | medium | beginner | open |
| `RSH-008` | Cross-achievement | cross-achievement-observation — good first issue | medium | beginner | open |

## Research tasks

### RSH-001 — Independently reproduce the Quickdraw qualifying window

**Achievement:** Quickdraw  
**Priority:** `critical`  
**Difficulty:** `advanced`  
**Target evidence:** `confirmed`

**Research question:** What is the shortest and longest reproducible issue or pull-request close interval that awards Quickdraw under normal public-repository use?

**Acceptance criteria**

- Provide dated observations from at least two independent accounts.
- Record creation, closure, and award-processing times without exposing private account data.
- Separate issue and pull-request results where behaviour differs.
- Document failed reproductions and possible confounding factors.

**Related evidence records:** `EVD-2026-002`

### RSH-002 — Independently reproduce the YOLO review-state trigger

**Achievement:** YOLO  
**Priority:** `critical`  
**Difficulty:** `advanced`  
**Target evidence:** `confirmed`

**Research question:** Which pull-request review states prevent or permit YOLO when the author merges their own pull request?

**Acceptance criteria**

- Test no review, comment-only review, requested-changes review, and approving review where repository rules permit.
- Use legitimate test repositories and substantive changes.
- Record branch-protection and merge-method conditions.
- Provide dated results from at least two independent accounts.

**Related evidence records:** `EVD-2026-003`

### RSH-003 — Strengthen Pull Shark tier evidence

**Achievement:** Pull Shark  
**Priority:** `high`  
**Difficulty:** `advanced`  
**Target evidence:** `confirmed`

**Research question:** Can each currently listed Pull Shark tier threshold be independently reproduced with attribution and processing-delay controls?

**Acceptance criteria**

- Provide dated account-level observations for every threshold being claimed.
- Distinguish merged pull-request count from author, committer, and merger identity.
- Record processing delays and repository visibility.
- Do not create meaningless pull requests solely to inflate counts.

**Related evidence records:** `EVD-2026-001`

### RSH-004 — Verify Galaxy Brain tier thresholds

**Achievement:** Galaxy Brain  
**Priority:** `high`  
**Difficulty:** `advanced`  
**Target evidence:** `confirmed`

**Research question:** Do the listed accepted-answer thresholds consistently award the corresponding Galaxy Brain tiers?

**Acceptance criteria**

- Use genuine GitHub Discussion answers accepted by repository maintainers.
- Record accepted-answer count before and after each observed award.
- Separate accepted answers from other verified or moderated answer states.
- Include at least two independent observations for any threshold promoted to confirmed.

**Related evidence records:** `EVD-2026-005`

### RSH-005 — Verify Starstruck ownership edge cases

**Achievement:** Starstruck  
**Priority:** `high`  
**Difficulty:** `advanced`  
**Target evidence:** `confirmed`

**Research question:** How do repository transfer, organization ownership, forks, archived repositories, and falling star counts affect Starstruck attribution?

**Acceptance criteria**

- Use only legitimate repository history and public metadata.
- Record ownership state at the time of award and after any transfer.
- Distinguish personal and organization-owned repositories.
- Document counterexamples as well as successful attribution.

**Related evidence records:** `EVD-2026-006`

### RSH-006 — Locate durable Arctic Code Vault sources

**Achievement:** Arctic Code Vault Contributor  
**Priority:** `medium`  
**Difficulty:** `beginner`  
**Target evidence:** `official`

**Research question:** Which official or well-preserved public sources best document the 2020 qualification event and its historical scope?

**Acceptance criteria**

- Provide an official or high-stability public source.
- Add an archive URL when lawful and available.
- Explain what the source proves and what it does not prove.
- Avoid account-specific private evidence.

**Related evidence records:** `EVD-2026-008`

### RSH-007 — Locate durable Mars 2020 qualification sources

**Achievement:** Mars 2020 Contributor  
**Priority:** `medium`  
**Difficulty:** `beginner`  
**Target evidence:** `official`

**Research question:** Which official or high-stability sources document the mission-linked contribution qualification and its limitations?

**Acceptance criteria**

- Provide a public source from GitHub, NASA, JPL, or another authoritative maintainer.
- Add an archive URL when lawful and available.
- Identify whether the source documents the badge, the repository list, or only mission use.
- Do not infer a complete qualification list from partial examples.

**Related evidence records:** `EVD-2026-009`

### RSH-008 — Document award-processing delay observations

**Achievement:** Cross-achievement  
**Priority:** `medium`  
**Difficulty:** `beginner`  
**Target evidence:** `observed`

**Research question:** What processing delays are observed between a qualifying event and profile-award visibility across different achievements?

**Acceptance criteria**

- Submit dated qualifying-event and first-visible-award timestamps.
- Identify the achievement and relevant repository visibility.
- Do not present a maximum guarantee from a small sample.
- Remove unnecessary account identifiers from submitted evidence.

**Related evidence records:** None

## Starting work

1. Choose an open task and open a research issue using the structured form.
2. State the task ID and planned reproduction method.
3. Preserve privacy and avoid fabricated or meaningless activity.
4. Submit both successful and failed observations with dates and limitations.

Machine-readable tasks are available from [`/api/research-queue.json`](../api/research-queue.json).
