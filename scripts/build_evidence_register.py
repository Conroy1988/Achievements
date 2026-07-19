from __future__ import annotations

from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REGISTER_PATH = ROOT / "data" / "evidence-register.json"
ACHIEVEMENTS_PATH = ROOT / "data" / "achievements.json"
MARKDOWN_PATH = ROOT / "docs" / "evidence-register.md"
API_PATH = ROOT / "api" / "evidence.json"
ID_PATTERN = re.compile(r"^EVD-(\d{4})-(\d{3})$")
ALLOWED_LEVELS = {"official", "confirmed", "observed", "community-reported", "unknown"}
ALLOWED_DECISIONS = {"accepted", "accepted-with-limitations", "provisional", "rejected", "needs-review"}
ALLOWED_PRIVACY = {"public-no-personal-data", "public-no-financial-data", "redacted", "withheld"}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_url(value: str) -> bool:
    parsed = urlsplit(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def validate(register: dict, achievements: dict) -> list[str]:
    failures: list[str] = []
    records = register.get("records")
    catalogue = achievements.get("achievements")
    if not isinstance(records, list):
        return ["records must be an array"]
    if not isinstance(catalogue, list):
        return ["achievement catalogue is invalid"]

    achievement_by_slug = {item["slug"]: item for item in catalogue}
    ids: set[str] = set()
    slugs: set[str] = set()
    today = date.today()

    for index, record in enumerate(records, start=1):
        prefix = f"record {index}"
        record_id = record.get("id", "")
        if not ID_PATTERN.fullmatch(record_id):
            failures.append(f"{prefix}: invalid id {record_id!r}")
        elif record_id in ids:
            failures.append(f"{prefix}: duplicate id {record_id}")
        ids.add(record_id)

        slug = record.get("achievement_slug", "")
        achievement = achievement_by_slug.get(slug)
        if achievement is None:
            failures.append(f"{prefix}: unknown achievement slug {slug!r}")
            continue
        if slug in slugs:
            failures.append(f"{prefix}: duplicate baseline record for {slug}")
        slugs.add(slug)

        if record.get("guide_path") != achievement.get("guide_path"):
            failures.append(f"{record_id}: guide path does not match the canonical catalogue")
        if not (ROOT / record.get("guide_path", "")).is_file():
            failures.append(f"{record_id}: guide file does not exist")

        level = record.get("evidence_level")
        if level not in ALLOWED_LEVELS:
            failures.append(f"{record_id}: invalid evidence level {level!r}")
        expected_level = achievement.get("evidence", {}).get("trigger")
        if level != expected_level:
            failures.append(f"{record_id}: evidence level {level!r} does not match trigger classification {expected_level!r}")

        if record.get("reviewer_decision") not in ALLOWED_DECISIONS:
            failures.append(f"{record_id}: invalid reviewer decision")
        if record.get("privacy_status") not in ALLOWED_PRIVACY:
            failures.append(f"{record_id}: invalid privacy status")

        for field in ("observed_at", "submitted_at"):
            try:
                parsed_date = date.fromisoformat(record.get(field, ""))
                if parsed_date > today:
                    failures.append(f"{record_id}: {field} is in the future")
            except ValueError:
                failures.append(f"{record_id}: invalid {field}")

        for field in ("source_urls", "archive_urls"):
            values = record.get(field)
            if not isinstance(values, list):
                failures.append(f"{record_id}: {field} must be an array")
                continue
            if len(values) != len(set(values)):
                failures.append(f"{record_id}: duplicate URL in {field}")
            for value in values:
                if not isinstance(value, str) or not validate_url(value):
                    failures.append(f"{record_id}: invalid public HTTPS URL in {field}")

        if not isinstance(record.get("contradictory_evidence"), list):
            failures.append(f"{record_id}: contradictory_evidence must be an array")
        for text_field in ("claim", "guide_section", "notes", "reproduction_status"):
            if not isinstance(record.get(text_field), str) or not record[text_field].strip():
                failures.append(f"{record_id}: {text_field} must be non-empty")

    expected_slugs = set(achievement_by_slug)
    if slugs != expected_slugs:
        missing = sorted(expected_slugs - slugs)
        extra = sorted(slugs - expected_slugs)
        if missing:
            failures.append(f"missing evidence records: {', '.join(missing)}")
        if extra:
            failures.append(f"unexpected evidence records: {', '.join(extra)}")
    return failures


def markdown(register: dict, achievements: dict) -> str:
    names = {item["slug"]: item["name"] for item in achievements["achievements"]}
    records = sorted(register["records"], key=lambda item: item["id"])
    lines = [
        "---",
        "layout: default",
        "title: Public evidence register",
        "description: Privacy-safe, reviewable evidence records supporting the encyclopedia's achievement claims.",
        "permalink: /evidence-register/",
        "---",
        "",
        "## Public evidence register",
        "",
        "This register links each canonical achievement to a dated, privacy-safe evidence record. It exposes uncertainty and limitations instead of converting community reports into official claims.",
        "",
        f"**Schema version:** `{register['schema_version']}`  ",
        f"**Records:** {len(records)}  ",
        "**Privacy policy:** [Evidence register policy](evidence-register-policy.md)",
        "",
        "| Record | Achievement | Evidence | Reproduction | Decision | Observed |",
        "|---|---|---|---|---|---|",
    ]
    for record in records:
        guide = record["guide_path"]
        name = names[record["achievement_slug"]]
        lines.append(
            f"| `{record['id']}` | [{name}](../{guide}) | {record['evidence_level']} | "
            f"{record['reproduction_status']} | {record['reviewer_decision']} | {record['observed_at']} |"
        )
    lines.extend([
        "",
        "## Record details",
        "",
    ])
    for record in records:
        name = names[record["achievement_slug"]]
        lines.extend([
            f"### {record['id']} — {name}",
            "",
            f"**Claim:** {record['claim']}",
            "",
            f"**Guide location:** `{record['guide_path']}` — {record['guide_section']}",
            "",
            f"**Privacy:** `{record['privacy_status']}`  ",
            f"**Sources:** {len(record['source_urls'])} public source(s), {len(record['archive_urls'])} archive source(s)  ",
            f"**Contradictory evidence:** {len(record['contradictory_evidence'])} item(s)",
            "",
            record["notes"],
            "",
        ])
    lines.extend([
        "## Using this register",
        "",
        "Evidence classification, reviewer decision, and reproduction status are separate fields. Consumers must preserve all three when presenting a record.",
        "",
        "Machine-readable data is available from [`/api/evidence.json`](../api/evidence.json).",
        "",
    ])
    return "\n".join(lines)


def api_payload(register: dict) -> str:
    payload = {
        "api_version": "1.0.0",
        "schema_version": register["schema_version"],
        "count": len(register["records"]),
        "privacy_policy": "/Achievements/evidence-policy/",
        "records": sorted(register["records"], key=lambda item: item["id"]),
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and publish the public evidence register.")
    parser.add_argument("--check", action="store_true", help="fail when committed outputs differ from generated content")
    parser.add_argument("--report", default="evidence-register-report.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    register = read_json(REGISTER_PATH)
    achievements = read_json(ACHIEVEMENTS_PATH)
    failures = validate(register, achievements)
    report_path = ROOT / args.report
    report_lines = [
        "# Evidence register validation",
        "",
        f"- Records: {len(register.get('records', []))}",
        f"- Achievements: {len(achievements.get('achievements', []))}",
        f"- Result: {'FAIL' if failures else 'PASS'}",
    ]
    if failures:
        report_lines.extend(["", "## Failures", "", *[f"- {failure}" for failure in failures]])
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    if failures:
        print("\n".join(failures))
        return 1

    outputs = {
        MARKDOWN_PATH: markdown(register, achievements),
        API_PATH: api_payload(register),
    }
    if args.check:
        drift = []
        for path, expected in outputs.items():
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                drift.append(str(path.relative_to(ROOT)))
        if drift:
            print("Generated evidence outputs are stale: " + ", ".join(drift))
            return 1
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    print(f"Evidence register passed with {len(register['records'])} records.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
