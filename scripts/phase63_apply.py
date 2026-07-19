from __future__ import annotations

from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-07-19"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path: str, value: dict, compact: bool = False) -> None:
    text = json.dumps(value, separators=(",", ":") if compact else None, indent=None if compact else 2, ensure_ascii=False) + "\n"
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"{path}: missing replacement anchor {old[:100]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def add_url(values: list[str], value: str) -> list[str]:
    return list(dict.fromkeys([*values, value]))


def update_claims() -> None:
    payload = load("data/claims.json")
    statements = {
        "CLM-001": "Opening pull requests that are merged can award Pull Shark.",
        "CLM-002": "Pull Shark milestones are the 2nd, 16th, 128th, and 1024th merged pull requests.",
        "CLM-003": "Closing a qualifying pull request within five minutes of opening can award Quickdraw.",
        "CLM-004": "Merging a pull request without a review can award YOLO.",
        "CLM-005": "Coauthored commits on merged pull requests can award Pair Extraordinaire.",
        "CLM-007": "Accepted answers in GitHub Discussions can award Galaxy Brain.",
        "CLM-008": "Galaxy Brain milestones are the 2nd, 8th, 16th, and 32nd accepted answers.",
        "CLM-009": "Creating a repository that reaches GitHub's published star milestones can award Starstruck.",
        "CLM-010": "Starstruck milestones are 16, 128, 512, and 4096 repository stars.",
    }
    for claim in payload["claims"]:
        if claim["id"] in statements:
            claim["statement"] = statements[claim["id"]]
            claim["evidence_level"] = "official"
            claim["status"] = "maintained-with-limitations"
            claim["last_reviewed"] = DATE
    save("data/claims.json", payload)


def update_achievements() -> None:
    payload = load("data/achievements.json")
    fragment_urls = {
        "pull-shark": "https://github.com/users/ljharb/achievements/pull-shark/detail?hovercard=1",
        "quickdraw": "https://github.com/users/Schweinepriester/achievements/quickdraw/detail?hovercard=1",
        "yolo": "https://github.com/users/Schweinepriester/achievements/yolo/detail?hovercard=1",
        "pair-extraordinaire": "https://github.com/users/Schweinepriester/achievements/pair-extraordinaire/detail?hovercard=1",
        "galaxy-brain": "https://github.com/users/ljharb/achievements/galaxy-brain/detail?hovercard=1",
        "starstruck": "https://github.com/users/Schweinepriester/achievements/starstruck/detail?hovercard=1",
    }
    triggers = {
        "pull-shark": "Opening pull requests that are merged can award Pull Shark.",
        "quickdraw": "Close a qualifying pull request within five minutes of opening.",
        "yolo": "Merge a pull request without a review.",
        "pair-extraordinaire": "Participate in coauthored commits on merged pull requests.",
        "galaxy-brain": "Have answers in GitHub Discussions accepted.",
        "starstruck": "Create a repository that reaches GitHub's published star milestones.",
    }
    tier_official = {"pull-shark", "galaxy-brain", "starstruck"}
    for item in payload["achievements"]:
        slug = item["slug"]
        if slug not in fragment_urls:
            continue
        item["trigger"] = triggers[slug]
        item["evidence"]["trigger"] = "official"
        if slug in tier_official:
            item["evidence"]["tiers"] = "official"
        item["last_verified"] = DATE
        item.setdefault("sources", {}).setdefault("official", [])
        item["sources"]["official"] = add_url(item["sources"]["official"], fragment_urls[slug])
    save("data/achievements.json", payload)


def update_evidence() -> None:
    payload = load("data/evidence-register.json")
    updates = {
        "EVD-2026-001": ("Pull Shark", "https://github.com/users/ljharb/achievements/pull-shark/detail?hovercard=1", "GitHub's live x4 detail fragment states the merged-pull-request trigger and the 2nd, 16th, 128th, and 1024th milestones."),
        "EVD-2026-002": ("Quickdraw", "https://github.com/users/Schweinepriester/achievements/quickdraw/detail?hovercard=1", "GitHub's live detail fragment links a qualifying pull request and states that it was closed within five minutes of opening."),
        "EVD-2026-003": ("YOLO", "https://github.com/users/Schweinepriester/achievements/yolo/detail?hovercard=1", "GitHub's live detail fragment links a qualifying pull request and states that it was merged without a review."),
        "EVD-2026-004": ("Pair Extraordinaire", "https://github.com/users/Schweinepriester/achievements/pair-extraordinaire/detail?hovercard=1", "GitHub's live detail fragment states that Pair Extraordinaire recognises coauthored commits on merged pull requests; numerical tier counts remain unpublished."),
        "EVD-2026-005": ("Galaxy Brain", "https://github.com/users/ljharb/achievements/galaxy-brain/detail?hovercard=1", "GitHub's live x4 detail fragment publishes accepted-answer milestones at 2, 8, 16, and 32."),
        "EVD-2026-006": ("Starstruck", "https://github.com/users/Schweinepriester/achievements/starstruck/detail?hovercard=1", "GitHub's live x4 detail fragment states the repository-creation trigger and star milestones at 16, 128, 512, and 4096."),
    }
    for record in payload["records"]:
        if record["id"] not in updates:
            continue
        name, url, notes = updates[record["id"]]
        record["claim"] = f"GitHub's live product fragment explicitly documents the material {name} contract."
        record["evidence_level"] = "official"
        record["observed_at"] = DATE
        record["submitted_at"] = DATE
        record["reproduction_status"] = "github-owned-live-product-fragment"
        record["reviewer_decision"] = "accepted-with-limitations"
        record["notes"] = notes
        record["source_urls"] = add_url(record.get("source_urls", []), url)
    save("data/evidence-register.json", payload)


def update_contradictions() -> None:
    payload = load("data/contradictions.json")
    resolutions = {
        "CTR-001": ("GAF-2026-001", "GitHub's live Quickdraw detail fragment explicitly states 'Closed within 5 minutes of opening' and links the qualifying pull request."),
        "CTR-003": ("GAF-2026-004", "GitHub's live Pull Shark x4 detail fragment publishes the 2nd, 16th, 128th, and 1024th merged-pull-request milestones."),
        "CTR-005": ("GAF-2026-005", "GitHub's live Galaxy Brain x4 detail fragment publishes the 2nd, 8th, 16th, and 32nd accepted-answer milestones."),
    }
    for row in payload["records"]:
        if row["id"] not in resolutions:
            continue
        basis, summary = resolutions[row["id"]]
        row["status"] = "resolved"
        row["resolved_at"] = DATE
        row["resolution_basis_ids"] = [basis]
        row["resolution_summary"] = summary
    save("data/contradictions.json", payload)


def update_research_queue() -> None:
    payload = load("data/research-queue.json")
    for row in payload["tasks"]:
        if row["id"] in {"RSH-001", "RSH-003", "RSH-004"}:
            row["status"] = "resolved"
    save("data/research-queue.json", payload)


def update_programme() -> None:
    payload = load("data/evidence-quality-programme.json")
    for phase in payload["phases"]:
        if phase["number"] == 56:
            phase["status"] = "implemented-release-ready"
    decision_levels = {
        "ADJ-D001": ("official", "official", "GitHub's live Quickdraw fragment now states the five-minute contract. Further work is limited to issue equivalence and processing-delay edge cases."),
        "ADJ-D002": ("official", "official", "GitHub's live YOLO fragment states 'Merged without a review'. Alternate review-state and merger-identity edge cases remain separate research."),
        "ADJ-D003": ("official", "official", "GitHub's live Pull Shark x4 fragment publishes the complete merged-pull-request milestone table."),
        "ADJ-D005": ("official", "official", "GitHub's live Galaxy Brain x4 fragment publishes the complete accepted-answer milestone table."),
        "ADJ-D006": ("official", "official", "GitHub's live Starstruck x4 fragment publishes the complete star milestone table; ownership-transfer persistence remains open."),
        "ADJ-D007": ("official", "official", "GitHub's live Pair Extraordinaire fragment states the broad coauthored-commit trigger; numerical tiers and merge-rewrite edge cases remain open."),
    }
    for row in payload["adjudication_decisions"]:
        if row["id"] in decision_levels:
            current, proposed, reason = decision_levels[row["id"]]
            row.update({"decision": "defer", "current_level": current, "proposed_level": proposed, "reason": reason})
    assessment_updates = {
        "CTR-001": ("resolved", ["GAF-2026-001"], "Resolved by GitHub's first-party five-minute Quickdraw criterion; issue equivalence and processing delay remain documented limitations outside the timing dispute."),
        "CTR-003": ("resolved", ["GAF-2026-004"], "Resolved by GitHub's first-party x4 Pull Shark milestone history: 2, 16, 128, and 1024 merged pull requests."),
        "CTR-005": ("resolved", ["GAF-2026-005"], "Resolved by GitHub's first-party x4 Galaxy Brain milestone history: 2, 8, 16, and 32 accepted answers."),
        "CTR-006": ("narrowed", ["GAF-2026-006"], "The exact star milestones are resolved; repository transfer, organisation ownership, forks, archival, falling counts, and persistence remain open."),
    }
    for row in payload["contradiction_assessments"]:
        if row["contradiction_id"] not in assessment_updates:
            continue
        outcome, basis, question = assessment_updates[row["contradiction_id"]]
        row["outcome"] = outcome
        row["basis_ids"] = basis
        row["remaining_question"] = question
    for boundary in payload["boundary_programmes"]:
        if boundary["id"] in {"BND-001", "BND-003", "BND-004", "BND-005"}:
            boundary["status"] = "complete"
            boundary["next_evidence"] = "Monitor the GitHub-owned achievement fragment for product-contract drift; no additional threshold search is required."
            boundary.pop("current_bracket", None)
    save("data/evidence-quality-programme.json", payload)


def update_quality_builder() -> None:
    replace_once("scripts/build_evidence_quality_programme.py", 'OBSERVATIONS = ROOT / "data/public-observations.json"\nCOVERAGE = ROOT / "api/coverage.json"', 'OBSERVATIONS = ROOT / "data/public-observations.json"\nFRAGMENTS = ROOT / "data/official-achievement-fragments.json"\nCOVERAGE = ROOT / "api/coverage.json"')
    replace_once("scripts/build_evidence_quality_programme.py", 'def validate(source: dict, claims: dict, contradictions: dict, observations: dict, coverage: dict) -> list[str]:', 'def validate(source: dict, claims: dict, contradictions: dict, observations: dict, fragments: dict, coverage: dict) -> list[str]:')
    replace_once("scripts/build_evidence_quality_programme.py", '    observation_ids = {row["id"] for row in observations.get("observations", [])}', '    observation_ids = {row["id"] for row in observations.get("observations", [])}\n    fragment_ids = {row["id"] for row in fragments.get("records", [])}')
    replace_once("scripts/build_evidence_quality_programme.py", '    if any(row.get("status") not in {"complete", "implemented-release-blocked"} for row in phases):', '    if any(row.get("status") not in {"complete", "implemented-release-blocked", "implemented-release-ready"} for row in phases):')
    replace_once("scripts/build_evidence_quality_programme.py", '    valid_basis = event_ids | boundary_ids', '    valid_basis = event_ids | boundary_ids | fragment_ids')
    replace_once("scripts/build_evidence_quality_programme.py", '        source, claims, contradictions, observations, coverage = map(load, [SOURCE, CLAIMS, CONTRADICTIONS, OBSERVATIONS, COVERAGE])', '        source, claims, contradictions, observations, fragments, coverage = map(load, [SOURCE, CLAIMS, CONTRADICTIONS, OBSERVATIONS, FRAGMENTS, COVERAGE])')
    replace_once("scripts/build_evidence_quality_programme.py", '    errors = validate(source, claims, contradictions, observations, coverage)', '    errors = validate(source, claims, contradictions, observations, fragments, coverage)')
    replace_once("scripts/build_evidence_quality_programme.py", '    lines += ["## Evidence quality release gate", "", f"**Candidate:** `{gate[\'candidate_version\']}`  ", f"**Status:** `{gate[\'status\']}`", "", "The release is intentionally blocked. Phases 52–55 improve the research system and narrow three contradictions, but they do not yet justify any canonical claim promotion or coverage increase.", "", "| Gate | Current | Required | Result |", "|---|---:|---:|---|", f"| Evidence coverage | {current[\'coverage_score\']} | ≥ {required[\'minimum_coverage_score\']} | FAIL |", f"| Official or confirmed claims | {current[\'official_or_confirmed_claims\']} | ≥ {required[\'minimum_official_or_confirmed_claims\']} | FAIL |", f"| Claims below confirmed | {current[\'claims_below_confirmed\']} | ≤ {required[\'maximum_claims_below_confirmed\']} | FAIL |", f"| Open contradictions | {current[\'open_contradictions\']} | ≤ {required[\'maximum_open_contradictions\']} | FAIL |", f"| Operational health | evaluated on merged `main` | {required[\'required_operational_health\']} | PENDING |", "", "## Publication rule", "", gate["publication_rule"], "", "## Machine-readable data", "", "See [`/api/release-readiness.json`](../api/release-readiness.json).", ""]', '    coverage_result = "PASS" if current["coverage_score"] >= required["minimum_coverage_score"] else "FAIL"\n    confirmed_result = "PASS" if current["official_or_confirmed_claims"] >= required["minimum_official_or_confirmed_claims"] else "FAIL"\n    weak_result = "PASS" if current["claims_below_confirmed"] <= required["maximum_claims_below_confirmed"] else "FAIL"\n    contradiction_result = "PASS" if current["open_contradictions"] <= required["maximum_open_contradictions"] else "FAIL"\n    summary = "All evidence gates pass. Publication still requires merged-main operational verification." if gate["status"] == "ready" else "One or more evidence gates remain blocked."\n    lines += ["## Evidence quality release gate", "", f"**Candidate:** `{gate[\'candidate_version\']}`  ", f"**Status:** `{gate[\'status\']}`", "", summary, "", "| Gate | Current | Required | Result |", "|---|---:|---:|---|", f"| Evidence coverage | {current[\'coverage_score\']} | ≥ {required[\'minimum_coverage_score\']} | {coverage_result} |", f"| Official or confirmed claims | {current[\'official_or_confirmed_claims\']} | ≥ {required[\'minimum_official_or_confirmed_claims\']} | {confirmed_result} |", f"| Claims below confirmed | {current[\'claims_below_confirmed\']} | ≤ {required[\'maximum_claims_below_confirmed\']} | {weak_result} |", f"| Open contradictions | {current[\'open_contradictions\']} | ≤ {required[\'maximum_open_contradictions\']} | {contradiction_result} |", f"| Operational health | evaluated on merged `main` | {required[\'required_operational_health\']} | PENDING |", "", "## Publication rule", "", gate["publication_rule"], "", "## Machine-readable data", "", "See [`/api/release-readiness.json`](../api/release-readiness.json).", ""]')
    replace_once("scripts/build_evidence_quality_programme.py", '    lines += ["", "Every current decision is deferred. No canonical claim level or evidence score changes in this programme.", ""]', '    lines += ["", "Decisions record remaining research after maintainer-reviewed canonical reconciliation. Generated observations never change claims automatically.", ""]')
    replace_once("scripts/build_evidence_quality_programme.py", '    lines += ["", "## Remaining questions", ""]', '    lines += ["", "## Assessment details", ""]')
    replace_once("scripts/build_evidence_quality_programme.py", '    print("Evidence quality programme passed: phases 52-56 validated; v1.4.0 remains blocked.")', '    print(f"Evidence quality programme passed: phases 52-56 validated; v1.4.0 is {source[\'release_gate\'][\'status\']}.")')


def rewrite_guides() -> None:
    replacements = {
        "docs/achievements/pull-shark.md": [
            ("The qualifying action is having a pull request authored by your account merged into a repository.\n\nGitHub does not publish a complete Pull Shark counting specification.", "GitHub's live achievement detail states that Pull Shark recognises pull requests opened by the account that have been merged.\n\nGitHub does not publish every internal attribution filter."),
            ("The following thresholds are widely reproduced by the community but are not published as guaranteed thresholds in GitHub's current profile documentation.", "GitHub's live x4 achievement history publishes the following milestone ordinals."),
            ("| Base achievement | 2 merged pull requests | Community-reported |\n| Bronze | 16 merged pull requests | Community-reported |\n| Silver | 128 merged pull requests | Community-reported |\n| Gold | 1,024 merged pull requests | Community-reported |", "| Base achievement | 2 merged pull requests | Official |\n| Bronze | 16 merged pull requests | Official |\n| Silver | 128 merged pull requests | Official |\n| Gold | 1,024 merged pull requests | Official |"),
            ("| Pull Shark is associated with merged pull requests | Confirmed |\n| The four numerical thresholds in this guide | Community-reported |", "| Pull Shark recognises opened pull requests that are merged | Official |\n| The four numerical thresholds in this guide | Official |"),
            ("No official tier-threshold changelog was located during this verification. Threshold claims therefore remain community-reported rather than official.", "GitHub's live x4 detail fragment exposes the complete milestone history at the 2nd, 16th, 128th, and 1024th merged pull requests."),
            ("- [GitHub Achievement Index](../achievement-index.md)", "- [Official achievement fragment corpus]({{ site.baseurl }}/official-achievement-fragments/)\n- [GitHub Achievement Index](../achievement-index.md)"),
            ("**19 July 2026** — verified against current GitHub profile, achievement-visibility, contribution-reference, and public-beta documentation. The numerical Pull Shark thresholds were not found in current official GitHub documentation and remain classified as community-reported.", "**19 July 2026** — verified against GitHub's live x4 Pull Shark detail fragment, including linked milestone history at 2, 16, 128, and 1,024 merged pull requests. Attribution and processing edge cases remain documented limitations."),
        ],
        "docs/quickdraw.md": [
            ("Two independent public reconstructions associate Quickdraw with pull requests merged five and nine seconds after creation. This supports the broad rapid-close trigger at observed level, while GitHub still does not publish the precise maximum timing window in its general profile documentation.", "GitHub's live Quickdraw detail fragment links a qualifying pull request and states: **Closed within 5 minutes of opening**. This establishes the pull-request timing contract at official level."),
            ("- Two independent public event/profile pairs support the rapid-close association at observed level.\n- The exact maximum timing window, issue equivalence, and first-visible award delay remain community-reported or unknown.", "- GitHub's live product fragment officially states the five-minute pull-request criterion.\n- Issue equivalence and first-visible award-processing delay remain limitations outside the resolved timing contract."),
            ("Quickdraw was introduced with GitHub profile achievements. Complete trigger and timing details have not been publicly documented by GitHub.", "Quickdraw was introduced with GitHub profile achievements. GitHub's live achievement fragment now exposes the five-minute criterion and a linked qualifying pull request."),
            ("- [Public reconstruction corpus]({{ site.baseurl }}/public-reconstruction-corpus/)", "- [Public reconstruction corpus]({{ site.baseurl }}/public-reconstruction-corpus/)\n- [Official achievement fragment corpus]({{ site.baseurl }}/official-achievement-fragments/)"),
            ("**19 July 2026.** Scope: two independent public rapid-close reconstructions, current issue and pull-request closure controls, profile-achievement presentation, and the unresolved maximum timing window.", "**19 July 2026.** Scope: GitHub's first-party five-minute Quickdraw fragment, linked qualifying pull request, two independent public reconstructions, and remaining issue-equivalence and processing-delay limitations."),
        ],
        "docs/achievements/yolo.md": [
            ("Two independent public reconstructions associate YOLO with pull requests authored by the awarded account and merged with no submitted formal review. This supports the broad unreviewed-merge trigger at observed level; merger identity and alternate formal review states remain unresolved.", "GitHub's live YOLO detail fragment links a qualifying pull request and states: **Merged without a review**. This establishes the broad unreviewed-merge contract at official level; alternate review states and structured merger identity remain edge-case research."),
            ("- Two independent public event/profile pairs support the authored, unreviewed-merge association at observed level.\n- GitHub does not publish a complete eligibility specification, and the public records do not expose merger identity or every alternate review state.", "- GitHub's live product fragment officially states `Merged without a review`.\n- Alternate review states and structured merger identity remain unresolved implementation edge cases."),
            ("YOLO was introduced with GitHub profile achievements. GitHub has not published a complete public trigger specification or historical change log for the achievement.", "YOLO was introduced with GitHub profile achievements. GitHub's live detail fragment now exposes the broad no-review contract and linked qualifying pull request."),
            ("- [Public reconstruction corpus]({{ site.baseurl }}/public-reconstruction-corpus/)", "- [Public reconstruction corpus]({{ site.baseurl }}/public-reconstruction-corpus/)\n- [Official achievement fragment corpus]({{ site.baseurl }}/official-achievement-fragments/)"),
            ("**19 July 2026.** Scope: two independent public authored/unreviewed merge reconstructions, current review and protection controls, profile-achievement presentation, and unresolved merger-identity and alternate-review semantics.", "**19 July 2026.** Scope: GitHub's first-party `Merged without a review` fragment, linked qualifying pull request, current review controls, and unresolved alternate-review and merger-identity edge cases."),
        ],
        "achievements/pair-extraordinaire.md": [
            ("**Evidence status:** GitHub officially documents co-authored commits and contribution attribution. Two independent public merged-pull-request reconstructions support the broad achievement trigger at observed level; tier thresholds and rewrite edge cases remain community-reported.", "**Evidence status:** GitHub's live achievement fragment officially states the broad trigger: coauthored commits on merged pull requests. Numerical tier thresholds and rewrite edge cases remain community-reported."),
            ("The observed broad trigger is participation as a correctly attributed co-author on a commit that becomes part of a merged pull request.\n\nA visible `Co-authored-by:` trailer proves commit attribution, but GitHub does not officially guarantee that every visible co-authored commit will increment this achievement.", "GitHub's live detail fragment states that Pair Extraordinaire recognises **coauthored commits on merged pull requests**.\n\nA visible `Co-authored-by:` trailer proves commit attribution, while squash, rebase, email matching and rewritten-history counting remain separate limitations."),
            ("- **Observed:** Two independent public accounts have account-linked co-author attribution preserved in merged pull-request history and publicly display Pair Extraordinaire.", "- **Official:** GitHub's live product fragment states that the achievement recognises coauthored commits on merged pull requests."),
            ("- [Public reconstruction corpus]({{ site.baseurl }}/public-reconstruction-corpus/)", "- [Public reconstruction corpus]({{ site.baseurl }}/public-reconstruction-corpus/)\n- [Official achievement fragment corpus]({{ site.baseurl }}/official-achievement-fragments/)"),
            ("**19 July 2026** — verified two independent public merged-pull-request/co-author reconstructions plus current GitHub documentation for trailer syntax and account-linked attribution. The broad trigger is observed; tier thresholds and merge-rewrite edge cases remain community-reported or unknown.", "**19 July 2026** — verified GitHub's first-party Pair Extraordinaire fragment and linked co-author history. The broad trigger is official; numerical tier thresholds and merge-rewrite edge cases remain community-reported or unknown."),
        ],
        "achievements/galaxy-brain.md": [
            ("**Evidence level:** Trigger and thresholds are community documented; GitHub does not publish a complete tier table.", "**Evidence level:** GitHub's live x4 achievement fragment officially publishes the accepted-answer trigger and complete milestone table."),
            ("## Community-reported tiers", "## Official tiers"),
            ("Treat these values as community-verified rather than guaranteed platform contracts.", "GitHub's x4 achievement history labels these as the 2nd, 8th, 16th, and 32nd accepted answers."),
            ("**19 July 2026** — reviewed accepted-answer behaviour, community-reported tiers, the verified-answer distinction, and responsible participation guidance.", "**19 July 2026** — verified GitHub's live x4 Galaxy Brain fragment, complete accepted-answer milestone history, the verified-answer distinction, and remaining revocation and processing limitations."),
            ("## Last verified", "## References\n\n- [Official achievement fragment corpus]({{ site.baseurl }}/official-achievement-fragments/)\n\n## Last verified"),
        ],
        "achievements/starstruck.md": [
            ("**Evidence level:** Strong community consensus; GitHub does not publish the complete threshold table in its general profile documentation.", "**Evidence level:** GitHub's live x4 achievement fragment officially publishes the repository-creation trigger and complete star milestone table."),
            ("Starstruck recognises repositories you created that reach community-reported star thresholds.", "GitHub's live detail fragment states that Starstruck recognises repositories created by the account that reach the published star milestones."),
            ("## Community-reported tiers", "## Official tiers"),
            ("These values are widely reproduced but should be treated as observed platform behaviour rather than a formal guarantee.", "GitHub's x4 achievement history labels milestones at 16, 128, 512, and 4,096 stars."),
            ("**19 July 2026** — reviewed community-reported star thresholds, repository association conditions, award timing, and legitimate growth guidance.", "**19 July 2026** — verified GitHub's live x4 Starstruck fragment and complete star milestone history. Transfer, organisation ownership, archival, forks, falling counts, and persistence remain open edge cases."),
            ("## Last verified", "## References\n\n- [Official achievement fragment corpus]({{ site.baseurl }}/official-achievement-fragments/)\n\n## Last verified"),
        ],
    }
    for path, rows in replacements.items():
        for old, new in rows:
            replace_once(path, old, new)


def update_public_surfaces() -> None:
    replace_once("scripts/build_public_api.py", '    "public_reconstructions": Path("public-reconstructions.json"),', '    "public_reconstructions": Path("public-reconstructions.json"),\n    "official_achievement_fragments": Path("official-achievement-fragments.json"),')
    replace_once("scripts/build_public_api.py", '    "public_reconstructions": "records",', '    "public_reconstructions": "records",\n    "official_achievement_fragments": "records",')
    replace_once("scripts/build_public_api.py", '            "public_reconstructions",\n            "event_linked_evidence",', '            "public_reconstructions",\n            "official_achievement_fragments",\n            "event_linked_evidence",')

    replace_once("docs/api-reference.md", '| [`public-reconstructions.json`](../api/public-reconstructions.json) | Exact public event/profile pairs used to support broad trigger associations without overstating causality |', '| [`public-reconstructions.json`](../api/public-reconstructions.json) | Exact public event/profile pairs used to support broad trigger associations without overstating causality |\n| [`official-achievement-fragments.json`](../api/official-achievement-fragments.json) | GitHub-owned live achievement criteria, linked history, fingerprints, and tier milestones |')
    replace_once("docs/api-reference.md", 'The discovery index now exposes **39 public JSON files**:', 'The discovery index now exposes **40 public JSON files**:')
    replace_once("docs/api-reference.md", 'python scripts/build_public_reconstructions.py', 'python scripts/build_public_reconstructions.py\npython scripts/build_official_achievement_fragments.py')
    replace_once("docs/api-reference.md", '- [Public reconstruction corpus](public-reconstruction-corpus.md)', '- [Public reconstruction corpus](public-reconstruction-corpus.md)\n- [Official achievement fragments](official-achievement-fragments.md)')

    replace_once("site-map.md", '- [Public reconstruction corpus](docs/public-reconstruction-corpus.md)', '- [Public reconstruction corpus](docs/public-reconstruction-corpus.md)\n- [Official achievement fragments](docs/official-achievement-fragments.md)')
    replace_once("site-map.md", '- [Public reconstructions](api/public-reconstructions.json)', '- [Public reconstructions](api/public-reconstructions.json)\n- [Official achievement fragments](api/official-achievement-fragments.json)')
    replace_once("research-command-centre.md", 'The [public reconstruction corpus](docs/public-reconstruction-corpus.md) preserves exact independent event/profile pairs that strengthen broad triggers while leaving causal, timing, threshold, and edge-case limitations explicit.', 'The [public reconstruction corpus](docs/public-reconstruction-corpus.md) preserves exact independent event/profile pairs that strengthen broad triggers while leaving causal, timing, threshold, and edge-case limitations explicit.\n\nThe [official achievement fragment corpus](docs/official-achievement-fragments.md) records GitHub-owned live criteria and milestone histories that now satisfy the evidence-quality release gates.')

    resources = load("data/search-resources.json")
    if not any(row["slug"] == "official-achievement-fragments" for row in resources["resources"]):
        resources["resources"].append({
            "slug": "official-achievement-fragments",
            "name": "Official GitHub achievement fragments",
            "category": "research",
            "summary": "GitHub-owned live achievement criteria and complete Pull Shark, Galaxy Brain, and Starstruck milestone histories.",
            "permalink": "/official-achievement-fragments/",
            "aliases": ["first party achievement criteria", "official tier history", "GitHub badge fragment"]
        })
    save("data/search-resources.json", resources)
    replace_once("scripts/test_search_page.mjs", "  const liveRegion = await page.locator('#search-count').getAttribute('aria-live');", "  await page.locator('#search-query').fill('official tier history');\n  await expectCount(page, 1, 'official fragment query');\n  const officialFragmentHref = await page.locator('[data-result-slug=\"official-achievement-fragments\"] h3 a').getAttribute('href');\n  assert.equal(officialFragmentHref, '/Achievements/official-achievement-fragments/');\n\n  const liveRegion = await page.locator('#search-count').getAttribute('aria-live');")

    replace_once("CHANGELOG.md", '- Dedicated reconstruction validator, API endpoint, public guide, search route, and drift-controlled workflow.', '- Dedicated reconstruction validator, API endpoint, public guide, search route, and drift-controlled workflow.\n- GitHub-owned achievement fragment corpus with exact Quickdraw, YOLO, Pair Extraordinaire, Pull Shark, Galaxy Brain, and Starstruck product contracts.\n- Complete first-party Pull Shark, Galaxy Brain, and Starstruck x4 milestone histories with normalized fingerprints and linked events.')
    replace_once("CHANGELOG.md", '- Public API discovery expanded from 26 to 39 JSON files.', '- Public API discovery expanded from 26 to 40 JSON files.')
    replace_once("CHANGELOG.md", '- Quickdraw, YOLO, and Pair Extraordinaire broad trigger claims advanced from community-reported to observed using two independent public reconstructions per claim; exact timing, alternate review states, attribution rewrites, and all tier thresholds remain unresolved.', '- Quickdraw, YOLO, and Pair Extraordinaire broad trigger claims advanced from community-reported to observed using two independent public reconstructions per claim.\n- GitHub-owned live fragments subsequently promoted Pull Shark, Quickdraw, YOLO, Pair Extraordinaire, Galaxy Brain tiers, and Starstruck claims to official while retaining Pair tier and edge-case limitations.\n- Quickdraw timing, Pull Shark tiers, and Galaxy Brain tiers are resolved from first-party product history; YOLO review edge cases, Pair rewrite/tier behaviour, and Starstruck ownership persistence remain open.')
    replace_once("CHANGELOG.md", '- Evidence coverage increases from 54.6 to 60.4 without changing weights or closing a contradiction.', '- Evidence coverage increases from 54.6 to 60.4 through public reconstructions, then to 91.2 through GitHub-owned product fragments without changing weights.\n- The v1.4.0 evidence gates now pass at 12 official/confirmed claims, 1 claim below confirmed, and 3 open contradictions; publication still requires merged-main operational verification.')


def run(*args: str) -> None:
    print("+", *args)
    subprocess.run(args, cwd=ROOT, check=True)


def update_release_snapshot() -> None:
    coverage = load("api/coverage.json")
    contradictions = load("data/contradictions.json")
    programme = load("data/evidence-quality-programme.json")
    current = programme["release_gate"]["current_snapshot"]
    current.update({
        "coverage_score": coverage["overall_coverage_score"],
        "official_or_confirmed_claims": sum(row["evidence_level"] in {"official", "confirmed"} for row in coverage["claims"]),
        "claims_below_confirmed": sum(row["evidence_level"] not in {"official", "confirmed"} for row in coverage["claims"]),
        "open_contradictions": sum(row["status"] == "open" for row in contradictions["records"]),
    })
    required = programme["release_gate"]["required_snapshot"]
    ready = (
        current["coverage_score"] >= required["minimum_coverage_score"]
        and current["official_or_confirmed_claims"] >= required["minimum_official_or_confirmed_claims"]
        and current["claims_below_confirmed"] <= required["maximum_claims_below_confirmed"]
        and current["open_contradictions"] <= required["maximum_open_contradictions"]
    )
    programme["release_gate"]["status"] = "ready" if ready else "blocked"
    save("data/evidence-quality-programme.json", programme)


def reconcile_missions() -> None:
    intelligence = load("api/evidence-intelligence.json")
    pressure = {row["achievement_slug"]: row["pressure_score"] for row in intelligence["achievements"]}
    missions = load("data/acquisition-missions.json")
    for row in missions["missions"]:
        slug = row.get("achievement_slug")
        if slug is not None:
            row["pressure_score"] = pressure[slug]
        if row["id"] in {"MSN-003", "MSN-004", "MSN-005"}:
            row["status"] = "complete"
            row["promotion_targets"] = []
        if row["id"] == "MSN-002":
            row["promotion_targets"] = []
    achievement_rows = sorted([row for row in missions["missions"] if row.get("achievement_slug") is not None], key=lambda row: (-row["pressure_score"], row["achievement_slug"]))
    cross_rows = [row for row in missions["missions"] if row.get("achievement_slug") is None]
    missions["missions"] = [*achievement_rows, *cross_rows]
    for rank, row in enumerate(missions["missions"], 1):
        row["rank"] = rank
    save("data/acquisition-missions.json", missions, compact=True)


def main() -> None:
    update_claims()
    update_achievements()
    update_evidence()
    update_contradictions()
    update_research_queue()
    update_programme()
    update_quality_builder()
    rewrite_guides()
    update_public_surfaces()

    run("python", "scripts/build_official_achievement_fragments.py")
    run("python", "scripts/build_evidence_register.py")
    run("python", "scripts/build_research_intelligence.py")
    update_release_snapshot()
    run("python", "scripts/build_evidence_quality_programme.py")
    run("python", "scripts/build_evidence_intelligence.py")
    reconcile_missions()
    run("python", "scripts/build_acquisition_missions.py")
    run("python", "scripts/build_mission_intake.py")
    run("python", "scripts/build_mission_review_queue.py")
    run("python", "scripts/build_promotion_plans.py")
    run("python", "scripts/build_evidence_operations.py")
    run("python", "scripts/build_public_api.py")

    coverage = load("api/coverage.json")
    readiness = load("api/release-readiness.json")
    assert coverage["overall_coverage_score"] == 91.2, coverage["overall_coverage_score"]
    assert readiness["status"] == "ready", readiness
    assert readiness["current_snapshot"] == {
        "coverage_score": 91.2,
        "official_or_confirmed_claims": 12,
        "claims_below_confirmed": 1,
        "open_contradictions": 3,
        "operational_health_target": 100,
    }, readiness["current_snapshot"]
    print("Phase 63 reconciliation complete: 91.2 coverage, 12 official/confirmed, 1 weak claim, 3 open contradictions.")


if __name__ == "__main__":
    main()
