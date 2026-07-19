from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
API = ROOT / "api"
DOCS = ROOT / "docs"
LEVEL = {"official": 100, "confirmed": 85, "observed": 60, "community-reported": 35, "unknown": 0}


def load(name: str) -> dict:
    value = json.loads((DATA / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"data/{name} must contain a JSON object")
    return value


def dump(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def validate(
    achievements: dict,
    claims: dict,
    queue: dict,
    contradictions: dict,
    protocols: dict,
    auditor: dict,
    submission_schema: dict,
) -> list[str]:
    errors: list[str] = []
    achievement_ids = {item["slug"] for item in achievements.get("achievements", [])}
    task_ids = {item["id"] for item in queue.get("tasks", [])}
    claim_rows = claims.get("claims", [])
    claim_ids = {item["id"] for item in claim_rows}

    if len(task_ids) != len(queue.get("tasks", [])):
        errors.append("research task IDs must be unique")

    weak_claims = [
        item for item in claim_rows
        if LEVEL.get(item.get("evidence_level"), -1) < 85
    ]
    unassigned = [
        item["id"] for item in weak_claims
        if not item.get("research_task_ids")
    ]
    if unassigned:
        errors.append("weak claims without research tasks: " + ", ".join(unassigned))

    for claim in claim_rows:
        if claim.get("achievement_slug") not in achievement_ids:
            errors.append(f"{claim.get('id', 'unknown')}: unknown achievement")
        unknown_tasks = set(claim.get("research_task_ids", [])) - task_ids
        if unknown_tasks:
            errors.append(
                f"{claim.get('id', 'unknown')}: unknown research tasks "
                + ", ".join(sorted(unknown_tasks))
            )

    contradiction_ids = {
        item["id"] for item in contradictions.get("records", [])
    }
    if len(contradiction_ids) != len(contradictions.get("records", [])):
        errors.append("contradiction IDs must be unique")

    protocol_rows = protocols.get("protocols", [])
    protocol_ids = {item.get("id") for item in protocol_rows}
    if len(protocol_ids) != len(protocol_rows) or any(
        not isinstance(item, str) or not re.fullmatch(r"LAB-[0-9]{3}", item)
        for item in protocol_ids
    ):
        errors.append("protocol IDs must be unique LAB-### values")

    for protocol in protocol_rows:
        protocol_id = protocol.get("id", "unknown")
        if protocol.get("achievement_slug") not in achievement_ids:
            errors.append(f"{protocol_id}: unknown achievement")
        unknown_tasks = set(protocol.get("research_task_ids", [])) - task_ids
        if unknown_tasks:
            errors.append(
                f"{protocol_id}: unknown research tasks "
                + ", ".join(sorted(unknown_tasks))
            )
        for field, minimum in (
            ("ethics", 2),
            ("prerequisites", 2),
            ("variables", 2),
            ("steps", 4),
            ("required_observations", 3),
            ("stop_conditions", 2),
            ("privacy_rules", 2),
        ):
            value = protocol.get(field)
            if not isinstance(value, list) or len(value) < minimum:
                errors.append(f"{protocol_id}: {field} requires at least {minimum} entries")

    rules = auditor.get("rules", [])
    rule_slugs = [item.get("achievement_slug") for item in rules]
    if set(rule_slugs) != achievement_ids or len(rule_slugs) != len(set(rule_slugs)):
        errors.append("auditor rules must cover every achievement exactly once")
    for rule in rules:
        if not rule.get("limitations") or rule.get("confidence") not in {
            "approximate", "unknown", "historical"
        }:
            errors.append(
                f"{rule.get('achievement_slug', 'unknown')}: invalid auditor rule"
            )

    required_schema_fields = {
        "research_task_id",
        "claim_id",
        "achievement_slug",
        "observation_date",
        "result",
        "privacy_declaration",
        "consent",
    }
    if submission_schema.get("type") != "object":
        errors.append("submission schema must describe an object")
    if not required_schema_fields.issubset(set(submission_schema.get("required", []))):
        errors.append("submission schema is missing required evidence fields")

    return errors


def command_centre(
    achievements: dict,
    claims: dict,
    queue: dict,
    contradictions: dict,
    protocols: dict,
) -> dict:
    claim_rows = claims["claims"]
    weak = [
        item for item in claim_rows
        if LEVEL[item["evidence_level"]] < 85
    ]
    unassigned = [
        item["id"] for item in weak
        if not item["research_task_ids"]
    ]
    tasks = queue["tasks"]
    open_tasks = [item for item in tasks if item["status"] != "resolved"]
    open_disputes = [
        item for item in contradictions["records"]
        if item["status"] != "resolved"
    ]
    return {
        "api_version": "1.0.0",
        "schema_version": "1.0.0",
        "count": 1,
        "metrics": {
            "achievement_count": len(achievements["achievements"]),
            "active_achievement_count": sum(
                item["status"] == "active"
                for item in achievements["achievements"]
            ),
            "claim_count": len(claim_rows),
            "weak_claim_count": len(weak),
            "unassigned_gap_count": len(unassigned),
            "research_task_count": len(tasks),
            "open_research_task_count": len(open_tasks),
            "open_contradiction_count": len(open_disputes),
            "reproduction_protocol_count": len(protocols["protocols"]),
        },
        "targets": {
            "operational_health": 100,
            "minimum_evidence_coverage": 70,
            "unassigned_gap_count": 0,
            "maximum_open_contradictions": 3,
            "minimum_confirmed_active_triggers": 5,
        },
        "routes": {
            "command_centre": "/Achievements/research-command-centre/",
            "profile_auditor": "/Achievements/profile-auditor/",
            "reproduction_lab": "/Achievements/reproduction-lab/",
            "research_hub": "/Achievements/research-hub/",
        },
    }


def build(
    achievements: dict,
    claims: dict,
    queue: dict,
    contradictions: dict,
    protocols: dict,
    auditor: dict,
    submission_schema: dict,
) -> dict[Path, str]:
    return {
        API / "lab-protocols.json": dump({
            "api_version": "1.0.0",
            "schema_version": protocols["schema_version"],
            "count": len(protocols["protocols"]),
            "protocols": protocols["protocols"],
        }),
        API / "auditor-rules.json": dump({
            "api_version": "1.0.0",
            "schema_version": auditor["schema_version"],
            "count": len(auditor["rules"]),
            "scope_statement": auditor["scope_statement"],
            "rules": auditor["rules"],
        }),
        API / "submission-schema.json": dump({
            "api_version": "1.0.0",
            "schema_version": "1.0.0",
            "count": len(submission_schema.get("properties", {})),
            "schema": submission_schema,
        }),
        API / "command-centre.json": dump(command_centre(
            achievements, claims, queue, contradictions, protocols
        )),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and publish evidence-operations infrastructure."
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", default="evidence-operations-report.md")
    args = parser.parse_args()

    try:
        achievements = load("achievements.json")
        claims = load("claims.json")
        queue = load("research-queue.json")
        contradictions = load("contradictions.json")
        protocols = load("reproduction-protocols.json")
        auditor = load("profile-auditor-rules.json")
        submission_schema = load("evidence-submission.schema.json")
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as error:
        print(error)
        return 1

    errors = validate(
        achievements,
        claims,
        queue,
        contradictions,
        protocols,
        auditor,
        submission_schema,
    )
    report = [
        "# Evidence operations validation",
        "",
        f"- Research tasks: {len(queue.get('tasks', []))}",
        f"- Reproduction protocols: {len(protocols.get('protocols', []))}",
        f"- Auditor rules: {len(auditor.get('rules', []))}",
        f"- Result: {'FAIL' if errors else 'PASS'}",
    ]
    if errors:
        report.extend(["", "## Failures", "", *[f"- {item}" for item in errors]])
    (ROOT / args.report).write_text("\n".join(report) + "\n", encoding="utf-8")

    if errors:
        print("\n".join(errors))
        return 1

    outputs = build(
        achievements,
        claims,
        queue,
        contradictions,
        protocols,
        auditor,
        submission_schema,
    )
    required_docs = [
        DOCS / "reproduction-lab.md",
        ROOT / "profile-auditor.md",
        ROOT / "research-command-centre.md",
        ROOT / "evidence-submission.md",
    ]

    if args.check:
        stale = [
            str(path.relative_to(ROOT))
            for path, content in outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != content
        ]
        missing = [
            str(path.relative_to(ROOT))
            for path in required_docs
            if not path.is_file()
        ]
        if stale or missing:
            print("Stale or missing outputs: " + ", ".join(stale + missing))
            return 1
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    print(
        "Evidence operations passed: "
        f"{len(queue['tasks'])} tasks, "
        f"{len(protocols['protocols'])} protocols, "
        f"{len(outputs)} API outputs."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
