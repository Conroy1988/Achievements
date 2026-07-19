from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "public-observations.json"
ACHIEVEMENTS_PATH = ROOT / "data" / "achievements.json"
CLAIMS_PATH = ROOT / "data" / "claims.json"
MARKDOWN_PATH = ROOT / "docs" / "public-observation-corpus.md"
API_PATH = ROOT / "api" / "public-observations.json"

ID_PATTERN = re.compile(r"^OBS-(\d{4})-(\d{3})$")
ALLOWED_TIERS = {"base", "x2", "x3", "x4", "not-tiered"}
ALLOWED_SCOPES = {
    "award-display-only",
    "tier-display-only",
    "tier-display-and-public-metric",
}
ALLOWED_PRIVACY = {"public-identifiers-only"}
ALLOWED_DECISIONS = {"accepted-as-observation", "needs-review", "rejected"}
ALLOWED_FACT_TYPES = {
    "owned-public-repository-stars",
    "public-pull-request-count",
    "public-accepted-answer-count",
}


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def public_github_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    return parsed.scheme == "https" and parsed.netloc == "github.com" and bool(parsed.path.strip("/"))


def validate(corpus: dict, achievements: dict, claims: dict) -> list[str]:
    errors: list[str] = []
    rows = corpus.get("observations")
    if not isinstance(rows, list) or not rows:
        return ["observations must be a non-empty array"]

    achievement_slugs = {item["slug"] for item in achievements.get("achievements", [])}
    claim_by_id = {item["id"]: item for item in claims.get("claims", [])}
    seen_ids: set[str] = set()
    seen_signatures: set[tuple[str, str, str, str]] = set()
    today = date.today()

    for position, row in enumerate(rows, start=1):
        prefix = f"observation {position}"
        observation_id = row.get("id", "")
        match = ID_PATTERN.fullmatch(observation_id)
        if not match:
            errors.append(f"{prefix}: invalid id {observation_id!r}")
        elif observation_id in seen_ids:
            errors.append(f"{prefix}: duplicate id {observation_id}")
        else:
            seen_ids.add(observation_id)

        try:
            observed_at = date.fromisoformat(row.get("observed_at", ""))
            if observed_at > today:
                errors.append(f"{observation_id}: observed_at is in the future")
            if match and observed_at.year != int(match.group(1)):
                errors.append(f"{observation_id}: id year differs from observed_at")
        except (TypeError, ValueError):
            errors.append(f"{observation_id}: invalid observed_at")

        slug = row.get("achievement_slug")
        if slug not in achievement_slugs:
            errors.append(f"{observation_id}: unknown achievement slug {slug!r}")

        claim_ids = row.get("claim_ids")
        if not isinstance(claim_ids, list) or not claim_ids:
            errors.append(f"{observation_id}: claim_ids must be a non-empty array")
        else:
            unknown = sorted(set(claim_ids) - set(claim_by_id))
            if unknown:
                errors.append(f"{observation_id}: unknown claim ids: {', '.join(unknown)}")
            mismatched = sorted(
                claim_id
                for claim_id in claim_ids
                if claim_id in claim_by_id
                and claim_by_id[claim_id].get("achievement_slug") != slug
            )
            if mismatched:
                errors.append(
                    f"{observation_id}: claims do not belong to {slug}: {', '.join(mismatched)}"
                )

        subject = row.get("subject_login")
        if not isinstance(subject, str) or not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", subject):
            errors.append(f"{observation_id}: invalid public GitHub login")

        profile_url = row.get("profile_url")
        if not public_github_url(profile_url):
            errors.append(f"{observation_id}: profile_url must be a public github.com URL")

        tier = row.get("displayed_tier")
        if tier not in ALLOWED_TIERS:
            errors.append(f"{observation_id}: invalid displayed_tier")
        scope = row.get("evidence_scope")
        if scope not in ALLOWED_SCOPES:
            errors.append(f"{observation_id}: invalid evidence_scope")
        if row.get("privacy_status") not in ALLOWED_PRIVACY:
            errors.append(f"{observation_id}: invalid privacy_status")
        if row.get("reviewer_decision") not in ALLOWED_DECISIONS:
            errors.append(f"{observation_id}: invalid reviewer_decision")

        facts = row.get("supporting_facts")
        if not isinstance(facts, list):
            errors.append(f"{observation_id}: supporting_facts must be an array")
            facts = []
        for fact in facts:
            if not isinstance(fact, dict):
                errors.append(f"{observation_id}: supporting fact must be an object")
                continue
            if fact.get("type") not in ALLOWED_FACT_TYPES:
                errors.append(f"{observation_id}: invalid supporting fact type")
            if not public_github_url(fact.get("url")):
                errors.append(f"{observation_id}: supporting fact URL must be public github.com")
            if not isinstance(fact.get("rendered_value"), str) or not fact["rendered_value"].strip():
                errors.append(f"{observation_id}: supporting fact requires rendered_value")
        if scope == "tier-display-and-public-metric" and not facts:
            errors.append(f"{observation_id}: metric scope requires supporting facts")

        limitations = row.get("limitations")
        if not isinstance(limitations, list) or len(limitations) < 2:
            errors.append(f"{observation_id}: at least two limitations are required")
        elif any(not isinstance(value, str) or not value.strip() for value in limitations):
            errors.append(f"{observation_id}: limitations must contain non-empty strings")

        if isinstance(subject, str) and isinstance(slug, str) and isinstance(tier, str):
            signature = (subject.lower(), slug, tier, str(row.get("observed_at")))
            if signature in seen_signatures:
                errors.append(f"{observation_id}: duplicate subject/achievement/tier/date observation")
            seen_signatures.add(signature)

    return errors


def payload(corpus: dict) -> dict:
    rows = sorted(corpus["observations"], key=lambda item: item["id"])
    achievements = Counter(item["achievement_slug"] for item in rows)
    tiers = Counter(item["displayed_tier"] for item in rows)
    return {
        "api_version": "1.0.0",
        "schema_version": corpus["schema_version"],
        "count": len(rows),
        "policy": "/Achievements/public-observation-corpus/",
        "metrics": {
            "achievement_count": len(achievements),
            "observation_count": len(rows),
            "tier_display_count": sum(item["displayed_tier"] != "not-tiered" for item in rows),
            "metric_backed_count": sum(bool(item["supporting_facts"]) for item in rows),
        },
        "by_achievement": dict(sorted(achievements.items())),
        "by_displayed_tier": dict(sorted(tiers.items())),
        "observations": rows,
    }


def markdown(corpus: dict) -> str:
    output = payload(corpus)
    rows = output["observations"]
    lines = [
        "---",
        "layout: default",
        "title: Public observation corpus",
        "description: Dated GitHub-owned profile and repository observations retained without overstating what they prove.",
        "permalink: /public-observation-corpus/",
        "---",
        "",
        "## Public observation corpus",
        "",
        "This corpus records public GitHub platform output that can support achievement research. An observation proves only the state visible at the cited URL on the recorded date. It does not automatically prove a trigger, exact threshold, causality, persistence, or the absence of hidden conditions.",
        "",
        f"**Observations:** {output['metrics']['observation_count']}  ",
        f"**Achievements represented:** {output['metrics']['achievement_count']}  ",
        f"**Metric-backed observations:** {output['metrics']['metric_backed_count']}  ",
        f"**Schema version:** `{corpus['schema_version']}`",
        "",
        "| Observation | Achievement | Public account | Display | Scope | Date |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['id']}` | {row['achievement_slug']} | "
            f"[`{row['subject_login']}`]({row['profile_url']}) | "
            f"{row['displayed_tier']} | {row['evidence_scope']} | {row['observed_at']} |"
        )
    lines.extend([
        "",
        "## Interpretation rules",
        "",
        "- A visible badge or tier is direct evidence that GitHub rendered that state for the public account.",
        "- A repository metric is a dated public value, not an immutable historical award-boundary record.",
        "- Rounded counts bracket a value but do not establish an exact threshold.",
        "- Badge display without event-linked detail does not prove the qualifying issue, pull request, commit, answer, review state, or processing interval.",
        "- Claim promotion still requires the acceptance criteria in the research queue and contradiction ledger.",
        "",
        "## Observation details",
        "",
    ])
    for row in rows:
        lines.extend([
            f"### {row['id']} — {row['achievement_slug']} / {row['displayed_tier']}",
            "",
            f"**Profile:** [`{row['subject_login']}`]({row['profile_url']})  ",
            f"**Claims:** {', '.join(f'`{claim_id}`' for claim_id in row['claim_ids'])}  ",
            f"**Decision:** `{row['reviewer_decision']}`  ",
            f"**Privacy:** `{row['privacy_status']}`",
            "",
        ])
        if row["supporting_facts"]:
            lines.append("**Supporting public facts**")
            lines.append("")
            for fact in row["supporting_facts"]:
                lines.append(
                    f"- [{fact['type']}]({fact['url']}): {fact['rendered_value']}"
                )
            lines.append("")
        lines.append("**Limitations**")
        lines.append("")
        lines.extend(f"- {value}" for value in row["limitations"])
        lines.append("")
    lines.extend([
        "## Machine-readable data",
        "",
        "The validated corpus is published at [`/api/public-observations.json`](../api/public-observations.json).",
        "",
    ])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and publish the public GitHub achievement observation corpus."
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", default="public-observation-report.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        corpus = load(DATA_PATH)
        achievements = load(ACHIEVEMENTS_PATH)
        claims = load(CLAIMS_PATH)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error)
        return 1

    errors = validate(corpus, achievements, claims)
    report = [
        "# Public observation validation",
        "",
        f"- Observations: {len(corpus.get('observations', []))}",
        f"- Result: {'FAIL' if errors else 'PASS'}",
    ]
    if errors:
        report.extend(["", "## Failures", "", *[f"- {error}" for error in errors]])
    (ROOT / args.report).write_text("\n".join(report) + "\n", encoding="utf-8")
    if errors:
        print("\n".join(errors))
        return 1

    outputs = {
        API_PATH: json.dumps(payload(corpus), indent=2, ensure_ascii=False) + "\n",
        MARKDOWN_PATH: markdown(corpus),
    }
    if args.check:
        stale = [
            str(path.relative_to(ROOT))
            for path, expected in outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != expected
        ]
        if stale:
            print("Stale or missing public observation outputs: " + ", ".join(stale))
            return 1
    else:
        for path, expected in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")

    print(
        "Public observation corpus passed: "
        f"{len(corpus['observations'])} observations across "
        f"{payload(corpus)['metrics']['achievement_count']} achievements."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
