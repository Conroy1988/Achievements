from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import argparse
import json
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
FIELD_PATTERN = re.compile(
    r"^### (?P<label>[^\n]+)\n\n(?P<value>.*?)(?=^### |\Z)",
    re.MULTILINE | re.DOTALL,
)
SENSITIVE_PATTERNS = {
    "GitHub token": re.compile(r"\b(?:ghp|github_pat|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b"),
    "API secret": re.compile(r"\b(?:api[_ -]?key|secret|password)\s*[:=]\s*\S+", re.IGNORECASE),
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "payment-card-like number": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
}
RESULTS = {
    "Awarded": "awarded",
    "Not awarded": "not-awarded",
    "Inconclusive": "inconclusive",
    "Blocked": "blocked",
    "Processing delayed": "processing-delayed",
}
VISIBILITY = {"Public": "public", "Not applicable": "not-applicable"}
SAFEGUARD_TEXT = (
    "I confirm that no artificial qualifying activity, spam, false attribution, "
    "star solicitation, answer farming, or protection bypass was used."
)
PRIVACY_TEXT = (
    "I confirm that this submission contains no credentials, private repository data, "
    "unnecessary personal identifiers, private communications, or financial details."
)
CONSENT_TEXT = "I consent to this mission evidence being reviewed and published in privacy-safe form."


def load_json(root: Path, relative: str) -> dict:
    value = json.loads((root / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{relative} must contain a JSON object")
    return value


def fields_from(body: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for match in FIELD_PATTERN.finditer(body.replace("\r\n", "\n")):
        value = match.group("value").strip()
        if value == "_No response_":
            value = ""
        result[match.group("label").strip()] = value
    return result


def parse_urls(value: str) -> tuple[list[str], list[str]]:
    urls: list[str] = []
    errors: list[str] = []
    for line in value.splitlines():
        candidate = line.strip().lstrip("-").strip()
        if not candidate:
            continue
        parsed = urlparse(candidate)
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append(f"Source URL must be a complete HTTPS URL: {candidate}")
        else:
            urls.append(candidate)
    if not urls:
        errors.append("At least one public HTTPS source URL is required.")
    if len(urls) > 10:
        errors.append("No more than ten source URLs may be submitted.")
    return urls, errors


def parse_evidence_values(value: str) -> tuple[dict[str, str], list[str]]:
    evidence: dict[str, str] = {}
    errors: list[str] = []
    for line_number, raw in enumerate(value.splitlines(), start=1):
        line = raw.strip().lstrip("-").strip()
        if not line:
            continue
        if ":" not in line:
            errors.append(f"Required evidence line {line_number} must use key: value format.")
            continue
        key, item_value = (part.strip() for part in line.split(":", 1))
        if not re.fullmatch(r"[a-z0-9_]+", key):
            errors.append(f"Required evidence key is invalid: {key}")
            continue
        if key in evidence:
            errors.append(f"Required evidence key is duplicated: {key}")
            continue
        if not item_value:
            errors.append(f"Required evidence value is empty: {key}")
            continue
        evidence[key] = item_value
    return evidence, errors


def optional_datetime(value: str, label: str, errors: list[str]) -> str | None:
    if not value:
        return None
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?Z", value):
        errors.append(f"{label} must use UTC ISO format such as 2026-07-22T19:00:00Z.")
    return value


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def privacy_findings(body: str) -> list[str]:
    return [label for label, pattern in SENSITIVE_PATTERNS.items() if pattern.search(body)]


def none_value(value: str) -> str | None:
    cleaned = value.strip()
    return None if cleaned.lower() in {"", "none", "not applicable", "n/a"} else cleaned.upper()


def triage(event: dict, repository_root: Path = ROOT) -> tuple[dict, dict | None, str]:
    issue = event.get("issue") or {}
    issue_number = int(issue.get("number") or 0)
    title = str(issue.get("title") or "")
    body = str(issue.get("body") or "")
    issue_url = str(issue.get("html_url") or "")
    author = str((issue.get("user") or {}).get("login") or "unknown")
    submission_time_raw = str(issue.get("updated_at") or issue.get("created_at") or "")

    missions = load_json(repository_root, "api/acquisition-missions.json")
    queue = load_json(repository_root, "data/research-queue.json")
    claims = load_json(repository_root, "data/claims.json")
    contradictions = load_json(repository_root, "data/contradictions.json")
    mission_map = {item["id"]: item for item in missions.get("missions", [])}
    task_map = {item["id"]: item for item in queue.get("tasks", [])}
    claim_map = {item["id"]: item for item in claims.get("claims", [])}
    contradiction_map = {item["id"]: item for item in contradictions.get("records", [])}
    values = fields_from(body)
    errors: list[str] = []

    if not title.startswith("[Mission Evidence]"):
        errors.append("Issue title must begin with [Mission Evidence].")

    mission_id = values.get("Mission ID", "").strip().upper()
    task_id = values.get("Research task ID", "").strip().upper()
    claim_id = none_value(values.get("Claim ID", ""))
    contradiction_id = none_value(values.get("Contradiction ID", ""))
    achievement = values.get("Achievement", "").strip()
    observation_date = values.get("Observation date", "").strip()
    result = RESULTS.get(values.get("Result", "").strip())
    visibility = VISIBILITY.get(values.get("Repository visibility", "").strip())
    event_time = optional_datetime(
        values.get("Qualifying event time (UTC)", "").strip(),
        "Qualifying event time",
        errors,
    )
    visible_time = optional_datetime(
        values.get("First badge visibility time (UTC)", "").strip(),
        "First badge visibility time",
        errors,
    )
    sources, url_errors = parse_urls(values.get("Source URLs", ""))
    errors.extend(url_errors)
    evidence_values, evidence_errors = parse_evidence_values(values.get("Required evidence values", ""))
    errors.extend(evidence_errors)
    environment = values.get("Environment and controls", "").strip()
    limitations = values.get("Limitations and failed attempts", "").strip()
    safeguard = values.get("Safeguard declaration", "").strip()
    privacy = values.get("Privacy declaration", "").strip()
    consent = values.get("Consent", "").strip()

    mission = mission_map.get(mission_id)
    if not mission:
        errors.append("Mission ID is missing or unknown.")
    else:
        if mission.get("status") in {"complete", "cancelled"}:
            errors.append("This mission is not accepting new evidence.")
        expected_achievement = mission.get("achievement_slug") or "cross-achievement"
        if achievement != expected_achievement:
            errors.append("Achievement does not match the selected mission.")
        if task_id not in mission.get("research_task_ids", []):
            errors.append("Research task is not linked to the selected mission.")
        if mission.get("claim_ids"):
            if claim_id not in mission["claim_ids"]:
                errors.append("Claim is missing or not linked to the selected mission.")
        elif claim_id is not None:
            errors.append("This cross-achievement mission does not accept a claim ID.")
        if mission.get("contradiction_ids"):
            if contradiction_id not in mission["contradiction_ids"]:
                errors.append("Contradiction is missing or not linked to the selected mission.")
        elif contradiction_id is not None:
            errors.append("This mission does not accept a contradiction ID.")
        missing_evidence = sorted(set(mission.get("required_evidence", [])) - set(evidence_values))
        if missing_evidence:
            errors.append("Missing required evidence keys: " + ", ".join(missing_evidence) + ".")
        unexpected_evidence = sorted(set(evidence_values) - set(mission.get("required_evidence", [])))
        if unexpected_evidence:
            errors.append("Unexpected required evidence keys: " + ", ".join(unexpected_evidence) + ".")
        if mission.get("status") == "scheduled":
            try:
                submission_time = parse_datetime(submission_time_raw)
                no_action_before = parse_datetime(str(mission["no_action_before"]))
                if submission_time < no_action_before:
                    errors.append(
                        "Scheduled mission evidence cannot be submitted before "
                        + str(mission["no_action_before"])
                        + "."
                    )
            except (KeyError, TypeError, ValueError):
                errors.append("Scheduled mission timing could not be validated.")

    if task_id not in task_map:
        errors.append("Research task ID is missing or unknown.")
    if claim_id is not None and claim_id not in claim_map:
        errors.append("Claim ID is unknown.")
    if contradiction_id is not None and contradiction_id not in contradiction_map:
        errors.append("Contradiction ID is unknown.")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", observation_date):
        errors.append("Observation date must use YYYY-MM-DD.")
    if result is None:
        errors.append("Result is invalid.")
    if visibility is None:
        errors.append("Repository visibility must be Public or Not applicable.")
    if len(environment) < 20:
        errors.append("Environment and controls requires at least 20 characters.")
    if len(limitations) < 10:
        errors.append("Limitations and failed attempts requires at least 10 characters.")
    if safeguard != SAFEGUARD_TEXT:
        errors.append("Safeguard declaration was not confirmed.")
    if privacy != PRIVACY_TEXT:
        errors.append("Privacy declaration was not confirmed.")
    if consent != CONSENT_TEXT:
        errors.append("Publication consent was not confirmed.")

    findings = privacy_findings(body)
    if findings:
        errors.append("Automated privacy screening detected: " + ", ".join(findings) + ".")

    status = "accepted-for-human-review" if not errors else "blocked"
    result_payload = {
        "schema_version": "1.0.0",
        "issue_number": issue_number,
        "issue_url": issue_url,
        "mission_id": mission_id or None,
        "status": status,
        "errors": errors,
        "privacy_findings": findings,
    }
    packet: dict | None = None
    if not errors and mission is not None:
        packet = {
            "schema_version": "1.0.0",
            "id": f"MISSION-DRAFT-ISSUE-{issue_number}",
            "source_issue": issue_url,
            "submitted_by": author,
            "submitted_at": submission_time_raw,
            "mission_id": mission_id,
            "mission_rank": mission["rank"],
            "mission_title": mission["title"],
            "mission_status_at_submission": mission["status"],
            "achievement_slug": achievement,
            "claim_id": claim_id,
            "contradiction_id": contradiction_id,
            "research_task_id": task_id,
            "protocol_ids": mission.get("protocol_ids", []),
            "observation_date": observation_date,
            "result": result,
            "repository_visibility": visibility,
            "qualifying_event_time_utc": event_time,
            "first_badge_visibility_time_utc": visible_time,
            "source_urls": sources,
            "required_evidence": evidence_values,
            "environment_and_controls": environment,
            "limitations": limitations,
            "safeguard_status": "declared-compliant",
            "privacy_status": "automated-screening-passed",
            "reviewer_decision": "pending-human-review",
        }

    summary = [
        f"## Mission evidence triage for issue #{issue_number}",
        "",
        f"**Result:** `{status}`",
        "",
    ]
    if errors:
        summary += ["### Required corrections", ""] + [f"- {item}" for item in errors]
    else:
        summary += [
            "The submission passed mission relationship, timing, structural, safeguard, and automated privacy screening.",
            "",
            "A draft mission-evidence packet and draft pull request can now be created. Human review remains mandatory before any canonical evidence or mission state changes.",
        ]
    return result_payload, packet, "\n".join(summary) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Triage a structured mission evidence issue.")
    parser.add_argument("--event", default=os.environ.get("GITHUB_EVENT_PATH"))
    parser.add_argument("--output", type=Path, default=Path("mission-triage-output"))
    args = parser.parse_args()
    if not args.event:
        print("No GitHub event payload was supplied.")
        return 1
    event = json.loads(Path(args.event).read_text(encoding="utf-8"))
    result, packet, summary = triage(event)
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.mkdir(parents=True, exist_ok=True)
    (output / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / "summary.md").write_text(summary, encoding="utf-8")
    if packet is not None:
        (output / "draft-mission-evidence-packet.json").write_text(
            json.dumps(packet, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(result["status"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
