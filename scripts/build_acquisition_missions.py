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
DATA = ROOT / "data"
API = ROOT / "api"
DOCS = ROOT / "docs"
MISSION_ID = re.compile(r"^MSN-[0-9]{3}$")
STATUSES = {"active", "participant-needed", "scheduled", "candidate-search", "passive-observation", "blocked", "complete", "cancelled"}
GATES = {"claims_below_confirmed", "official_or_confirmed_claims", "open_contradictions", "coverage_score"}


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


def validate(programme: dict, queue: dict, protocols: dict, claims: dict, contradictions: dict, intelligence: dict) -> list[str]:
    errors: list[str] = []
    missions = programme.get("missions")
    if not isinstance(missions, list) or not missions:
        return ["missions must be a non-empty array"]
    task_by_id = {row["id"]: row for row in queue.get("tasks", [])}
    protocol_by_id = {row["id"]: row for row in protocols.get("protocols", [])}
    claim_by_id = {row["id"]: row for row in claims.get("claims", [])}
    contradiction_ids = {row["id"] for row in contradictions.get("records", [])}
    pressure = {row["achievement_slug"]: row["pressure_score"] for row in intelligence.get("achievements", [])}
    ids: set[str] = set()
    ranks: set[int] = set()
    all_claims: set[str] = set()
    all_contradictions: set[str] = set()

    for mission in missions:
        mid = mission.get("id", "")
        if not MISSION_ID.fullmatch(str(mid)) or mid in ids:
            errors.append(f"invalid or duplicate mission id: {mid!r}")
        ids.add(str(mid))
        rank = mission.get("rank")
        if not isinstance(rank, int) or rank < 1 or rank in ranks:
            errors.append(f"{mid}: invalid or duplicate rank")
        else:
            ranks.add(rank)
        status = mission.get("status")
        if status not in STATUSES:
            errors.append(f"{mid}: invalid status")
        slug = mission.get("achievement_slug")
        if slug is None:
            if mission.get("pressure_score") != 0:
                errors.append(f"{mid}: cross-achievement pressure must be zero")
        elif slug not in pressure or mission.get("pressure_score") != pressure[slug]:
            errors.append(f"{mid}: pressure score does not match evidence intelligence")

        task_ids = mission.get("research_task_ids", [])
        if not task_ids:
            errors.append(f"{mid}: at least one research task is required")
        for task_id in task_ids:
            task = task_by_id.get(task_id)
            if not task:
                errors.append(f"{mid}: unknown research task {task_id}")
            elif slug is not None and task.get("achievement_slug") not in {slug, None}:
                errors.append(f"{mid}: task {task_id} belongs to another achievement")

        for protocol_id in mission.get("protocol_ids", []):
            protocol = protocol_by_id.get(protocol_id)
            if not protocol:
                errors.append(f"{mid}: unknown protocol {protocol_id}")
            elif slug is not None and protocol.get("achievement_slug") != slug:
                errors.append(f"{mid}: protocol {protocol_id} belongs to another achievement")
            elif not set(protocol.get("research_task_ids", [])).intersection(task_ids):
                errors.append(f"{mid}: protocol {protocol_id} is not linked to a mission task")

        claim_ids = mission.get("claim_ids", [])
        for claim_id in claim_ids:
            claim = claim_by_id.get(claim_id)
            if not claim:
                errors.append(f"{mid}: unknown claim {claim_id}")
            elif slug is not None and claim.get("achievement_slug") != slug:
                errors.append(f"{mid}: claim {claim_id} belongs to another achievement")
            all_claims.add(claim_id)
        contradiction_values = mission.get("contradiction_ids", [])
        unknown = set(contradiction_values) - contradiction_ids
        if unknown:
            errors.append(f"{mid}: unknown contradictions: {', '.join(sorted(unknown))}")
        all_contradictions.update(contradiction_values)

        for field, minimum in (("prerequisites", 3), ("controls", 3), ("steps", 4), ("required_evidence", 5), ("stop_conditions", 3), ("ethics", 2)):
            value = mission.get(field)
            if not isinstance(value, list) or len(value) < minimum or any(not isinstance(item, str) or not item.strip() for item in value):
                errors.append(f"{mid}: invalid {field}")
        if mission.get("artificial_activity_prohibited") is not True or mission.get("spam_prohibited") is not True:
            errors.append(f"{mid}: anti-abuse safeguards must be true")
        gates = mission.get("release_gate_relevance", [])
        if not gates or set(gates) - GATES:
            errors.append(f"{mid}: invalid release-gate relevance")
        for target in mission.get("promotion_targets", []):
            if target.get("claim_id") not in claim_ids or target.get("target_level") not in {"observed", "confirmed", "official"}:
                errors.append(f"{mid}: invalid promotion target")
        if status == "scheduled":
            for field in ("scheduled_check_at", "no_action_before"):
                try:
                    datetime.fromisoformat(mission.get(field, ""))
                except (TypeError, ValueError):
                    errors.append(f"{mid}: invalid {field}")
            if not github_url(mission.get("checkpoint_url")):
                errors.append(f"{mid}: invalid checkpoint URL")

    if ranks != set(range(1, len(missions) + 1)):
        errors.append("mission ranks must be contiguous")
    ranked = [row for row in missions if row.get("achievement_slug") is not None]
    expected = sorted(ranked, key=lambda row: (-pressure[row["achievement_slug"]], row["achievement_slug"]))
    if [row["id"] for row in ranked] != [row["id"] for row in expected]:
        errors.append("achievement missions must follow descending pressure")
    if all_contradictions != contradiction_ids:
        errors.append("missions must target all contradictions")
    if len(all_claims) < 10:
        errors.append("missions must target at least ten claims")
    scheduled = [row for row in missions if row.get("status") == "scheduled"]
    if len(scheduled) != 1 or scheduled[0].get("achievement_slug") != "pull-shark":
        errors.append("exactly one scheduled Pull Shark checkpoint is required")
    active = [row for row in missions if row.get("status") == "active"]
    if len(active) != 1 or active[0].get("id") != programme.get("primary_mission_id") or active[0].get("achievement_slug") != "yolo":
        errors.append("exactly one active YOLO primary mission is required")
    if programme.get("campaign_version") != "v1.5.0":
        errors.append("mission programme must identify the v1.5.0 campaign")
    return errors


def summary(row: dict) -> dict:
    fields = (
        "id", "rank", "achievement_slug", "title", "status", "pressure_score", "claim_ids",
        "contradiction_ids", "research_task_ids", "protocol_ids", "objective", "promotion_targets",
        "release_gate_relevance", "controls", "required_evidence", "stop_conditions", "ethics",
        "artificial_activity_prohibited", "spam_prohibited",
    )
    result = {field: row[field] for field in fields}
    for field in ("scheduled_check_at", "checkpoint_url", "no_action_before"):
        if field in row:
            result[field] = row[field]
    return result


def payload(programme: dict, intelligence: dict) -> dict:
    missions = sorted(programme["missions"], key=lambda row: row["rank"])
    statuses = Counter(row["status"] for row in missions)
    claims = sorted({value for row in missions for value in row["claim_ids"]})
    contradictions = sorted({value for row in missions for value in row["contradiction_ids"]})
    tasks = sorted({value for row in missions for value in row["research_task_ids"]})
    protocols = sorted({value for row in missions for value in row["protocol_ids"]})
    return {
        "api_version": "1.0.0",
        "schema_version": programme["schema_version"],
        "status": "live",
        "policy": "/Achievements/targeted-evidence-missions/",
        "mission_date": programme["mission_date"],
        "campaign_version": programme["campaign_version"],
        "primary_mission_id": programme["primary_mission_id"],
        "count": len(missions),
        "metrics": {
            "mission_count": len(missions),
            "achievement_mission_count": sum(row["achievement_slug"] is not None for row in missions),
            "active_count": statuses["active"],
            "scheduled_count": statuses["scheduled"],
            "participant_needed_count": statuses["participant-needed"],
            "blocked_count": statuses["blocked"],
            "candidate_search_count": statuses["candidate-search"],
            "passive_observation_count": statuses["passive-observation"],
            "targeted_claim_count": len(claims),
            "targeted_contradiction_count": len(contradictions),
            "research_task_count": len(tasks),
            "protocol_count": len(protocols),
        },
        "campaign_gaps_at_launch": intelligence.get("campaign_gaps", {}),
        "targeted_claim_ids": claims,
        "targeted_contradiction_ids": contradictions,
        "research_task_ids": tasks,
        "protocol_ids": protocols,
        "by_status": dict(sorted(statuses.items())),
        "missions": [summary(row) for row in missions],
    }


def markdown(programme: dict, intelligence: dict) -> str:
    output = payload(programme, intelligence)
    lines = [
        "---", "layout: default", "title: Targeted evidence acquisition missions",
        "description: Ranked, ethical, fail-closed missions for converting evidence pressure into adjudicable observations.",
        "permalink: /targeted-evidence-missions/", "---", "", "## Targeted evidence acquisition missions", "",
        "These missions turn the evidence-intelligence ranking into bounded research. They prohibit spam, false attribution, repository manipulation, achievement farming, and automatic claim promotion.", "",
        f"**Missions:** {output['metrics']['mission_count']}  ",
        f"**Claims targeted:** {output['metrics']['targeted_claim_count']}  ",
        f"**Contradictions targeted:** {output['metrics']['targeted_contradiction_count']}  ",
        f"**Active missions:** {output['metrics']['active_count']}  ",
        f"**Blocked missions:** {output['metrics']['blocked_count']}  ",
        f"**Scheduled checkpoints:** {output['metrics']['scheduled_count']}", "",
        "Mission rank remains evidence-pressure order; the active status identifies the current execution priority.", "",
        "| Rank | Mission | Achievement | Pressure | Status |", "|---:|---|---|---:|---|",
    ]
    for row in output["missions"]:
        lines.append(f"| {row['rank']} | `{row['id']}` — {row['title']} | {row['achievement_slug'] or 'cross-achievement'} | {row['pressure_score']} | {row['status']} |")
    lines += ["", "## Operating rules", "", "- Every underlying GitHub action must remain independently useful.", "- Existing protections and maintainer decisions override mission completion.", "- Negative, blocked, delayed, and inconclusive outcomes remain visible.", "- Completion creates a reviewable evidence package, never an automatic promotion.", ""]
    for row in output["missions"]:
        lines += [f"### {row['rank']}. {row['id']} — {row['title']}", "", row["objective"], "", f"**Status:** `{row['status']}`  ", f"**Claims:** {', '.join(f'`{value}`' for value in row['claim_ids']) or 'none'}  ", f"**Contradictions:** {', '.join(f'`{value}`' for value in row['contradiction_ids']) or 'none'}"]
        if row.get("scheduled_check_at"):
            lines += ["", f"**Scheduled checkpoint:** `{row['scheduled_check_at']}`  ", f"**No action before:** `{row['no_action_before']}`  ", f"**Checkpoint:** [{row['checkpoint_url']}]({row['checkpoint_url']})"]
        for heading, field in (("Controls", "controls"), ("Required evidence", "required_evidence"), ("Stop conditions", "stop_conditions"), ("Ethics", "ethics")):
            lines += ["", f"**{heading}**", ""] + [f"- {value}" for value in row[field]]
        lines.append("")
    lines += ["## Machine-readable queue", "", "The validated summaries are published at [`/api/acquisition-missions.json`](../api/acquisition-missions.json). The complete execution plans remain canonical in [`data/acquisition-missions.json`](../data/acquisition-missions.json).", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and publish targeted evidence acquisition missions.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", default="acquisition-missions-report.md")
    args = parser.parse_args()
    try:
        programme = load(DATA / "acquisition-missions.json")
        queue = load(DATA / "research-queue.json")
        protocols = load(DATA / "reproduction-protocols.json")
        claims = load(DATA / "claims.json")
        contradictions = load(DATA / "contradictions.json")
        intelligence = load(API / "evidence-intelligence.json")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error)
        return 1
    errors = validate(programme, queue, protocols, claims, contradictions, intelligence)
    report = ["# Acquisition mission validation", "", f"- Missions: {len(programme.get('missions', []))}", f"- Result: {'FAIL' if errors else 'PASS'}"]
    if errors:
        report += ["", "## Failures", ""] + [f"- {value}" for value in errors]
    (ROOT / args.report).write_text("\n".join(report) + "\n", encoding="utf-8")
    if errors:
        print("\n".join(errors))
        return 1
    outputs = {
        API / "acquisition-missions.json": json.dumps(payload(programme, intelligence), separators=(",", ":"), ensure_ascii=False) + "\n",
        DOCS / "targeted-evidence-missions.md": markdown(programme, intelligence),
    }
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, expected in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != expected]
        if stale:
            print("Stale or missing acquisition mission outputs: " + ", ".join(stale))
            return 1
    else:
        for path, expected in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
    print(f"Acquisition missions passed: {len(programme['missions'])} missions targeting {payload(programme, intelligence)['metrics']['targeted_claim_count']} claims.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
