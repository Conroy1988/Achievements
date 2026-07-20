from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
MISSION_API = ROOT / "api" / "acquisition-missions.json"
SCHEMA_PATH = ROOT / "data" / "mission-evidence-submission.schema.json"
FORM_PATH = ROOT / ".github" / "ISSUE_TEMPLATE" / "mission-evidence.yml"
TRIAGE_PATH = ROOT / "scripts" / "triage_mission_submission.py"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "mission-evidence-triage.yml"
API_PATH = ROOT / "api" / "mission-submission-schema.json"
DOC_PATH = ROOT / "docs" / "mission-execution-intake.md"
FORM_URL = "https://github.com/Conroy1988/Achievements/issues/new?template=mission-evidence.yml"

REQUIRED_SCHEMA_FIELDS = {
    "mission_id",
    "research_task_id",
    "claim_id",
    "contradiction_id",
    "achievement_slug",
    "observation_date",
    "result",
    "repository_visibility",
    "source_urls",
    "required_evidence",
    "environment_and_controls",
    "limitations",
    "safeguard_acknowledgement",
    "privacy_declaration",
    "consent",
}
REQUIRED_FORM_LABELS = {
    "Mission ID",
    "Research task ID",
    "Claim ID",
    "Contradiction ID",
    "Achievement",
    "Observation date",
    "Result",
    "Repository visibility",
    "Qualifying event time (UTC)",
    "First badge visibility time (UTC)",
    "Source URLs",
    "Required evidence values",
    "Environment and controls",
    "Limitations and failed attempts",
    "Safeguard declaration",
    "Privacy declaration",
    "Consent",
}


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def validate(missions: dict, schema: dict, form: str) -> list[str]:
    errors: list[str] = []
    mission_rows = missions.get("missions")
    if not isinstance(mission_rows, list) or len(mission_rows) != 8:
        errors.append("mission API must contain exactly eight missions")
    if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
        errors.append("mission submission schema must be a closed object")
    required = set(schema.get("required", []))
    if not REQUIRED_SCHEMA_FIELDS.issubset(required):
        errors.append("mission submission schema is missing required fields")
    properties = schema.get("properties", {})
    if set(properties) != REQUIRED_SCHEMA_FIELDS | {
        "qualifying_event_time_utc",
        "first_badge_visibility_time_utc",
    }:
        errors.append("mission submission schema properties do not match the contract")
    result_values = set(properties.get("result", {}).get("enum", []))
    if result_values != {"awarded", "not-awarded", "inconclusive", "blocked", "processing-delayed"}:
        errors.append("mission submission result enum is incomplete")
    for label in REQUIRED_FORM_LABELS:
        if f"label: {label}" not in form:
            errors.append(f"mission issue form is missing label: {label}")
    for mission in mission_rows or []:
        mission_id = mission.get("id", "unknown")
        if not mission.get("required_evidence"):
            errors.append(f"{mission_id}: required_evidence is empty")
        if len(mission.get("controls", [])) < 3:
            errors.append(f"{mission_id}: controls are incomplete")
        if len(mission.get("stop_conditions", [])) < 3:
            errors.append(f"{mission_id}: stop conditions are incomplete")
        if mission.get("artificial_activity_prohibited") is not True:
            errors.append(f"{mission_id}: artificial activity prohibition is missing")
        if mission.get("spam_prohibited") is not True:
            errors.append(f"{mission_id}: spam prohibition is missing")
        if mission.get("status") == "scheduled":
            for field in ("scheduled_check_at", "checkpoint_url", "no_action_before"):
                if not mission.get(field):
                    errors.append(f"{mission_id}: scheduled field {field} is missing")
    for path in (TRIAGE_PATH, WORKFLOW_PATH):
        if not path.is_file():
            errors.append(f"required intake file is missing: {path.relative_to(ROOT)}")
    return errors


def api_payload(missions: dict, schema: dict) -> dict:
    return {
        "api_version": "1.0.0",
        "schema_version": "1.0.0",
        "count": len(schema.get("properties", {})),
        "mission_count": len(missions.get("missions", [])),
        "form_url": FORM_URL,
        "schema": schema,
    }


def markdown(missions: dict) -> str:
    rows = sorted(missions["missions"], key=lambda item: item["rank"])
    lines = [
        "---",
        "layout: default",
        "title: Mission execution intake",
        "description: Structured intake, validation, privacy screening, and draft review packets for targeted evidence missions.",
        "permalink: /mission-execution-intake/",
        "---",
        "",
        "## Mission execution intake",
        "",
        "The mission intake converts a completed or blocked mission observation into a reviewable evidence packet. It does not unlock achievements, create qualifying activity, or promote claims automatically.",
        "",
        f"[Open the mission evidence form]({FORM_URL})",
        "",
        "## Submission matrix",
        "",
        "| Mission | Status | Achievement | Claims | Contradiction | Required evidence fields |",
        "|---|---|---|---|---|---:|",
    ]
    for mission in rows:
        lines.append(
            f"| `{mission['id']}` — {mission['title']} | {mission['status']} | "
            f"{mission['achievement_slug'] or 'cross-achievement'} | "
            f"{', '.join(mission['claim_ids']) or 'none'} | "
            f"{', '.join(mission['contradiction_ids']) or 'none'} | "
            f"{len(mission['required_evidence'])} |"
        )
    lines += [
        "",
        "## Intake checks",
        "",
        "1. The mission, task, claim, contradiction, and achievement relationships must match the published mission queue.",
        "2. Every required evidence key for the selected mission must be supplied using `key: value` lines.",
        "3. Scheduled missions are blocked until their published `no_action_before` timestamp.",
        "4. Public HTTPS sources, timestamps, environment controls, limitations, and result state are validated.",
        "5. Safeguard, privacy, and publication declarations are mandatory.",
        "6. Automated screening blocks credentials, email addresses, secret-like values, payment-card-like numbers, and prohibited material.",
        "7. Passing submissions create a draft packet and draft pull request for human review.",
        "",
        "## Required evidence format",
        "",
        "Copy each key from the selected mission and provide one value per line:",
        "",
        "```text",
        "public_pull_request_url: https://github.com/example/repository/pull/123",
        "final_commit_url: https://github.com/example/repository/commit/abc123",
        "merge_method: squash",
        "```",
        "",
        "Unknown keys, duplicated keys, empty values, and missing mission keys are rejected.",
        "",
        "## Review boundary",
        "",
        "Automated acceptance means only that the packet passed structural, relationship, timing, safeguard, and privacy checks. A maintainer must still inspect the public sources and decide whether the packet affects event evidence, a contradiction assessment, a threshold programme, or a canonical claim.",
        "",
        "## Machine-readable contract",
        "",
        "The submission schema is published at [`/api/mission-submission-schema.json`](../api/mission-submission-schema.json). The active mission requirements are published at [`/api/acquisition-missions.json`](../api/acquisition-missions.json).",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and publish mission execution intake.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", default="mission-intake-report.md")
    args = parser.parse_args()
    try:
        missions = load(MISSION_API)
        schema = load(SCHEMA_PATH)
        form = FORM_PATH.read_text(encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error)
        return 1
    errors = validate(missions, schema, form)
    report = [
        "# Mission execution intake validation",
        "",
        f"- Missions: {len(missions.get('missions', []))}",
        f"- Schema fields: {len(schema.get('properties', {}))}",
        f"- Result: {'FAIL' if errors else 'PASS'}",
    ]
    if errors:
        report += ["", "## Failures", ""] + [f"- {item}" for item in errors]
    (ROOT / args.report).write_text("\n".join(report) + "\n", encoding="utf-8")
    if errors:
        print("\n".join(errors))
        return 1
    outputs = {
        API_PATH: json.dumps(api_payload(missions, schema), indent=2, ensure_ascii=False) + "\n",
        DOC_PATH: markdown(missions),
    }
    if args.check:
        stale = [
            str(path.relative_to(ROOT))
            for path, expected in outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != expected
        ]
        if stale:
            print("Stale or missing mission intake outputs: " + ", ".join(stale))
            return 1
    else:
        for path, expected in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
    print(f"Mission intake passed: {len(missions['missions'])} missions and {len(schema['properties'])} schema fields.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
