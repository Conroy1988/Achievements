---
layout: default
title: Targeted evidence acquisition missions
description: Ranked, ethical, fail-closed missions for converting evidence pressure into adjudicable observations.
permalink: /targeted-evidence-missions/
---

## Targeted evidence acquisition missions

These missions turn the evidence-intelligence ranking into bounded research. They prohibit spam, false attribution, repository manipulation, achievement farming, and automatic claim promotion.

**Missions:** 7  
**Claims targeted:** 10  
**Contradictions targeted:** 6  
**Scheduled checkpoints:** 1

| Rank | Mission | Achievement | Pressure | Status |
|---:|---|---|---:|---|
| 1 | `MSN-002` — Measure Pull Shark processing and attributed-count behaviour | pull-shark | 67 | scheduled |
| 2 | `MSN-001` — Preserve real co-author attribution across merge methods | pair-extraordinaire | 58 | participant-needed |
| 3 | `MSN-004` — Find exact public observations around the Starstruck x4 boundary | starstruck | 58 | candidate-search |
| 4 | `MSN-005` — Link accepted-answer counts to visible Galaxy Brain tiers | galaxy-brain | 55 | participant-needed |
| 5 | `MSN-003` — Bracket the Quickdraw timing boundary | quickdraw | 52 | participant-needed |
| 6 | `MSN-006` — Separate YOLO review-state and merger-identity conditions | yolo | 42 | participant-needed |
| 7 | `MSN-007` — Maintain a passive cross-achievement processing-delay ledger | cross-achievement | 0 | passive-observation |

## Operating rules

- Every underlying GitHub action must remain independently useful.
- Existing protections and maintainer decisions override mission completion.
- Negative, blocked, delayed, and inconclusive outcomes remain visible.
- Completion creates a reviewable evidence package, never an automatic promotion.

### 1. MSN-002 — Measure Pull Shark processing and attributed-count behaviour

Capture the public Pull Shark detail state after a bounded processing window and preserve a reproducible support package without generating additional badge-chasing activity.

**Status:** `scheduled`  
**Claims:** `CLM-001`, `CLM-002`  
**Contradictions:** `CTR-003`

**Scheduled checkpoint:** `2026-07-22T20:00:00+01:00`  
**No action before:** `2026-07-22T20:00:00+01:00`  
**Checkpoint:** [https://github.com/Conroy1988?achievement=pull-shark&tab=achievements](https://github.com/Conroy1988?achievement=pull-shark&tab=achievements)

**Controls**

- Create no additional pull requests solely for this mission before the checkpoint.
- Separate raw authored-and-merged pull-request counts from GitHub's unknown qualifying count.
- Treat a missing badge as negative-inconclusive unless GitHub provides an explicit exclusion reason.

**Required evidence**

- achievement_detail_url
- observed_time_utc
- displayed_tier_or_absence
- contributing_event_links_if_exposed
- processing_interval
- support_escalation_package_if_absent

**Stop conditions**

- Do not create test or empty pull requests to provoke a recalculation.
- Do not interpret profile absence as proof that every existing merge is ineligible.
- Stop after the scheduled observation and bounded escalation package are complete.

**Ethics**

- Only existing substantive development activity is used.
- Negative and inconclusive results remain visible in the evidence record.

### 2. MSN-001 — Preserve real co-author attribution across merge methods

Collect legitimate collaborative pull requests that show whether merge commit, squash, and rebase workflows preserve qualifying final-history co-author attribution and any observable tier transition.

**Status:** `participant-needed`  
**Claims:** `CLM-005`, `CLM-006`  
**Contradictions:** `CTR-004`

**Controls**

- Inspect the final merged commit rather than relying only on the pull-request interface.
- Record merge method, trailer preservation, account linkage, and visible achievement state.
- Retain naturally occurring failed attribution cases; do not manufacture false co-authorship as a negative control.

**Required evidence**

- public_pull_request_url
- final_commit_url
- merge_method
- trailer_preserved
- account_linkage_state
- achievement_state_before
- achievement_state_after
- first_visible_time_utc_or_cutoff

**Stop conditions**

- Stop if either contributor did not make a real contribution.
- Stop if attribution would expose a private email address without consent.
- Do not create additional pull requests solely to move a counter.

**Ethics**

- False Co-authored-by trailers are prohibited.
- Every repository change must remain independently useful and reviewable.

### 3. MSN-004 — Find exact public observations around the Starstruck x4 boundary

Locate public account-owned repositories immediately below and above the reported x4 boundary while preserving exact API star counts and ownership state.

**Status:** `candidate-search`  
**Claims:** `CLM-009`, `CLM-010`  
**Contradictions:** `CTR-006`

**Controls**

- Record exact API counts and rendered profile text separately.
- Distinguish personal ownership from organization ownership and forks.
- Capture observation time because star counts can change.

**Required evidence**

- profile_achievement_url
- repository_url
- exact_stargazer_count
- rendered_star_count
- displayed_tier
- owner_type
- fork_status
- archive_status
- observed_time_utc

**Stop conditions**

- Do not solicit, purchase, exchange, or coordinate stars.
- Do not infer a boundary from rounded display text alone.
- Stop when two independent near-boundary observations exist on each relevant side or the candidate search is exhausted.

**Ethics**

- This mission is observation-only.
- Repository popularity must not be manipulated for research.

### 4. MSN-005 — Link accepted-answer counts to visible Galaxy Brain tiers

Capture exact accepted-answer counts, moderation state, and profile-processing time around genuine Discussion answers and any observed tier transition.

**Status:** `participant-needed`  
**Claims:** `CLM-007`, `CLM-008`  
**Contradictions:** `CTR-005`

**Controls**

- Separate accepted answers from labels, reactions, verified answers, and other moderation states.
- Record exact count before and after acceptance.
- Retain revocation or no-award results where they occur naturally.

**Required evidence**

- public_discussion_url
- moderation_state
- accepted_count_before
- accepted_count_after
- accepted_time_utc
- achievement_state_before
- achievement_state_after
- first_visible_time_utc_or_cutoff

**Stop conditions**

- Do not ask a maintainer to accept an incorrect or low-quality answer.
- Stop if participation is unwelcome or the Discussion is removed.
- Do not create artificial questions solely to generate accepted answers.

**Ethics**

- Questions and answers must be genuine and useful.
- Maintainer moderation remains independent.

### 5. MSN-003 — Bracket the Quickdraw timing boundary

Collect independent positive and negative controls around the reported five-minute boundary for both issues and pull requests under legitimate repository use.

**Status:** `participant-needed`  
**Claims:** `CLM-003`  
**Contradictions:** `CTR-001`

**Controls**

- Separate issue and pull-request observations.
- Retain both positive and negative outcomes around the proposed boundary.
- Record creator, closer, visibility, and processing delay as potential confounders.

**Required evidence**

- public_object_url
- object_type
- creation_time_utc
- closure_time_utc
- elapsed_seconds
- creator_closer_relation
- achievement_state_before
- first_visible_time_utc_or_cutoff
- result

**Stop conditions**

- Stop after the pre-registered matrix cell is complete.
- Stop immediately if maintainers object.
- Do not flood a repository with repeated timing tests.

**Ethics**

- Every issue or pull request must have a legitimate repository purpose.
- Repeated artificial open-close activity is prohibited.

### 6. MSN-006 — Separate YOLO review-state and merger-identity conditions

Observe no-review, comment-only, changes-requested, and approved-review states across legitimate self-merged pull requests without weakening repository safeguards.

**Status:** `participant-needed`  
**Claims:** `CLM-004`  
**Contradictions:** `CTR-002`

**Controls**

- Record exact formal review state rather than inferring from comments.
- Record author, merger, branch rules, and merge method.
- Use existing repository policy; do not disable required reviews or administrator safeguards.

**Required evidence**

- public_pull_request_url
- review_state
- review_object_urls
- branch_rules
- author_merger_relation
- merge_method
- achievement_state_before
- first_visible_time_utc_or_cutoff
- result

**Stop conditions**

- Do not bypass or weaken protected-branch safeguards.
- Do not create meaningless pull requests for matrix completion.
- Stop when the naturally available review-state cell is documented.

**Ethics**

- Normal review quality and repository safety take precedence over the mission.
- A missing matrix cell is preferable to manufactured activity.

### 7. MSN-007 — Maintain a passive cross-achievement processing-delay ledger

Record qualifying-event and first-visible-award timestamps from normal activity so processing delay is measured rather than assumed.

**Status:** `passive-observation`  
**Claims:** none  
**Contradictions:** none

**Controls**

- Do not create an event solely to populate this ledger.
- Record first-visible time separately from first-check time.
- Do not generalise a maximum processing guarantee from a small sample.

**Required evidence**

- achievement_slug
- public_event_url
- event_time_utc
- first_check_time_utc
- first_visible_time_utc_or_cutoff
- repository_visibility
- result

**Stop conditions**

- Stop after the bounded observation window.
- Stop if the participant withdraws consent.
- Do not expose private repositories, messages, or authentication material.

**Ethics**

- The ledger is passive and must never drive artificial qualifying activity.
- Unsuccessful and long-delay observations are retained.

## Machine-readable queue

The validated summaries are published at [`/api/acquisition-missions.json`](../api/acquisition-missions.json). The complete execution plans remain canonical in [`data/acquisition-missions.json`](../data/acquisition-missions.json).
