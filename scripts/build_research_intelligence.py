from __future__ import annotations

from collections import defaultdict
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
WEAKNESS = {"official": 0, "confirmed": 5, "observed": 15, "community-reported": 25, "unknown": 30}
PRIORITY = {"critical": 40, "high": 30, "medium": 20, "low": 10}
SEVERITY = {"critical": 20, "high": 15, "medium": 10, "low": 5}


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def dump(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def rating(score: float) -> str:
    return "robust" if score >= 80 else "developing" if score >= 60 else "fragile" if score >= 40 else "critical"


def validate(a: dict, e: dict, q: dict, m: dict, c: dict, d: dict) -> list[str]:
    errors: list[str] = []
    achievements = {x["slug"]: x for x in a["achievements"]}
    evidence = {x["id"] for x in e["records"]}
    tasks = {x["id"] for x in q["tasks"]}
    claims = c["claims"]
    claim_ids = {x["id"] for x in claims}
    if len(claim_ids) != len(claims) or any(not re.fullmatch(r"CLM-\d{3}", x) for x in claim_ids):
        errors.append("claim ids must be unique CLM-### values")
    grouped: dict[str, set[str]] = defaultdict(set)
    for x in claims:
        grouped[x["achievement_slug"]].add(x["claim_type"])
        if x["achievement_slug"] not in achievements or x["evidence_level"] not in LEVEL:
            errors.append(f"{x['id']}: invalid achievement or evidence level")
        if not x["evidence_ids"] or set(x["evidence_ids"]) - evidence or set(x["research_task_ids"]) - tasks:
            errors.append(f"{x['id']}: invalid evidence or research links")
    for slug, item in achievements.items():
        trigger = "historical-trigger" if item["status"] == "retired" else "trigger"
        if trigger not in grouped[slug] or (item["tiered"] and "tiers" not in grouped[slug]):
            errors.append(f"{slug}: incomplete claim coverage")
    records = d["records"]
    record_ids = {x["id"] for x in records}
    if len(record_ids) != len(records) or any(not re.fullmatch(r"CTR-\d{3}", x) for x in record_ids):
        errors.append("contradiction ids must be unique CTR-### values")
    for x in records:
        if not x["claim_ids"] or set(x["claim_ids"]) - claim_ids or set(x["evidence_ids"]) - evidence or set(x["research_task_ids"]) - tasks:
            errors.append(f"{x['id']}: invalid relationships")
        if len(x["positions"]) < 2 or not x["resolution_criteria"]:
            errors.append(f"{x['id']}: incomplete dispute record")
    if len({x["id"] for x in m["documents"]}) != len(m["documents"]):
        errors.append("monitored document ids must be unique")
    return errors


def open_disputes(records: list[dict]) -> dict[str, list[dict]]:
    result: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        if record["status"] != "resolved":
            for claim_id in record["claim_ids"]:
                result[claim_id].append(record)
    return result


def build(a: dict, q: dict, m: dict, c: dict, d: dict) -> dict[Path, str]:
    claims, records = c["claims"], d["records"]
    achievements = {x["slug"]: x for x in a["achievements"]}
    disputes = open_disputes(records)

    claim_rows = []
    by_achievement: dict[str, list[dict]] = defaultdict(list)
    for claim in claims:
        score = max(0, LEVEL[claim["evidence_level"]] - (10 if disputes.get(claim["id"]) else 0))
        row = {"claim_id": claim["id"], "achievement_slug": claim["achievement_slug"], "claim_type": claim["claim_type"], "evidence_level": claim["evidence_level"], "open_disputes": [x["id"] for x in disputes.get(claim["id"], [])], "research_task_ids": claim["research_task_ids"], "coverage_score": score, "unassigned_gap": score < 85 and not claim["research_task_ids"]}
        claim_rows.append(row)
        by_achievement[claim["achievement_slug"]].append(row)
    achievement_rows = []
    for slug, item in achievements.items():
        rows = by_achievement[slug]
        score = round(sum(x["coverage_score"] for x in rows) / len(rows), 1)
        achievement_rows.append({"achievement_slug": slug, "achievement_name": item["name"], "achievement_status": item["status"], "claim_count": len(rows), "coverage_score": score, "rating": rating(score), "open_disputes": sorted({y for x in rows for y in x["open_disputes"]}), "unassigned_gaps": [x["claim_id"] for x in rows if x["unassigned_gap"]]})
    overall = round(sum(x["coverage_score"] for x in claim_rows) / len(claim_rows), 1)
    coverage = {"api_version": "1.0.0", "schema_version": "1.0.0", "overall_coverage_score": overall, "overall_rating": rating(overall), "claim_count": len(claim_rows), "achievement_count": len(achievement_rows), "unassigned_gap_count": sum(x["unassigned_gap"] for x in claim_rows), "achievements": achievement_rows, "claims": claim_rows}

    claims_by_task: dict[str, list[dict]] = defaultdict(list)
    disputes_by_task: dict[str, list[dict]] = defaultdict(list)
    for claim in claims:
        for task_id in claim["research_task_ids"]:
            claims_by_task[task_id].append(claim)
    for record in records:
        if record["status"] != "resolved":
            for task_id in record["research_task_ids"]:
                disputes_by_task[task_id].append(record)
    priority_rows = []
    for task in q["tasks"]:
        if task["status"] == "resolved":
            continue
        linked = claims_by_task.get(task["id"], [])
        parts = {"declared_priority": PRIORITY[task["priority"]], "evidence_weakness": max((WEAKNESS[x["evidence_level"]] for x in linked), default=30), "open_dispute": max((SEVERITY[x["severity"]] for x in disputes_by_task.get(task["id"], [])), default=0), "active_scope": 10 if task.get("achievement_slug") and achievements[task["achievement_slug"]]["status"] == "active" else 5 if task.get("achievement_slug") is None else 0, "good_first_issue": 3 if task.get("good_first_issue") else 0, "status_adjustment": 10 if task["status"] == "blocked" else -10 if task["status"] == "in-progress" else 0}
        priority_rows.append({"task_id": task["id"], "title": task["title"], "achievement_slug": task.get("achievement_slug"), "declared_priority": task["priority"], "status": task["status"], "good_first_issue": task.get("good_first_issue", False), "score": min(100, sum(parts.values())), "score_components": parts, "claim_ids": [x["id"] for x in linked], "contradiction_ids": [x["id"] for x in disputes_by_task.get(task["id"], [])]})
    priority_rows.sort(key=lambda x: (-x["score"], x["task_id"]))
    for rank, row in enumerate(priority_rows, 1):
        row["rank"] = rank
    priorities = {"api_version": "1.0.0", "schema_version": "1.0.0", "count": len(priority_rows), "priorities": priority_rows}

    impact_rows = []
    for document in m["documents"]:
        linked = sorted([x for slug in document["affected_achievements"] for x in claims if x["achievement_slug"] == slug], key=lambda x: x["id"])
        contradiction_ids = sorted({y["id"] for x in linked for y in disputes.get(x["id"], [])})
        severe = [x for x in records if x["id"] in contradiction_ids]
        levels = {x["evidence_level"] for x in linked}
        risk = "critical" if any(x["severity"] == "critical" for x in severe) else "high" if severe or levels & {"community-reported", "unknown"} else "medium" if "observed" in levels else "low"
        impact_rows.append({"document_id": document["id"], "url": document["url"], "risk": risk, "affected_achievements": document["affected_achievements"], "claim_ids": [x["id"] for x in linked], "contradiction_ids": contradiction_ids, "research_task_ids": sorted({task for x in linked for task in x["research_task_ids"]}), "review_action": "Re-run mapped claim, contradiction, guide, and API reviews when the monitored fingerprint changes."})
    impact = {"api_version": "1.0.0", "schema_version": "1.0.0", "count": len(impact_rows), "documents": impact_rows}

    return {API / "claims.json": dump({"api_version": "1.0.0", "schema_version": c["schema_version"], "count": len(claims), "claims": claims}), API / "contradictions.json": dump({"api_version": "1.0.0", "schema_version": d["schema_version"], "count": len(records), "records": records}), API / "coverage.json": dump(coverage), API / "priorities.json": dump(priorities), API / "change-impact.json": dump(impact)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate claim-level research intelligence.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", default="research-intelligence-report.md")
    args = parser.parse_args()
    try:
        a, e, q, m, c, d = [load(x) for x in ("achievements.json", "evidence-register.json", "research-queue.json", "official-document-monitor.json", "claims.json", "contradictions.json")]
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as error:
        print(error)
        return 1
    errors = validate(a, e, q, m, c, d)
    (ROOT / args.report).write_text(f"# Research intelligence validation\n\n- Claims: {len(c['claims'])}\n- Contradictions: {len(d['records'])}\n- Result: {'FAIL' if errors else 'PASS'}\n" + (("\n## Failures\n\n" + "\n".join(f"- {x}" for x in errors) + "\n") if errors else ""), encoding="utf-8")
    if errors:
        print("\n".join(errors))
        return 1
    outputs = build(a, q, m, c, d)
    required_docs = [DOCS / x for x in ("claim-register.md", "contradiction-ledger.md", "evidence-coverage.md", "research-priorities.md", "change-impact-map.md")]
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, text in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != text]
        missing = [str(path.relative_to(ROOT)) for path in required_docs if not path.exists()]
        if stale or missing:
            print("Stale or missing outputs: " + ", ".join(stale + missing))
            return 1
    else:
        for path, text in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    print(f"Research intelligence passed: {len(c['claims'])} claims, {len(d['records'])} contradictions, {len(outputs)} API outputs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
