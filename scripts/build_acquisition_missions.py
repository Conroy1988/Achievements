from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "acquisition-missions.json"
QUEUE_PATH = ROOT / "data" / "research-queue.json"
PROTOCOLS_PATH = ROOT / "data" / "reproduction-protocols.json"
CLAIMS_PATH = ROOT / "data" / "claims.json"
CONTRADICTIONS_PATH = ROOT / "data" / "contradictions.json"
INTELLIGENCE_PATH = ROOT / "api" / "evidence-intelligence.json"
API_PATH = ROOT / "api" / "acquisition-missions.json"
DOC_PATH = ROOT / "docs" / "targeted-evidence-missions.md"

MISSION_ID = re.compile(r"^MSN-[0-9]{3}$")
ALLOWED_STATUSES = {
    "participant-needed",
    "scheduled",
    "candidate-search",
    "passive-observation",
    "complete",
    "cancelled",
}
GATE_NAMES = {
    "claims_below_confirmed",
    "official_or_confirmed_claims",
    "open_contradictions",
    "coverage_score",
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


def validate(
    programme: dict,
    queue: dict,
    protocols: dict,
    claims: dict,
    contradictions: dict,
    intelligence: dict,
) -> list[str]:
    errors: list[str] = []
    missions = programme.get("missions")
    if not isinstance(missions, list) or not missions:
        return ["missions must be a non-empty array"]

    task_by_id = {item["id"]: item for item in queue.get("tasks", [])}
    protocol_by_id = {item["id"]: item for item in protocols.get("protocols", [])}
    claim_by_id = {item["id"]: item for item in claims.get("claims", [])}
    contradiction_ids = {item["id"] for item in contradictions.get("records", [])}
    pressure_by_slug = {
        item["achievement_slug"]: item["pressure_score"]
        for item in intelligence.get("achievements", [])
    }

    ids: set[str] = set()
    ranks: set[int] = set()
    targeted_claims: set[str] = set()
    targeted_contradictions: set[str] = set()

    for mission in missions:
        mission_id = mission.get("id", "")
        if not MISSION_ID.fullmatch(str(mission_id)):
            errors.append(f"invalid mission id: {mission_id!r}")
        elif mission_id in ids:
            errors.append(f"duplicate mission id: {mission_id}")
        ids.add(str(mission_id))

        rank = mission.get("rank")
        if not isinstance(rank, int) or rank < 1:
            errors.append(f"{mission_id}: rank must be a positive integer")
        elif rank in ranks:
            errors.append(f"{mission_id}: duplicate rank {rank}")
        else:
            ranks.add(rank)

        status = mission.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{mission_id}: invalid status {status!r}")

        slug = mission.get("achievement_slug")
        pressure = mission.get("pressure_score")
        if slug is not None:
            if slug not in pressure_by_slug:
                errors.append(f"{mission_id}: unknown achievement slug {slug!r}")
            elif pressure != pressure_by_slug[slug]:
                errors.append(
                    f"{mission_id}: pressure score {pressure!r} does not match intelligence value {pressure_by_slug[slug]}"
                )
        elif pressure != 0:
            errors.append(f"{mission_id}: cross-achievement mission pressure must be 0")

        task_ids = mission.get("research_task_ids")
        if not isinstance(task_ids, list) or not task_ids:
            errors.append(f"{mission_id}: at least one research task is required")
            task_ids = []
        for task_id in task_ids:
            task = task_by_id.get(task_id)
            if not task:
                errors.append(f"{mission_id}: unknown research task {task_id}")
            elif slug is not None and task.get("achievement_slug") not in {slug, None}:
                errors.append(f"{mission_id}: research task {task_id} belongs to another achievement")

        protocol_ids = mission.get("protocol_ids")
        if not isinstance(protocol_ids, list):
            errors.append(f"{mission_id}: protocol_ids must be an array")
            protocol_ids = []
        for protocol_id in protocol_ids:
            protocol = protocol_by_id.get(protocol_id)
            if not protocol:
                errors.append(f"{mission_id}: unknown protocol {protocol_id}")
            elif slug is not None and protocol.get("achievement_slug") != slug:
                errors.append(f"{mission_id}: protocol {protocol_id} belongs to another achievement")
            elif not set(protocol.get("research_task_ids", [])).intersection(task_ids):
                errors.append(f"{mission_id}: protocol {protocol_id} is not linked to a mission task")

        claim_ids = mission.get("claim_ids")
        if not isinstance(claim_ids, list):
            errors.append(f"{mission_id}: claim_ids must be an array")
            claim_ids = []
        for claim_id in claim_ids:
            claim = claim_by_id.get(claim_id)
            if not claim:
                errors.append(f"{mission_id}: unknown claim {claim_id}")
            elif slug is not None and claim.get("achievement_slug") != slug:
                errors.append(f"{mission_id}: claim {claim_id} belongs to another achievement")
            targeted_claims.add(claim_id)

        contradiction_values = mission.get("contradiction_ids")
        if not isinstance(contradiction_values, list):
            errors.append(f"{mission_id}: contradiction_ids must be an array")
            contradiction_values = []
        unknown_contradictions = set(contradiction_values) - contradiction_ids
        if unknown_contradictions:
            errors.append(
                f"{mission_id}: unknown contradictions: {', '.join(sorted(unknown_contradictions))}"
            )
        targeted_contradictions.update(contradiction_values)

        for field, minimum in (
            ("prerequisites", 3),
            ("controls", 3),
            ("steps", 4),
            ("required_evidence", 5),
            ("stop_conditions", 3),
            ("ethics", 2),
        ):
            value = mission.get(field)
            if not isinstance(value, list) or len(value) < minimum:
                errors.append(f"{mission_id}: {field} requires at least {minimum} entries")
            elif any(not isinstance(item, str) or not item.strip() for item in value):
                errors.append(f"{mission_id}: {field} must contain non-empty strings")

        if mission.get("artificial_activity_prohibited") is not True:
            errors.append(f"{mission_id}: artificial activity must be explicitly prohibited")
        if mission.get("spam_prohibited") is not True:
            errors.append(f"{mission_id}: spam must be explicitly prohibited")

        gates = mission.get("release_gate_relevance")
        if not isinstance(gates, list) or not gates:
            errors.append(f"{mission_id}: release_gate_relevance must be a non-empty array")
        elif set(gates) - GATE_NAMES:
            errors.append(f"{mission_id}: unknown release gate names")

        targets = mission.get("promotion_targets")
        if not isinstance(targets, list):
            errors.append(f"{mission_id}: promotion_targets must be an array")
            targets = []
        for target in targets:
            if not isinstance(target, dict):
                errors.append(f"{mission_id}: promotion target must be an object")
                continue
            if target.get("claim_id") not in claim_ids:
                errors.append(f"{mission_id}: promotion target references a non-mission claim")
            if target.get("target_level") not in {"observed", "confirmed", "official"}:
                errors.append(f"{mission_id}: invalid promotion target level")

        if status == "scheduled":
            for field in ("scheduled_check_at", "no_action_before"):
                try:
                    datetime.fromisoformat(mission.get(field, ""))
                except (TypeError, ValueError):
                    errors.append(f"{mission_id}: scheduled mission requires valid {field}")
            if not public_github_url(mission.get("checkpoint_url")):
                errors.append(f"{mission_id}: scheduled mission requires a public GitHub checkpoint URL")

    expected_ranks = set(range(1, len(missions) + 1))
    if ranks != expected_ranks:
        errors.append("mission ranks must be contiguous from 1")

    ranked = [item for item in missions if item.get("achievement_slug") is not None]
    expected_order = sorted(
        ranked,
        key=lambda item: (-pressure_by_slug[item["achievement_slug"]], item["achievement_slug"]),
    )
    if [item["id"] for item in ranked] != [item["id"] for item in expected_order]:
        errors.append("achievement missions must follow descending evidence-intelligence pressure")

    if targeted_contradictions != contradiction_ids:
        missing = sorted(contradiction_ids - targeted_contradictions)
        errors.append("missions do not target every contradiction: " + ", ".join(missing))

    if len(targeted_claims) < 10:
        errors.append("missions must target at least ten unresolved claims")

    scheduled = [item for item in missions if item.get("status") == "scheduled"]
    if len(scheduled) != 1 or scheduled[0].get("achievement_slug") != "pull-shark":
        errors.append("exactly one scheduled Pull Shark checkpoint is required")

    return errors


def payload(programme: dict, intelligence: dict) -> dict:
    missions = sorted(programme["missions"], key=lambda item: item["rank"])
    statuses = Counter(item["status"] for item in missions)
    claims = sorted({claim_id for item in missions for claim_id in item["claim_ids"]})
    contradictions = sorted({value for item in missions for value in item["contradiction_ids"]})
    tasks = sorted({value for item in missions for value in item["research_task_ids"]})
    protocols = sorted({value for item in missions for value in item["protocol_ids"]})
    gates = sorted({value for item in missions for value in item["release_gate_relevance"]})
    return {
        "api_version": "1.0.0",
        "schema_version": programme["schema_version"],
        "status": "live",
        "policy": "/Achievements/targeted-evidence-missions/",
        "mission_date": programme["mission_date"],
        "count": len(missions),
        "metrics": {
            "mission_count": len(missions),
            "achievement_mission_count": sum(item["achievement_slug"] is not None for item in missions),
            "scheduled_count": statuses["scheduled"],
            "participant_needed_count": statuses["participant-needed"],
            "candidate_search_count": statuses["candidate-search"],
            "passive_observation_count": statuses["passive-observation"],
            "targeted_claim_count": len(claims),
            "targeted_contradiction_count": len(contradictions),
            "research_task_count": len(tasks),
            "protocol_count": len(protocols),
        },
        "release_gaps_at_launch": intelligence.get("release_gaps", {}),
        "targeted_claim_ids": claims,
        "targeted_contradiction_ids": contradictions,
        "research_task_ids": tasks,
        "protocol_ids": protocols,
        "release_gate_names": gates,
        "by_status": dict(sorted(statuses.items())),
        "missions": missions,
    }


def markdown(programme: dict, intelligence: dict) -> str:
    output = payload(programme, intelligence)
    missions = output["missions"]
    lines = [
        "---",
        "layout: default",
        "title: Targeted evidence acquisition missions",
        "description: Ranked, ethical, fail-closed missions for converting the evidence-intelligence backlog into adjudicable observations.",
        "permalink: /targeted-evidence-missions/",
        "---",
        "",
        "## Targeted evidence acquisition missions",
        "",
        "These missions convert the evidence-intelligence pressure ranking into bounded research work. They do not authorise spam, false attribution, repository manipulation, achievement farming, or automatic claim promotion.",
        "",
        f"**Missions:** {output['metrics']['mission_count']}  ",
        f"**Claims targeted:** {output['metrics']['targeted_claim_count']}  ",
        f"**Contradictions targeted:** {output['metrics']['targeted_contradiction_count']}  ",
        f"**Scheduled checkpoints:** {output['metrics']['scheduled_count']}  ",
        f"**Schema:** `{programme['schema_version']}`",
        "",
        "## Mission board",
        "",
        "| Rank | Mission | Achievement | Pressure | Status | Primary target |",
        "|---:|---|---|---:|---|---|",
    ]
    for mission in missions:
        achievement = mission["achievement_slug"] or "cross-achievement"
        targets = ", ".join(item["claim_id"] for item in mission["promotion_targets"]) or "processing evidence"
        lines.append(
            f"| {mission['rank']} | `{mission['id']}` — {mission['title']} | {achievement} | "
            f"{mission['pressure_score']} | {mission['status']} | {targets} |"
        )

    lines.extend([
        "",
        "## Non-negotiable operating rules",
        "",
        "- No meaningless issues, pull requests, commits, Discussions, answers, sponsorships, stars, or co-author trailers may be created for a mission.",
        "- Existing repository protections and maintainer decisions take precedence over completing a matrix cell.",
        "- Negative, delayed, blocked, and inconclusive outcomes remain part of the evidence package.",
        "- Mission completion produces a reviewable evidence package; it never changes a canonical claim automatically.",
        "",
        "## Release-gap context at launch",
        "",
    ])
    gaps = output["release_gaps_at_launch"]
    for key, value in sorted(gaps.items()):
        lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")

    lines.extend(["", "## Mission details", ""])
    for mission in missions:
        lines.extend([
            f"### {mission['rank']}. {mission['id']} — {mission['title']}",
            "",
            f"**Achievement:** `{mission['achievement_slug'] or 'cross-achievement'}`  ",
            f"**Status:** `{mission['status']}`  ",
            f"**Pressure:** {mission['pressure_score']}  ",
            f"**Claims:** {', '.join(f'`{value}`' for value in mission['claim_ids']) or 'none'}  ",
            f"**Contradictions:** {', '.join(f'`{value}`' for value in mission['contradiction_ids']) or 'none'}  ",
            f"**Research tasks:** {', '.join(f'`{value}`' for value in mission['research_task_ids'])}  ",
            f"**Protocols:** {', '.join(f'`{value}`' for value in mission['protocol_ids']) or 'none'}",
            "",
            mission["objective"],
            "",
        ])
        if mission.get("scheduled_check_at"):
            lines.extend([
                f"**Scheduled checkpoint:** `{mission['scheduled_check_at']}`  ",
                f"**No-action-before:** `{mission['no_action_before']}`  ",
                f"**Checkpoint:** [{mission['checkpoint_url']}]({mission['checkpoint_url']})",
                "",
            ])
        for heading, field in (
            ("Prerequisites", "prerequisites"),
            ("Controls", "controls"),
            ("Execution", "steps"),
            ("Required evidence", "required_evidence"),
            ("Stop conditions", "stop_conditions"),
            ("Ethics", "ethics"),
        ):
            lines.extend([f"**{heading}**", ""])
            lines.extend(f"- {value}" for value in mission[field])
            lines.append("")

    lines.extend([
        "## Machine-readable mission queue",
        "",
        "The validated mission queue is published at [`/api/acquisition-missions.json`](../api/acquisition-missions.json).",
        "",
    ])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and publish targeted evidence acquisition missions.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", default="acquisition-missions-report.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        programme = load(DATA_PATH)
        queue = load(QUEUE_PATH)
        protocols = load(PROTOCOLS_PATH)
        claims = load(CLAIMS_PATH)
        contradictions = load(CONTRADICTIONS_PATH)
        intelligence = load(INTELLIGENCE_PATH)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error)
        return 1

    errors = validate(programme, queue, protocols, claims, contradictions, intelligence)
    report = [
        "# Acquisition mission validation",
        "",
        f"- Missions: {len(programme.get('missions', []))}",
        f"- Result: {'FAIL' if errors else 'PASS'}",
    ]
    if errors:
        report.extend(["", "## Failures", "", *[f"- {error}" for error in errors]])
    (ROOT / args.report).write_text("\n".join(report) + "\n", encoding="utf-8")
    if errors:
        print("\n".join(errors))
        return 1

    outputs = {
        API_PATH: json.dumps(payload(programme, intelligence), indent=2, ensure_ascii=False) + "\n",
        DOC_PATH: markdown(programme, intelligence),
    }
    if args.check:
        stale = [
            str(path.relative_to(ROOT))
            for path, expected in outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != expected
        ]
        if stale:
            print("Stale or missing acquisition mission outputs: " + ", ".join(stale))
            return 1
    else:
        for path, expected in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")

    print(
        "Acquisition missions passed: "
        f"{len(programme['missions'])} missions targeting "
        f"{payload(programme, intelligence)['metrics']['targeted_claim_count']} claims."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
