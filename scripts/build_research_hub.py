from __future__ import annotations

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


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(queue: dict, achievements: dict, evidence: dict) -> list[str]:
    failures: list[str] = []
    tasks = queue.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return ["tasks must be a non-empty array"]
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
        if task.get("status") not in ALLOWED_STATUS:
            failures.append(f"{prefix}: invalid status")
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
    return failures


def render_markdown(queue: dict, achievements: dict) -> str:
    names = {item["slug"]: item["name"] for item in achievements["achievements"]}
    tasks = sorted(queue["tasks"], key=lambda item: (item["status"] != "open", {"critical": 0, "high": 1, "medium": 2, "low": 3}[item["priority"]], item["id"]))
    open_count = sum(item["status"] == "open" for item in tasks)
    good_first = sum(item["good_first_issue"] and item["status"] == "open" for item in tasks)
    lines = [
        "---",
        "layout: default",
        "title: Contributor research hub",
        "description: Structured, reproducible research tasks for improving GitHub achievement evidence.",
        "permalink: /research-hub/",
        "---",
        "",
        "## Contributor research hub",
        "",
        "This hub converts known evidence gaps into bounded research tasks. Contributions must follow the evidence register policy and may document failed or contradictory results.",
        "",
        f"**Open tasks:** {open_count}  ",
        f"**Good first research tasks:** {good_first}  ",
        f"**Schema version:** `{queue['schema_version']}`",
        "",
        "| Task | Achievement | Type | Priority | Difficulty | Status |",
        "|---|---|---|---|---|---|",
    ]
    for task in tasks:
        achievement = names.get(task["achievement_slug"], "Cross-achievement")
        first = " — good first issue" if task["good_first_issue"] else ""
        lines.append(f"| `{task['id']}` | {achievement} | {task['task_type']}{first} | {task['priority']} | {task['difficulty']} | {task['status']} |")
    lines.extend(["", "## Research tasks", ""])
    for task in tasks:
        achievement = names.get(task["achievement_slug"], "Cross-achievement")
        lines.extend([
            f"### {task['id']} — {task['title']}",
            "",
            f"**Achievement:** {achievement}  ",
            f"**Priority:** `{task['priority']}`  ",
            f"**Difficulty:** `{task['difficulty']}`  ",
            f"**Target evidence:** `{task['target_evidence_level']}`",
            "",
            f"**Research question:** {task['research_question']}",
            "",
            "**Acceptance criteria**",
            "",
        ])
        lines.extend(f"- {criterion}" for criterion in task["acceptance_criteria"])
        related = task["related_evidence_ids"]
        lines.extend(["", f"**Related evidence records:** {', '.join(f'`{item}`' for item in related) if related else 'None'}", ""])
    lines.extend([
        "## Starting work",
        "",
        "1. Choose an open task and open a research issue using the structured form.",
        "2. State the task ID and planned reproduction method.",
        "3. Preserve privacy and avoid fabricated or meaningless activity.",
        "4. Submit both successful and failed observations with dates and limitations.",
        "",
        "Machine-readable tasks are available from [`/api/research-queue.json`](../api/research-queue.json).",
        "",
    ])
    return "\n".join(lines)


def render_api(queue: dict) -> str:
    return json.dumps({
        "api_version": "1.0.0",
        "schema_version": queue["schema_version"],
        "count": len(queue["tasks"]),
        "tasks": queue["tasks"],
    }, indent=2, ensure_ascii=False) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and publish the contributor research hub.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", default="research-hub-report.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    queue = load(QUEUE_PATH)
    achievements = load(ACHIEVEMENTS_PATH)
    evidence = load(EVIDENCE_PATH)
    failures = validate(queue, achievements, evidence)
    report = [
        "# Contributor research hub validation",
        "",
        f"- Tasks: {len(queue.get('tasks', []))}",
        f"- Result: {'FAIL' if failures else 'PASS'}",
    ]
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
    print(f"Research hub passed with {len(queue['tasks'])} tasks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
