from __future__ import annotations

from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "official-achievement-fragments.json"
CLAIMS = ROOT / "data" / "claims.json"
CONTRADICTIONS = ROOT / "data" / "contradictions.json"
API = ROOT / "api" / "official-achievement-fragments.json"
DOC = ROOT / "docs" / "official-achievement-fragments.md"
ID = re.compile(r"^GAF-\d{4}-\d{3}$")
SHA = re.compile(r"^[0-9a-f]{64}$")

REQUIRED_CONTRACTS = {
    "quickdraw": {
        "criterion": "Closed within 5 minutes of opening",
        "milestones": [5],
        "unit": "minutes",
        "claim_ids": {"CLM-003"},
    },
    "yolo": {
        "criterion": "Merged without a review",
        "milestones": [],
        "unit": None,
        "claim_ids": {"CLM-004"},
    },
    "pair-extraordinaire": {
        "criterion": "coauthored commits on merged pull requests",
        "milestones": [],
        "unit": None,
        "claim_ids": {"CLM-005"},
    },
    "pull-shark": {
        "criterion": "opened pull requests that have been merged",
        "milestones": [2, 16, 128, 1024],
        "unit": "merged pull requests",
        "claim_ids": {"CLM-001", "CLM-002"},
    },
    "galaxy-brain": {
        "criterion": "answered discussions",
        "milestones": [2, 8, 16, 32],
        "unit": "accepted answers",
        "claim_ids": {"CLM-007", "CLM-008"},
    },
    "starstruck": {
        "criterion": "created a repository that has many stars",
        "milestones": [16, 128, 512, 4096],
        "unit": "repository stars",
        "claim_ids": {"CLM-009", "CLM-010"},
    },
}
EXPECTED_RESOLUTIONS = {"CTR-001", "CTR-003", "CTR-005"}


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def github_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    return parsed.scheme == "https" and parsed.netloc == "github.com" and bool(parsed.path.strip("/"))


def validate(source: dict, claims: dict, contradictions: dict) -> list[str]:
    errors: list[str] = []
    records = source.get("records")
    if source.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    if source.get("source_classification") != "github-owned-live-product-fragment":
        errors.append("source classification must identify a GitHub-owned live product fragment")
    if not isinstance(records, list) or len(records) != len(REQUIRED_CONTRACTS):
        return [*errors, "exactly six decisive fragment records are required"]

    claim_map = {row["id"]: row for row in claims.get("claims", [])}
    contradiction_ids = {row["id"] for row in contradictions.get("records", [])}
    seen_ids: set[str] = set()
    seen_slugs: set[str] = set()
    resolutions: set[str] = set()

    for row in records:
        rid = row.get("id")
        slug = row.get("achievement_slug")
        if not isinstance(rid, str) or not ID.fullmatch(rid) or rid in seen_ids:
            errors.append(f"invalid or duplicate fragment id: {rid!r}")
        seen_ids.add(str(rid))
        if slug not in REQUIRED_CONTRACTS or slug in seen_slugs:
            errors.append(f"{rid}: invalid or duplicate achievement slug {slug!r}")
            continue
        seen_slugs.add(slug)
        expected = REQUIRED_CONTRACTS[slug]
        if row.get("criterion_text") != expected["criterion"]:
            errors.append(f"{rid}: criterion text drift")
        if row.get("milestones") != expected["milestones"]:
            errors.append(f"{rid}: milestone table drift")
        if row.get("milestone_unit") != expected["unit"]:
            errors.append(f"{rid}: milestone unit drift")
        if set(row.get("claim_ids", [])) != expected["claim_ids"]:
            errors.append(f"{rid}: claim relationship drift")
        for claim_id in row.get("claim_ids", []):
            claim = claim_map.get(claim_id)
            if not claim or claim.get("achievement_slug") != slug:
                errors.append(f"{rid}: invalid claim {claim_id}")
        for contradiction_id in row.get("resolves_contradiction_ids", []):
            if contradiction_id not in contradiction_ids:
                errors.append(f"{rid}: unknown contradiction {contradiction_id}")
            resolutions.add(contradiction_id)
        expected_path = f"/users/{row.get('subject_login')}/achievements/{slug}/detail"
        parsed = urlsplit(str(row.get("detail_url", "")))
        if not github_url(row.get("detail_url")) or parsed.path != expected_path or parsed.query != "hovercard=1":
            errors.append(f"{rid}: invalid first-party detail URL")
        if row.get("displayed_tier") not in {"base", "x2", "x3", "x4"}:
            errors.append(f"{rid}: invalid displayed tier")
        if not isinstance(row.get("normalized_text_sha256"), str) or not SHA.fullmatch(row["normalized_text_sha256"]):
            errors.append(f"{rid}: invalid normalized text fingerprint")
        event_urls = row.get("event_urls")
        if not isinstance(event_urls, list) or not event_urls or any(not github_url(value) for value in event_urls):
            errors.append(f"{rid}: public GitHub event URLs are required")
        limitations = row.get("limitations")
        if not isinstance(limitations, list) or len(limitations) < 2:
            errors.append(f"{rid}: at least two limitations are required")

    if seen_slugs != set(REQUIRED_CONTRACTS):
        errors.append("fragment corpus does not cover every required achievement")
    if resolutions != EXPECTED_RESOLUTIONS:
        errors.append("fragment contradiction-resolution mapping drift")
    return errors


def payload(source: dict) -> dict:
    records = source["records"]
    return {
        "api_version": "1.0.0",
        "schema_version": source["schema_version"],
        "status": "live",
        "policy": "/Achievements/official-achievement-fragments/",
        "observed_at": source["observed_at"],
        "source_classification": source["source_classification"],
        "count": len(records),
        "metrics": {
            "fragment_count": len(records),
            "achievement_count": len({row["achievement_slug"] for row in records}),
            "official_claim_count": len({claim_id for row in records for claim_id in row["claim_ids"]}),
            "resolved_contradiction_count": len({value for row in records for value in row["resolves_contradiction_ids"]}),
            "complete_tier_table_count": sum(row["displayed_tier"] == "x4" and bool(row["milestones"]) for row in records),
            "automatic_canonical_mutation_count": 0,
        },
        "by_achievement": dict(sorted(Counter(row["achievement_slug"] for row in records).items())),
        "records": records,
    }


def markdown(source: dict) -> str:
    output = payload(source)
    lines = [
        "---",
        "layout: default",
        "title: Official GitHub achievement fragments",
        "description: GitHub-owned live product fragments that explicitly state achievement criteria and tier milestones.",
        "permalink: /official-achievement-fragments/",
        "---",
        "",
        "## Official GitHub achievement fragments",
        "",
        "GitHub profile badges expose public achievement-detail fragments through the platform's own hovercard endpoints. These first-party fragments state the material criterion, link qualifying history, and—where present—publish tier milestone ordinals.",
        "",
        f"**Fragments:** {output['metrics']['fragment_count']}  ",
        f"**Official claims supported:** {output['metrics']['official_claim_count']}  ",
        f"**Complete tier tables:** {output['metrics']['complete_tier_table_count']}  ",
        f"**Contradictions resolved:** {output['metrics']['resolved_contradiction_count']}  ",
        "**Automatic canonical mutations:** 0",
        "",
        "| Achievement | GitHub criterion | Published milestones | Source account |",
        "|---|---|---|---|",
    ]
    for row in output["records"]:
        milestones = ", ".join(str(value) for value in row["milestones"]) or "not published"
        lines.append(
            f"| {row['achievement_slug']} | {row['criterion_text']} | {milestones} {row['milestone_unit'] or ''} | "
            f"[`{row['subject_login']}`]({row['detail_url']}) |"
        )
    lines.extend([
        "",
        "## Scope boundaries",
        "",
        "- Quickdraw's fragment states a five-minute maximum; processing delay remains separate.",
        "- YOLO's fragment states `Merged without a review`; alternate review-state and merger-identity edge cases remain under research.",
        "- Pair Extraordinaire's fragment states the broad co-authored-commit trigger but does not publish numerical tier thresholds.",
        "- Pull Shark and Galaxy Brain expose complete x4 milestone histories.",
        "- Starstruck exposes the complete star table but not transfer, organization-ownership, archival, fork, or falling-count persistence.",
        "",
        "## Machine-readable data",
        "",
        "See [`/api/official-achievement-fragments.json`](../api/official-achievement-fragments.json).",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and publish GitHub-owned achievement fragments.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", default="official-achievement-fragments-report.md")
    args = parser.parse_args()
    try:
        source = load(SOURCE)
        claims = load(CLAIMS)
        contradictions = load(CONTRADICTIONS)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error)
        return 1
    errors = validate(source, claims, contradictions)
    report = [
        "# Official achievement fragment validation",
        "",
        f"- Fragments: {len(source.get('records', []))}",
        f"- Result: {'FAIL' if errors else 'PASS'}",
    ]
    if errors:
        report += ["", "## Failures", ""] + [f"- {value}" for value in errors]
    (ROOT / args.report).write_text("\n".join(report) + "\n", encoding="utf-8")
    if errors:
        print("\n".join(errors))
        return 1
    outputs = {
        API: json.dumps(payload(source), indent=2, ensure_ascii=False) + "\n",
        DOC: markdown(source),
    }
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, expected in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != expected]
        if stale:
            print("Stale or missing official fragment outputs: " + ", ".join(stale))
            return 1
    else:
        for path, expected in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
    print(f"Official achievement fragments passed: {len(source['records'])} fragments, automatic mutations 0.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
