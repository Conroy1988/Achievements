from __future__ import annotations

from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-07-19"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path: str, value: dict) -> None:
    (ROOT / path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"{path}: replacement anchor not found: {old[:80]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def append_unique(values: list[str], additions: list[str]) -> list[str]:
    return list(dict.fromkeys([*values, *additions]))


def update_claims() -> None:
    payload = load("data/claims.json")
    statements = {
        "CLM-003": "Closing an issue or pull request very shortly after creation can award Quickdraw.",
        "CLM-004": "A pull request authored by the account and merged without a submitted formal review can award YOLO.",
        "CLM-005": "A correctly attributed co-authored commit incorporated into a merged pull request can qualify for Pair Extraordinaire.",
    }
    for claim in payload["claims"]:
        if claim["id"] in statements:
            claim["statement"] = statements[claim["id"]]
            claim["evidence_level"] = "observed"
            claim["status"] = "maintained-with-limitations"
            claim["last_reviewed"] = DATE
    save("data/claims.json", payload)


def update_achievements() -> None:
    payload = load("data/achievements.json")
    triggers = {
        "quickdraw": "Closing an issue or pull request very shortly after creation can award Quickdraw.",
        "yolo": "A pull request authored by the account and merged without a submitted formal review can award YOLO.",
        "pair-extraordinaire": "A correctly attributed co-authored commit incorporated into a merged pull request can qualify for Pair Extraordinaire.",
    }
    for item in payload["achievements"]:
        slug = item["slug"]
        if slug in triggers:
            item["trigger"] = triggers[slug]
            item["evidence"]["trigger"] = "observed"
            item["last_verified"] = DATE
    save("data/achievements.json", payload)


def update_evidence_register() -> None:
    payload = load("data/evidence-register.json")
    by_id = {row["id"]: row for row in payload["records"]}
    quick = by_id["EVD-2026-002"]
    quick.update({
        "claim": "Closing an issue or pull request very shortly after creation can award Quickdraw.",
        "evidence_level": "observed",
        "observed_at": DATE,
        "submitted_at": DATE,
        "reproduction_status": "two-independent-public-reconstructions",
        "reviewer_decision": "accepted-with-limitations",
        "notes": "Two independent public pull requests were merged within five and nine seconds and both accounts publicly display Quickdraw. The exact maximum interval and direct contributing-event link remain unresolved."
    })
    quick["source_urls"] = append_unique(quick.get("source_urls", []), [
        "https://github.com/Schweinepriester/Fira/pull/1",
        "https://github.com/Schweinepriester?achievement=quickdraw&tab=achievements",
        "https://github.com/tronicapp/tronic-track/pull/1",
        "https://github.com/kmcclosk?achievement=quickdraw&tab=achievements"
    ])
    yolo = by_id["EVD-2026-003"]
    yolo.update({
        "claim": "A pull request authored by the account and merged without a submitted formal review can award YOLO.",
        "evidence_level": "observed",
        "observed_at": DATE,
        "submitted_at": DATE,
        "reproduction_status": "two-independent-public-reconstructions",
        "reviewer_decision": "accepted-with-limitations",
        "notes": "Two independent authored pull requests were merged with zero submitted formal reviews and both accounts publicly display YOLO. Merger identity and alternate review-state controls remain unresolved."
    })
    yolo["source_urls"] = append_unique(yolo.get("source_urls", []), [
        "https://github.com/Schweinepriester/Fira/pull/1",
        "https://github.com/Schweinepriester?achievement=yolo&tab=achievements",
        "https://github.com/tronicapp/tronic-track/pull/1",
        "https://github.com/kmcclosk?achievement=yolo&tab=achievements"
    ])
    pair = by_id["EVD-2026-004"]
    pair.update({
        "claim": "A correctly attributed co-authored commit incorporated into a merged pull request can qualify for Pair Extraordinaire.",
        "evidence_level": "observed",
        "observed_at": DATE,
        "submitted_at": DATE,
        "reproduction_status": "two-independent-public-reconstructions",
        "reviewer_decision": "accepted-with-limitations",
        "notes": "Two independent public accounts have account-linked co-author attribution preserved in merged pull-request history and publicly display Pair Extraordinaire. Exact counts and rewrite edge cases remain unresolved."
    })
    pair["source_urls"] = append_unique(pair.get("source_urls", []), [
        "https://github.com/devflash101/POC/pull/11",
        "https://github.com/devflash101/POC/commit/113d443b2e745314c68f33db8d7e6518d14a4d2f",
        "https://github.com/Rongronggg9?achievement=pair-extraordinaire&tab=achievements",
        "https://github.com/Fyrd/caniuse/pull/7466",
        "https://github.com/Fyrd/caniuse/commit/188bc05673b7c6bf83077982cbed0c2ec15df532",
        "https://github.com/Schweinepriester?achievement=pair-extraordinaire&tab=achievements"
    ])
    save("data/evidence-register.json", payload)


def reconstruction_events() -> list[dict]:
    return [
        {
            "id": "EVT-2026-006", "achievement_slug": "quickdraw", "claim_ids": ["CLM-003"],
            "event_type": "pull-request-close-and-merge", "event_url": "https://github.com/Schweinepriester/Fira/pull/1",
            "subject_login": "Schweinepriester", "created_at": "2016-01-26T12:41:15Z", "completed_at": "2016-01-26T12:41:20Z", "elapsed_seconds": 5,
            "public_facts": ["The pull request was authored by Schweinepriester and merged into master five seconds after creation.", "The pull request has no submitted formal reviews and the account publicly displays Quickdraw."],
            "award_link": "public-profile-visible-no-contributing-fragment", "adjudication_status": "accepted", "independent_account_count": 2,
            "limitations": ["The anonymous achievement fragment does not expose the contributing event.", "The event does not establish the maximum qualifying interval."]
        },
        {
            "id": "EVT-2026-007", "achievement_slug": "quickdraw", "claim_ids": ["CLM-003"],
            "event_type": "pull-request-close-and-merge", "event_url": "https://github.com/tronicapp/tronic-track/pull/1",
            "subject_login": "kmcclosk", "created_at": "2023-11-17T14:09:59Z", "completed_at": "2023-11-17T14:10:08Z", "elapsed_seconds": 9,
            "public_facts": ["The pull request was authored by kmcclosk and merged into main nine seconds after creation.", "The pull request has no submitted formal reviews and the account publicly displays Quickdraw."],
            "award_link": "public-profile-visible-no-contributing-fragment", "adjudication_status": "accepted", "independent_account_count": 2,
            "limitations": ["The anonymous achievement fragment does not expose the contributing event.", "The event does not establish issue equivalence or the maximum interval."]
        },
        {
            "id": "EVT-2026-008", "achievement_slug": "yolo", "claim_ids": ["CLM-004"],
            "event_type": "pull-request-merge-without-formal-review", "event_url": "https://github.com/Schweinepriester/Fira/pull/1",
            "subject_login": "Schweinepriester", "created_at": "2016-01-26T12:41:15Z", "completed_at": "2016-01-26T12:41:20Z", "elapsed_seconds": 5,
            "public_facts": ["The account authored the merged pull request and no formal review was submitted.", "The account publicly displays YOLO."],
            "award_link": "public-profile-visible-no-contributing-fragment", "adjudication_status": "accepted", "independent_account_count": 2,
            "limitations": ["The normalized pull-request record does not expose the merging actor.", "Comment-only, changes-requested, dismissed, and approved states are not tested."]
        },
        {
            "id": "EVT-2026-009", "achievement_slug": "yolo", "claim_ids": ["CLM-004"],
            "event_type": "pull-request-merge-without-formal-review", "event_url": "https://github.com/tronicapp/tronic-track/pull/1",
            "subject_login": "kmcclosk", "created_at": "2023-11-17T14:09:59Z", "completed_at": "2023-11-17T14:10:08Z", "elapsed_seconds": 9,
            "public_facts": ["The account authored the merged pull request and no formal review was submitted.", "The account publicly displays YOLO."],
            "award_link": "public-profile-visible-no-contributing-fragment", "adjudication_status": "accepted", "independent_account_count": 2,
            "limitations": ["The normalized pull-request record does not expose the merging actor.", "Alternate formal review states are not tested."]
        },
        {
            "id": "EVT-2026-010", "achievement_slug": "pair-extraordinaire", "claim_ids": ["CLM-005"],
            "event_type": "coauthored-commit-in-merged-pull-request", "event_url": "https://github.com/devflash101/POC/pull/11",
            "subject_login": "Rongronggg9", "created_at": "2025-11-26T18:41:38Z", "completed_at": "2025-11-26T18:41:59Z", "elapsed_seconds": 21,
            "public_facts": ["The pull request merged into main and retained an account-linked Rongronggg9 co-author trailer in its one-commit history.", "Rongronggg9 publicly displays Pair Extraordinaire x4."],
            "award_link": "public-profile-visible-no-contributing-fragment", "adjudication_status": "accepted", "independent_account_count": 2,
            "limitations": ["The exact attributed qualifying count is not public.", "The merge-commit example does not establish squash or rebase behaviour."]
        },
        {
            "id": "EVT-2026-011", "achievement_slug": "pair-extraordinaire", "claim_ids": ["CLM-005"],
            "event_type": "coauthored-final-merge-commit", "event_url": "https://github.com/Fyrd/caniuse/pull/7466",
            "subject_login": "Schweinepriester", "created_at": "2026-01-31T02:01:50Z", "completed_at": "2026-02-06T06:16:48Z", "elapsed_seconds": 447898,
            "public_facts": ["The pull request merged into main and the final merge commit contains an account-linked Schweinepriester co-author trailer.", "Schweinepriester publicly displays Pair Extraordinaire x3."],
            "award_link": "public-profile-visible-no-contributing-fragment", "adjudication_status": "accepted", "independent_account_count": 2,
            "limitations": ["The exact attributed qualifying count is not public.", "The example does not resolve every squash, rebase, email-matching, or history-rewrite case."]
        }
    ]


def update_programme_before_coverage() -> None:
    payload = load("data/evidence-quality-programme.json")
    event_ids = {row["id"] for row in payload["event_evidence"]}
    for row in reconstruction_events():
        if row["id"] not in event_ids:
            payload["event_evidence"].append(row)
    decisions = {row["id"]: row for row in payload["adjudication_decisions"]}
    for did, cid, reason in [
        ("ADJ-D001", "CLM-003", "Two independent public reconstructions support the broad rapid-close association at observed level; controlled boundary reproduction and measured award timing are still required for confirmed status."),
        ("ADJ-D002", "CLM-004", "Two independent authored and unreviewed merged pull requests support the broad YOLO association at observed level; merger identity and alternate review-state controls remain unresolved."),
    ]:
        row = decisions[did]
        row.update({"claim_id": cid, "decision": "defer", "current_level": "observed", "proposed_level": "confirmed", "reason": reason})
    if "ADJ-D007" not in decisions:
        payload["adjudication_decisions"].append({
            "id": "ADJ-D007", "claim_id": "CLM-005", "decision": "defer", "current_level": "observed", "proposed_level": "confirmed",
            "reason": "Two independent account-linked co-author reconstructions support the broad merged-pull-request association at observed level; controlled merge-method and rewrite tests remain required for confirmed status."
        })
    for assessment in payload["contradiction_assessments"]:
        cid = assessment["contradiction_id"]
        if cid == "CTR-001":
            assessment["outcome"] = "narrowed"
            assessment["basis_ids"] = list(dict.fromkeys([*assessment["basis_ids"], "EVT-2026-006", "EVT-2026-007"]))
            assessment["remaining_question"] = "What is the maximum qualifying interval, do issue and pull-request closure behave identically, and when does the award first become visible?"
        elif cid == "CTR-002":
            assessment["outcome"] = "narrowed"
            assessment["basis_ids"] = list(dict.fromkeys([*assessment["basis_ids"], "EVT-2026-008", "EVT-2026-009"]))
            assessment["remaining_question"] = "Do comment-only, changes-requested, dismissed, or approved review objects prevent the award, and must the author also be the merger?"
        elif cid == "CTR-004":
            assessment["outcome"] = "narrowed"
            assessment["basis_ids"] = list(dict.fromkeys([*assessment["basis_ids"], "EVT-2026-010", "EVT-2026-011"]))
            assessment["remaining_question"] = "How squash, rebase, email mismatch, and rewritten history affect final achievement attribution and exact tier counts."
    save("data/evidence-quality-programme.json", payload)


def update_guides() -> None:
    replace_once("docs/quickdraw.md",
        "The reported qualifying event is opening an issue or pull request and closing it within a short interval. GitHub does not publish the precise timing window in its general profile documentation.",
        "Two independent public reconstructions associate Quickdraw with pull requests merged five and nine seconds after creation. This supports the broad rapid-close trigger at observed level, while GitHub still does not publish the precise maximum timing window in its general profile documentation.")
    replace_once("docs/quickdraw.md",
        "- The association with a rapid close is strongly observed.\n- The exact timing window remains community-reported or unknown.",
        "- Two independent public event/profile pairs support the rapid-close association at observed level.\n- The exact maximum timing window, issue equivalence, and first-visible award delay remain community-reported or unknown.")
    replace_once("docs/quickdraw.md",
        "- [GitHub profile reference](https://docs.github.com/en/account-and-profile/reference/profile-reference)",
        "- [GitHub profile reference](https://docs.github.com/en/account-and-profile/reference/profile-reference)\n- [Public reconstruction corpus]({{ site.baseurl }}/public-reconstruction-corpus/)")
    replace_once("docs/quickdraw.md",
        "**19 July 2026.** Scope: current issue and pull-request closure controls, profile-achievement presentation, and uncertainty around the reported timing window.",
        "**19 July 2026.** Scope: two independent public rapid-close reconstructions, current issue and pull-request closure controls, profile-achievement presentation, and the unresolved maximum timing window.")

    replace_once("docs/achievements/yolo.md",
        "The observed qualifying event is a pull request merged without an approval, requested-changes review, or comment review being submitted through GitHub's pull-request review system.",
        "Two independent public reconstructions associate YOLO with pull requests authored by the awarded account and merged with no submitted formal review. This supports the broad unreviewed-merge trigger at observed level; merger identity and alternate formal review states remain unresolved.")
    replace_once("docs/achievements/yolo.md",
        "- The unreviewed-merge association is strongly observed.\n- GitHub does not publish a complete eligibility specification for the badge.",
        "- Two independent public event/profile pairs support the authored, unreviewed-merge association at observed level.\n- GitHub does not publish a complete eligibility specification, and the public records do not expose merger identity or every alternate review state.")
    replace_once("docs/achievements/yolo.md",
        "- [GitHub profile reference](https://docs.github.com/en/account-and-profile/reference/profile-reference)",
        "- [GitHub profile reference](https://docs.github.com/en/account-and-profile/reference/profile-reference)\n- [Public reconstruction corpus]({{ site.baseurl }}/public-reconstruction-corpus/)")
    replace_once("docs/achievements/yolo.md",
        "**19 July 2026.** Scope: current merge, review, and protection controls; profile-achievement presentation; and the evidence status of the unreviewed-merge trigger.",
        "**19 July 2026.** Scope: two independent public authored/unreviewed merge reconstructions, current review and protection controls, profile-achievement presentation, and unresolved merger-identity and alternate-review semantics.")

    replace_once("achievements/pair-extraordinaire.md",
        "**Evidence status:** GitHub officially documents co-authored commits and contribution attribution. The achievement trigger and tier thresholds remain community-reported because GitHub does not publish a complete Pair Extraordinaire specification.",
        "**Evidence status:** GitHub officially documents co-authored commits and contribution attribution. Two independent public merged-pull-request reconstructions support the broad achievement trigger at observed level; tier thresholds and rewrite edge cases remain community-reported.")
    replace_once("achievements/pair-extraordinaire.md",
        "The community-observed trigger is participation as a correctly attributed co-author on a commit that becomes part of a merged pull request.",
        "The observed broad trigger is participation as a correctly attributed co-author on a commit that becomes part of a merged pull request.")
    replace_once("achievements/pair-extraordinaire.md",
        "- **Community-reported:** Pair Extraordinaire is linked to co-authored commits contained in merged pull requests.",
        "- **Observed:** Two independent public accounts have account-linked co-author attribution preserved in merged pull-request history and publicly display Pair Extraordinaire.")
    replace_once("achievements/pair-extraordinaire.md",
        "- [GitHub achievement index]({{ site.baseurl }}/docs/achievement-index.html)",
        "- [GitHub achievement index]({{ site.baseurl }}/docs/achievement-index.html)\n- [Public reconstruction corpus]({{ site.baseurl }}/public-reconstruction-corpus/)")
    replace_once("achievements/pair-extraordinaire.md",
        "**19 July 2026** — verified the current GitHub documentation for co-authored commit syntax, account-associated email requirements, no-reply addresses, visible attribution, and profile contribution behaviour. The achievement trigger and tier thresholds remain classified as community-reported.",
        "**19 July 2026** — verified two independent public merged-pull-request/co-author reconstructions plus current GitHub documentation for trailer syntax and account-linked attribution. The broad trigger is observed; tier thresholds and merge-rewrite edge cases remain community-reported or unknown.")


def update_public_surfaces() -> None:
    replace_once("scripts/build_public_api.py",
        '    "public_observations": Path("public-observations.json"),',
        '    "public_observations": Path("public-observations.json"),\n    "public_reconstructions": Path("public-reconstructions.json"),')
    replace_once("scripts/build_public_api.py",
        '    "public_observations": "observations",',
        '    "public_observations": "observations",\n    "public_reconstructions": "records",')
    replace_once("scripts/build_public_api.py",
        '            "public_observations",\n            "event_linked_evidence",',
        '            "public_observations",\n            "public_reconstructions",\n            "event_linked_evidence",')

    replace_once("docs/api-reference.md",
        '| [`public-observations.json`](../api/public-observations.json) | Dated GitHub-owned profile, tier, and repository observations with explicit limitations |',
        '| [`public-observations.json`](../api/public-observations.json) | Dated GitHub-owned profile, tier, and repository observations with explicit limitations |\n| [`public-reconstructions.json`](../api/public-reconstructions.json) | Exact public event/profile pairs used to support broad trigger associations without overstating causality |')
    replace_once("docs/api-reference.md",
        'The discovery index now exposes **38 public JSON files**:',
        'The discovery index now exposes **39 public JSON files**:')
    replace_once("docs/api-reference.md",
        'python scripts/build_public_observations.py',
        'python scripts/build_public_observations.py\npython scripts/build_public_reconstructions.py')
    replace_once("docs/api-reference.md",
        '- [Public observation corpus](public-observation-corpus.md)',
        '- [Public observation corpus](public-observation-corpus.md)\n- [Public reconstruction corpus](public-reconstruction-corpus.md)')

    replace_once("site-map.md",
        '- [Public observation corpus](docs/public-observation-corpus.md)',
        '- [Public observation corpus](docs/public-observation-corpus.md)\n- [Public reconstruction corpus](docs/public-reconstruction-corpus.md)')
    replace_once("site-map.md",
        '- [Public observations](api/public-observations.json)',
        '- [Public observations](api/public-observations.json)\n- [Public reconstructions](api/public-reconstructions.json)')
    replace_once("research-command-centre.md",
        'The [mission evidence promotion planner](docs/promotion-planner.md) converts only accepted promotion proposals into isolated canonical-change previews with impact and rollback instructions; it never applies them.',
        'The [mission evidence promotion planner](docs/promotion-planner.md) converts only accepted promotion proposals into isolated canonical-change previews with impact and rollback instructions; it never applies them.\n\nThe [public reconstruction corpus](docs/public-reconstruction-corpus.md) preserves exact independent event/profile pairs that strengthen broad triggers while leaving causal, timing, threshold, and edge-case limitations explicit.')

    resources = load("data/search-resources.json")
    if not any(row["slug"] == "public-reconstruction-corpus" for row in resources["resources"]):
        resources["resources"].append({
            "slug": "public-reconstruction-corpus",
            "name": "Public reconstruction corpus",
            "category": "research",
            "summary": "Independent public event/profile pairs for Quickdraw, YOLO, and Pair Extraordinaire with explicit causal and boundary limitations.",
            "permalink": "/public-reconstruction-corpus/",
            "aliases": ["retrospective evidence", "public event reconstruction", "independent trigger observations"]
        })
    save("data/search-resources.json", resources)
    replace_once("scripts/test_search_page.mjs",
        "  const liveRegion = await page.locator('#search-count').getAttribute('aria-live');",
        "  await page.locator('#search-query').fill('public event reconstruction');\n  await expectCount(page, 1, 'public reconstruction query');\n  const reconstructionHref = await page.locator('[data-result-slug=\"public-reconstruction-corpus\"] h3 a').getAttribute('href');\n  assert.equal(reconstructionHref, '/Achievements/public-reconstruction-corpus/');\n\n  const liveRegion = await page.locator('#search-count').getAttribute('aria-live');")

    replace_once("CHANGELOG.md",
        '- Dedicated mission packet review workflow and public queue/schema endpoints.',
        '- Dedicated mission packet review workflow and public queue/schema endpoints.\n- Six-record public reconstruction corpus linking exact public pull-request, review, co-author, and profile state across three independent achievement triggers.\n- Dedicated reconstruction validator, API endpoint, public guide, search route, and drift-controlled workflow.')
    replace_once("CHANGELOG.md",
        '- Public API discovery expanded from 26 to 38 JSON files.',
        '- Public API discovery expanded from 26 to 39 JSON files.')
    replace_once("CHANGELOG.md",
        '- Promotion proposals now require two reviewers, one unconflicted reviewer, the applicable adjudication rule, the published mission target, and a fully passing checklist.',
        '- Promotion proposals now require two reviewers, one unconflicted reviewer, the applicable adjudication rule, the published mission target, and a fully passing checklist.\n- Quickdraw, YOLO, and Pair Extraordinaire broad trigger claims advanced from community-reported to observed using two independent public reconstructions per claim; exact timing, alternate review states, attribution rewrites, and all tier thresholds remain unresolved.')
    replace_once("CHANGELOG.md",
        '- No canonical claim level changed during Phases 52–61.',
        '- Three broad trigger claims changed from community-reported to observed in Phase 62; no claim was promoted to confirmed or official.')
    replace_once("CHANGELOG.md",
        '- Evidence coverage remains 54.6/100.',
        '- Evidence coverage increases from 54.6 to 60.4 without changing weights or closing a contradiction.')


def run(*args: str) -> None:
    print("+", *args)
    subprocess.run(args, cwd=ROOT, check=True)


def update_release_snapshot() -> None:
    coverage = load("api/coverage.json")
    contradictions = load("data/contradictions.json")
    programme = load("data/evidence-quality-programme.json")
    snapshot = programme["release_gate"]["current_snapshot"]
    snapshot.update({
        "coverage_score": coverage["overall_coverage_score"],
        "official_or_confirmed_claims": sum(row["evidence_level"] in {"official", "confirmed"} for row in coverage["claims"]),
        "claims_below_confirmed": sum(row["evidence_level"] not in {"official", "confirmed"} for row in coverage["claims"]),
        "open_contradictions": sum(row["status"] == "open" for row in contradictions["records"]),
    })
    required = programme["release_gate"]["required_snapshot"]
    programme["release_gate"]["status"] = "ready" if (
        snapshot["coverage_score"] >= required["minimum_coverage_score"]
        and snapshot["official_or_confirmed_claims"] >= required["minimum_official_or_confirmed_claims"]
        and snapshot["claims_below_confirmed"] <= required["maximum_claims_below_confirmed"]
        and snapshot["open_contradictions"] <= required["maximum_open_contradictions"]
    ) else "blocked"
    save("data/evidence-quality-programme.json", programme)


def reconcile_mission_pressure() -> None:
    intelligence = load("api/evidence-intelligence.json")
    pressure = {row["achievement_slug"]: row["pressure_score"] for row in intelligence["achievements"]}
    missions = load("data/acquisition-missions.json")
    achievement_rows = [row for row in missions["missions"] if row.get("achievement_slug") is not None]
    cross_rows = [row for row in missions["missions"] if row.get("achievement_slug") is None]
    for row in achievement_rows:
        row["pressure_score"] = pressure[row["achievement_slug"]]
    achievement_rows.sort(key=lambda row: (-row["pressure_score"], row["achievement_slug"]))
    ordered = [*achievement_rows, *cross_rows]
    for rank, row in enumerate(ordered, 1):
        row["rank"] = rank
    missions["missions"] = ordered
    save("data/acquisition-missions.json", missions)


def main() -> None:
    update_claims()
    update_achievements()
    update_evidence_register()
    update_programme_before_coverage()
    update_guides()
    update_public_surfaces()

    run("python", "scripts/build_public_reconstructions.py")
    run("python", "scripts/build_evidence_register.py")
    run("python", "scripts/build_research_intelligence.py")
    update_release_snapshot()
    run("python", "scripts/build_evidence_quality_programme.py")
    run("python", "scripts/build_evidence_intelligence.py")
    reconcile_mission_pressure()
    run("python", "scripts/build_acquisition_missions.py")
    run("python", "scripts/build_mission_intake.py")
    run("python", "scripts/build_mission_review_queue.py")
    run("python", "scripts/build_promotion_plans.py")
    run("python", "scripts/build_evidence_operations.py")
    run("python", "scripts/build_public_api.py")

    coverage = load("api/coverage.json")
    assert coverage["overall_coverage_score"] == 60.4, coverage["overall_coverage_score"]
    readiness = load("api/release-readiness.json")
    assert readiness["status"] == "blocked"
    assert readiness["current_snapshot"]["official_or_confirmed_claims"] == 5
    assert readiness["current_snapshot"]["claims_below_confirmed"] == 8
    assert readiness["current_snapshot"]["open_contradictions"] == 6
    print("Phase 62 reconciliation complete: coverage 60.4, release remains blocked.")


if __name__ == "__main__":
    main()
