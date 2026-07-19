from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
import argparse
import json
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
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
RESULTS = {"Awarded": "awarded", "Not awarded": "not-awarded", "Inconclusive": "inconclusive"}
VISIBILITY = {"Public": "public", "Not applicable": "not-applicable"}


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


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
    return urls, errors


def optional_datetime(value: str, label: str, errors: list[str]) -> str | None:
    if not value:
        return None
    if not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?Z",
        value,
    ):
        errors.append(f"{label} must use UTC ISO format such as 2026-07-19T12:34:00Z.")
    return value


def privacy_findings(body: str) -> list[str]:
    findings: list[str] = []
    for label, pattern in SENSITIVE_PATTERNS.items():
        if pattern.search(body):
            findings.append(label)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Triage a structured evidence issue.")
    parser.add_argument("--event", default=os.environ.get("GITHUB_EVENT_PATH"))
    parser.add_argument("--output", type=Path, default=Path("triage-output"))
    args = parser.parse_args()

    if not args.event:
        print("No GitHub event payload was supplied.")
        return 1

    event = json.loads(Path(args.event).read_text(encoding="utf-8"))
    issue = event.get("issue") or {}
    issue_number = int(issue.get("number") or 0)
    title = str(issue.get("title") or "")
    body = str(issue.get("body") or "")
    issue_url = str(issue.get("html_url") or "")
    author = str((issue.get("user") or {}).get("login") or "unknown")

    queue = load("research-queue.json")
    claims = load("claims.json")
    task_map = {item["id"]: item for item in queue["tasks"]}
    claim_map = {item["id"]: item for item in claims["claims"]}
    values = fields_from(body)
    errors: list[str] = []

    if not title.startswith("[Evidence]"):
        errors.append("Issue title must begin with [Evidence].")

    task_id = values.get("Research task ID", "").strip().upper()
    claim_id = values.get("Claim ID", "").strip().upper()
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
    environment = values.get("Environment and controls", "").strip()
    limitations = values.get("Limitations and failed attempts", "").strip()
    privacy = values.get("Privacy declaration", "").strip()
    consent = values.get("Consent", "").strip()

    if task_id not in task_map:
        errors.append("Research task ID is missing or unknown.")
    if claim_id not in claim_map:
        errors.append("Claim ID is missing or unknown.")
    if claim_id in claim_map and task_id and task_id not in claim_map[claim_id]["research_task_ids"]:
        errors.append("The research task is not linked to the submitted claim.")
    if claim_id in claim_map and achievement != claim_map[claim_id]["achievement_slug"]:
        errors.append("Achievement does not match the selected claim.")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", observation_date):
        errors.append("Observation date must use YYYY-MM-DD.")
    if result is None:
        errors.append("Result must be Awarded, Not awarded, or Inconclusive.")
    if visibility is None:
        errors.append("Repository visibility must be Public or Not applicable.")
    if len(environment) < 20:
        errors.append("Environment and controls requires at least 20 characters.")
    if len(limitations) < 10:
        errors.append("Limitations and failed attempts requires at least 10 characters.")
    if privacy != "I confirm that this submission contains no credentials, private repository data, unnecessary personal identifiers, or financial details.":
        errors.append("Privacy declaration was not confirmed.")
    if consent != "I consent to this observation being reviewed and published in privacy-safe form.":
        errors.append("Publication consent was not confirmed.")

    findings = privacy_findings(body)
    if findings:
        errors.append("Automated privacy screening detected: " + ", ".join(findings) + ".")

    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.mkdir(parents=True, exist_ok=True)
    accepted = not errors
    status = "accepted-for-human-review" if accepted else "blocked"
    result_payload = {
        "schema_version": "1.0.0",
        "issue_number": issue_number,
        "issue_url": issue_url,
        "status": status,
        "errors": errors,
        "privacy_findings": findings,
    }
    (output / "result.json").write_text(
        json.dumps(result_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    if accepted:
        draft = {
            "schema_version": "1.0.0",
            "id": f"DRAFT-ISSUE-{issue_number}",
            "source_issue": issue_url,
            "submitted_by": author,
            "achievement_slug": achievement,
            "claim_id": claim_id,
            "research_task_id": task_id,
            "observed_at": observation_date,
            "result": result,
            "repository_visibility": visibility,
            "qualifying_event_time_utc": event_time,
            "first_badge_visibility_time_utc": visible_time,
            "source_urls": sources,
            "environment_and_controls": environment,
            "limitations": limitations,
            "reproduction_status": {
                "awarded": "positive-observation",
                "not-awarded": "negative-observation",
                "inconclusive": "inconclusive-observation",
            }[result],
            "reviewer_decision": "pending-human-review",
            "privacy_status": "automated-screening-passed",
        }
        (output / "draft-evidence-record.json").write_text(
            json.dumps(draft, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    summary = [
        f"## Evidence triage for issue #{issue_number}",
        "",
        f"**Result:** `{status}`",
        "",
    ]
    if errors:
        summary.extend(["### Required corrections", "", *[f"- {item}" for item in errors]])
    else:
        summary.extend([
            "The submission passed structural and automated privacy screening.",
            "",
            "A draft evidence record and draft pull request can now be created. "
            "Human review remains mandatory before the evidence register changes.",
        ])
    (output / "summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(status)
    return 0


if __name__ == "__main__":
    sys.exit(main())
