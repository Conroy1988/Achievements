from __future__ import annotations

from collections import Counter
from pathlib import Path
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "research-campaign.json"
QUEUE = ROOT / "data" / "research-queue.json"
MISSIONS = ROOT / "data" / "acquisition-missions.json"
CLAIMS = ROOT / "data" / "claims.json"
CONTRADICTIONS = ROOT / "data" / "contradictions.json"
COVERAGE = ROOT / "api" / "coverage.json"
STATUS = ROOT / "api" / "status.json"
API = ROOT / "api" / "campaign-status.json"
DOC = ROOT / "docs" / "research-campaign-status.md"
SEMVER = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+$")
LIFECYCLES = {"post-release", "collecting-evidence", "release-candidate", "release-ready", "published", "archived"}
BUCKETS = {"active", "blocked", "monitoring", "queued"}


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def snapshot(coverage: dict, claims: dict, contradictions: dict, status: dict) -> dict:
    rows = claims.get("claims", [])
    return {
        "coverage_score": coverage.get("overall_coverage_score"),
        "official_or_confirmed_claims": sum(row.get("evidence_level") in {"official", "confirmed"} for row in rows),
        "claims_below_confirmed": sum(row.get("evidence_level") not in {"official", "confirmed"} for row in rows),
        "open_contradictions": sum(row.get("status") == "open" for row in contradictions.get("records", [])),
        "operational_health": status.get("health", {}).get("score"),
    }


def gate(current: dict, required: dict) -> tuple[str, dict]:
    gaps = {
        "coverage_points_needed": round(max(0.0, required["minimum_coverage_score"] - current["coverage_score"]), 1),
        "official_or_confirmed_claims_needed": max(0, required["minimum_official_or_confirmed_claims"] - current["official_or_confirmed_claims"]),
        "claims_to_promote": max(0, current["claims_below_confirmed"] - required["maximum_claims_below_confirmed"]),
        "contradictions_to_resolve": max(0, current["open_contradictions"] - required["maximum_open_contradictions"]),
        "operational_health_points_needed": max(0, required["required_operational_health"] - current["operational_health"]),
    }
    return ("ready" if not any(gaps.values()) else "blocked"), gaps


def validate(source: dict, queue: dict, missions: dict, claims: dict, contradictions: dict, coverage: dict, status: dict) -> list[str]:
    errors: list[str] = []
    if source.get("schema_version") != "1.0.0":
        errors.append("campaign schema_version must be 1.0.0")
    if set(source.get("lifecycle_states", [])) != LIFECYCLES:
        errors.append("campaign lifecycle_states are incomplete")
    active = source.get("active_campaign", {})
    if active.get("version") != "v1.5.0" or not SEMVER.fullmatch(str(active.get("version", ""))):
        errors.append("active campaign must identify v1.5.0")
    if active.get("phase") != 65:
        errors.append("active campaign must identify Phase 65")
    if active.get("lifecycle") not in LIFECYCLES - {"published", "archived"}:
        errors.append("active campaign lifecycle is invalid")
    actual = snapshot(coverage, claims, contradictions, status)
    if active.get("current_snapshot") != actual:
        errors.append(f"active campaign snapshot drift: expected {actual!r}")
    required = active.get("required_snapshot", {})
    gate_status, _ = gate(actual, required)
    if active.get("lifecycle") == "release-ready" and gate_status != "ready":
        errors.append("release-ready lifecycle requires a passing campaign gate")
    queue_tasks = {row["id"]: row for row in queue.get("tasks", [])}
    bucket_map = source.get("task_buckets", {})
    if set(bucket_map) != BUCKETS:
        errors.append("task_buckets must contain active, blocked, monitoring, and queued")
    flattened = [task_id for bucket in BUCKETS for task_id in bucket_map.get(bucket, [])]
    unresolved = {task_id for task_id, task in queue_tasks.items() if task.get("status") != "resolved"}
    if set(flattened) != unresolved or len(flattened) != len(set(flattened)):
        errors.append("campaign buckets must classify every unresolved task exactly once")
    for bucket, task_ids in bucket_map.items():
        for task_id in task_ids:
            if queue_tasks.get(task_id, {}).get("campaign_bucket") != bucket:
                errors.append(f"{task_id}: campaign bucket differs from research queue")
    mission_by_id = {row["id"]: row for row in missions.get("missions", [])}
    primary = mission_by_id.get(active.get("primary_mission_id"))
    if not primary or primary.get("status") != "active" or primary.get("achievement_slug") != "yolo":
        errors.append("primary campaign mission must be the active YOLO mission")
    archived = source.get("archived_campaigns", [])
    if len(archived) != 1 or archived[0].get("version") != "v1.4.0" or archived[0].get("status") != "published":
        errors.append("the immutable v1.4.0 published campaign must be archived")
    if archived and archived[0].get("version") == active.get("version"):
        errors.append("an archived release cannot also be the active campaign")
    if len(source.get("operating_rules", [])) < 4:
        errors.append("campaign operating rules are incomplete")
    return errors


def payload(source: dict, queue: dict, missions: dict, claims: dict, contradictions: dict, coverage: dict, status: dict) -> dict:
    active = dict(source["active_campaign"])
    current = snapshot(coverage, claims, contradictions, status)
    gate_status, gaps = gate(current, active["required_snapshot"])
    active["current_snapshot"] = current
    active["evidence_gate_status"] = gate_status
    mission_by_id = {row["id"]: row for row in missions["missions"]}
    primary = mission_by_id[active["primary_mission_id"]]
    buckets = source["task_buckets"]
    return {
        "api_version": "1.0.0",
        "schema_version": source["schema_version"],
        "status": "live",
        "active_campaign": active,
        "campaign_gaps": gaps,
        "task_buckets": buckets,
        "metrics": {
            "active_task_count": len(buckets["active"]),
            "blocked_task_count": len(buckets["blocked"]),
            "monitoring_task_count": len(buckets["monitoring"]),
            "queued_task_count": len(buckets["queued"]),
            "archived_campaign_count": len(source["archived_campaigns"]),
            "operational_health": current["operational_health"],
        },
        "primary_mission": {
            "id": primary["id"],
            "title": primary["title"],
            "status": primary["status"],
            "achievement_slug": primary["achievement_slug"],
            "research_task_ids": primary["research_task_ids"],
            "protocol_ids": primary["protocol_ids"],
        },
        "archived_campaigns": source["archived_campaigns"],
        "operating_rules": source["operating_rules"],
    }


def markdown(data: dict) -> str:
    active, gaps = data["active_campaign"], data["campaign_gaps"]
    lines = [
        "---", "layout: default", "title: Research campaign status",
        "description: Live Phase 65 campaign lifecycle, evidence gates, task buckets, primary mission, and immutable release history.",
        "permalink: /research-campaign-status/", "---", "", "## Research campaign status", "",
        "This is the authoritative live campaign control plane. Published release gates remain historical and are never reused as active candidates.", "",
        f"**Campaign:** `{active['version']}` — {active['name']}  ",
        f"**Phase:** {active['phase']}  ", f"**Lifecycle:** `{active['lifecycle']}`  ",
        f"**Evidence gate:** `{active['evidence_gate_status']}`  ",
        f"**Primary mission:** `{data['primary_mission']['id']}` — {data['primary_mission']['title']}", "",
        "## Campaign gate", "", "| Gate | Current | Required | Remaining |", "|---|---:|---:|---:|",
        f"| Coverage | {active['current_snapshot']['coverage_score']} | ≥ {active['required_snapshot']['minimum_coverage_score']} | {gaps['coverage_points_needed']} points |",
        f"| Official or confirmed claims | {active['current_snapshot']['official_or_confirmed_claims']} | ≥ {active['required_snapshot']['minimum_official_or_confirmed_claims']} | {gaps['official_or_confirmed_claims_needed']} claims |",
        f"| Claims below confirmed | {active['current_snapshot']['claims_below_confirmed']} | ≤ {active['required_snapshot']['maximum_claims_below_confirmed']} | {gaps['claims_to_promote']} promotions |",
        f"| Open contradictions | {active['current_snapshot']['open_contradictions']} | ≤ {active['required_snapshot']['maximum_open_contradictions']} | {gaps['contradictions_to_resolve']} resolutions |",
        f"| Operational health | {active['current_snapshot']['operational_health']} | {active['required_snapshot']['required_operational_health']} | {gaps['operational_health_points_needed']} points |", "",
        "## Task buckets", "", "| Bucket | Tasks |", "|---|---|",
    ]
    for bucket in ("active", "blocked", "monitoring", "queued"):
        lines.append(f"| {bucket} | {', '.join(f'`{task}`' for task in data['task_buckets'][bucket])} |")
    lines.extend(["", "## Lifecycle rule", "", active["publication_rule"], "", "## Archived campaigns", ""])
    for archived in data["archived_campaigns"]:
        lines.extend([
            f"### {archived['version']} — {archived['status']}", "",
            f"Published: `{archived['published_at']}`  ", f"Release commit: `{archived['release_commit']}`  ",
            f"Baseline record: `{archived['baseline_record_commit']}`  ", f"[GitHub Release]({archived['release_url']})", "",
        ])
    lines.extend(["## Operating rules", "", *[f"- {rule}" for rule in data["operating_rules"]], "", "## Machine-readable data", "", "See [`/api/campaign-status.json`](../api/campaign-status.json).", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and publish the live research campaign status.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", default="research-campaign-report.md")
    args = parser.parse_args()
    try:
        source, queue, missions, claims, contradictions, coverage, status = map(load, [SOURCE, QUEUE, MISSIONS, CLAIMS, CONTRADICTIONS, COVERAGE, STATUS])
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error)
        return 1
    errors = validate(source, queue, missions, claims, contradictions, coverage, status)
    report = ["# Research campaign validation", "", f"- Active campaign: {source.get('active_campaign', {}).get('version', 'unknown')}", f"- Result: {'FAIL' if errors else 'PASS'}"]
    if errors:
        report.extend(["", "## Failures", "", *[f"- {error}" for error in errors]])
    (ROOT / args.report).write_text("\n".join(report) + "\n", encoding="utf-8")
    if errors:
        print("\n".join(errors))
        return 1
    data = payload(source, queue, missions, claims, contradictions, coverage, status)
    outputs = {API: json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", DOC: markdown(data)}
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, expected in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != expected]
        if stale:
            print("Stale or missing research campaign outputs: " + ", ".join(stale))
            return 1
    else:
        for path, expected in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
    print(f"Research campaign passed: {data['active_campaign']['version']} is {data['active_campaign']['lifecycle']} with gate {data['active_campaign']['evidence_gate_status']}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
