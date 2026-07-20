---
layout: default
title: Contributor research hub
description: Campaign-classified, reproducible research tasks for improving GitHub achievement evidence.
permalink: /research-hub/
---

## Contributor research hub

This hub converts known evidence gaps into bounded research tasks. Phase 65 separates work that is active, blocked, monitored, queued, or complete without weakening evidence requirements.

**Campaign:** `v1.5.0`  
**Active:** 3  
**Blocked:** 1  
**Monitoring:** 1  
**Queued:** 2  
**Good first research tasks:** 1  
**Schema version:** `1.2.0`

| Task | Achievement | Type | Priority | Difficulty | Campaign | Status |
|---|---|---|---|---|---|---|
| `RSH-002` | YOLO | independent-reproduction | critical | advanced | active | in-progress |
| `RSH-009` | Pair Extraordinaire | independent-reproduction | high | advanced | active | in-progress |
| `RSH-008` | Cross-achievement | cross-achievement-observation — good first issue | medium | beginner | active | in-progress |
| `RSH-010` | Pair Extraordinaire | threshold-verification | high | advanced | blocked | blocked |
| `RSH-005` | Starstruck | edge-case-research | high | advanced | monitoring | in-progress |
| `RSH-011` | Galaxy Brain | edge-case-research | high | intermediate | queued | open |
| `RSH-012` | Public Sponsor | edge-case-research | high | intermediate | queued | open |
| `RSH-001` | Quickdraw | independent-reproduction | critical | advanced | complete | resolved |
| `RSH-003` | Pull Shark | threshold-verification | high | advanced | complete | resolved |
| `RSH-004` | Galaxy Brain | threshold-verification | high | advanced | complete | resolved |
| `RSH-006` | Arctic Code Vault Contributor | source-replacement — good first issue | medium | beginner | complete | resolved |
| `RSH-007` | Mars 2020 Contributor | source-replacement — good first issue | medium | beginner | complete | resolved |

## Active tasks

### RSH-002 — Independently reproduce the YOLO review-state trigger

**Achievement:** YOLO  
**Priority:** `critical`  
**Difficulty:** `advanced`  
**Target evidence:** `confirmed`

**Research question:** Which submitted pull-request review states prevent or permit YOLO after the pending-review-request subcase is excluded?

**Acceptance criteria**

- Test submitted comment-only, requested-changes, approving, dismissed, and automation review states where repository rules permit.
- Separate requested reviewers from submitted review objects.
- Record author and merger identity, branch protection, and merge method.
- Provide dated results from at least two independent accounts using legitimate substantive changes.

**Related evidence records:** `EVD-2026-003`

### RSH-009 — Reproduce Pair Extraordinaire merge attribution

**Achievement:** Pair Extraordinaire  
**Priority:** `high`  
**Difficulty:** `advanced`  
**Target evidence:** `confirmed`

**Research question:** Which rebase, fast-forward, email-matching, stripped-trailer, and post-merge rewrite states preserve Pair Extraordinaire attribution after squash preservation is observed?

**Acceptance criteria**

- Test legitimate rebase or fast-forward and merge-commit cases where repository policy permits.
- Record whether the final merged history retains an account-linked Co-authored-by trailer.
- Include an email-mismatch or stripped-trailer negative control without misattributing a real person.
- Provide dated results from at least two independent accounts and retain failed reproductions.

**Related evidence records:** `EVD-2026-004`

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


## Blocked tasks

### RSH-010 — Verify Pair Extraordinaire tier thresholds

**Achievement:** Pair Extraordinaire  
**Priority:** `high`  
**Difficulty:** `advanced`  
**Target evidence:** `confirmed`

**Research question:** Can the reported 1, 10, 24, and 48 Pair Extraordinaire boundaries be observed with exact qualifying counts rather than inferred from x3 or x4 badge sightings?

**Acceptance criteria**

- Record qualifying count immediately below, at, and above each proposed boundary.
- Confirm final merged history retains the co-author identity used for counting.
- Separate base, bronze, silver, and gold transitions and measure processing delay.
- Do not manufacture meaningless pull requests or misattribute co-authorship.

**Related evidence records:** `EVD-2026-004`


## Monitoring tasks

### RSH-005 — Verify Starstruck ownership edge cases

**Achievement:** Starstruck  
**Priority:** `high`  
**Difficulty:** `advanced`  
**Target evidence:** `confirmed`

**Research question:** How do transfer timing, forks, archival, falling star counts, deletion, restoration, and revocation affect Starstruck after organization ownership is shown to remain attributable in some cases?

**Acceptance criteria**

- Use only legitimate repository history and public metadata.
- Record ownership state and milestone state before and after a documented transition.
- Separate current organization ownership from the exact timing of transfer and award processing.
- Document counterexamples, persistence, and revocation without soliciting artificial stars.

**Related evidence records:** `EVD-2026-006`


## Queued tasks

### RSH-011 — Verify Galaxy Brain accepted-answer semantics and processing

**Achievement:** Galaxy Brain  
**Priority:** `high`  
**Difficulty:** `intermediate`  
**Target evidence:** `confirmed`

**Research question:** How does GitHub’s official “answer deemed helpful” description map to current accepted-answer interface states, revocation behaviour, and profile-processing delay?

**Acceptance criteria**

- Use genuine Discussion questions and answers moderated by the repository maintainer.
- Record answer, acceptance, revocation where applicable, and first-visible-award timestamps.
- Distinguish accepted answers from verified answers, labels, reactions, and other moderation states.
- Provide observations from at least two independent accounts without publishing restricted content.

**Related evidence records:** `EVD-2026-005`

### RSH-012 — Verify Public Sponsor visibility and processing edge cases

**Achievement:** Public Sponsor  
**Priority:** `high`  
**Difficulty:** `intermediate`  
**Target evidence:** `confirmed`

**Research question:** How do sponsorship visibility, cancellation, account state, and processing delay affect an officially documented Public Sponsor award?

**Acceptance criteria**

- Record only public sponsorship state, activation date, and profile-award visibility; exclude payment details.
- Compare public and private sponsorship visibility only where participants can do so safely and legitimately.
- Record cancellation or visibility-change outcomes without exposing financial or eligibility data.
- Provide dated observations from at least two independent accounts.

**Related evidence records:** `EVD-2026-007`


## Complete tasks

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

## Starting work

1. Start with an active task or a queued task that has become naturally actionable.
2. Preserve the published mission, protocol, safeguards, and evidence requirements.
3. Never manufacture activity to unblock a threshold or fill a matrix cell.
4. Submit successful, failed, delayed, and contradictory observations with dates and limitations.

Machine-readable tasks are available from [`/api/research-queue.json`](../api/research-queue.json).
