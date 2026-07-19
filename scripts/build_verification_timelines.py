from __future__ import annotations

from datetime import date
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
TIMELINES_PATH = ROOT / "data" / "verification-timelines.json"
ACHIEVEMENTS_PATH = ROOT / "data" / "achievements.json"
EVIDENCE_PATH = ROOT / "data" / "evidence-register.json"
MARKDOWN_PATH = ROOT / "docs" / "verification-timelines.md"
API_PATH = ROOT / "api" / "timelines.json"
ALLOWED_LEVELS = {"official", "confirmed", "observed", "community-reported", "unknown"}
ALLOWED_PRECISION = {"day", "month", "year"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(payload: dict, achievements: dict, evidence: dict) -> list[str]:
    failures: list[str] = []
    timelines = payload.get("timelines")
    catalogue = achievements.get("achievements")
    if not isinstance(timelines, list):
        return ["timelines must be an array"]
    if not isinstance(catalogue, list):
        return ["achievement catalogue is invalid"]

    achievement_by_slug = {item["slug"]: item for item in catalogue}
    evidence_slugs = {item["achievement_slug"] for item in evidence.get("records", [])}
    seen: set[str] = set()
    today = date.today()

    for index, timeline in enumerate(timelines, start=1):
        slug = timeline.get("achievement_slug", "")
        prefix = f"timeline {index} ({slug or 'missing slug'})"
        achievement = achievement_by_slug.get(slug)
        if achievement is None:
            failures.append(f"{prefix}: unknown achievement")
            continue
        if slug in seen:
            failures.append(f"{prefix}: duplicate timeline")
        seen.add(slug)
        if slug not in evidence_slugs:
            failures.append(f"{prefix}: no evidence-register record")
        if timeline.get("last_reviewed") != achievement.get("last_verified"):
            failures.append(f"{prefix}: last_reviewed must match the canonical last_verified date")
        try:
            reviewed = date.fromisoformat(timeline.get("last_reviewed", ""))
            if reviewed > today:
                failures.append(f"{prefix}: last_reviewed is in the future")
        except ValueError:
            failures.append(f"{prefix}: invalid last_reviewed date")
        limitations = timeline.get("history_limitations")
        if not isinstance(limitations, list) or not limitations:
            failures.append(f"{prefix}: history_limitations must be a non-empty array")
        events = timeline.get("events")
        if not isinstance(events, list) or not events:
            failures.append(f"{prefix}: events must be a non-empty array")
            continue
        previous: date | None = None
        for event_index, event in enumerate(events, start=1):
            label = f"{prefix} event {event_index}"
            try:
                event_date = date.fromisoformat(event.get("date", ""))
                if event_date > today:
                    failures.append(f"{label}: date is in the future")
                if previous and event_date < previous:
                    failures.append(f"{label}: events must be chronological")
                previous = event_date
            except ValueError:
                failures.append(f"{label}: invalid date")
            precision = event.get("date_precision", "day")
            if precision not in ALLOWED_PRECISION:
                failures.append(f"{label}: invalid date precision")
            if event.get("evidence_level") not in ALLOWED_LEVELS:
                failures.append(f"{label}: invalid evidence level")
            for field in ("type", "summary"):
                if not isinstance(event.get(field), str) or not event[field].strip():
                    failures.append(f"{label}: {field} must be non-empty")

    expected = set(achievement_by_slug)
    if seen != expected:
        missing = sorted(expected - seen)
        extra = sorted(seen - expected)
        if missing:
            failures.append("missing timelines: " + ", ".join(missing))
        if extra:
            failures.append("unexpected timelines: " + ", ".join(extra))
    return failures


def display_date(event: dict) -> str:
    precision = event.get("date_precision", "day")
    parsed = date.fromisoformat(event["date"])
    if precision == "year":
        return str(parsed.year)
    if precision == "month":
        return parsed.strftime("%B %Y")
    return parsed.strftime("%d %B %Y").lstrip("0")


def render_markdown(payload: dict, achievements: dict) -> str:
    names = {item["slug"]: item["name"] for item in achievements["achievements"]}
    lines = [
        "---",
        "layout: default",
        "title: Achievement verification timelines",
        "description: Dated verification history, evidence changes, and documented uncertainty for every canonical achievement.",
        "permalink: /verification-timelines/",
        "---",
        "",
        "## Achievement verification timelines",
        "",
        payload["timeline_scope"],
        "",
        f"**Timelines:** {len(payload['timelines'])}  ",
        f"**Schema version:** `{payload['schema_version']}`",
        "",
    ]
    for timeline in payload["timelines"]:
        name = names[timeline["achievement_slug"]]
        lines.extend([
            f"### {name}",
            "",
            f"**Last reviewed:** {timeline['last_reviewed']}",
            "",
            "| Date | Event | Evidence | Summary |",
            "|---|---|---|---|",
        ])
        for event in timeline["events"]:
            lines.append(
                f"| {display_date(event)} | {event['type']} | {event['evidence_level']} | {event['summary']} |"
            )
        lines.extend(["", "**Known history limitations**", ""])
        lines.extend(f"- {item}" for item in timeline["history_limitations"])
        lines.append("")
    lines.extend([
        "## Interpretation",
        "",
        "A timeline event records a dated review or supported historical point. It does not imply that the listed date is the achievement's original rollout date unless the event explicitly says so.",
        "",
        "Machine-readable timelines are available from [`/api/timelines.json`](../api/timelines.json).",
        "",
    ])
    return "\n".join(lines)


def render_api(payload: dict) -> str:
    return json.dumps({
        "api_version": "1.0.0",
        "schema_version": payload["schema_version"],
        "count": len(payload["timelines"]),
        "timeline_scope": payload["timeline_scope"],
        "timelines": payload["timelines"],
    }, indent=2, ensure_ascii=False) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and publish achievement verification timelines.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", default="verification-timeline-report.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = load(TIMELINES_PATH)
    achievements = load(ACHIEVEMENTS_PATH)
    evidence = load(EVIDENCE_PATH)
    failures = validate(payload, achievements, evidence)
    report = [
        "# Verification timeline validation",
        "",
        f"- Timelines: {len(payload.get('timelines', []))}",
        f"- Result: {'FAIL' if failures else 'PASS'}",
    ]
    if failures:
        report.extend(["", "## Failures", "", *[f"- {item}" for item in failures]])
    (ROOT / args.report).write_text("\n".join(report) + "\n", encoding="utf-8")
    if failures:
        print("\n".join(failures))
        return 1
    outputs = {
        MARKDOWN_PATH: render_markdown(payload, achievements),
        API_PATH: render_api(payload),
    }
    if args.check:
        drift = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if drift:
            print("Generated timeline outputs are stale: " + ", ".join(drift))
            return 1
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    print(f"Verification timelines passed for {len(payload['timelines'])} achievements.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
