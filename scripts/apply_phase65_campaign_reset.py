from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def write(path: str, value: object) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Expected source fragment not found in {path}: {old[:100]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def update_research_queue() -> None:
    queue = load("data/research-queue.json")
    queue["schema_version"] = "1.2.0"
    queue["campaign_version"] = "v1.5.0"
    queue["campaign_buckets"] = ["active", "blocked", "monitoring", "queued", "complete"]
    buckets = {
        "RSH-002": "active",
        "RSH-008": "active",
        "RSH-009": "active",
        "RSH-010": "blocked",
        "RSH-005": "monitoring",
        "RSH-011": "queued",
        "RSH-012": "queued",
    }
    for task in queue["tasks"]:
        task_id = task["id"]
        task["campaign_bucket"] = "complete" if task["status"] == "resolved" else buckets[task_id]
        if task_id == "RSH-008":
            task["status"] = "in-progress"
    write("data/research-queue.json", queue)


def pair_boundary_mission() -> dict:
    return {
        "id": "MSN-008",
        "rank": 2,
        "achievement_slug": "pair-extraordinaire",
        "title": "Observe exact Pair Extraordinaire tier transitions",
        "status": "blocked",
        "pressure_score": 49,
        "claim_ids": ["CLM-006"],
        "contradiction_ids": ["CTR-004"],
        "research_task_ids": ["RSH-010"],
        "protocol_ids": ["LAB-003"],
        "objective": "Preserve dated qualifying counts immediately below, at, and above the reported 1, 10, 24, and 48 boundaries without creating artificial pull requests or inferring counts from an x3 or x4 badge sighting.",
        "promotion_targets": [{"claim_id": "CLM-006", "target_level": "observed"}],
        "release_gate_relevance": ["claims_below_confirmed", "official_or_confirmed_claims", "open_contradictions", "coverage_score"],
        "prerequisites": [
            "A consenting public account is naturally approaching a reported Pair Extraordinaire boundary.",
            "The exact qualifying merged-pull-request count can be reconstructed from public final history.",
            "The co-author identity is account-linked and every underlying contribution is genuine.",
        ],
        "controls": [
            "Record exact below, at, and above counts rather than relying on a displayed multiplier alone.",
            "Inspect final default-branch history for retained account-linked Co-authored-by trailers.",
            "Measure first-visible tier time separately from merge time and retain negative or delayed results.",
        ],
        "steps": [
            "Wait for a naturally occurring account to approach one of the reported boundaries.",
            "Record the exact qualifying count and displayed tier before the next legitimate collaborative merge.",
            "Preserve the public pull request, final commit, merge method, trailer, and account-linkage state.",
            "Record the exact qualifying count after merge and observe the first visible tier state or bounded cutoff.",
            "Repeat only for a naturally available missing boundary cell and retain counterexamples.",
        ],
        "required_evidence": [
            "public_pull_request_url",
            "final_commit_url",
            "qualifying_count_before",
            "qualifying_count_after",
            "displayed_tier_before",
            "displayed_tier_after",
            "merge_method",
            "account_linkage_state",
            "first_visible_time_utc_or_cutoff",
        ],
        "stop_conditions": [
            "Stop if the exact qualifying count cannot be reconstructed from public history.",
            "Do not create additional pull requests solely to approach or cross a boundary.",
            "Stop if attribution would be false, misleading, or expose a private email address.",
        ],
        "ethics": [
            "Every co-author must have made a real contribution.",
            "A blocked boundary is preferable to manufactured activity or inferred evidence.",
        ],
        "artificial_activity_prohibited": True,
        "spam_prohibited": True,
    }


def update_missions() -> None:
    programme = load("data/acquisition-missions.json")
    programme["schema_version"] = "1.1.0"
    programme["mission_date"] = "2026-07-20"
    programme["campaign_version"] = "v1.5.0"
    programme["primary_mission_id"] = "MSN-006"
    programme["statuses"] = [
        "active", "participant-needed", "scheduled", "candidate-search",
        "passive-observation", "blocked", "complete", "cancelled",
    ]
    by_id = {mission["id"]: mission for mission in programme["missions"]}

    pair = by_id["MSN-001"]
    pair["title"] = "Preserve real co-author attribution across remaining merge methods"
    pair["claim_ids"] = ["CLM-005"]
    pair["research_task_ids"] = ["RSH-009"]
    pair["objective"] = "Collect legitimate collaborative pull requests that show whether rebase, fast-forward, stripped-trailer, email-mismatch, and later rewrite states preserve qualifying final-history co-author attribution after squash preservation was observed."
    pair["promotion_targets"] = [{"claim_id": "CLM-005", "target_level": "confirmed"}]
    pair["release_gate_relevance"] = ["open_contradictions", "coverage_score"]

    yolo = by_id["MSN-006"]
    yolo["status"] = "active"
    yolo["title"] = "Run the active YOLO submitted-review-state matrix"
    yolo["objective"] = "Observe submitted COMMENT, REQUEST_CHANGES, APPROVE, dismissed, automated-review, and differing-merger states across legitimate pull requests after the pending-review-request subcase was resolved."

    if "MSN-008" not in by_id:
        programme["missions"].append(pair_boundary_mission())

    ranks = {
        "MSN-001": 1,
        "MSN-008": 2,
        "MSN-004": 3,
        "MSN-002": 4,
        "MSN-006": 5,
        "MSN-005": 6,
        "MSN-003": 7,
        "MSN-007": 8,
    }
    for mission in programme["missions"]:
        mission["rank"] = ranks[mission["id"]]
    programme["missions"] = sorted(programme["missions"], key=lambda item: item["rank"])
    write("data/acquisition-missions.json", programme)


def update_historical_release_gate() -> None:
    source = load("data/evidence-quality-programme.json")
    gate = source["release_gate"]
    gate.update({
        "status": "published",
        "historical": True,
        "published_at": "2026-07-20T00:16:51Z",
        "release_commit": "98d478c7b73cff9c6e8fa5235640f12597544b67",
        "baseline_record_commit": "c2dc2f43bd860b4ae6282daf066359fdd9a94e22",
        "release_url": "https://github.com/Conroy1988/Achievements/releases/tag/v1.4.0",
        "active_campaign_endpoint": "/Achievements/api/campaign-status.json",
        "publication_rule": "Historical v1.4.0 evidence gate. The release was published only after the evidence snapshot passed and merged-main operational health was verified at 100/100. Live campaign state is published separately at /Achievements/api/campaign-status.json.",
    })
    write("data/evidence-quality-programme.json", source)


def create_campaign_source() -> None:
    campaign = {
        "schema_version": "1.0.0",
        "programme_date": "2026-07-20",
        "lifecycle_states": ["post-release", "collecting-evidence", "release-candidate", "release-ready", "published", "archived"],
        "active_campaign": {
            "version": "v1.5.0",
            "phase": 65,
            "name": "Post-v1.4 Research Operations",
            "lifecycle": "collecting-evidence",
            "started_on": "2026-07-20",
            "primary_mission_id": "MSN-006",
            "secondary_mission_ids": ["MSN-007", "MSN-001"],
            "current_snapshot": {
                "coverage_score": 91.2,
                "official_or_confirmed_claims": 12,
                "claims_below_confirmed": 1,
                "open_contradictions": 3,
                "operational_health": 100,
            },
            "required_snapshot": {
                "minimum_coverage_score": 92.0,
                "minimum_official_or_confirmed_claims": 12,
                "maximum_claims_below_confirmed": 1,
                "maximum_open_contradictions": 2,
                "required_operational_health": 100,
            },
            "publication_rule": "The v1.5.0 campaign may advance to release-candidate only after its evidence gate passes, all generated outputs are current, and a maintainer explicitly changes the lifecycle. Release-ready additionally requires a fully passing merged-main operational audit.",
        },
        "task_buckets": {
            "active": ["RSH-002", "RSH-008", "RSH-009"],
            "blocked": ["RSH-010"],
            "monitoring": ["RSH-005"],
            "queued": ["RSH-011", "RSH-012"],
        },
        "archived_campaigns": [
            {
                "version": "v1.4.0",
                "phase_range": [52, 64],
                "status": "published",
                "published_at": "2026-07-20T00:16:51Z",
                "release_commit": "98d478c7b73cff9c6e8fa5235640f12597544b67",
                "baseline_record_commit": "c2dc2f43bd860b4ae6282daf066359fdd9a94e22",
                "release_url": "https://github.com/Conroy1988/Achievements/releases/tag/v1.4.0",
                "final_snapshot": {
                    "coverage_score": 91.2,
                    "official_or_confirmed_claims": 12,
                    "claims_below_confirmed": 1,
                    "open_contradictions": 3,
                    "operational_health": 100,
                },
            }
        ],
        "operating_rules": [
            "An archived release snapshot is immutable and cannot be reused as the active campaign.",
            "Campaign lifecycle changes require a maintainer-reviewed source change; builders only validate and publish state.",
            "Blocked evidence remains blocked until the published evidence requirement is met without artificial activity.",
            "Active missions must preserve repository safeguards, independent usefulness, privacy, and fail-closed adjudication.",
        ],
    }
    write("data/research-campaign.json", campaign)


def replace_research_hub_builder() -> None:
    content = '''from __future__ import annotations

from collections import Counter
from pathlib import Path
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "data" / "research-queue.json"
ACHIEVEMENTS_PATH = ROOT / "data" / "achievements.json"
EVIDENCE_PATH = ROOT / "data" / "evidence-register.json"
MARKDOWN_PATH = ROOT / "docs" / "research-hub.md"
API_PATH = ROOT / "api" / "research-queue.json"
ID_PATTERN = re.compile(r"^RSH-[0-9]{3}$")
ALLOWED_STATUS = {"open", "in-progress", "blocked", "resolved"}
ALLOWED_PRIORITY = {"critical", "high", "medium", "low"}
ALLOWED_DIFFICULTY = {"beginner", "intermediate", "advanced"}
ALLOWED_TARGETS = {"official", "confirmed", "observed", "community-reported", "unknown"}
ALLOWED_BUCKETS = {"active", "blocked", "monitoring", "queued", "complete"}
BUCKET_ORDER = {"active": 0, "blocked": 1, "monitoring": 2, "queued": 3, "complete": 4}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(queue: dict, achievements: dict, evidence: dict) -> list[str]:
    failures: list[str] = []
    tasks = queue.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return ["tasks must be a non-empty array"]
    if queue.get("campaign_version") != "v1.5.0":
        failures.append("campaign_version must identify v1.5.0")
    if set(queue.get("campaign_buckets", [])) != ALLOWED_BUCKETS:
        failures.append("campaign_buckets must declare the complete Phase 65 bucket set")
    achievement_slugs = {item["slug"] for item in achievements.get("achievements", [])}
    evidence_ids = {item["id"] for item in evidence.get("records", [])}
    seen: set[str] = set()
    for index, task in enumerate(tasks, start=1):
        task_id = task.get("id", "")
        prefix = f"task {index} ({task_id or 'missing id'})"
        if not ID_PATTERN.fullmatch(task_id):
            failures.append(f"{prefix}: invalid id")
        elif task_id in seen:
            failures.append(f"{prefix}: duplicate id")
        seen.add(task_id)
        slug = task.get("achievement_slug")
        if slug is not None and slug not in achievement_slugs:
            failures.append(f"{prefix}: unknown achievement slug")
        status = task.get("status")
        bucket = task.get("campaign_bucket")
        if status not in ALLOWED_STATUS:
            failures.append(f"{prefix}: invalid status")
        if bucket not in ALLOWED_BUCKETS:
            failures.append(f"{prefix}: invalid campaign bucket")
        if status == "resolved" and bucket != "complete":
            failures.append(f"{prefix}: resolved tasks must be complete")
        if status == "blocked" and bucket != "blocked":
            failures.append(f"{prefix}: blocked tasks must use the blocked bucket")
        if bucket == "active" and status != "in-progress":
            failures.append(f"{prefix}: active tasks must be in-progress")
        if bucket == "queued" and status != "open":
            failures.append(f"{prefix}: queued tasks must be open")
        if task.get("priority") not in ALLOWED_PRIORITY:
            failures.append(f"{prefix}: invalid priority")
        if task.get("difficulty") not in ALLOWED_DIFFICULTY:
            failures.append(f"{prefix}: invalid difficulty")
        if task.get("target_evidence_level") not in ALLOWED_TARGETS:
            failures.append(f"{prefix}: invalid target evidence level")
        if not isinstance(task.get("good_first_issue"), bool):
            failures.append(f"{prefix}: good_first_issue must be boolean")
        related = task.get("related_evidence_ids")
        if not isinstance(related, list):
            failures.append(f"{prefix}: related_evidence_ids must be an array")
        else:
            unknown = sorted(set(related) - evidence_ids)
            if unknown:
                failures.append(f"{prefix}: unknown evidence ids: {', '.join(unknown)}")
        criteria = task.get("acceptance_criteria")
        if not isinstance(criteria, list) or len(criteria) < 2:
            failures.append(f"{prefix}: at least two acceptance criteria are required")
        for field in ("title", "task_type", "research_question"):
            if not isinstance(task.get(field), str) or not task[field].strip():
                failures.append(f"{prefix}: {field} must be non-empty")
    unresolved = [task for task in tasks if task.get("status") != "resolved"]
    if len(unresolved) != 7:
        failures.append("Phase 65 must classify exactly seven unresolved research tasks")
    if sum(task.get("campaign_bucket") == "active" for task in unresolved) != 3:
        failures.append("Phase 65 must expose exactly three active tasks")
    return failures


def render_markdown(queue: dict, achievements: dict) -> str:
    names = {item["slug"]: item["name"] for item in achievements["achievements"]}
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    tasks = sorted(queue["tasks"], key=lambda item: (BUCKET_ORDER[item["campaign_bucket"]], priority_order[item["priority"]], item["id"]))
    counts = Counter(item["campaign_bucket"] for item in tasks)
    good_first = sum(item["good_first_issue"] and item["campaign_bucket"] in {"active", "queued"} for item in tasks)
    lines = [
        "---", "layout: default", "title: Contributor research hub",
        "description: Campaign-classified, reproducible research tasks for improving GitHub achievement evidence.",
        "permalink: /research-hub/", "---", "", "## Contributor research hub", "",
        "This hub converts known evidence gaps into bounded research tasks. Phase 65 separates work that is active, blocked, monitored, queued, or complete without weakening evidence requirements.", "",
        f"**Campaign:** `{queue['campaign_version']}`  ",
        f"**Active:** {counts['active']}  ", f"**Blocked:** {counts['blocked']}  ",
        f"**Monitoring:** {counts['monitoring']}  ", f"**Queued:** {counts['queued']}  ",
        f"**Good first research tasks:** {good_first}  ", f"**Schema version:** `{queue['schema_version']}`", "",
        "| Task | Achievement | Type | Priority | Difficulty | Campaign | Status |",
        "|---|---|---|---|---|---|---|",
    ]
    for task in tasks:
        achievement = names.get(task["achievement_slug"], "Cross-achievement")
        first = " — good first issue" if task["good_first_issue"] else ""
        lines.append(f"| `{task['id']}` | {achievement} | {task['task_type']}{first} | {task['priority']} | {task['difficulty']} | {task['campaign_bucket']} | {task['status']} |")
    for bucket in ("active", "blocked", "monitoring", "queued", "complete"):
        lines.extend(["", f"## {bucket.title()} tasks", ""])
        for task in [item for item in tasks if item["campaign_bucket"] == bucket]:
            achievement = names.get(task["achievement_slug"], "Cross-achievement")
            lines.extend([
                f"### {task['id']} — {task['title']}", "",
                f"**Achievement:** {achievement}  ", f"**Priority:** `{task['priority']}`  ",
                f"**Difficulty:** `{task['difficulty']}`  ", f"**Target evidence:** `{task['target_evidence_level']}`", "",
                f"**Research question:** {task['research_question']}", "", "**Acceptance criteria**", "",
            ])
            lines.extend(f"- {criterion}" for criterion in task["acceptance_criteria"])
            related = task["related_evidence_ids"]
            lines.extend(["", f"**Related evidence records:** {', '.join(f'`{item}`' for item in related) if related else 'None'}", ""])
    lines.extend([
        "## Starting work", "", "1. Start with an active task or a queued task that has become naturally actionable.",
        "2. Preserve the published mission, protocol, safeguards, and evidence requirements.",
        "3. Never manufacture activity to unblock a threshold or fill a matrix cell.",
        "4. Submit successful, failed, delayed, and contradictory observations with dates and limitations.", "",
        "Machine-readable tasks are available from [`/api/research-queue.json`](../api/research-queue.json).", "",
    ])
    return "\n".join(lines)


def render_api(queue: dict) -> str:
    counts = Counter(task["campaign_bucket"] for task in queue["tasks"])
    return json.dumps({
        "api_version": "1.1.0", "schema_version": queue["schema_version"],
        "campaign_version": queue["campaign_version"], "count": len(queue["tasks"]),
        "metrics": dict(sorted(counts.items())), "tasks": queue["tasks"],
    }, indent=2, ensure_ascii=False) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and publish the contributor research hub.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", default="research-hub-report.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    queue, achievements, evidence = load(QUEUE_PATH), load(ACHIEVEMENTS_PATH), load(EVIDENCE_PATH)
    failures = validate(queue, achievements, evidence)
    report = ["# Contributor research hub validation", "", f"- Tasks: {len(queue.get('tasks', []))}", f"- Result: {'FAIL' if failures else 'PASS'}"]
    if failures:
        report.extend(["", "## Failures", "", *[f"- {item}" for item in failures]])
    (ROOT / args.report).write_text("\n".join(report) + "\n", encoding="utf-8")
    if failures:
        print("\n".join(failures))
        return 1
    outputs = {MARKDOWN_PATH: render_markdown(queue, achievements), API_PATH: render_api(queue)}
    if args.check:
        drift = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if drift:
            print("Generated research outputs are stale: " + ", ".join(drift))
            return 1
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    print(f"Research hub passed with {len(queue['tasks'])} tasks across Phase 65 campaign buckets.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
    (ROOT / "scripts/build_research_hub.py").write_text(content, encoding="utf-8")


def create_campaign_builder() -> None:
    content = '''from __future__ import annotations

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
SEMVER = re.compile(r"^v[0-9]+\\.[0-9]+\\.[0-9]+$")
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
'''
    (ROOT / "scripts/build_research_campaign.py").write_text(content, encoding="utf-8")


def patch_builders() -> None:
    replace_once(
        "scripts/build_acquisition_missions.py",
        'STATUSES = {"participant-needed", "scheduled", "candidate-search", "passive-observation", "complete", "cancelled"}',
        'STATUSES = {"active", "participant-needed", "scheduled", "candidate-search", "passive-observation", "blocked", "complete", "cancelled"}',
    )
    replace_once(
        "scripts/build_acquisition_missions.py",
        '    scheduled = [row for row in missions if row.get("status") == "scheduled"]\n    if len(scheduled) != 1 or scheduled[0].get("achievement_slug") != "pull-shark":\n        errors.append("exactly one scheduled Pull Shark checkpoint is required")\n    return errors',
        '    scheduled = [row for row in missions if row.get("status") == "scheduled"]\n    if len(scheduled) != 1 or scheduled[0].get("achievement_slug") != "pull-shark":\n        errors.append("exactly one scheduled Pull Shark checkpoint is required")\n    active = [row for row in missions if row.get("status") == "active"]\n    if len(active) != 1 or active[0].get("id") != programme.get("primary_mission_id") or active[0].get("achievement_slug") != "yolo":\n        errors.append("exactly one active YOLO primary mission is required")\n    if programme.get("campaign_version") != "v1.5.0":\n        errors.append("mission programme must identify the v1.5.0 campaign")\n    return errors',
    )
    replace_once(
        "scripts/build_acquisition_missions.py",
        '            "scheduled_count": statuses["scheduled"],\n            "participant_needed_count": statuses["participant-needed"],',
        '            "active_count": statuses["active"],\n            "scheduled_count": statuses["scheduled"],\n            "participant_needed_count": statuses["participant-needed"],\n            "blocked_count": statuses["blocked"],',
    )
    replace_once(
        "scripts/build_acquisition_missions.py",
        '        "mission_date": programme["mission_date"],\n        "count": len(missions),',
        '        "mission_date": programme["mission_date"],\n        "campaign_version": programme["campaign_version"],\n        "primary_mission_id": programme["primary_mission_id"],\n        "count": len(missions),',
    )
    replace_once(
        "scripts/build_acquisition_missions.py",
        '        "release_gaps_at_launch": intelligence.get("release_gaps", {}),',
        '        "campaign_gaps_at_launch": intelligence.get("campaign_gaps", {}),',
    )
    replace_once(
        "scripts/build_acquisition_missions.py",
        '        f"**Scheduled checkpoints:** {output[\'metrics\'][\'scheduled_count\']}", "",',
        '        f"**Active missions:** {output[\'metrics\'][\'active_count\']}  ",\n        f"**Blocked missions:** {output[\'metrics\'][\'blocked_count\']}  ",\n        f"**Scheduled checkpoints:** {output[\'metrics\'][\'scheduled_count\']}", "",\n        "Mission rank remains evidence-pressure order; the active status identifies the current execution priority.", "",',
    )

    replace_once(
        "scripts/build_evidence_quality_programme.py",
        '    if gate.get("status") != ("ready" if passes else "blocked"):\n        errors.append("release gate status does not match current evidence")',
        '    status = gate.get("status")\n    if status == "published":\n        if not passes:\n            errors.append("a published historical release gate must retain a passing evidence snapshot")\n        for field in ("published_at", "release_commit", "baseline_record_commit", "release_url", "active_campaign_endpoint"):\n            if not gate.get(field):\n                errors.append(f"published release gate is missing {field}")\n    elif status != ("ready" if passes else "blocked"):\n        errors.append("release gate status does not match current evidence")',
    )
    old_release_page = '''def release_page(source: dict) -> str:\n    gate, current, required = source["release_gate"], source["release_gate"]["current_snapshot"], source["release_gate"]["required_snapshot"]\n    lines = frontmatter("Evidence quality release gate", "Fail-closed publication criteria for the proposed v1.4.0 evidence-quality release.", "/evidence-quality-release-gate/")\n    coverage_result = "PASS" if current["coverage_score"] >= required["minimum_coverage_score"] else "FAIL"\n    confirmed_result = "PASS" if current["official_or_confirmed_claims"] >= required["minimum_official_or_confirmed_claims"] else "FAIL"\n    weak_result = "PASS" if current["claims_below_confirmed"] <= required["maximum_claims_below_confirmed"] else "FAIL"\n    contradiction_result = "PASS" if current["open_contradictions"] <= required["maximum_open_contradictions"] else "FAIL"\n    summary = "All evidence gates pass. Publication still requires merged-main operational verification." if gate["status"] == "ready" else "One or more evidence gates remain blocked."\n    lines += ["## Evidence quality release gate", "", f"**Candidate:** `{gate['candidate_version']}`  ", f"**Status:** `{gate['status']}`", "", summary, "", "| Gate | Current | Required | Result |", "|---|---:|---:|---|", f"| Evidence coverage | {current['coverage_score']} | ≥ {required['minimum_coverage_score']} | {coverage_result} |", f"| Official or confirmed claims | {current['official_or_confirmed_claims']} | ≥ {required['minimum_official_or_confirmed_claims']} | {confirmed_result} |", f"| Claims below confirmed | {current['claims_below_confirmed']} | ≤ {required['maximum_claims_below_confirmed']} | {weak_result} |", f"| Open contradictions | {current['open_contradictions']} | ≤ {required['maximum_open_contradictions']} | {contradiction_result} |", f"| Operational health | evaluated on merged `main` | {required['required_operational_health']} | PENDING |", "", "## Publication rule", "", gate["publication_rule"], "", "## Machine-readable data", "", "See [`/api/release-readiness.json`](../api/release-readiness.json).", ""]\n    return "\\n".join(lines)'''
    new_release_page = '''def release_page(source: dict) -> str:\n    gate, current, required = source["release_gate"], source["release_gate"]["current_snapshot"], source["release_gate"]["required_snapshot"]\n    lines = frontmatter("v1.4.0 evidence release baseline", "Immutable evidence and operational publication baseline for the published v1.4.0 release.", "/evidence-quality-release-gate/")\n    coverage_result = "PASS" if current["coverage_score"] >= required["minimum_coverage_score"] else "FAIL"\n    confirmed_result = "PASS" if current["official_or_confirmed_claims"] >= required["minimum_official_or_confirmed_claims"] else "FAIL"\n    weak_result = "PASS" if current["claims_below_confirmed"] <= required["maximum_claims_below_confirmed"] else "FAIL"\n    contradiction_result = "PASS" if current["open_contradictions"] <= required["maximum_open_contradictions"] else "FAIL"\n    summary = "This gate is a historical published baseline. It is not the active release candidate." if gate["status"] == "published" else "This gate has not yet been published."\n    lines += ["## v1.4.0 evidence release baseline", "", f"**Release:** `{gate['candidate_version']}`  ", f"**Status:** `{gate['status']}`", "", summary, "", "| Gate | Final | Required | Result |", "|---|---:|---:|---|", f"| Evidence coverage | {current['coverage_score']} | ≥ {required['minimum_coverage_score']} | {coverage_result} |", f"| Official or confirmed claims | {current['official_or_confirmed_claims']} | ≥ {required['minimum_official_or_confirmed_claims']} | {confirmed_result} |", f"| Claims below confirmed | {current['claims_below_confirmed']} | ≤ {required['maximum_claims_below_confirmed']} | {weak_result} |", f"| Open contradictions | {current['open_contradictions']} | ≤ {required['maximum_open_contradictions']} | {contradiction_result} |", f"| Operational health | {current['operational_health_target']} | {required['required_operational_health']} | PASS |", "", "## Immutable release record", "", f"- Published: `{gate['published_at']}`", f"- Release commit: `{gate['release_commit']}`", f"- Baseline record: `{gate['baseline_record_commit']}`", f"- [GitHub Release]({gate['release_url']})", "", "## Historical publication rule", "", gate["publication_rule"], "", "## Active campaign", "", "The live campaign is published at [`/api/campaign-status.json`](../api/campaign-status.json) and [Research campaign status](research-campaign-status.md).", "", "## Machine-readable data", "", "See [`/api/release-readiness.json`](../api/release-readiness.json).", ""]\n    return "\\n".join(lines)'''
    replace_once("scripts/build_evidence_quality_programme.py", old_release_page, new_release_page)
    replace_once(
        "scripts/build_evidence_quality_programme.py",
        '    print(f"Evidence quality programme passed: phases 52-56 validated; v1.4.0 is {source[\'release_gate\'][\'status\']}.")',
        '    print(f"Evidence quality programme passed: phases 52-56 validated; v1.4.0 baseline is {source[\'release_gate\'][\'status\']}.")',
    )

    replace_once(
        "scripts/build_evidence_intelligence.py",
        '    "release": API / "release-readiness.json",',
        '    "campaign": API / "campaign-status.json",',
    )
    replace_once(
        "scripts/build_evidence_intelligence.py",
        '        "release": ("candidate_version", "status", "current_snapshot", "required_snapshot"),',
        '        "campaign": ("active_campaign", "campaign_gaps", "task_buckets"),',
    )
    replace_once(
        "scripts/build_evidence_intelligence.py",
        '    release = documents["release"]\n    if release.get("status") not in {"blocked", "ready"}:\n        errors.append("release readiness status must be blocked or ready")',
        '    active_campaign = documents["campaign"].get("active_campaign", {})\n    if active_campaign.get("lifecycle") not in {"post-release", "collecting-evidence", "release-candidate", "release-ready"}:\n        errors.append("active campaign lifecycle is invalid")\n    if active_campaign.get("evidence_gate_status") not in {"blocked", "ready"}:\n        errors.append("active campaign evidence gate must be blocked or ready")',
    )
    replace_once(
        "scripts/build_evidence_intelligence.py",
        '    release = documents["release"]',
        '    campaign = documents["campaign"]\n    active_campaign = campaign["active_campaign"]',
    )
    replace_once(
        "scripts/build_evidence_intelligence.py",
        '    current = release["current_snapshot"]\n    required = release["required_snapshot"]',
        '    current = active_campaign["current_snapshot"]\n    required = active_campaign["required_snapshot"]',
    )
    replace_once(
        "scripts/build_evidence_intelligence.py",
        '            "/Achievements/api/release-readiness.json",',
        '            "/Achievements/api/campaign-status.json",',
    )
    replace_once(
        "scripts/build_evidence_intelligence.py",
        '            "release_status": release["status"],',
        '            "campaign_lifecycle": active_campaign["lifecycle"],\n            "campaign_gate_status": active_campaign["evidence_gate_status"],',
    )
    replace_once(
        "scripts/build_evidence_intelligence.py",
        '        "release_candidate": release["candidate_version"],\n        "release_gaps": release_gaps,',
        '        "campaign_version": active_campaign["version"],\n        "campaign_gaps": release_gaps,\n        "release_candidate": active_campaign["version"],\n        "release_gaps": release_gaps,',
    )
    replace_once(
        "scripts/build_evidence_intelligence.py",
        '        f"**Release status:** `{metrics[\'release_status\']}`",',
        '        f"**Campaign lifecycle:** `{metrics[\'campaign_lifecycle\']}`  ",\n        f"**Campaign gate:** `{metrics[\'campaign_gate_status\']}`",',
    )
    replace_once(
        "scripts/build_evidence_intelligence.py",
        '        "## Distance to the evidence-quality release",',
        '        "## Distance to the active campaign gate",',
    )
    replace_once(
        "scripts/build_evidence_intelligence.py",
        'This dashboard combines the public evidence-operation endpoints into one read-only decision surface. It does not promote claims, resolve contradictions, or override the formal release gate.',
        'This dashboard combines the public evidence-operation endpoints into one read-only decision surface. It does not promote claims, resolve contradictions, or override the active research campaign lifecycle.',
    )

    replace_once(
        "scripts/build_public_api.py",
        '    "release_readiness": Path("release-readiness.json"),',
        '    "release_readiness": Path("release-readiness.json"),\n    "campaign_status": Path("campaign-status.json"),',
    )
    replace_once(
        "scripts/build_public_api.py",
        '        if name == "release_readiness":\n            for field in ("candidate_version", "status", "current_snapshot", "required_snapshot", "publication_rule"):\n                if field not in payload:\n                    errors.append(f"api/release-readiness.json is missing {field}")',
        '        if name == "release_readiness":\n            for field in ("candidate_version", "status", "current_snapshot", "required_snapshot", "publication_rule"):\n                if field not in payload:\n                    errors.append(f"api/release-readiness.json is missing {field}")\n        if name == "campaign_status":\n            for field in ("active_campaign", "campaign_gaps", "task_buckets", "primary_mission", "archived_campaigns", "metrics"):\n                if field not in payload:\n                    errors.append(f"api/campaign-status.json is missing {field}")',
    )

    replace_once(
        "scripts/build_promotion_plans.py",
        'def payload(policy: dict, plans: list[dict], release_readiness: dict) -> dict:',
        'def payload(policy: dict, plans: list[dict], campaign_status: dict) -> dict:',
    )
    replace_once(
        "scripts/build_promotion_plans.py",
        '        "current_release_snapshot": release_readiness.get("current_snapshot", {}),\n        "current_release_status": release_readiness.get("status"),',
        '        "current_campaign_version": campaign_status.get("active_campaign", {}).get("version"),\n        "current_campaign_snapshot": campaign_status.get("active_campaign", {}).get("current_snapshot", {}),\n        "current_campaign_lifecycle": campaign_status.get("active_campaign", {}).get("lifecycle"),\n        "current_release_status": "published",',
    )
    replace_once(
        "scripts/build_promotion_plans.py",
        'def markdown(policy: dict, plans: list[dict], release_readiness: dict) -> str:',
        'def markdown(policy: dict, plans: list[dict], campaign_status: dict) -> str:',
    )
    replace_once(
        "scripts/build_promotion_plans.py",
        '        f"**Current release status:** `{release_readiness.get(\'status\', \'unknown\')}`",',
        '        f"**Current campaign:** `{campaign_status.get(\'active_campaign\', {}).get(\'version\', \'unknown\')}`  ",\n        f"**Campaign lifecycle:** `{campaign_status.get(\'active_campaign\', {}).get(\'lifecycle\', \'unknown\')}`",',
    )
    replace_once(
        "scripts/build_promotion_plans.py",
        '        release_readiness = load(API / "release-readiness.json")',
        '        campaign_status = load(API / "campaign-status.json")',
    )
    replace_once(
        "scripts/build_promotion_plans.py",
        '        API / "promotion-plans.json": json.dumps(payload(policy, plans, release_readiness), indent=2, ensure_ascii=False) + "\\n",',
        '        API / "promotion-plans.json": json.dumps(payload(policy, plans, campaign_status), indent=2, ensure_ascii=False) + "\\n",',
    )
    replace_once(
        "scripts/build_promotion_plans.py",
        '        DOCS / "promotion-planner.md": markdown(policy, plans, release_readiness),',
        '        DOCS / "promotion-planner.md": markdown(policy, plans, campaign_status),',
    )


def update_policy_and_navigation() -> None:
    policy = load("data/promotion-plan-policy.json")
    policy["policy_date"] = "2026-07-20"
    if "data/research-campaign.json" not in policy["canonical_source_paths"]:
        policy["canonical_source_paths"].insert(-1, "data/research-campaign.json")
    for path in ("api/campaign-status.json", "docs/research-campaign-status.md"):
        if path not in policy["generated_output_paths"]:
            policy["generated_output_paths"].append(path)
    if "python scripts/build_research_campaign.py --check" not in policy["validation_commands"]:
        policy["validation_commands"].insert(-2, "python scripts/build_research_campaign.py --check")
    policy["publication_rules"] = [
        rule.replace("Release readiness must be regenerated after the canonical change; the plan may not declare v1.4.0 publishable in advance.", "The active campaign status must be regenerated after a canonical change; a plan may not advance the campaign lifecycle or declare a release ready.")
        for rule in policy["publication_rules"]
    ]
    write("data/promotion-plan-policy.json", policy)

    api_reference = ROOT / "docs/api-reference.md"
    text = api_reference.read_text(encoding="utf-8")
    text = text.replace("adjudication, release readiness, schema, and repository health.", "adjudication, campaign lifecycle, release history, schema, and repository health.")
    text = text.replace("| [`release-readiness.json`](../api/release-readiness.json) | Deterministic v1.4.0 evidence and operational publication gate |", "| [`release-readiness.json`](../api/release-readiness.json) | Immutable published v1.4.0 evidence and operational baseline |\n| [`campaign-status.json`](../api/campaign-status.json) | Live v1.5.0 campaign lifecycle, task buckets, mission priority, gate distance, and archived release history |")
    text = text.replace("The discovery index now exposes **40 public JSON files**", "The discovery index now exposes **41 public JSON files**")
    text = text.replace("python scripts/build_evidence_intelligence.py\n", "python scripts/build_research_campaign.py\npython scripts/build_evidence_intelligence.py\n")
    text = text.replace("- [Evidence quality release gate](evidence-quality-release-gate.md)", "- [Research campaign status](research-campaign-status.md)\n- [Published v1.4.0 release baseline](evidence-quality-release-gate.md)")
    api_reference.write_text(text, encoding="utf-8")

    site_map = ROOT / "site-map.md"
    text = site_map.read_text(encoding="utf-8")
    text = text.replace("- [Evidence intelligence dashboard](docs/evidence-intelligence-dashboard.md)\n", "- [Research campaign status](docs/research-campaign-status.md)\n- [Evidence intelligence dashboard](docs/evidence-intelligence-dashboard.md)\n", 1)
    text = text.replace("- [Evidence road to 100](docs/evidence-road-to-100.md)\n", "- [Research campaign status](docs/research-campaign-status.md)\n- [Evidence road to 100](docs/evidence-road-to-100.md)\n")
    text = text.replace("- [Evidence release readiness](api/release-readiness.json)\n", "- [Live campaign status](api/campaign-status.json)\n- [Published release baseline](api/release-readiness.json)\n")
    site_map.write_text(text, encoding="utf-8")

    changelog = ROOT / "CHANGELOG.md"
    text = changelog.read_text(encoding="utf-8")
    marker = "## Unreleased\n"
    addition = "\n### Added\n\n- Phase 65 live research campaign control plane for `v1.5.0`, including lifecycle, campaign gates, task buckets, mission priority, and archived release history.\n- Dedicated campaign-status API, public campaign dashboard, and validation workflow.\n\n### Changed\n\n- Archived the published `v1.4.0` readiness gate as an immutable historical baseline.\n- Classified the seven unresolved research tasks as active, blocked, monitoring, or queued.\n- Activated the YOLO submitted-review-state mission and separated the blocked Pair tier-boundary mission from merge-attribution work.\n- Rewired evidence intelligence and promotion planning to the live campaign rather than the historical release gate.\n"
    if "Phase 65 live research campaign control plane" not in text:
        text = text.replace(marker, marker + addition, 1)
    changelog.write_text(text, encoding="utf-8")


def main() -> None:
    update_research_queue()
    update_missions()
    update_historical_release_gate()
    create_campaign_source()
    replace_research_hub_builder()
    create_campaign_builder()
    patch_builders()
    update_policy_and_navigation()
    print("Applied Phase 65 v1.5.0 campaign reset source migration.")


if __name__ == "__main__":
    main()
