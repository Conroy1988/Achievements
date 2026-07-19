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
DATA = ROOT / "data" / "public-reconstructions.json"
CLAIMS = ROOT / "data" / "claims.json"
API = ROOT / "api" / "public-reconstructions.json"
DOC = ROOT / "docs" / "public-reconstruction-corpus.md"
ID = re.compile(r"^RCN-\d{4}-\d{3}$")


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def public_github_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    return parsed.scheme == "https" and parsed.netloc == "github.com" and bool(parsed.path.strip("/"))


def parse_time(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def validate(corpus: dict, claims: dict) -> list[str]:
    errors: list[str] = []
    records = corpus.get("records")
    if not isinstance(records, list) or len(records) < 6:
        return ["public reconstruction corpus requires at least six records"]
    claim_map = {row["id"]: row for row in claims.get("claims", [])}
    seen: set[str] = set()
    subjects_by_claim: dict[str, set[str]] = {}
    for row in records:
        rid = row.get("id")
        if not isinstance(rid, str) or not ID.fullmatch(rid) or rid in seen:
            errors.append(f"invalid or duplicate reconstruction id: {rid!r}")
        seen.add(str(rid))
        claim_ids = row.get("claim_ids")
        if not isinstance(claim_ids, list) or not claim_ids:
            errors.append(f"{rid}: claim_ids must be non-empty")
            claim_ids = []
        for claim_id in claim_ids:
            claim = claim_map.get(claim_id)
            if not claim:
                errors.append(f"{rid}: unknown claim {claim_id}")
            elif claim.get("achievement_slug") != row.get("achievement_slug"):
                errors.append(f"{rid}: claim achievement mismatch")
            subjects_by_claim.setdefault(claim_id, set()).add(str(row.get("subject_login")))
        for field in ("event_url", "profile_url"):
            if not public_github_url(row.get(field)):
                errors.append(f"{rid}: {field} must be a public GitHub URL")
        if "commit_url" in row and not public_github_url(row.get("commit_url")):
            errors.append(f"{rid}: commit_url must be a public GitHub URL")
        created = parse_time(row.get("created_at"))
        completed = parse_time(row.get("completed_at"))
        elapsed = row.get("elapsed_seconds")
        if created is None or completed is None or completed < created:
            errors.append(f"{rid}: invalid event timestamps")
        elif not isinstance(elapsed, int) or elapsed != int((completed - created).total_seconds()):
            errors.append(f"{rid}: elapsed_seconds does not match timestamps")
        controls = row.get("public_controls")
        if not isinstance(controls, dict) or len(controls) < 4:
            errors.append(f"{rid}: insufficient public controls")
        limitations = row.get("limitations")
        if not isinstance(limitations, list) or len(limitations) < 2:
            errors.append(f"{rid}: at least two limitations are required")
        if row.get("privacy_status") != "public-identifiers-only":
            errors.append(f"{rid}: privacy_status must be public-identifiers-only")
        if not isinstance(row.get("supports"), str) or len(row["supports"].strip()) < 40:
            errors.append(f"{rid}: supports statement is incomplete")
    for claim_id in ("CLM-003", "CLM-004", "CLM-005"):
        if len(subjects_by_claim.get(claim_id, set())) < 2:
            errors.append(f"{claim_id}: requires two independent public subjects")
    return errors


def payload(corpus: dict) -> dict:
    records = corpus["records"]
    achievements = Counter(row["achievement_slug"] for row in records)
    claims = Counter(claim for row in records for claim in row["claim_ids"])
    return {
        "api_version": "1.0.0",
        "schema_version": corpus["schema_version"],
        "status": "live",
        "policy": "/Achievements/public-reconstruction-corpus/",
        "count": len(records),
        "metrics": {
            "record_count": len(records),
            "independent_subject_count": len({row["subject_login"] for row in records}),
            "achievement_count": len(achievements),
            "claim_count": len(claims),
            "privacy_safe_count": sum(row["privacy_status"] == "public-identifiers-only" for row in records),
            "automatic_canonical_mutation_count": 0
        },
        "by_achievement": dict(sorted(achievements.items())),
        "by_claim": dict(sorted(claims.items())),
        "records": records
    }


def markdown(corpus: dict) -> str:
    output = payload(corpus)
    lines = [
        "---",
        "layout: default",
        "title: Public reconstruction corpus",
        "description: Dated public event and profile pairs used to strengthen broad GitHub achievement trigger claims without overstating causality or thresholds.",
        "permalink: /public-reconstruction-corpus/",
        "---",
        "",
        "## Public reconstruction corpus",
        "",
        "This corpus links exact public GitHub event state to independently visible profile achievements. A reconstruction can support a broad trigger association, but it does not prove that the cited event was the unique award cause, the maximum timing boundary, an exact tier threshold, or every edge case.",
        "",
        f"**Records:** {output['metrics']['record_count']}  ",
        f"**Independent subjects:** {output['metrics']['independent_subject_count']}  ",
        f"**Achievements covered:** {output['metrics']['achievement_count']}  ",
        "**Automatic canonical mutations:** 0",
        "",
        "| Record | Achievement | Subject | Event | Elapsed |",
        "|---|---|---|---|---:|",
    ]
    for row in output["records"]:
        lines.append(
            f"| `{row['id']}` | {row['achievement_slug']} | `{row['subject_login']}` | "
            f"[public event]({row['event_url']}) | {row['elapsed_seconds']} seconds |"
        )
    lines.extend([
        "",
        "## Interpretation boundary",
        "",
        "- Two independent event/profile pairs support an **observed** broad trigger association under the project evidence policy.",
        "- Anonymous achievement pages currently fail to expose their contributing-event fragments reliably, so no record is treated as direct causal proof.",
        "- Exact Quickdraw timing, YOLO alternate review states and merger identity, and Pair Extraordinaire merge-rewrite behaviour remain open contradictions.",
        "- Tier thresholds remain unchanged unless exact boundary evidence independently satisfies the published criteria.",
        "",
        "## Machine-readable data",
        "",
        "The validated corpus is published at [`/api/public-reconstructions.json`](../api/public-reconstructions.json).",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and publish public achievement reconstructions.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", default="public-reconstruction-report.md")
    args = parser.parse_args()
    try:
        corpus = load(DATA)
        claims = load(CLAIMS)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error)
        return 1
    errors = validate(corpus, claims)
    report = [
        "# Public reconstruction validation",
        "",
        f"- Records: {len(corpus.get('records', []))}",
        f"- Result: {'FAIL' if errors else 'PASS'}",
    ]
    if errors:
        report += ["", "## Failures", ""] + [f"- {error}" for error in errors]
    (ROOT / args.report).write_text("\n".join(report) + "\n", encoding="utf-8")
    if errors:
        print("\n".join(errors))
        return 1
    outputs = {
        API: json.dumps(payload(corpus), indent=2, ensure_ascii=False) + "\n",
        DOC: markdown(corpus),
    }
    if args.check:
        stale = [str(path.relative_to(ROOT)) for path, expected in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != expected]
        if stale:
            print("Stale or missing reconstruction outputs: " + ", ".join(stale))
            return 1
    else:
        for path, expected in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
    print(f"Public reconstructions passed: {len(corpus['records'])} records, automatic mutations 0.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
