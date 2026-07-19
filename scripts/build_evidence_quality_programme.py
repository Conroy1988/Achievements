from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/evidence-quality-programme.json"
CLAIMS = ROOT / "data/claims.json"
CONTRADICTIONS = ROOT / "data/contradictions.json"
OBSERVATIONS = ROOT / "data/public-observations.json"
FRAGMENTS = ROOT / "data/official-achievement-fragments.json"
COVERAGE = ROOT / "api/coverage.json"

DOCS = {
    "event": ROOT / "docs/event-linked-evidence.md",
    "boundary": ROOT / "docs/threshold-boundary-programme.md",
    "adjudication": ROOT / "docs/evidence-adjudication-engine.md",
    "contradiction": ROOT / "docs/contradiction-resolution-programme.md",
    "release": ROOT / "docs/evidence-quality-release-gate.md",
}
APIS = {
    "event": ROOT / "api/event-linked-evidence.json",
    "boundary": ROOT / "api/threshold-boundaries.json",
    "adjudication": ROOT / "api/adjudication.json",
    "contradiction": ROOT / "api/contradiction-assessments.json",
    "release": ROOT / "api/release-readiness.json",
}

PATTERNS = {
    "event": re.compile(r"^EVT-\d{4}-\d{3}$"),
    "boundary": re.compile(r"^BND-\d{3}$"),
    "rule": re.compile(r"^ADJ-R\d{2}$"),
    "decision": re.compile(r"^ADJ-D\d{3}$"),
}


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def public_github(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    return parsed.scheme == "https" and parsed.netloc == "github.com" and bool(parsed.path.strip("/"))


def timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc) if parsed.tzinfo else None


def check_ids(rows: list[dict], field: str, pattern: re.Pattern[str], errors: list[str]) -> set[str]:
    seen: set[str] = set()
    for row in rows:
        value = row.get(field)
        if not isinstance(value, str) or not pattern.fullmatch(value):
            errors.append(f"invalid {field}: {value!r}")
        elif value in seen:
            errors.append(f"duplicate {field}: {value}")
        else:
            seen.add(value)
    return seen


def validate(source: dict, claims: dict, contradictions: dict, observations: dict, fragments: dict, coverage: dict) -> list[str]:
    errors: list[str] = []
    claim_by_id = {row["id"]: row for row in claims.get("claims", [])}
    contradiction_ids = {row["id"] for row in contradictions.get("records", [])}
    observation_ids = {row["id"] for row in observations.get("observations", [])}
    fragment_ids = {row["id"] for row in fragments.get("records", [])}

    if source.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    phases = source.get("phases", [])
    if [row.get("number") for row in phases] != [52, 53, 54, 55, 56]:
        errors.append("phases must contain 52 through 56 in order")
    if any(row.get("status") not in {"complete", "implemented-release-blocked", "implemented-release-ready"} for row in phases):
        errors.append("invalid phase status")

    events = source.get("event_evidence", [])
    event_ids = check_ids(events, "id", PATTERNS["event"], errors)
    if not events:
        errors.append("event_evidence must be non-empty")
    for row in events:
        rid = row.get("id", "event")
        if not public_github(row.get("event_url")):
            errors.append(f"{rid}: event_url must be public github.com")
        created, completed = timestamp(row.get("created_at")), timestamp(row.get("completed_at"))
        if not created or not completed or completed < created:
            errors.append(f"{rid}: invalid timestamps")
        elif row.get("elapsed_seconds") != int((completed - created).total_seconds()):
            errors.append(f"{rid}: elapsed_seconds drift")
        if row.get("adjudication_status") not in {"candidate-observed", "negative-inconclusive", "accepted", "rejected"}:
            errors.append(f"{rid}: invalid adjudication status")
        claim_ids = row.get("claim_ids", [])
        if not claim_ids or any(cid not in claim_by_id for cid in claim_ids):
            errors.append(f"{rid}: unknown or missing claim")
        elif any(claim_by_id[cid]["achievement_slug"] != row.get("achievement_slug") for cid in claim_ids):
            errors.append(f"{rid}: claim achievement mismatch")
        if len(row.get("public_facts", [])) < 2 or len(row.get("limitations", [])) < 2:
            errors.append(f"{rid}: two public facts and two limitations are required")

    boundaries = source.get("boundary_programmes", [])
    boundary_ids = check_ids(boundaries, "id", PATTERNS["boundary"], errors)
    if not boundaries:
        errors.append("boundary_programmes must be non-empty")
    for row in boundaries:
        rid = row.get("id", "boundary")
        cid = row.get("claim_id")
        if cid not in claim_by_id or claim_by_id[cid]["achievement_slug"] != row.get("achievement_slug"):
            errors.append(f"{rid}: invalid claim relationship")
        values = row.get("reported_boundaries", [])
        if not values or values != sorted(set(values)) or any(not isinstance(v, int) or v <= 0 for v in values):
            errors.append(f"{rid}: boundaries must be unique increasing positive integers")
        if any(ref not in observation_ids for ref in row.get("observation_ids", [])):
            errors.append(f"{rid}: unknown observation reference")
        if any(ref not in event_ids for ref in row.get("event_ids", [])):
            errors.append(f"{rid}: unknown event reference")

    rules = source.get("adjudication_rules", [])
    check_ids(rules, "id", PATTERNS["rule"], errors)
    if len(rules) < 4 or any(not row.get("requirements") for row in rules):
        errors.append("adjudication rules are incomplete")
    decisions = source.get("adjudication_decisions", [])
    check_ids(decisions, "id", PATTERNS["decision"], errors)
    if not decisions:
        errors.append("adjudication decisions are missing")
    for row in decisions:
        if row.get("claim_id") not in claim_by_id or row.get("decision") not in {"promote", "defer", "reject", "retract"}:
            errors.append(f"{row.get('id')}: invalid adjudication decision")
        if row.get("decision") == "promote":
            errors.append(f"{row.get('id')}: automatic promotion is prohibited")

    assessments = source.get("contradiction_assessments", [])
    seen_ctr: set[str] = set()
    valid_basis = event_ids | boundary_ids | fragment_ids
    if len(assessments) != len(contradiction_ids):
        errors.append("every contradiction requires one assessment")
    for row in assessments:
        cid = row.get("contradiction_id")
        if cid not in contradiction_ids or cid in seen_ctr:
            errors.append(f"invalid or duplicate contradiction assessment: {cid}")
        seen_ctr.add(cid)
        if row.get("outcome") not in {"resolved", "narrowed", "still-disputed", "currently-unknowable"}:
            errors.append(f"{cid}: invalid outcome")
        if any(ref not in valid_basis for ref in row.get("basis_ids", [])):
            errors.append(f"{cid}: unknown basis")

    gate = source.get("release_gate", {})
    current = gate.get("current_snapshot", {})
    actual = {
        "coverage_score": coverage.get("overall_coverage_score"),
        "official_or_confirmed_claims": sum(row.get("evidence_level") in {"official", "confirmed"} for row in coverage.get("claims", [])),
        "claims_below_confirmed": sum(row.get("evidence_level") not in {"official", "confirmed"} for row in coverage.get("claims", [])),
        "open_contradictions": sum(row.get("status") == "open" for row in contradictions.get("records", [])),
    }
    for key, value in actual.items():
        if current.get(key) != value:
            errors.append(f"release gate {key} drift: expected {value!r}")
    required = gate.get("required_snapshot", {})
    passes = (
        current.get("coverage_score", 0) >= required.get("minimum_coverage_score", 10**9)
        and current.get("official_or_confirmed_claims", 0) >= required.get("minimum_official_or_confirmed_claims", 10**9)
        and current.get("claims_below_confirmed", 10**9) <= required.get("maximum_claims_below_confirmed", -1)
        and current.get("open_contradictions", 10**9) <= required.get("maximum_open_contradictions", -1)
    )
    if gate.get("status") != ("ready" if passes else "blocked"):
        errors.append("release gate status does not match current evidence")
    return errors


def frontmatter(title: str, description: str, permalink: str) -> list[str]:
    return ["---", "layout: default", f"title: {title}", f"description: {description}", f"permalink: {permalink}", "---", ""]


def event_page(source: dict) -> str:
    rows = source["event_evidence"]
    counts = Counter(row["adjudication_status"] for row in rows)
    lines = frontmatter("Event-linked evidence", "Public GitHub events linked to achievement claims without overstating causality.", "/event-linked-evidence/")
    lines += ["## Event-linked evidence collector", "", "This register links public GitHub events to achievement claims. A link is not automatically causal: participant reports, processing delay, hidden attribution, and missing controls remain explicit.", "", f"**Events:** {len(rows)}  ", f"**Candidate observations:** {counts['candidate-observed']}  ", f"**Negative or inconclusive:** {counts['negative-inconclusive']}", "", "| Event | Achievement | Public object | Result | Elapsed |", "|---|---|---|---|---:|"]
    for row in rows:
        lines.append(f"| `{row['id']}` | {row['achievement_slug']} | [{row['event_type']}]({row['event_url']}) | {row['adjudication_status']} | {row['elapsed_seconds']} seconds |")
    lines += ["", "## Event records", ""]
    for row in rows:
        lines += [f"### {row['id']} — {row['achievement_slug']}", "", f"**Claims:** {', '.join(f'`{v}`' for v in row['claim_ids'])}  ", f"**Account:** `{row['subject_login']}`  ", f"**Award link:** `{row['award_link']}`  ", f"**Adjudication:** `{row['adjudication_status']}`", "", "**Public facts**", "", *[f"- {v}" for v in row["public_facts"]], "", "**Limitations**", "", *[f"- {v}" for v in row["limitations"]], ""]
    return "\n".join(lines + ["## Machine-readable data", "", "See [`/api/event-linked-evidence.json`](../api/event-linked-evidence.json).", ""])


def boundary_page(source: dict) -> str:
    rows = source["boundary_programmes"]
    lines = frontmatter("Threshold boundary programme", "Boundary-focused research plans for achievement tiers and timing windows.", "/threshold-boundary-programme/")
    lines += ["## Threshold boundary programme", "", "A high-tier badge far above a proposed threshold is weak boundary evidence. This programme records the exact below/at/above observations still required.", "", "| Programme | Achievement | Proposed boundaries | Status |", "|---|---|---|---|"]
    for row in rows:
        lines.append(f"| `{row['id']}` | {row['achievement_slug']} | {', '.join(str(v) for v in row['reported_boundaries'])} {row['unit']} | {row['status']} |")
    lines += ["", "## Required next evidence", ""]
    for row in rows:
        lines += [f"### {row['id']} — {row['achievement_slug']}", "", row["next_evidence"], ""]
        if row.get("current_bracket"):
            b = row["current_bracket"]
            lines += [f"Current public bracket: **{b['lower_display']}** to **{b['upper_display']}**. The reported boundary is **{b['reported_x4_boundary']}**, but rounded counts do not confirm it.", ""]
    return "\n".join(lines + ["## Machine-readable data", "", "See [`/api/threshold-boundaries.json`](../api/threshold-boundaries.json).", ""])


def adjudication_page(source: dict) -> str:
    lines = frontmatter("Evidence adjudication engine", "Fail-closed rules and current decisions for evidence-level promotion.", "/evidence-adjudication-engine/")
    lines += ["## Evidence adjudication engine", "", "The engine separates collection from promotion. Generated observations never modify canonical claim levels automatically.", "", "## Promotion rules", ""]
    for row in source["adjudication_rules"]:
        lines += [f"### {row['id']} — {row['transition']}", "", *[f"- {v}" for v in row["requirements"]], ""]
    lines += ["## Current decisions", "", "| Decision | Claim | Outcome | Proposed level |", "|---|---|---|---|"]
    for row in source["adjudication_decisions"]:
        lines.append(f"| `{row['id']}` | `{row['claim_id']}` | {row['decision']} | {row['proposed_level']} |")
    lines += ["", "Decisions record remaining research after maintainer-reviewed canonical reconciliation. Generated observations never change claims automatically.", ""]
    for row in source["adjudication_decisions"]:
        lines += [f"### {row['id']} — {row['claim_id']}", "", row["reason"], ""]
    return "\n".join(lines + ["## Machine-readable data", "", "See [`/api/adjudication.json`](../api/adjudication.json).", ""])


def contradiction_page(source: dict) -> str:
    rows = source["contradiction_assessments"]
    counts = Counter(row["outcome"] for row in rows)
    lines = frontmatter("Contradiction resolution programme", "Evidence-backed assessments of every open achievement contradiction.", "/contradiction-resolution-programme/")
    lines += ["## Contradiction resolution programme", "", "All six contradictions have been reassessed against event-linked and boundary evidence. Narrowing a dispute is not the same as resolving it.", "", f"**Narrowed:** {counts['narrowed']}  ", f"**Still disputed:** {counts['still-disputed']}  ", f"**Resolved:** {counts['resolved']}", "", "| Contradiction | Outcome | Evidence basis |", "|---|---|---|"]
    for row in rows:
        lines.append(f"| `{row['contradiction_id']}` | {row['outcome']} | {', '.join(f'`{v}`' for v in row['basis_ids'])} |")
    lines += ["", "## Assessment details", ""]
    for row in rows:
        lines += [f"### {row['contradiction_id']} — {row['outcome']}", "", row["remaining_question"], ""]
    return "\n".join(lines + ["## Machine-readable data", "", "See [`/api/contradiction-assessments.json`](../api/contradiction-assessments.json).", ""])


def release_page(source: dict) -> str:
    gate, current, required = source["release_gate"], source["release_gate"]["current_snapshot"], source["release_gate"]["required_snapshot"]
    lines = frontmatter("Evidence quality release gate", "Fail-closed publication criteria for the proposed v1.4.0 evidence-quality release.", "/evidence-quality-release-gate/")
    coverage_result = "PASS" if current["coverage_score"] >= required["minimum_coverage_score"] else "FAIL"
    confirmed_result = "PASS" if current["official_or_confirmed_claims"] >= required["minimum_official_or_confirmed_claims"] else "FAIL"
    weak_result = "PASS" if current["claims_below_confirmed"] <= required["maximum_claims_below_confirmed"] else "FAIL"
    contradiction_result = "PASS" if current["open_contradictions"] <= required["maximum_open_contradictions"] else "FAIL"
    summary = "All evidence gates pass. Publication still requires merged-main operational verification." if gate["status"] == "ready" else "One or more evidence gates remain blocked."
    lines += ["## Evidence quality release gate", "", f"**Candidate:** `{gate['candidate_version']}`  ", f"**Status:** `{gate['status']}`", "", summary, "", "| Gate | Current | Required | Result |", "|---|---:|---:|---|", f"| Evidence coverage | {current['coverage_score']} | ≥ {required['minimum_coverage_score']} | {coverage_result} |", f"| Official or confirmed claims | {current['official_or_confirmed_claims']} | ≥ {required['minimum_official_or_confirmed_claims']} | {confirmed_result} |", f"| Claims below confirmed | {current['claims_below_confirmed']} | ≤ {required['maximum_claims_below_confirmed']} | {weak_result} |", f"| Open contradictions | {current['open_contradictions']} | ≤ {required['maximum_open_contradictions']} | {contradiction_result} |", f"| Operational health | evaluated on merged `main` | {required['required_operational_health']} | PENDING |", "", "## Publication rule", "", gate["publication_rule"], "", "## Machine-readable data", "", "See [`/api/release-readiness.json`](../api/release-readiness.json).", ""]
    return "\n".join(lines)


def serialise(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def outputs(source: dict) -> dict[Path, str]:
    events = {"api_version": "1.0.0", "schema_version": source["schema_version"], "generated_from": "data/evidence-quality-programme.json", "count": len(source["event_evidence"]), "metrics": dict(Counter(v["adjudication_status"] for v in source["event_evidence"])), "events": source["event_evidence"]}
    boundaries = {"api_version": "1.0.0", "schema_version": source["schema_version"], "generated_from": "data/evidence-quality-programme.json", "count": len(source["boundary_programmes"]), "programmes": source["boundary_programmes"]}
    adjudication = {"api_version": "1.0.0", "schema_version": source["schema_version"], "generated_from": "data/evidence-quality-programme.json", "metrics": dict(Counter(v["decision"] for v in source["adjudication_decisions"])), "rules": source["adjudication_rules"], "decisions": source["adjudication_decisions"]}
    contradictions = {"api_version": "1.0.0", "schema_version": source["schema_version"], "generated_from": "data/evidence-quality-programme.json", "count": len(source["contradiction_assessments"]), "metrics": dict(Counter(v["outcome"] for v in source["contradiction_assessments"])), "assessments": source["contradiction_assessments"]}
    release = {"api_version": "1.0.0", "schema_version": source["schema_version"], "generated_from": "data/evidence-quality-programme.json", **source["release_gate"]}
    return {DOCS["event"]: event_page(source), DOCS["boundary"]: boundary_page(source), DOCS["adjudication"]: adjudication_page(source), DOCS["contradiction"]: contradiction_page(source), DOCS["release"]: release_page(source), APIS["event"]: serialise(events), APIS["boundary"]: serialise(boundaries), APIS["adjudication"]: serialise(adjudication), APIS["contradiction"]: serialise(contradictions), APIS["release"]: serialise(release)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and publish evidence-quality programme phases 52-56.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", default="evidence-quality-programme-report.md")
    args = parser.parse_args()
    try:
        source, claims, contradictions, observations, fragments, coverage = map(load, [SOURCE, CLAIMS, CONTRADICTIONS, OBSERVATIONS, FRAGMENTS, COVERAGE])
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error)
        return 1
    errors = validate(source, claims, contradictions, observations, fragments, coverage)
    report = ["# Evidence quality programme validation", "", f"- Event records: {len(source.get('event_evidence', []))}", f"- Boundary programmes: {len(source.get('boundary_programmes', []))}", f"- Adjudication decisions: {len(source.get('adjudication_decisions', []))}", f"- Contradiction assessments: {len(source.get('contradiction_assessments', []))}", f"- Release status: {source.get('release_gate', {}).get('status', 'unknown')}", f"- Result: {'FAIL' if errors else 'PASS'}"]
    if errors:
        report += ["", "## Failures", "", *[f"- {error}" for error in errors]]
    (ROOT / args.report).write_text("\n".join(report) + "\n", encoding="utf-8")
    if errors:
        print("\n".join(errors))
        return 1
    expected = outputs(source)
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, content in expected.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            print("Stale or missing evidence-quality outputs: " + ", ".join(stale))
            return 1
    else:
        for path, content in expected.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    print(f"Evidence quality programme passed: phases 52-56 validated; v1.4.0 is {source['release_gate']['status']}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
