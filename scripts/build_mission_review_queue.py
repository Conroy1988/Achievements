from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
API = ROOT / "api"
DOCS = ROOT / "docs"
PACKETS = ROOT / "triage" / "mission-drafts"
REVIEWS = ROOT / "reviews" / "mission"

REVIEW_ID = re.compile(r"^MRV-[0-9]{4}-[0-9]{3}$")
PACKET_ID = re.compile(r"^MISSION-DRAFT-ISSUE-[0-9]+$")
LOGIN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def load_records(directory: Path) -> list[tuple[Path, dict]]:
    if not directory.exists():
        return []
    rows: list[tuple[Path, dict]] = []
    for path in sorted(directory.glob("*.json")):
        if path.name.endswith(".template.json"):
            continue
        rows.append((path, load(path)))
    return rows


def parse_time(value: object, label: str, errors: list[str]) -> None:
    if not isinstance(value, str):
        errors.append(f"{label} must be an ISO date-time string")
        return
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} must be a valid ISO date-time")


def validate_policy(policy: dict, adjudication: dict) -> list[str]:
    errors: list[str] = []
    rules = {item.get("id") for item in adjudication.get("rules", [])}
    if policy.get("canonical_mutation_allowed") is not False:
        errors.append("policy must prohibit automatic canonical mutation")
    dispositions = policy.get("dispositions")
    if not isinstance(dispositions, dict) or len(dispositions) < 5:
        errors.append("policy must define the five review dispositions")
    checklist = policy.get("required_checklist")
    if not isinstance(checklist, list) or len(checklist) < 10 or len(checklist) != len(set(checklist)):
        errors.append("policy required_checklist must contain ten unique fields")
    promotions = policy.get("promotion_requirements")
    if not isinstance(promotions, dict) or set(promotions) != {"observed", "confirmed", "official"}:
        errors.append("policy must define observed, confirmed, and official promotion requirements")
        promotions = {}
    for level, requirement in promotions.items():
        if requirement.get("rule_id") not in rules:
            errors.append(f"promotion level {level} references an unknown adjudication rule")
        if requirement.get("minimum_reviewers", 0) < 2:
            errors.append(f"promotion level {level} must require at least two reviewers")
        if requirement.get("minimum_unconflicted_reviewers", 0) < 1:
            errors.append(f"promotion level {level} must require an unconflicted reviewer")
    if not policy.get("publication_rules") or len(policy["publication_rules"]) < 5:
        errors.append("policy must publish at least five review rules")
    return errors


def validate_packet(path: Path, packet: dict, missions: dict, claims: dict, contradictions: dict) -> list[str]:
    label = str(path.relative_to(ROOT))
    errors: list[str] = []
    packet_id = packet.get("id")
    if not isinstance(packet_id, str) or not PACKET_ID.fullmatch(packet_id):
        errors.append(f"{label}: invalid packet id")
    mission = missions.get(packet.get("mission_id"))
    if not mission:
        errors.append(f"{label}: unknown mission")
        return errors
    if packet.get("mission_title") != mission.get("title"):
        errors.append(f"{label}: mission title drift")
    if packet.get("achievement_slug") != (mission.get("achievement_slug") or "cross-achievement"):
        errors.append(f"{label}: achievement does not match mission")
    if packet.get("research_task_id") not in mission.get("research_task_ids", []):
        errors.append(f"{label}: research task does not match mission")
    claim_id = packet.get("claim_id")
    if mission.get("claim_ids"):
        if claim_id not in mission["claim_ids"] or claim_id not in claims:
            errors.append(f"{label}: claim does not match mission")
    elif claim_id is not None:
        errors.append(f"{label}: cross-achievement packet must not define a claim")
    contradiction_id = packet.get("contradiction_id")
    if mission.get("contradiction_ids"):
        if contradiction_id not in mission["contradiction_ids"] or contradiction_id not in contradictions:
            errors.append(f"{label}: contradiction does not match mission")
    elif contradiction_id is not None:
        errors.append(f"{label}: packet must not define a contradiction")
    evidence = packet.get("required_evidence")
    if not isinstance(evidence, dict) or set(evidence) != set(mission.get("required_evidence", [])):
        errors.append(f"{label}: required evidence does not match mission contract")
    if packet.get("reviewer_decision") != "pending-human-review":
        errors.append(f"{label}: draft packet must remain pending human review")
    if packet.get("privacy_status") != "automated-screening-passed":
        errors.append(f"{label}: packet did not pass privacy screening")
    if packet.get("safeguard_status") != "declared-compliant":
        errors.append(f"{label}: packet did not confirm safeguards")
    if not isinstance(packet.get("source_urls"), list) or not packet["source_urls"]:
        errors.append(f"{label}: packet must include public source URLs")
    return errors


def validate_review(path: Path, review: dict, packet: dict | None, policy: dict, missions: dict, claims: dict, rule_ids: set[str]) -> list[str]:
    label = str(path.relative_to(ROOT))
    errors: list[str] = []
    review_id = review.get("id")
    if not isinstance(review_id, str) or not REVIEW_ID.fullmatch(review_id):
        errors.append(f"{label}: invalid review id")
    if packet is None:
        errors.append(f"{label}: packet_id does not reference an existing draft")
        return errors
    if review.get("packet_id") != packet.get("id"):
        errors.append(f"{label}: packet id mismatch")
    if review.get("mission_id") != packet.get("mission_id"):
        errors.append(f"{label}: mission id mismatch")
    expected_source = str(Path("triage/mission-drafts") / Path(review.get("source_packet", "")).name)
    if review.get("source_packet") != expected_source:
        errors.append(f"{label}: source_packet must point into triage/mission-drafts")
    disposition = review.get("disposition")
    disposition_rule = policy.get("dispositions", {}).get(disposition)
    if not disposition_rule:
        errors.append(f"{label}: unknown disposition")
        disposition_rule = {}
    parse_time(review.get("reviewed_at"), f"{label}: reviewed_at", errors)

    reviewers = review.get("reviewers")
    if not isinstance(reviewers, list) or not reviewers:
        errors.append(f"{label}: at least one reviewer is required")
        reviewers = []
    logins: list[str] = []
    conflicts = set(policy.get("conflict_values", []))
    for reviewer in reviewers:
        if not isinstance(reviewer, dict):
            errors.append(f"{label}: reviewer entries must be objects")
            continue
        login = reviewer.get("login")
        if not isinstance(login, str) or not LOGIN.fullmatch(login):
            errors.append(f"{label}: invalid reviewer login")
        else:
            logins.append(login.lower())
        if reviewer.get("conflict") not in conflicts:
            errors.append(f"{label}: invalid reviewer conflict disclosure")
        notes = reviewer.get("notes")
        if not isinstance(notes, str) or len(notes.strip()) < 2:
            errors.append(f"{label}: reviewer notes are required")
    if len(logins) != len(set(logins)):
        errors.append(f"{label}: reviewer logins must be unique")
    if len(reviewers) < int(disposition_rule.get("minimum_reviewers", 1)):
        errors.append(f"{label}: disposition does not meet its reviewer minimum")

    checklist = review.get("checklist")
    required_checklist = policy.get("required_checklist", [])
    if not isinstance(checklist, dict) or set(checklist) != set(required_checklist):
        errors.append(f"{label}: checklist fields do not match policy")
        checklist = {}
    elif any(not isinstance(value, bool) for value in checklist.values()):
        errors.append(f"{label}: checklist values must be booleans")
    rationale = review.get("rationale")
    if not isinstance(rationale, str) or len(rationale.strip()) < 40:
        errors.append(f"{label}: rationale must contain at least 40 characters")
    if review.get("canonical_mutation") is not False:
        errors.append(f"{label}: canonical_mutation must be false")

    proposal = review.get("promotion_proposal")
    if not isinstance(proposal, dict):
        errors.append(f"{label}: promotion_proposal must be an object")
        return errors
    target_level = proposal.get("target_level")
    target_claim = proposal.get("target_claim_id")
    applied_rules = proposal.get("applied_rule_ids")
    if not isinstance(applied_rules, list) or len(applied_rules) != len(set(applied_rules)):
        errors.append(f"{label}: applied_rule_ids must be a unique array")
        applied_rules = []
    unknown_rules = set(applied_rules) - rule_ids
    if unknown_rules:
        errors.append(f"{label}: unknown adjudication rules: {', '.join(sorted(unknown_rules))}")

    if target_level == "none":
        if target_claim is not None or applied_rules:
            errors.append(f"{label}: no-promotion review must not define a target claim or rules")
    elif target_level in policy.get("promotion_requirements", {}):
        if disposition != "accept-evidence":
            errors.append(f"{label}: promotion proposals require accept-evidence disposition")
        if target_claim != packet.get("claim_id") or target_claim not in claims:
            errors.append(f"{label}: promotion target claim must match the packet")
        mission = missions.get(packet.get("mission_id"), {})
        allowed = {item.get("target_level") for item in mission.get("promotion_targets", []) if item.get("claim_id") == target_claim}
        if target_level not in allowed:
            errors.append(f"{label}: promotion level is not published by the mission")
        requirement = policy["promotion_requirements"][target_level]
        if requirement["rule_id"] not in applied_rules:
            errors.append(f"{label}: required adjudication rule is missing")
        if len(reviewers) < requirement["minimum_reviewers"]:
            errors.append(f"{label}: promotion proposal lacks the required reviewers")
        unconflicted = sum(item.get("conflict") == "none" for item in reviewers if isinstance(item, dict))
        if unconflicted < requirement["minimum_unconflicted_reviewers"]:
            errors.append(f"{label}: promotion proposal lacks an unconflicted reviewer")
        if checklist and not all(checklist.values()):
            errors.append(f"{label}: every checklist item must pass for a promotion proposal")
    else:
        errors.append(f"{label}: invalid promotion target level")
    return errors


def build_queue(policy: dict, packet_rows: list[tuple[Path, dict]], review_rows: list[tuple[Path, dict]]) -> dict:
    review_by_packet = {row["packet_id"]: (path, row) for path, row in review_rows}
    dispositions = policy["dispositions"]
    queue: list[dict] = []
    for path, packet in packet_rows:
        review_info = review_by_packet.get(packet["id"])
        if review_info:
            review_path, review = review_info
            promotion = review["promotion_proposal"]
            queue.append({
                "packet_id": packet["id"], "mission_id": packet["mission_id"], "mission_title": packet["mission_title"],
                "achievement_slug": packet["achievement_slug"], "claim_id": packet.get("claim_id"),
                "contradiction_id": packet.get("contradiction_id"), "research_task_id": packet["research_task_id"],
                "source_issue": packet["source_issue"], "packet_path": str(path.relative_to(ROOT)),
                "review_path": str(review_path.relative_to(ROOT)), "status": dispositions[review["disposition"]]["queue_status"],
                "disposition": review["disposition"], "reviewer_count": len(review["reviewers"]),
                "promotion_target_level": promotion["target_level"], "promotion_target_claim_id": promotion["target_claim_id"],
                "canonical_mutation": False,
            })
        else:
            queue.append({
                "packet_id": packet["id"], "mission_id": packet["mission_id"], "mission_title": packet["mission_title"],
                "achievement_slug": packet["achievement_slug"], "claim_id": packet.get("claim_id"),
                "contradiction_id": packet.get("contradiction_id"), "research_task_id": packet["research_task_id"],
                "source_issue": packet["source_issue"], "packet_path": str(path.relative_to(ROOT)), "review_path": None,
                "status": "pending-review", "disposition": None, "reviewer_count": 0,
                "promotion_target_level": "none", "promotion_target_claim_id": None, "canonical_mutation": False,
            })
    counts = Counter(item["status"] for item in queue)
    return {
        "api_version": "1.0.0", "schema_version": policy["schema_version"], "status": "live",
        "policy": "/Achievements/mission-review-queue/", "review_schema": "/Achievements/api/mission-review-schema.json",
        "packet_directory": policy["packet_directory"], "review_directory": policy["review_directory"], "count": len(queue),
        "metrics": {
            "packet_count": len(queue), "pending_review_count": counts["pending-review"], "accepted_count": counts["accepted"],
            "deferred_count": counts["deferred"], "retained_inconclusive_count": counts["retained-inconclusive"],
            "needs_correction_count": counts["needs-correction"], "rejected_count": counts["rejected"],
            "promotion_proposal_count": sum(item["promotion_target_level"] != "none" for item in queue),
            "automatic_canonical_mutation_count": 0,
        },
        "by_status": dict(sorted(counts.items())), "queue": queue,
    }


def build_schema(schema: dict) -> dict:
    return {"api_version": "1.0.0", "schema_version": "1.0.0", "count": len(schema.get("properties", {})), "schema": schema}


def markdown(queue: dict, policy: dict) -> str:
    lines = [
        "---", "layout: default", "title: Mission packet review queue",
        "description: Human review and adjudication queue for privacy-screened mission evidence packets.",
        "permalink: /mission-review-queue/", "---", "", "## Mission packet review queue", "",
        "This queue begins after automated mission intake. A packet appears here only after structural, relationship, timing, safeguard, and privacy screening has passed.", "",
        f"**Packets:** {queue['metrics']['packet_count']}  ", f"**Pending review:** {queue['metrics']['pending_review_count']}  ",
        f"**Promotion proposals:** {queue['metrics']['promotion_proposal_count']}  ", "**Automatic canonical mutations:** 0", "",
        "## Review dispositions", "", "| Disposition | Queue result | Promotion proposal |", "|---|---|---|",
    ]
    for name, rule in policy["dispositions"].items():
        lines.append(f"| `{name}` | `{rule['queue_status']}` | {'allowed' if rule['promotion_proposal_allowed'] else 'not allowed'} |")
    lines += ["", "## Current queue", ""]
    if not queue["queue"]:
        lines.append("No mission packet has passed intake yet. The empty queue is the correct launch state.")
    else:
        lines += ["| Packet | Mission | Achievement | Status | Promotion |", "|---|---|---|---|---|"]
        for item in queue["queue"]:
            lines.append(f"| `{item['packet_id']}` | `{item['mission_id']}` | {item['achievement_slug']} | `{item['status']}` | `{item['promotion_target_level']}` |")
    lines += [
        "", "## Promotion controls", "",
        "- Promotion proposals require the mission to publish that exact claim and target level.",
        "- The applicable adjudication rule must be named explicitly.",
        "- At least two reviewers and one unconflicted reviewer are required.",
        "- Every checklist item must pass.",
        "- A proposal cannot edit canonical claims, contradictions, thresholds, missions, or releases automatically.",
        "", "## Machine-readable contracts", "", "- [Review queue](../api/mission-review-queue.json)",
        "- [Review record schema](../api/mission-review-schema.json)", "- [Review policy](../data/mission-review-policy.json)", "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate mission packet reviews and publish the review queue.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", default="mission-review-report.md")
    args = parser.parse_args()
    try:
        policy = load(DATA / "mission-review-policy.json")
        schema = load(DATA / "mission-review.schema.json")
        missions_payload = load(API / "acquisition-missions.json")
        claims_payload = load(DATA / "claims.json")
        contradictions_payload = load(DATA / "contradictions.json")
        adjudication = load(API / "adjudication.json")
        packet_rows = load_records(PACKETS)
        review_rows = load_records(REVIEWS)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error)
        return 1
    missions = {item["id"]: item for item in missions_payload.get("missions", [])}
    claims = {item["id"]: item for item in claims_payload.get("claims", [])}
    contradictions = {item["id"]: item for item in contradictions_payload.get("records", [])}
    rule_ids = {item["id"] for item in adjudication.get("rules", [])}
    errors = validate_policy(policy, adjudication)
    packets_by_id: dict[str, dict] = {}
    for path, packet in packet_rows:
        errors.extend(validate_packet(path, packet, missions, claims, contradictions))
        packet_id = packet.get("id")
        if isinstance(packet_id, str):
            if packet_id in packets_by_id:
                errors.append(f"duplicate packet id: {packet_id}")
            packets_by_id[packet_id] = packet
    reviewed_packets: set[str] = set()
    review_ids: set[str] = set()
    for path, review in review_rows:
        review_id = review.get("id")
        if isinstance(review_id, str):
            if review_id in review_ids:
                errors.append(f"duplicate review id: {review_id}")
            review_ids.add(review_id)
        packet_id = review.get("packet_id")
        if isinstance(packet_id, str):
            if packet_id in reviewed_packets:
                errors.append(f"multiple final review records for packet: {packet_id}")
            reviewed_packets.add(packet_id)
        errors.extend(validate_review(path, review, packets_by_id.get(packet_id), policy, missions, claims, rule_ids))
    queue = build_queue(policy, packet_rows, review_rows)
    outputs = {
        API / "mission-review-queue.json": json.dumps(queue, indent=2, ensure_ascii=False) + "\n",
        API / "mission-review-schema.json": json.dumps(build_schema(schema), indent=2, ensure_ascii=False) + "\n",
        DOCS / "mission-review-queue.md": markdown(queue, policy),
    }
    report = ["# Mission packet review validation", "", f"- Draft packets: {len(packet_rows)}", f"- Review records: {len(review_rows)}", f"- Queue entries: {len(queue['queue'])}", f"- Result: {'FAIL' if errors else 'PASS'}"]
    if errors:
        report += ["", "## Failures", ""] + [f"- {item}" for item in errors]
    (ROOT / args.report).write_text("\n".join(report) + "\n", encoding="utf-8")
    if errors:
        print("\n".join(errors))
        return 1
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, expected in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != expected]
        if stale:
            print("Stale or missing mission review outputs: " + ", ".join(stale))
            return 1
    else:
        for path, expected in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
    print(f"Mission review queue passed: {len(packet_rows)} packets, {len(review_rows)} reviews.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
