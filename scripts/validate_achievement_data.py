from __future__ import annotations

from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
import argparse
import json
import re
import sys

from check_verification_dates import read_verification_date

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "achievements.json"
SCHEMA_PATH = ROOT / "data" / "achievement.schema.json"
INDEX_PATH = ROOT / "docs" / "achievement-index.md"
INDEX_ROW = re.compile(
    r"^\| \[([^\]]+)\]\(([^)]+\.md)\) \| ([^|]+?) \| ([^|]+?) \| [^|]+ \|$",
    re.MULTILINE,
)
PERMALINK = re.compile(r"^permalink:\s*(\S+)\s*$", re.MULTILINE)
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
EVIDENCE_LEVELS = {
    "official",
    "confirmed",
    "observed",
    "community-reported",
    "unknown",
    "not-applicable",
}
REQUIRED_FIELDS = {
    "slug",
    "name",
    "status",
    "category",
    "tiered",
    "primary_action",
    "trigger",
    "guide_path",
    "permalink",
    "evidence",
    "tiers",
    "last_verified",
    "aliases",
    "sources",
    "known_limitations",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the machine-readable achievement catalogue.")
    parser.add_argument("--report", type=Path, default=Path("achievement-data-report.md"))
    return parser.parse_args()


def index_records() -> dict[str, dict[str, object]]:
    text = INDEX_PATH.read_text(encoding="utf-8").split("## Evidence labels", 1)[0]
    records: dict[str, dict[str, object]] = {}
    for name, target, action, state in INDEX_ROW.findall(text):
        resolved = (INDEX_PATH.parent / target).resolve().relative_to(ROOT).as_posix()
        state = state.strip()
        records[name] = {
            "guide_path": resolved,
            "primary_action": action.strip(),
            "tiered": state == "Yes",
            "status": "retired" if state == "Retired" else "active",
        }
    return records


def valid_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_schema(schema: object, errors: list[str]) -> None:
    if not isinstance(schema, dict):
        errors.append("Schema root must be an object.")
        return
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("Schema must declare JSON Schema draft 2020-12.")
    if schema.get("type") != "object":
        errors.append("Schema root type must be object.")
    if "achievement" not in schema.get("$defs", {}):
        errors.append("Schema must define $defs.achievement.")


def validate_item(item: object, position: int, errors: list[str]) -> None:
    prefix = f"Achievement {position}"
    if not isinstance(item, dict):
        errors.append(f"{prefix} must be an object.")
        return

    missing = sorted(REQUIRED_FIELDS - set(item))
    extra = sorted(set(item) - REQUIRED_FIELDS)
    if missing:
        errors.append(f"{prefix} is missing fields: {', '.join(missing)}.")
    if extra:
        errors.append(f"{prefix} has unsupported fields: {', '.join(extra)}.")
    if missing:
        return

    if not isinstance(item["slug"], str) or not SLUG.fullmatch(item["slug"]):
        errors.append(f"{prefix} has an invalid slug.")
    if not isinstance(item["name"], str) or not item["name"].strip():
        errors.append(f"{prefix} has an invalid name.")
    if item["status"] not in {"active", "retired", "restricted"}:
        errors.append(f"{prefix} has an invalid status.")
    if not isinstance(item["tiered"], bool):
        errors.append(f"{prefix} tiered must be boolean.")
    for field in ("category", "primary_action", "trigger", "permalink"):
        if not isinstance(item[field], str) or not item[field].strip():
            errors.append(f"{prefix} has an invalid {field} value.")

    guide_path = item["guide_path"]
    if not isinstance(guide_path, str) or not guide_path.endswith(".md"):
        errors.append(f"{prefix} has an invalid guide path.")
    else:
        full_path = ROOT / guide_path
        if not full_path.exists():
            errors.append(f"{prefix} guide does not exist: {guide_path}.")
        else:
            text = full_path.read_text(encoding="utf-8")
            permalink_match = PERMALINK.search(text)
            if permalink_match and permalink_match.group(1) != item["permalink"]:
                errors.append(f"{prefix} permalink differs from guide front matter.")
            verified, verification_error = read_verification_date(Path(guide_path))
            if verification_error or verified is None:
                errors.append(f"{prefix} guide verification metadata is invalid: {verification_error}.")
            elif verified.isoformat() != item["last_verified"]:
                errors.append(f"{prefix} last_verified differs from the guide.")

    try:
        verified_date = date.fromisoformat(item["last_verified"])
        if verified_date > date.today():
            errors.append(f"{prefix} has a future last_verified date.")
    except (TypeError, ValueError):
        errors.append(f"{prefix} last_verified is not an ISO date.")

    evidence = item["evidence"]
    if not isinstance(evidence, dict) or set(evidence) != {"trigger", "tiers"}:
        errors.append(f"{prefix} evidence must contain trigger and tiers only.")
    elif any(level not in EVIDENCE_LEVELS for level in evidence.values()):
        errors.append(f"{prefix} contains an unsupported evidence level.")

    tiers = item["tiers"]
    if not isinstance(tiers, list):
        errors.append(f"{prefix} tiers must be an array.")
    elif item["tiered"]:
        names = [tier.get("name") for tier in tiers if isinstance(tier, dict)]
        thresholds = [tier.get("threshold") for tier in tiers if isinstance(tier, dict)]
        if names != ["Base", "Bronze", "Silver", "Gold"]:
            errors.append(f"{prefix} tier progression must be Base, Bronze, Silver, Gold.")
        if len(thresholds) != 4 or any(not isinstance(value, int) or value < 1 for value in thresholds):
            errors.append(f"{prefix} has invalid tier thresholds.")
        elif thresholds != sorted(thresholds) or len(set(thresholds)) != 4:
            errors.append(f"{prefix} tier thresholds must be unique and increasing.")
    elif tiers:
        errors.append(f"{prefix} is not tiered but defines tiers.")

    aliases = item["aliases"]
    if not isinstance(aliases, list) or not aliases or any(not isinstance(value, str) or not value.strip() for value in aliases):
        errors.append(f"{prefix} aliases must contain non-empty strings.")

    sources = item["sources"]
    if not isinstance(sources, dict) or set(sources) != {"official", "community"}:
        errors.append(f"{prefix} sources must contain official and community arrays.")
    else:
        for kind, values in sources.items():
            if not isinstance(values, list) or any(not valid_url(value) for value in values):
                errors.append(f"{prefix} {kind} sources contain an invalid URL.")

    limitations = item["known_limitations"]
    if not isinstance(limitations, list) or not limitations or any(
        not isinstance(value, str) or not value.strip() for value in limitations
    ):
        errors.append(f"{prefix} known_limitations must contain non-empty strings.")


def build_report(data: dict, index: dict[str, dict[str, object]], errors: list[str]) -> str:
    achievements = data.get("achievements", []) if isinstance(data, dict) else []
    active = sum(isinstance(item, dict) and item.get("status") == "active" for item in achievements)
    retired = sum(isinstance(item, dict) and item.get("status") == "retired" for item in achievements)
    tiered = sum(isinstance(item, dict) and item.get("tiered") is True for item in achievements)
    lines = [
        "# Achievement data validation report",
        "",
        f"- Dataset records: **{len(achievements)}**",
        f"- Catalogue records: **{len(index)}**",
        f"- Active: **{active}**",
        f"- Retired: **{retired}**",
        f"- Tiered: **{tiered}**",
        f"- Validation errors: **{len(errors)}**",
        "",
    ]
    if errors:
        lines.extend(["## Errors", ""] + [f"- {error}" for error in errors] + [""])
    else:
        lines.extend(["## Result", "", "Dataset, schema, guide metadata, and catalogue are consistent.", ""])
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        index = index_records()
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Achievement data validation could not start: {error}")
        return 1

    validate_schema(schema, errors)
    if not isinstance(data, dict):
        errors.append("Dataset root must be an object.")
        achievements: list[object] = []
    else:
        if not SEMVER.fullmatch(str(data.get("schema_version", ""))):
            errors.append("schema_version must use semantic versioning.")
        if data.get("catalogue") != "docs/achievement-index.md":
            errors.append("catalogue must identify docs/achievement-index.md.")
        achievements = data.get("achievements", [])
        if not isinstance(achievements, list):
            errors.append("achievements must be an array.")
            achievements = []

    if len(achievements) != 9:
        errors.append(f"Expected 9 achievements, found {len(achievements)}.")
    for position, item in enumerate(achievements, start=1):
        validate_item(item, position, errors)

    items = [item for item in achievements if isinstance(item, dict)]
    for key in ("slug", "name", "guide_path"):
        values = [item.get(key) for item in items]
        if len(values) != len(set(values)):
            errors.append(f"Achievement {key} values must be unique.")

    dataset_by_name = {str(item.get("name")): item for item in items}
    if set(dataset_by_name) != set(index):
        errors.append(
            "Dataset and achievement index names differ: "
            f"dataset-only={sorted(set(dataset_by_name) - set(index))}; "
            f"index-only={sorted(set(index) - set(dataset_by_name))}."
        )
    for name in sorted(set(dataset_by_name) & set(index)):
        item = dataset_by_name[name]
        expected = index[name]
        for field in ("guide_path", "primary_action", "tiered", "status"):
            if item.get(field) != expected[field]:
                errors.append(f"{name} {field} differs from the achievement index.")

    statuses = [item.get("status") for item in items]
    if statuses.count("active") != 7 or statuses.count("retired") != 2:
        errors.append("Dataset must contain 7 active and 2 retired achievements.")

    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(data if isinstance(data, dict) else {}, index, errors), encoding="utf-8")

    if errors:
        print("Achievement data validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Validated 9 achievement records against schema, guides, and catalogue.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
