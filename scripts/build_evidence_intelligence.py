from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "api"
DOC = ROOT / "docs" / "evidence-intelligence-dashboard.md"
OUTPUT = API / "evidence-intelligence.json"

INPUTS = {
    "coverage": API / "coverage.json",
    "events": API / "event-linked-evidence.json",
    "boundaries": API / "threshold-boundaries.json",
    "adjudication": API / "adjudication.json",
    "contradictions": API / "contradiction-assessments.json",
    "release": API / "release-readiness.json",
}


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def validate(documents: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    required = {
        "coverage": ("achievements", "claims", "overall_coverage_score"),
        "events": ("events", "metrics"),
        "boundaries": ("programmes",),
        "adjudication": ("decisions", "metrics"),
        "contradictions": ("assessments", "metrics"),
        "release": ("candidate_version", "status", "current_snapshot", "required_snapshot"),
    }
    for name, fields in required.items():
        document = documents[name]
        for field in fields:
            if field not in document:
                errors.append(f"api/{INPUTS[name].name} is missing {field}")

    coverage_slugs = {
        item.get("achievement_slug")
        for item in documents["coverage"].get("achievements", [])
        if isinstance(item, dict)
    }
    if len(coverage_slugs) != 9 or None in coverage_slugs:
        errors.append("coverage must identify exactly nine achievements")

    claim_to_slug = {
        item.get("claim_id"): item.get("achievement_slug")
        for item in documents["coverage"].get("claims", [])
        if isinstance(item, dict)
    }
    for decision in documents["adjudication"].get("decisions", []):
        if decision.get("claim_id") not in claim_to_slug:
            errors.append(f"{decision.get('id', 'decision')}: unknown claim")
    for collection, key in (("events", "events"), ("boundaries", "programmes")):
        for item in documents[collection].get(key, []):
            if item.get("achievement_slug") not in coverage_slugs:
                errors.append(f"{item.get('id', collection)}: unknown achievement")

    release = documents["release"]
    if release.get("status") not in {"blocked", "ready"}:
        errors.append("release readiness status must be blocked or ready")
    return errors


def pressure_score(
    coverage_score: float,
    contradiction_outcome: str,
    boundary_count: int,
    deferred_count: int,
    negative_count: int,
) -> int:
    contradiction_weight = {
        "still-disputed": 20,
        "narrowed": 12,
        "resolved": 0,
        "none": 0,
    }.get(contradiction_outcome, 20)
    raw = (
        (100.0 - coverage_score) * 0.45
        + contradiction_weight
        + (10 if boundary_count else 0)
        + (8 if deferred_count else 0)
        + min(9, negative_count * 3)
    )
    return min(100, round(raw))


def build(documents: dict[str, dict]) -> dict:
    coverage = documents["coverage"]
    events = documents["events"]["events"]
    boundaries = documents["boundaries"]["programmes"]
    decisions = documents["adjudication"]["decisions"]
    assessments = documents["contradictions"]["assessments"]
    release = documents["release"]

    claim_to_slug = {
        item["claim_id"]: item["achievement_slug"]
        for item in coverage["claims"]
    }
    event_counts: dict[str, Counter] = defaultdict(Counter)
    for event in events:
        event_counts[event["achievement_slug"]][event["adjudication_status"]] += 1

    boundary_by_slug: dict[str, list[dict]] = defaultdict(list)
    for programme in boundaries:
        boundary_by_slug[programme["achievement_slug"]].append(programme)

    decisions_by_slug: dict[str, list[dict]] = defaultdict(list)
    for decision in decisions:
        decisions_by_slug[claim_to_slug[decision["claim_id"]]].append(decision)

    outcome_by_id = {
        item["contradiction_id"]: item["outcome"]
        for item in assessments
    }

    rows = []
    for achievement in coverage["achievements"]:
        slug = achievement["achievement_slug"]
        dispute_outcomes = [
            outcome_by_id.get(dispute_id, "still-disputed")
            for dispute_id in achievement.get("open_disputes", [])
        ]
        if "still-disputed" in dispute_outcomes:
            outcome = "still-disputed"
        elif "narrowed" in dispute_outcomes:
            outcome = "narrowed"
        elif dispute_outcomes:
            outcome = dispute_outcomes[0]
        else:
            outcome = "none"

        event_statuses = event_counts[slug]
        programmes = boundary_by_slug[slug]
        deferred = [
            item for item in decisions_by_slug[slug]
            if item.get("decision") == "defer"
        ]
        row = {
            "achievement_slug": slug,
            "achievement_name": achievement["achievement_name"],
            "achievement_status": achievement["achievement_status"],
            "coverage_score": achievement["coverage_score"],
            "coverage_rating": achievement["rating"],
            "claim_count": achievement["claim_count"],
            "event_count": sum(event_statuses.values()),
            "candidate_observed_event_count": event_statuses["candidate-observed"],
            "negative_inconclusive_event_count": event_statuses["negative-inconclusive"],
            "boundary_programme_count": len(programmes),
            "deferred_adjudication_count": len(deferred),
            "contradiction_outcome": outcome,
            "next_evidence": [item["next_evidence"] for item in programmes],
        }
        row["pressure_score"] = pressure_score(
            row["coverage_score"],
            outcome,
            row["boundary_programme_count"],
            row["deferred_adjudication_count"],
            row["negative_inconclusive_event_count"],
        )
        rows.append(row)

    rows.sort(key=lambda item: (-item["pressure_score"], item["achievement_name"]))

    current = release["current_snapshot"]
    required = release["required_snapshot"]
    release_gaps = {
        "coverage_points_needed": round(
            max(0.0, required["minimum_coverage_score"] - current["coverage_score"]), 1
        ),
        "official_or_confirmed_claims_needed": max(
            0,
            required["minimum_official_or_confirmed_claims"]
            - current["official_or_confirmed_claims"],
        ),
        "claims_to_promote_to_confirmed_or_official": max(
            0,
            current["claims_below_confirmed"]
            - required["maximum_claims_below_confirmed"],
        ),
        "contradictions_to_resolve": max(
            0,
            current["open_contradictions"]
            - required["maximum_open_contradictions"],
        ),
    }

    return {
        "api_version": "1.0.0",
        "schema_version": "1.0.0",
        "status": "live",
        "source_endpoints": [
            "/Achievements/api/coverage.json",
            "/Achievements/api/event-linked-evidence.json",
            "/Achievements/api/threshold-boundaries.json",
            "/Achievements/api/adjudication.json",
            "/Achievements/api/contradiction-assessments.json",
            "/Achievements/api/release-readiness.json",
        ],
        "metrics": {
            "achievement_count": len(rows),
            "active_achievement_count": sum(
                item["achievement_status"] == "active" for item in rows
            ),
            "event_count": len(events),
            "boundary_programme_count": len(boundaries),
            "deferred_adjudication_count": sum(
                item.get("decision") == "defer" for item in decisions
            ),
            "narrowed_contradiction_count": sum(
                item.get("outcome") == "narrowed" for item in assessments
            ),
            "still_disputed_contradiction_count": sum(
                item.get("outcome") == "still-disputed" for item in assessments
            ),
            "overall_coverage_score": coverage["overall_coverage_score"],
            "release_status": release["status"],
        },
        "pressure_formula": {
            "coverage_gap_weight": 0.45,
            "still_disputed_contradiction_points": 20,
            "narrowed_contradiction_points": 12,
            "boundary_programme_points": 10,
            "deferred_adjudication_points": 8,
            "negative_inconclusive_event_points_each": 3,
            "negative_inconclusive_event_cap": 9,
            "maximum_score": 100,
        },
        "release_candidate": release["candidate_version"],
        "release_gaps": release_gaps,
        "achievements": rows,
    }


def markdown(payload: dict) -> str:
    metrics = payload["metrics"]
    gaps = payload["release_gaps"]
    lines = [
        "---",
        "layout: default",
        "title: Evidence intelligence dashboard",
        "description: Deterministic analytics across coverage, event evidence, boundary investigations, adjudication, contradictions, and release readiness.",
        "permalink: /evidence-intelligence/",
        "---",
        "",
        "## Evidence intelligence dashboard",
        "",
        "This dashboard combines the public evidence-operation endpoints into one read-only decision surface. It does not promote claims, resolve contradictions, or override the formal release gate.",
        "",
        f"**Evidence coverage:** {metrics['overall_coverage_score']}/100  ",
        f"**Event-linked records:** {metrics['event_count']}  ",
        f"**Boundary investigations:** {metrics['boundary_programme_count']}  ",
        f"**Deferred adjudications:** {metrics['deferred_adjudication_count']}  ",
        f"**Release status:** `{metrics['release_status']}`",
        "",
        "## Distance to the evidence-quality release",
        "",
        "| Gate | Remaining gap |",
        "|---|---:|",
        f"| Coverage | {gaps['coverage_points_needed']} points |",
        f"| Official or confirmed claims | {gaps['official_or_confirmed_claims_needed']} claims |",
        f"| Claims below confirmed | {gaps['claims_to_promote_to_confirmed_or_official']} promotions |",
        f"| Open contradictions | {gaps['contradictions_to_resolve']} resolutions |",
        "",
        "## Research pressure ranking",
        "",
        "| Rank | Achievement | Pressure | Coverage | Events | Boundaries | Deferred | Contradiction |",
        "|---:|---|---:|---:|---:|---:|---:|---|",
    ]
    for rank, row in enumerate(payload["achievements"], start=1):
        lines.append(
            f"| {rank} | {row['achievement_name']} | {row['pressure_score']} | "
            f"{row['coverage_score']} | {row['event_count']} | "
            f"{row['boundary_programme_count']} | "
            f"{row['deferred_adjudication_count']} | "
            f"{row['contradiction_outcome']} |"
        )
    lines.extend(["", "## Immediate evidence requirements", ""])
    for row in payload["achievements"]:
        if not row["next_evidence"]:
            continue
        lines.extend([f"### {row['achievement_name']}", ""])
        lines.extend(f"- {requirement}" for requirement in row["next_evidence"])
        lines.append("")
    lines.extend([
        "## Pressure-score contract",
        "",
        "The score is a prioritisation aid, not an evidence-confidence score:",
        "",
        "- 45% of the remaining coverage gap contributes to pressure.",
        "- A still-disputed contradiction adds 20 points; a narrowed contradiction adds 12.",
        "- An unresolved boundary programme adds 10 points.",
        "- Any deferred adjudication adds 8 points.",
        "- Each negative or inconclusive event adds 3 points, capped at 9.",
        "- The final score is rounded and capped at 100.",
        "",
        "High pressure means the claim area combines weak coverage with unresolved work. It does not mean the underlying community claim is likely to be true.",
        "",
        "## Machine-readable data",
        "",
        "The generated analytics are published at [`/api/evidence-intelligence.json`](../api/evidence-intelligence.json).",
        "",
    ])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build or verify the evidence intelligence dashboard."
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", default="evidence-intelligence-report.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        documents = {name: load(path) for name, path in INPUTS.items()}
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error)
        return 1

    errors = validate(documents)
    report = [
        "# Evidence intelligence validation",
        "",
        f"- Inputs: {len(INPUTS)}",
        f"- Result: {'FAIL' if errors else 'PASS'}",
    ]
    if errors:
        report.extend(["", "## Failures", "", *[f"- {error}" for error in errors]])
    (ROOT / args.report).write_text("\n".join(report) + "\n", encoding="utf-8")
    if errors:
        print("\n".join(errors))
        return 1

    payload = build(documents)
    outputs = {
        OUTPUT: json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        DOC: markdown(payload),
    }
    if args.check:
        stale = [
            str(path.relative_to(ROOT))
            for path, expected in outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != expected
        ]
        if stale:
            print("Stale or missing evidence intelligence outputs: " + ", ".join(stale))
            return 1
    else:
        for path, expected in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")

    print(
        "Evidence intelligence passed: "
        f"{payload['metrics']['achievement_count']} achievements, "
        f"{payload['metrics']['event_count']} events, "
        f"{payload['metrics']['boundary_programme_count']} boundary programmes."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
