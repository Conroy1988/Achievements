from __future__ import annotations

from collections import Counter
from pathlib import Path
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
API = ROOT / "api"
DOCS = ROOT / "docs"

PLAN_ID = re.compile(r"^PPL-[0-9]{4}-[0-9]{3}$")
REVIEW_ID = re.compile(r"^MRV-[0-9]{4}-[0-9]{3}$")
PACKET_ID = re.compile(r"^MISSION-DRAFT-ISSUE-[0-9]+$")


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def validate_policy(policy: dict) -> list[str]:
    errors: list[str] = []
    if policy.get("automatic_application_allowed") is not False:
        errors.append("promotion policy must prohibit automatic application")
    if policy.get("eligible_queue_statuses") != ["accepted"]:
        errors.append("only accepted review-queue entries may produce plans")
    levels = policy.get("evidence_level_order")
    if levels != ["unknown", "community-reported", "observed", "confirmed", "official"]:
        errors.append("evidence level order is invalid")
    if set(policy.get("eligible_target_levels", [])) != {"observed", "confirmed", "official"}:
        errors.append("eligible target levels are invalid")
    if set(policy.get("plan_statuses", [])) != {"ready-for-maintainer-review", "blocked"}:
        errors.append("plan statuses are invalid")
    if len(policy.get("canonical_source_paths", [])) < 6:
        errors.append("canonical source path inventory is incomplete")
    if len(policy.get("generated_output_paths", [])) < 10:
        errors.append("generated output inventory is incomplete")
    if len(policy.get("required_preconditions", [])) < 7:
        errors.append("promotion policy requires at least seven preconditions")
    if len(policy.get("validation_commands", [])) < 6:
        errors.append("promotion policy requires at least six validation commands")
    if len(policy.get("rollback_rules", [])) < 5:
        errors.append("promotion policy requires at least five rollback rules")
    if len(policy.get("publication_rules", [])) < 6:
        errors.append("promotion policy requires at least six publication rules")
    return errors


def review_path(value: object) -> Path | None:
    if not isinstance(value, str):
        return None
    path = ROOT / value
    try:
        path.relative_to(ROOT / "reviews" / "mission")
    except ValueError:
        return None
    return path


def plan_id(review_id: str) -> str:
    return "PPL-" + review_id.removeprefix("MRV-")


def source_operations(claim: dict, queue_item: dict, guide_path: str) -> list[dict]:
    claim_type = claim["claim_type"]
    evidence_key = "trigger" if claim_type == "trigger" else "tiers"
    return [
        {
            "path": "data/evidence-register.json",
            "operation": "create-or-update",
            "rationale": "Add the accepted mission packet as a canonical privacy-safe evidence record with a maintainer-approved identifier.",
        },
        {
            "path": "data/claims.json",
            "operation": "update",
            "rationale": "Change the reviewed claim evidence level, link the accepted evidence record, and refresh review metadata.",
        },
        {
            "path": "data/achievements.json",
            "operation": "update",
            "rationale": f"Keep the achievement catalogue evidence.{evidence_key} classification aligned with the reviewed claim.",
        },
        {
            "path": guide_path,
            "operation": "update",
            "rationale": "Update the public guide classification, evidence explanation, and limitations without overstating the reviewed result.",
        },
        {
            "path": "data/contradictions.json",
            "operation": "reassess",
            "rationale": "Reassess the linked contradiction against its own resolution criteria; claim promotion alone must not close it.",
        },
        {
            "path": "data/evidence-quality-programme.json",
            "operation": "update",
            "rationale": "Record the accepted adjudication basis and preserve negative or inconclusive evidence that remains material.",
        },
        {
            "path": "CHANGELOG.md",
            "operation": "record",
            "rationale": "Record the evidence-backed canonical classification change and its review provenance.",
        },
    ]


def release_impact(current: str, proposed: str, order: list[str]) -> dict:
    current_rank = order.index(current)
    proposed_rank = order.index(proposed)
    confirmed_rank = order.index("confirmed")
    crosses_confirmed = current_rank < confirmed_rank <= proposed_rank
    return {
        "coverage_score": "recalculate-after-canonical-change",
        "claims_below_confirmed": -1 if crosses_confirmed else 0,
        "official_or_confirmed_claims": 1 if crosses_confirmed else 0,
        "open_contradictions": 0,
        "publication_status": "must-be-regenerated",
    }


def build_plans(
    policy: dict,
    queue_payload: dict,
    claims_payload: dict,
    achievements_payload: dict | None = None,
) -> tuple[list[dict], list[str]]:
    errors: list[str] = []
    queue = queue_payload.get("queue")
    if not isinstance(queue, list):
        return [], ["mission review queue must contain a queue array"]
    metrics = queue_payload.get("metrics", {})
    if metrics.get("automatic_canonical_mutation_count") != 0:
        errors.append("mission review queue reports automatic canonical mutation")
    claim_map = {item["id"]: item for item in claims_payload.get("claims", [])}
    achievement_map = {
        item["slug"]: item
        for item in (achievements_payload or {}).get("achievements", [])
        if isinstance(item, dict) and isinstance(item.get("slug"), str)
    }
    order = policy["evidence_level_order"]
    plans: list[dict] = []
    planned_claims: set[str] = set()

    for item in queue:
        target = item.get("promotion_target_level")
        if target == "none":
            continue
        if item.get("status") not in policy["eligible_queue_statuses"]:
            errors.append(f"{item.get('packet_id')}: promotion proposal is not accepted")
            continue
        if item.get("canonical_mutation") is not False:
            errors.append(f"{item.get('packet_id')}: queue item permits canonical mutation")
            continue
        packet_id = item.get("packet_id")
        if not isinstance(packet_id, str) or not PACKET_ID.fullmatch(packet_id):
            errors.append("promotion queue item has an invalid packet id")
            continue
        claim_id = item.get("promotion_target_claim_id")
        claim = claim_map.get(claim_id)
        if not claim or claim_id != item.get("claim_id"):
            errors.append(f"{packet_id}: promotion target claim is missing or mismatched")
            continue
        if claim.get("achievement_slug") != item.get("achievement_slug"):
            errors.append(f"{packet_id}: claim achievement does not match the queue item")
            continue
        if claim_id in planned_claims:
            errors.append(f"{packet_id}: duplicate active promotion proposal for {claim_id}")
            continue
        planned_claims.add(claim_id)
        if target not in policy["eligible_target_levels"]:
            errors.append(f"{packet_id}: invalid promotion target {target!r}")
            continue
        path = review_path(item.get("review_path"))
        if path is None or not path.is_file():
            errors.append(f"{packet_id}: source review path is missing or outside reviews/mission")
            continue
        review = load(path)
        rid = review.get("id")
        if not isinstance(rid, str) or not REVIEW_ID.fullmatch(rid):
            errors.append(f"{packet_id}: source review id is invalid")
            continue
        proposal = review.get("promotion_proposal")
        if review.get("packet_id") != packet_id or review.get("disposition") != "accept-evidence":
            errors.append(f"{packet_id}: source review does not represent accepted evidence")
            continue
        if review.get("canonical_mutation") is not False:
            errors.append(f"{packet_id}: source review permits canonical mutation")
            continue
        if not isinstance(proposal, dict) or proposal.get("target_level") != target or proposal.get("target_claim_id") != claim_id:
            errors.append(f"{packet_id}: source review promotion proposal drift")
            continue
        rules = proposal.get("applied_rule_ids")
        if not isinstance(rules, list) or not rules or len(rules) != len(set(rules)):
            errors.append(f"{packet_id}: source review must cite unique adjudication rules")
            continue
        current = claim.get("evidence_level")
        blockers: list[str] = []
        if current not in order:
            errors.append(f"{packet_id}: current claim level is invalid")
            continue
        if order.index(target) <= order.index(current):
            blockers.append("The proposed evidence level is not stronger than the current canonical level.")
        pid = plan_id(rid)
        if not PLAN_ID.fullmatch(pid):
            errors.append(f"{packet_id}: derived promotion plan id is invalid")
            continue
        achievement = achievement_map.get(item["achievement_slug"])
        if achievements_payload is not None and not achievement:
            errors.append(f"{packet_id}: achievement is missing from the canonical catalogue")
            continue
        guide_path = (
            achievement.get("guide_path")
            if achievement
            else f"docs/achievements/{item['achievement_slug']}.md"
        )
        if not isinstance(guide_path, str) or not guide_path:
            errors.append(f"{packet_id}: canonical guide path is missing")
            continue
        operations = source_operations(claim, item, guide_path)
        restore_paths = list(dict.fromkeys([entry["path"] for entry in operations]))
        plans.append({
            "id": pid,
            "source_packet_id": packet_id,
            "source_review_id": rid,
            "source_review_path": item["review_path"],
            "source_issue": item["source_issue"],
            "mission_id": item["mission_id"],
            "achievement_slug": item["achievement_slug"],
            "claim_id": claim_id,
            "claim_type": claim["claim_type"],
            "current_level": current,
            "proposed_level": target,
            "contradiction_id": item.get("contradiction_id"),
            "applied_rule_ids": rules,
            "status": "blocked" if blockers else "ready-for-maintainer-review",
            "blockers": blockers,
            "preconditions": policy["required_preconditions"],
            "source_operations": operations,
            "generated_outputs": policy["generated_output_paths"],
            "validation_commands": policy["validation_commands"],
            "release_gate_impact": release_impact(current, target, order),
            "rollback": {
                "strategy": "revert-isolated-canonical-promotion-commit",
                "isolated_commit_required": True,
                "restore_paths": restore_paths,
                "preserve_review_record": True,
            },
            "maintainer_approval_required": True,
            "separate_pull_request_required": True,
            "automatic_application": False,
        })

    expected_count = sum(
        item.get("promotion_target_level") != "none"
        for item in queue
    )
    if metrics.get("promotion_proposal_count") != expected_count:
        errors.append("mission review queue promotion proposal metric drift")
    return sorted(plans, key=lambda item: item["id"]), errors


def payload(policy: dict, plans: list[dict], campaign_status: dict) -> dict:
    counts = Counter(item["status"] for item in plans)
    return {
        "api_version": "1.0.0",
        "schema_version": policy["schema_version"],
        "status": "live",
        "policy": "/Achievements/promotion-planner/",
        "plan_schema": "/Achievements/api/promotion-plan-schema.json",
        "source_review_queue": "/Achievements/api/mission-review-queue.json",
        "count": len(plans),
        "metrics": {
            "plan_count": len(plans),
            "ready_for_maintainer_review_count": counts["ready-for-maintainer-review"],
            "blocked_count": counts["blocked"],
            "affected_claim_count": len({item["claim_id"] for item in plans}),
            "automatic_application_count": 0,
        },
        "current_campaign_version": campaign_status.get("active_campaign", {}).get("version"),
        "current_campaign_snapshot": campaign_status.get("active_campaign", {}).get("current_snapshot", {}),
        "current_campaign_lifecycle": campaign_status.get("active_campaign", {}).get("lifecycle"),
        "current_release_status": "published",
        "plans": plans,
    }


def schema_payload(policy: dict, schema: dict) -> dict:
    return {
        "api_version": "1.0.0",
        "schema_version": policy["schema_version"],
        "required_property_count": len(schema.get("required", [])),
        "schema": schema,
    }


def markdown(policy: dict, plans: list[dict], campaign_status: dict) -> str:
    ready = sum(item["status"] == "ready-for-maintainer-review" for item in plans)
    blocked = sum(item["status"] == "blocked" for item in plans)
    lines = [
        "---",
        "layout: default",
        "title: Mission evidence promotion planner",
        "description: Fail-closed canonical change plans generated from accepted mission packet reviews.",
        "permalink: /promotion-planner/",
        "---",
        "",
        "## Mission evidence promotion planner",
        "",
        "The planner converts accepted mission-review promotion proposals into isolated impact previews. It never edits canonical evidence, claims, contradictions, missions, thresholds, release gates, tags, or releases.",
        "",
        f"**Plans:** {len(plans)}  ",
        f"**Ready for maintainer review:** {ready}  ",
        f"**Blocked:** {blocked}  ",
        f"**Automatic applications:** 0  ",
        f"**Current campaign:** `{campaign_status.get('active_campaign', {}).get('version', 'unknown')}`  ",
        f"**Campaign lifecycle:** `{campaign_status.get('active_campaign', {}).get('lifecycle', 'unknown')}`",
        "",
        "## Planning rules",
        "",
    ]
    lines.extend(f"- {rule}" for rule in policy["publication_rules"])
    lines.extend(["", "## Promotion plans", ""])
    if not plans:
        lines.append("No accepted mission-review promotion proposal currently qualifies for a canonical change plan. This is the expected launch state.")
    else:
        lines.extend([
            "| Plan | Claim | Transition | Status | Source review |",
            "|---|---|---|---|---|",
        ])
        for item in plans:
            lines.append(
                f"| `{item['id']}` | `{item['claim_id']}` | {item['current_level']} → {item['proposed_level']} | "
                f"{item['status']} | `{item['source_review_id']}` |"
            )
    lines.extend([
        "",
        "## Implementation boundary",
        "",
        "A ready plan still requires a separate maintainer-reviewed pull request. The implementation PR must assign the canonical evidence ID, edit the named source files, regenerate every output, run the complete validation suite, and remain isolated for clean rollback.",
        "",
        "The machine-readable planner output is published at [`/api/promotion-plans.json`](../api/promotion-plans.json).",
        "",
    ])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build or verify mission evidence promotion plans.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", default="promotion-planner-report.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        policy = load(DATA / "promotion-plan-policy.json")
        schema = load(DATA / "promotion-plan.schema.json")
        queue_payload = load(API / "mission-review-queue.json")
        claims_payload = load(DATA / "claims.json")
        achievements_payload = load(DATA / "achievements.json")
        campaign_status = load(API / "campaign-status.json")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error)
        return 1

    errors = validate_policy(policy)
    plans, plan_errors = build_plans(policy, queue_payload, claims_payload, achievements_payload)
    errors.extend(plan_errors)
    report = [
        "# Promotion planner validation",
        "",
        f"- Plans: {len(plans)}",
        f"- Result: {'FAIL' if errors else 'PASS'}",
    ]
    if errors:
        report.extend(["", "## Failures", ""] + [f"- {error}" for error in errors])
    (ROOT / args.report).write_text("\n".join(report) + "\n", encoding="utf-8")
    if errors:
        print("\n".join(errors))
        return 1

    outputs = {
        API / "promotion-plans.json": json.dumps(payload(policy, plans, campaign_status), indent=2, ensure_ascii=False) + "\n",
        API / "promotion-plan-schema.json": json.dumps(schema_payload(policy, schema), indent=2, ensure_ascii=False) + "\n",
        DOCS / "promotion-planner.md": markdown(policy, plans, campaign_status),
    }
    if args.check:
        stale = [
            str(path.relative_to(ROOT))
            for path, expected in outputs.items()
            if not path.is_file() or path.read_text(encoding="utf-8") != expected
        ]
        if stale:
            print("Stale or missing promotion planner outputs: " + ", ".join(stale))
            return 1
    else:
        for path, expected in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")

    print(f"Promotion planner passed: {len(plans)} plan(s), automatic applications 0.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
