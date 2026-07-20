from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-07-20"
OBSERVED_AT = "2026-07-20T01:38:16Z"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path: str, value: dict) -> None:
    (ROOT / path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def by_id(rows: list[dict], row_id: str) -> dict:
    for row in rows:
        if row.get("id") == row_id:
            return row
    raise KeyError(row_id)


def replace(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise ValueError(f"{path}: expected text not found: {old[:80]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def event_records() -> list[dict]:
    return [
        {
            "id": "EVT-2026-012",
            "achievement_slug": "yolo",
            "claim_ids": ["CLM-004"],
            "event_type": "merge-with-review-request-but-no-submitted-review",
            "event_url": "https://github.com/Schweinepriester/achievement-testarea/pull/4",
            "subject_login": "Schweinepriester",
            "created_at": "2022-06-12T20:40:00Z",
            "completed_at": "2022-06-12T20:40:02Z",
            "elapsed_seconds": 2,
            "public_facts": [
                "The pull request had a requested reviewer at merge time, but the public reviews endpoint contains no submitted review objects.",
                "GitHub's achievement-detail fragment links this pull request and states that it was merged without a review."
            ],
            "award_link": "github-owned-achievement-fragment-linked-event",
            "adjudication_status": "accepted",
            "independent_account_count": 1,
            "limitations": [
                "This establishes that requesting a reviewer is not itself a submitted review for this observed award.",
                "It does not establish how submitted COMMENT, REQUEST_CHANGES, APPROVE, or dismissed reviews affect qualification."
            ]
        },
        {
            "id": "EVT-2026-013",
            "achievement_slug": "pair-extraordinaire",
            "claim_ids": ["CLM-005"],
            "event_type": "squash-merge-preserving-coauthor-attribution",
            "event_url": "https://github.com/Fyrd/caniuse/pull/6271",
            "subject_login": "Schweinepriester",
            "created_at": "2022-05-15T13:45:46Z",
            "completed_at": "2022-05-26T04:31:39Z",
            "elapsed_seconds": 917153,
            "public_facts": [
                "The two-commit pull request was squash-merged and its final default-branch commit retained an account-linked Schweinepriester Co-authored-by trailer.",
                "GitHub's Pair Extraordinaire x3 achievement-detail fragment links this pull request in its contributing history."
            ],
            "award_link": "github-owned-achievement-fragment-linked-event",
            "adjudication_status": "accepted",
            "independent_account_count": 2,
            "limitations": [
                "The fragment does not expose how many qualifying pull requests GitHub attributed to the account.",
                "One successful squash configuration does not prove that every squash setting preserves attribution."
            ]
        },
        {
            "id": "EVT-2026-014",
            "achievement_slug": "pair-extraordinaire",
            "claim_ids": ["CLM-005"],
            "event_type": "squash-merge-preserving-coauthor-attribution",
            "event_url": "https://github.com/Fyrd/caniuse/pull/7306",
            "subject_login": "Schweinepriester",
            "created_at": "2025-04-14T01:33:01Z",
            "completed_at": "2025-04-16T05:41:36Z",
            "elapsed_seconds": 187715,
            "public_facts": [
                "The two-commit pull request was squash-merged and its final default-branch commit retained an account-linked Schweinepriester Co-authored-by trailer.",
                "GitHub's Pair Extraordinaire x3 achievement-detail fragment independently links this pull request in its contributing history."
            ],
            "award_link": "github-owned-achievement-fragment-linked-event",
            "adjudication_status": "accepted",
            "independent_account_count": 2,
            "limitations": [
                "The fragment does not expose the internal attributed count or the exact tier boundary crossed by this event.",
                "Rebase, stripped-trailer, mismatched-email, and later history-rewrite cases remain outside this observation."
            ]
        },
        {
            "id": "EVT-2026-015",
            "achievement_slug": "starstruck",
            "claim_ids": ["CLM-009", "CLM-010"],
            "event_type": "creator-attribution-on-organization-owned-repository",
            "event_url": "https://github.com/users/balloob/achievements/starstruck/detail?hovercard=1",
            "subject_login": "balloob",
            "created_at": OBSERVED_AT,
            "completed_at": OBSERVED_AT,
            "elapsed_seconds": 0,
            "public_facts": [
                "GitHub's Starstruck x4 fragment credits balloob and links home-assistant/core for published star milestones.",
                "The linked repository is currently owned by the home-assistant organization rather than the credited personal account."
            ],
            "award_link": "github-owned-achievement-fragment",
            "adjudication_status": "accepted",
            "independent_account_count": 2,
            "limitations": [
                "The fragment does not publish the repository transfer date or prove whether transfer occurred before or after each milestone.",
                "Fork, archive, deletion, restoration, falling-count, and award-removal behavior remain unresolved."
            ]
        },
        {
            "id": "EVT-2026-016",
            "achievement_slug": "starstruck",
            "claim_ids": ["CLM-009", "CLM-010"],
            "event_type": "creator-attribution-on-organization-owned-repository",
            "event_url": "https://github.com/users/tiangolo/achievements/starstruck/detail?hovercard=1",
            "subject_login": "tiangolo",
            "created_at": OBSERVED_AT,
            "completed_at": OBSERVED_AT,
            "elapsed_seconds": 0,
            "public_facts": [
                "GitHub's Starstruck x4 fragment credits tiangolo and links fastapi/fastapi for the published 4096-star milestone.",
                "The linked repository is currently owned by the fastapi organization rather than the credited personal account."
            ],
            "award_link": "github-owned-achievement-fragment",
            "adjudication_status": "accepted",
            "independent_account_count": 2,
            "limitations": [
                "The fragment does not expose the ownership state at the exact moment the milestone or award was processed.",
                "It does not resolve forks, archival, falling star counts, deletion, restoration, or revocation behavior."
            ]
        }
    ]


def update_programme() -> None:
    value = load("data/evidence-quality-programme.json")
    value["programme_date"] = DATE
    events = value["event_evidence"]
    existing = {row["id"] for row in events}
    for row in event_records():
        if row["id"] not in existing:
            events.append(row)
    events.sort(key=lambda row: row["id"])

    boundary = by_id(value["boundary_programmes"], "BND-002")
    boundary["status"] = "blocked-missing-boundary-counts"
    boundary["next_evidence"] = (
        "GitHub-owned x3 and x4 fragments confirm that multiple Pair Extraordinaire tiers exist, and two independent "
        "squash-merge cases preserve final-history attribution. Exact 1, 10, 24, and 48 boundaries still require "
        "dated below/at/above account counts; a high-tier sighting alone cannot confirm them."
    )

    decision = by_id(value["adjudication_decisions"], "ADJ-D002")
    decision["reason"] = (
        "GitHub's linked YOLO event shows that an outstanding review request with zero submitted reviews can still be "
        "classified as 'Merged without a review'. Submitted COMMENT, REQUEST_CHANGES, APPROVE, dismissed-review, and "
        "merger-identity cases remain separate controls."
    )
    decision = by_id(value["adjudication_decisions"], "ADJ-D004")
    decision["reason"] = (
        "GitHub-owned x3 and x4 fragments confirm tier existence, but not the reported 1, 10, 24, and 48 boundaries. "
        "The numeric claim remains community-reported pending controlled boundary counts."
    )
    decision = by_id(value["adjudication_decisions"], "ADJ-D006")
    decision["reason"] = (
        "GitHub's Starstruck fragments publish the complete milestone table and retain creator attribution for at least "
        "two currently organization-owned repositories. Transfer timing, forks, archival, falling counts, and award "
        "persistence remain bounded edge cases."
    )
    decision = by_id(value["adjudication_decisions"], "ADJ-D007")
    decision["reason"] = (
        "The broad trigger is official. Two independent GitHub-linked squash cases show that attribution can survive "
        "when the final commit retains the account-linked trailer; rebase, stripped trailers, email mismatch, later "
        "rewrites, and exact tier counts remain open."
    )

    assessment = {row["contradiction_id"]: row for row in value["contradiction_assessments"]}
    assessment["CTR-002"].update({
        "outcome": "narrowed",
        "basis_ids": ["EVT-2026-002", "EVT-2026-008", "EVT-2026-009", "EVT-2026-012"],
        "remaining_question": (
            "A pending review request is now distinguished from a submitted review and did not prevent the linked award. "
            "Submitted COMMENT, REQUEST_CHANGES, APPROVE, dismissed-review, automation-review, and merger-identity cases remain open."
        )
    })
    assessment["CTR-004"].update({
        "outcome": "narrowed",
        "basis_ids": ["BND-002", "EVT-2026-010", "EVT-2026-011", "EVT-2026-013", "EVT-2026-014"],
        "remaining_question": (
            "Two independent GitHub-linked squash cases preserve attribution when the final commit retains the trailer. "
            "Rebase or fast-forward behavior, stripped trailers, email mismatch, later rewrites, and exact tier counts remain open."
        )
    })
    assessment["CTR-006"].update({
        "outcome": "narrowed",
        "basis_ids": ["GAF-2026-006", "EVT-2026-015", "EVT-2026-016"],
        "remaining_question": (
            "Current organization ownership does not necessarily erase creator attribution: two GitHub-owned fragments "
            "credit personal creators for organization-owned repositories. Transfer timing, forks, archival, falling counts, "
            "deletion, restoration, and award persistence remain open."
        )
    })
    save("data/evidence-quality-programme.json", value)


def update_contradictions() -> None:
    value = load("data/contradictions.json")
    records = value["records"]

    row = by_id(records, "CTR-002")
    row.update({
        "positions": [
            "A requested reviewer without a submitted review does not itself defeat YOLO in the GitHub-linked observed case.",
            "Submitted COMMENT, REQUEST_CHANGES, APPROVE, dismissed, or automated review objects may affect qualification differently."
        ],
        "resolution_criteria": (
            "Controlled tests covering submitted comment-only, changes-requested, approved, dismissed, and automation review states, "
            "plus author-versus-merger identity; the pending-review-request subcase is resolved."
        ),
        "last_reviewed": DATE,
        "resolved_subcases": [
            "A reviewer may be requested while zero formal reviews are submitted; GitHub still linked the merge as a YOLO event."
        ],
        "remaining_subcases": [
            "Submitted COMMENT review", "Submitted REQUEST_CHANGES review", "Submitted APPROVE review",
            "Dismissed review", "Automation-submitted review", "Author and merger are different accounts"
        ]
    })

    row = by_id(records, "CTR-004")
    row.update({
        "positions": [
            "A squash merge can preserve Pair Extraordinaire attribution when the final commit retains an account-linked Co-authored-by trailer.",
            "Rebase, stripped trailers, email mismatch, and later history rewriting can still alter or remove final attribution."
        ],
        "resolution_criteria": (
            "Controlled rebase or fast-forward, stripped-trailer, email-mismatch, and post-merge rewrite tests with final-history inspection; "
            "the squash-preservation subcase is supported by two independent GitHub-linked events."
        ),
        "last_reviewed": DATE,
        "resolved_subcases": [
            "Two independent squash merges retained account-linked trailers in their final commits and are linked by GitHub from Pair Extraordinaire history."
        ],
        "remaining_subcases": [
            "Rebase or fast-forward merge", "Trailer removed during squash", "Email not linked to account",
            "Commit history rewritten after merge", "Exact unit counting across merge methods"
        ]
    })

    row = by_id(records, "CTR-006")
    row.update({
        "positions": [
            "GitHub can retain creator attribution when a milestone repository is currently owned by an organization.",
            "Transfer timing, forks, archival, falling counts, deletion, restoration, and revocation may still affect attribution or persistence."
        ],
        "resolution_criteria": (
            "Dated before-and-after observations for transfer timing, forks, archival, falling counts, deletion or restoration, and award persistence; "
            "the current organization-ownership subcase is supported by two independent GitHub-owned fragments."
        ),
        "last_reviewed": DATE,
        "resolved_subcases": [
            "GitHub currently credits balloob for home-assistant/core and tiangolo for fastapi/fastapi while both repositories are organization-owned."
        ],
        "remaining_subcases": [
            "Transfer timing relative to milestone", "Fork ownership", "Archived repository", "Falling below a milestone",
            "Repository deletion or restoration", "Award or tier revocation"
        ]
    })
    save("data/contradictions.json", value)


def update_claims_and_queue() -> None:
    claims = load("data/claims.json")
    for claim_id in ("CLM-004", "CLM-005", "CLM-006", "CLM-009", "CLM-010"):
        by_id(claims["claims"], claim_id)["last_reviewed"] = DATE
    save("data/claims.json", claims)

    queue = load("data/research-queue.json")
    row = by_id(queue["tasks"], "RSH-002")
    row.update({
        "status": "in-progress",
        "research_question": "Which submitted pull-request review states prevent or permit YOLO after the pending-review-request subcase is excluded?",
        "acceptance_criteria": [
            "Test submitted comment-only, requested-changes, approving, dismissed, and automation review states where repository rules permit.",
            "Separate requested reviewers from submitted review objects.",
            "Record author and merger identity, branch protection, and merge method.",
            "Provide dated results from at least two independent accounts using legitimate substantive changes."
        ]
    })
    row = by_id(queue["tasks"], "RSH-005")
    row.update({
        "status": "in-progress",
        "research_question": "How do transfer timing, forks, archival, falling star counts, deletion, restoration, and revocation affect Starstruck after organization ownership is shown to remain attributable in some cases?",
        "acceptance_criteria": [
            "Use only legitimate repository history and public metadata.",
            "Record ownership state and milestone state before and after a documented transition.",
            "Separate current organization ownership from the exact timing of transfer and award processing.",
            "Document counterexamples, persistence, and revocation without soliciting artificial stars."
        ]
    })
    row = by_id(queue["tasks"], "RSH-009")
    row.update({
        "status": "in-progress",
        "research_question": "Which rebase, fast-forward, email-matching, stripped-trailer, and post-merge rewrite states preserve Pair Extraordinaire attribution after squash preservation is observed?",
        "acceptance_criteria": [
            "Test legitimate rebase or fast-forward and merge-commit cases where repository policy permits.",
            "Record whether the final merged history retains an account-linked Co-authored-by trailer.",
            "Include an email-mismatch or stripped-trailer negative control without misattributing a real person.",
            "Provide dated results from at least two independent accounts and retain failed reproductions."
        ]
    })
    row = by_id(queue["tasks"], "RSH-010")
    row.update({
        "status": "blocked",
        "research_question": "Can the reported 1, 10, 24, and 48 Pair Extraordinaire boundaries be observed with exact qualifying counts rather than inferred from x3 or x4 badge sightings?",
        "acceptance_criteria": [
            "Record qualifying count immediately below, at, and above each proposed boundary.",
            "Confirm final merged history retains the co-author identity used for counting.",
            "Separate base, bronze, silver, and gold transitions and measure processing delay.",
            "Do not manufacture meaningless pull requests or misattribute co-authorship."
        ]
    })
    save("data/research-queue.json", queue)


def update_guides() -> None:
    replace(
        "docs/achievements/yolo.md",
        "- No formal pull-request review should have been submitted before merge.\n- Branch protection, rulesets, and organisation policy may require reviews and prevent this route.\n- Ordinary issue comments and pull-request conversation comments are distinct from submitted reviews, but GitHub does not publish every internal qualification detail.",
        "- No formal pull-request review should have been submitted before merge.\n- A requested reviewer is not itself a submitted review: GitHub links one award event where a reviewer was requested but the reviews endpoint remained empty.\n- Branch protection, rulesets, and organisation policy may require reviews and prevent this route.\n- Ordinary issue comments and pull-request conversation comments are distinct from submitted reviews; submitted COMMENT, REQUEST_CHANGES, APPROVE, dismissed, and automated review states remain under investigation."
    )
    replace(
        "docs/achievements/yolo.md",
        "- Alternate review states and structured merger identity remain unresolved implementation edge cases.",
        "- A pending review request with zero submitted reviews is observed as compatible with the linked award.\n- Submitted review states and structured merger identity remain unresolved implementation edge cases."
    )
    replace(
        "docs/achievements/yolo.md",
        "**19 July 2026.** Scope: GitHub's first-party `Merged without a review` fragment, linked qualifying pull request, current review controls, and unresolved alternate-review and merger-identity edge cases.",
        "**20 July 2026.** Scope: GitHub's first-party `Merged without a review` fragment, its linked pull request with a requested reviewer but zero submitted reviews, and the remaining submitted-review and merger-identity controls."
    )

    replace(
        "achievements/pair-extraordinaire.md",
        "A visible `Co-authored-by:` trailer proves commit attribution, while squash, rebase, email matching and rewritten-history counting remain separate limitations.",
        "A visible `Co-authored-by:` trailer proves commit attribution. Two independent GitHub-linked events now show that squash merging can preserve Pair Extraordinaire attribution when the final commit retains the account-linked trailer. Rebase, stripped-trailer, email-matching, later rewrite, and exact counting behavior remain separate limitations."
    )
    replace(
        "achievements/pair-extraordinaire.md",
        "- **Unknown:** The exact treatment of every private-repository, squash-merge, rebase, rewritten-history, and delayed-processing scenario.",
        "- **Observed:** Two independent squash merges retained account-linked trailers in their final commits and appear in GitHub's Pair Extraordinaire history.\n- **Unknown:** Rebase or fast-forward behavior, stripped trailers, email mismatch, later rewritten history, private repositories, exact unit counting, and delayed processing."
    )
    replace(
        "achievements/pair-extraordinaire.md",
        "- Rewriting or squashing commits can remove or alter the original trailer.",
        "- Squash merging can preserve attribution when the final commit retains the linked trailer, but settings or edits that strip the trailer can still remove it."
    )
    replace(
        "achievements/pair-extraordinaire.md",
        "**19 July 2026** — verified GitHub's first-party Pair Extraordinaire fragment and linked co-author history. The broad trigger is official; numerical tier thresholds and merge-rewrite edge cases remain community-reported or unknown.",
        "**20 July 2026** — verified GitHub's first-party Pair Extraordinaire fragments plus two independent linked squash-merge histories. The broad trigger is official and squash preservation is observed; numerical thresholds and remaining rewrite states stay community-reported or unknown."
    )

    star = ROOT / "docs/achievements/starstruck.md"
    star.write_text("""# Starstruck

## Summary

Starstruck is an active, tiered GitHub profile achievement for creating repositories that reach GitHub's published star milestones.

## Trigger

GitHub's live achievement fragment states that Starstruck recognises an account that **created a repository that has many stars**. GitHub-owned milestone histories also show that creator attribution can remain visible when the linked repository is currently organization-owned.

## Progression and tiers

| Level | Repository stars | Evidence status |
|---|---:|---|
| Base | 16 | Official product fragment |
| Bronze | 128 | Official product fragment |
| Silver | 512 | Official product fragment |
| Gold | 4,096 | Official product fragment |

GitHub's x4 Starstruck detail fragments publish the 16, 128, 512, and 4,096 milestones directly.

## Eligibility conditions

- The repository must be attributed by GitHub to the account that created it.
- Stars must represent ordinary independent GitHub star events.
- Current organization ownership does not necessarily erase creator attribution: GitHub currently credits balloob for `home-assistant/core` and tiangolo for `fastapi/fastapi`.
- The exact timing of a transfer relative to milestone processing is not exposed by those fragments.
- Forks, archival, deletion, restoration, falling counts, and award revocation remain incompletely documented.

## Award timing

Repository star counts update quickly, but profile-achievement processing may lag. A repository can visibly reach a milestone before the badge or tier refreshes.

## Verification

1. Open the GitHub-owned Starstruck detail fragment for the account.
2. Record the repository linked to each published milestone.
3. Confirm the repository's current owner type and visible star count.
4. Preserve the observation date and distinguish current ownership from transfer timing.
5. Recheck after processing delay when studying a new milestone or ownership transition.

## Evidence status

- **Official:** GitHub's product fragment states the creator-based trigger.
- **Official:** The milestones are 16, 128, 512, and 4,096 stars.
- **Observed from GitHub-owned fragments:** Creator attribution can persist for repositories currently owned by organizations.
- **Unknown:** Exact transfer timing, fork treatment, archival, falling counts, deletion, restoration, and award or tier revocation.

## Known limitations and edge cases

- A current organization-owned link proves persistence in that observed state, not the exact date or mechanism of transfer.
- Star counts can decrease when users remove stars or accounts are removed.
- A screenshot captures only a point-in-time count.
- Repository transfer, visibility changes, deletion, restoration, or archival can complicate later verification.
- GitHub does not publish a complete revocation contract for falling below a milestone.

## Troubleshooting

- Inspect the GitHub-owned achievement history rather than assuming current repository ownership is the only attribution rule.
- Confirm the visible milestone and linked repository.
- Allow time for profile processing.
- Record ownership transitions with dates where available.
- Treat fork, archive, deletion, restoration, falling-count, and revocation behavior as unresolved without reproducible evidence.

## Responsible participation

Build useful software or documentation, explain it clearly, and share it with relevant communities. Stars should reflect independent interest rather than coordinated activity created solely to alter an achievement count.

## History

Starstruck was introduced with GitHub profile achievements. GitHub's live x4 fragments now expose the complete milestone sequence and provide first-party creator-attribution examples across personal and organization-owned repositories.

## References

- [Saving repositories with stars](https://docs.github.com/en/get-started/exploring-projects-on-github/saving-repositories-with-stars)
- [GitHub profile reference](https://docs.github.com/en/account-and-profile/reference/profile-reference)
- [Event-linked evidence]({{ site.baseurl }}/event-linked-evidence/)
- [Official achievement fragment corpus]({{ site.baseurl }}/official-achievement-fragments/)

## Last verified

**20 July 2026.** Scope: first-party trigger and milestone fragments, current organization-owned creator-attribution examples, and the remaining transfer-timing, fork, archival, falling-count, deletion, restoration, and revocation edge cases.

[Back to the achievement index]({{ site.baseurl }}/docs/achievement-index.html)
""", encoding="utf-8")


def update_changelog() -> None:
    replace(
        "CHANGELOG.md",
        "## Unreleased\n",
        "## Unreleased\n\n### Changed\n\n- Narrowed the remaining YOLO, Pair Extraordinaire, and Starstruck contradiction backlog with five privacy-safe GitHub-owned event records.\n- Distinguished requested reviewers from submitted reviews for YOLO.\n- Confirmed two independent squash-merge attribution-preservation cases for Pair Extraordinaire while retaining exact tier thresholds as community-reported.\n- Confirmed creator attribution on two currently organization-owned Starstruck repositories while retaining transfer-timing and persistence limitations.\n- Re-scoped the remaining research tasks to the unresolved formal-review, rebase, exact-boundary, transfer-timing, fork, archival, falling-count, and revocation controls.\n"
    )


def main() -> int:
    update_programme()
    update_contradictions()
    update_claims_and_queue()
    update_guides()
    update_changelog()
    print("Applied evidence backlog reconciliation without promoting unresolved numeric claims.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
