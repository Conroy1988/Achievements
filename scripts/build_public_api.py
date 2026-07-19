from __future__ import annotations

from pathlib import Path
import argparse
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "achievements.json"
SCHEMA = ROOT / "data" / "achievement.schema.json"
DEFAULT_OUTPUT = ROOT / "api"
API_VERSION = "1.1.0"
PUBLIC_BASE = "/Achievements/api"

AUXILIARY_ENDPOINTS = {
    "evidence": Path("evidence.json"),
    "timelines": Path("timelines.json"),
    "research_queue": Path("research-queue.json"),
    "claims": Path("claims.json"),
    "contradictions": Path("contradictions.json"),
    "coverage": Path("coverage.json"),
    "priorities": Path("priorities.json"),
    "change_impact": Path("change-impact.json"),
    "lab_protocols": Path("lab-protocols.json"),
    "auditor_rules": Path("auditor-rules.json"),
    "submission_schema": Path("submission-schema.json"),
    "mission_submission_schema": Path("mission-submission-schema.json"),
    "mission_review_queue": Path("mission-review-queue.json"),
    "mission_review_schema": Path("mission-review-schema.json"),
    "promotion_plans": Path("promotion-plans.json"),
    "promotion_plan_schema": Path("promotion-plan-schema.json"),
    "command_centre": Path("command-centre.json"),
    "public_observations": Path("public-observations.json"),
    "public_reconstructions": Path("public-reconstructions.json"),
    "official_achievement_fragments": Path("official-achievement-fragments.json"),
    "event_linked_evidence": Path("event-linked-evidence.json"),
    "evidence_intelligence": Path("evidence-intelligence.json"),
    "acquisition_missions": Path("acquisition-missions.json"),
    "threshold_boundaries": Path("threshold-boundaries.json"),
    "adjudication": Path("adjudication.json"),
    "contradiction_assessments": Path("contradiction-assessments.json"),
    "release_readiness": Path("release-readiness.json"),
}
AUXILIARY_COLLECTIONS = {
    "evidence": "records",
    "timelines": "timelines",
    "research_queue": "tasks",
    "claims": "claims",
    "contradictions": "records",
    "priorities": "priorities",
    "change_impact": "documents",
    "lab_protocols": "protocols",
    "auditor_rules": "rules",
    "public_observations": "observations",
    "public_reconstructions": "records",
    "official_achievement_fragments": "records",
    "event_linked_evidence": "events",
    "evidence_intelligence": "achievements",
    "acquisition_missions": "missions",
    "mission_review_queue": "queue",
    "promotion_plans": "plans",
    "threshold_boundaries": "programmes",
    "contradiction_assessments": "assessments",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build or verify the static achievement API.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def resolved(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def serialise(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def expected_documents() -> dict[Path, object]:
    dataset = load_json(DATASET)
    schema = load_json(SCHEMA)
    achievements = dataset.get("achievements")
    if not isinstance(achievements, list) or len(achievements) != 9:
        raise ValueError("Canonical dataset must contain exactly 9 achievements")

    slugs: list[str] = []
    documents: dict[Path, object] = {
        Path("achievements.json"): {
            "api_version": API_VERSION,
            "dataset_schema_version": dataset.get("schema_version"),
            "count": len(achievements),
            "achievements": achievements,
        },
        Path("schema.json"): schema,
    }
    for achievement in achievements:
        if not isinstance(achievement, dict) or not isinstance(achievement.get("slug"), str):
            raise ValueError("Every achievement must define a string slug")
        slug = achievement["slug"]
        if slug in slugs:
            raise ValueError(f"Duplicate achievement slug: {slug}")
        slugs.append(slug)
        documents[Path("achievements") / f"{slug}.json"] = {
            "api_version": API_VERSION,
            "dataset_schema_version": dataset.get("schema_version"),
            "achievement": achievement,
        }

    endpoints = {
        "index": f"{PUBLIC_BASE}/index.json",
        "achievements": f"{PUBLIC_BASE}/achievements.json",
        "achievement_template": f"{PUBLIC_BASE}/achievements/{{slug}}.json",
        "schema": f"{PUBLIC_BASE}/schema.json",
        "status": f"{PUBLIC_BASE}/status.json",
    }
    endpoints.update({name: f"{PUBLIC_BASE}/{path.as_posix()}" for name, path in AUXILIARY_ENDPOINTS.items()})
    documents[Path("index.json")] = {
        "api_version": API_VERSION,
        "dataset_schema_version": dataset.get("schema_version"),
        "achievement_count": len(achievements),
        "endpoints": endpoints,
        "achievement_slugs": slugs,
    }
    return documents


def validate_status(output: Path, errors: list[str]) -> None:
    path = output / "status.json"
    if not path.exists():
        errors.append("api/status.json is missing")
        return
    try:
        payload = load_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        errors.append(f"api/status.json is invalid: {error}")
        return
    for field in ("schema_version", "repository", "generated_at", "health", "workflows", "metrics"):
        if field not in payload:
            errors.append(f"api/status.json is missing {field}")
    if payload.get("repository") != "Conroy1988/Achievements":
        errors.append("api/status.json identifies the wrong repository")


def validate_auxiliary(output: Path, errors: list[str]) -> None:
    for name, relative in AUXILIARY_ENDPOINTS.items():
        path = output / relative
        if not path.exists():
            errors.append(f"Missing auxiliary API endpoint: {path.relative_to(ROOT)}")
            continue
        try:
            payload = load_json(path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            errors.append(f"Invalid auxiliary endpoint {path.relative_to(ROOT)}: {error}")
            continue
        for field in ("api_version", "schema_version"):
            if field not in payload:
                errors.append(f"{path.relative_to(ROOT)} is missing {field}")
        collection = AUXILIARY_COLLECTIONS.get(name)
        if collection and not isinstance(payload.get(collection), list):
            errors.append(f"{path.relative_to(ROOT)} is missing {collection}")
        if name == "coverage":
            for field in ("overall_coverage_score", "unassigned_gap_count", "achievements", "claims"):
                if field not in payload:
                    errors.append(f"{path.relative_to(ROOT)} is missing {field}")
        if name in {
            "submission_schema",
            "mission_submission_schema",
            "mission_review_schema",
            "promotion_plan_schema",
        } and not isinstance(payload.get("schema"), dict):
            errors.append(f"api/{relative.name} is missing schema")
        if name == "mission_submission_schema":
            for field in ("mission_count", "form_url"):
                if field not in payload:
                    errors.append(f"api/mission-submission-schema.json is missing {field}")
        if name == "mission_review_queue":
            for field in ("policy", "review_schema", "packet_directory", "review_directory", "metrics"):
                if field not in payload:
                    errors.append(f"api/mission-review-queue.json is missing {field}")
            metrics = payload.get("metrics")
            if isinstance(metrics, dict) and metrics.get("automatic_canonical_mutation_count") != 0:
                errors.append("api/mission-review-queue.json reports an automatic canonical mutation")
        if name == "promotion_plan_schema":
            if not isinstance(payload.get("required_property_count"), int):
                errors.append("api/promotion-plan-schema.json is missing required_property_count")
        if name == "promotion_plans":
            for field in ("policy", "plan_schema", "source_review_queue", "metrics", "current_release_status"):
                if field not in payload:
                    errors.append(f"api/promotion-plans.json is missing {field}")
            metrics = payload.get("metrics")
            if isinstance(metrics, dict) and metrics.get("automatic_application_count") != 0:
                errors.append("api/promotion-plans.json reports an automatic application")
        if name == "command_centre" and not isinstance(payload.get("metrics"), dict):
            errors.append("api/command-centre.json is missing metrics")
        if name in {
            "public_observations",
            "public_reconstructions",
            "official_achievement_fragments",
            "event_linked_evidence",
            "contradiction_assessments",
            "evidence_intelligence",
            "acquisition_missions",
            "mission_review_queue",
            "promotion_plans",
        } and not isinstance(payload.get("metrics"), dict):
            errors.append(f"api/{relative.name} is missing metrics")
        if name == "acquisition_missions":
            for field in ("policy", "mission_date", "targeted_claim_ids", "targeted_contradiction_ids"):
                if field not in payload:
                    errors.append(f"api/acquisition-missions.json is missing {field}")
        if name == "adjudication":
            if not isinstance(payload.get("rules"), list) or not isinstance(payload.get("decisions"), list):
                errors.append("api/adjudication.json is missing rules or decisions")
        if name == "release_readiness":
            for field in ("candidate_version", "status", "current_snapshot", "required_snapshot", "publication_rule"):
                if field not in payload:
                    errors.append(f"api/release-readiness.json is missing {field}")


def write_documents(output: Path, documents: dict[Path, object]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(output / "achievements", ignore_errors=True)
    for relative, value in documents.items():
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(serialise(value), encoding="utf-8")


def check_documents(output: Path, documents: dict[Path, object]) -> list[str]:
    errors: list[str] = []
    expected_paths = set(documents)
    for relative, value in documents.items():
        destination = output / relative
        if not destination.exists():
            errors.append(f"Missing API endpoint: {destination.relative_to(ROOT)}")
            continue
        try:
            actual = json.loads(destination.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"Invalid API endpoint {destination.relative_to(ROOT)}: {error}")
            continue
        if actual != value:
            errors.append(f"API drift detected: {destination.relative_to(ROOT)}")
    achievement_dir = output / "achievements"
    if achievement_dir.exists():
        for path in achievement_dir.glob("*.json"):
            if path.relative_to(output) not in expected_paths:
                errors.append(f"Stale API endpoint: {path.relative_to(ROOT)}")
    validate_status(output, errors)
    validate_auxiliary(output, errors)
    return errors


def main() -> int:
    args = parse_args()
    output = resolved(args.output)
    try:
        documents = expected_documents()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Public API generation failed: {error}")
        return 1

    if args.check:
        errors = check_documents(output, documents)
        if errors:
            print("Public API validation failed:")
            print("\n".join(f"- {error}" for error in errors))
            return 1
        print(
            "Public API matches the canonical dataset across "
            f"{len(documents)} generated endpoints, "
            f"{len(AUXILIARY_ENDPOINTS)} auxiliary endpoints, and status.json."
        )
        return 0

    write_documents(output, documents)
    errors: list[str] = []
    validate_status(output, errors)
    validate_auxiliary(output, errors)
    if errors:
        print("Public API generated, but auxiliary validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"Generated {len(documents)} static API endpoints from 9 achievement records.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
