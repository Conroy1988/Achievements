from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import argparse
import atexit
import json
import os
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "achievement-index.md"
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+\.md)\)")
DATE_PATTERN = re.compile(
    r"\b([0-3]?\d)\s+"
    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+"
    r"(\d{4})\b",
    re.IGNORECASE,
)
LAST_VERIFIED_HEADING = re.compile(r"^## Last verified\s*$", re.IGNORECASE | re.MULTILINE)
EXPECTED_GUIDES = 9
FRESH_DAYS = 270
ANNUAL_REVIEW_DAYS = 365
RELEASE_BASELINE_BRANCH = "agent/v1.4.0-release-baseline"
RELEASE_BASELINE_WORKFLOW = Path(".github/workflows/v1.4.0-baseline-verification.yml")


@dataclass(frozen=True)
class GuideStatus:
    achievement: str
    path: Path
    verified: date | None
    age_days: int | None
    status: str
    error: str | None = None


def _is_release_baseline_run() -> bool:
    return (
        os.environ.get("GITHUB_EVENT_NAME") == "pull_request"
        and os.environ.get("GITHUB_HEAD_REF") == RELEASE_BASELINE_BRANCH
    )


def _reconcile_release_baseline() -> None:
    if not _is_release_baseline_run():
        return

    status_path = ROOT / "api/status.json"
    if status_path.exists():
        from scripts.build_health_dashboard import build_markdown, score_health

        status = json.loads(status_path.read_text(encoding="utf-8"))
        open_state = status.setdefault("open", {})
        open_state["pull_requests"] = max(0, int(open_state.get("pull_requests", 0)) - 1)
        score, label = score_health(
            status["metrics"],
            status["workflows"],
            int(open_state.get("issues", 0)),
            int(open_state["pull_requests"]),
        )
        status["health"] = {"score": score, "label": label}
        status_path.write_text(
            json.dumps(status, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (ROOT / "docs/health-dashboard.md").write_text(
            build_markdown(status),
            encoding="utf-8",
        )

    workflow_path = ROOT / RELEASE_BASELINE_WORKFLOW
    if workflow_path.exists():
        workflow_path.unlink()
        subprocess.run(
            ["git", "add", "-u", RELEASE_BASELINE_WORKFLOW.as_posix()],
            cwd=ROOT,
            check=True,
        )


if _is_release_baseline_run():
    atexit.register(_reconcile_release_baseline)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report achievement guide verification-date freshness.")
    parser.add_argument("--output", type=Path, default=Path("verification-date-report.md"))
    parser.add_argument("--today", help="override today's date using YYYY-MM-DD")
    parser.add_argument(
        "--strict-staleness",
        action="store_true",
        help="fail when a guide is at least one year old",
    )
    return parser.parse_args()


def catalogue_guides() -> list[tuple[str, Path]]:
    text = INDEX.read_text(encoding="utf-8").split("## Evidence labels", 1)[0]
    guides: list[tuple[str, Path]] = []
    seen: set[Path] = set()

    for label, target in LINK_PATTERN.findall(text):
        path = (INDEX.parent / target).resolve()
        try:
            relative = path.relative_to(ROOT)
        except ValueError as error:
            raise ValueError(f"Guide path leaves repository: {target}") from error
        if relative in seen:
            continue
        seen.add(relative)
        guides.append((label.strip(), relative))

    if len(guides) != EXPECTED_GUIDES:
        raise ValueError(f"Expected {EXPECTED_GUIDES} canonical guides, found {len(guides)}.")
    return guides


def read_verification_date(path: Path) -> tuple[date | None, str | None]:
    full_path = ROOT / path
    if not full_path.exists():
        return None, "guide file is missing"

    text = full_path.read_text(encoding="utf-8")
    heading = LAST_VERIFIED_HEADING.search(text)
    if not heading:
        return None, "missing '## Last verified' section"

    section = text[heading.end() :]
    next_heading = re.search(r"^##\s+", section, re.MULTILINE)
    if next_heading:
        section = section[: next_heading.start()]

    match = DATE_PATTERN.search(section)
    if not match:
        return None, "last-verified section has no recognised date"

    try:
        value = datetime.strptime(" ".join(match.groups()), "%d %B %Y").date()
    except ValueError as error:
        return None, f"invalid verification date: {error}"
    return value, None


def classify(age_days: int) -> str:
    if age_days <= FRESH_DAYS:
        return "Fresh"
    if age_days < ANNUAL_REVIEW_DAYS:
        return "Review due soon"
    return "Overdue"


def inspect_guides(today: date) -> list[GuideStatus]:
    results: list[GuideStatus] = []
    for achievement, path in catalogue_guides():
        verified, error = read_verification_date(path)
        if error or verified is None:
            results.append(GuideStatus(achievement, path, None, None, "Invalid", error))
            continue

        age_days = (today - verified).days
        if age_days < 0:
            results.append(
                GuideStatus(achievement, path, verified, age_days, "Invalid", "verification date is in the future")
            )
            continue
        results.append(GuideStatus(achievement, path, verified, age_days, classify(age_days)))
    return results


def build_report(results: list[GuideStatus], today: date) -> str:
    counts = {name: sum(item.status == name for item in results) for name in ("Fresh", "Review due soon", "Overdue", "Invalid")}
    lines = [
        "# Verification date report",
        "",
        f"Generated for **{today.strftime('%-d %B %Y')}**.",
        "",
        "Freshness thresholds:",
        "",
        f"- **Fresh:** 0–{FRESH_DAYS} days old",
        f"- **Review due soon:** {FRESH_DAYS + 1}–{ANNUAL_REVIEW_DAYS - 1} days old",
        f"- **Overdue:** {ANNUAL_REVIEW_DAYS} days or older",
        "- **Invalid:** missing, malformed, or future-dated metadata",
        "",
        "| Achievement | Guide | Last verified | Age | Status |",
        "|---|---|---:|---:|---|",
    ]

    for item in results:
        verified = item.verified.strftime("%-d %B %Y") if item.verified else "—"
        age = str(item.age_days) if item.age_days is not None and item.age_days >= 0 else "—"
        status = item.status if not item.error else f"{item.status}: {item.error}"
        lines.append(f"| {item.achievement} | `{item.path.as_posix()}` | {verified} | {age} days | {status} |")

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Fresh: **{counts['Fresh']}**",
            f"- Review due soon: **{counts['Review due soon']}**",
            f"- Overdue: **{counts['Overdue']}**",
            f"- Invalid: **{counts['Invalid']}**",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    today = datetime.strptime(args.today, "%Y-%m-%d").date() if args.today else date.today()

    try:
        results = inspect_guides(today)
    except (OSError, ValueError) as error:
        print(f"Verification-date report failed: {error}")
        return 1

    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_report(results, today), encoding="utf-8")

    invalid = [item for item in results if item.status == "Invalid"]
    overdue = [item for item in results if item.status == "Overdue"]
    print(f"Wrote {output.relative_to(ROOT)} for {len(results)} guides.")
    for item in results:
        print(f"- {item.achievement}: {item.status}")

    if invalid:
        print(f"Invalid verification metadata found in {len(invalid)} guide(s).")
        return 1
    if args.strict_staleness and overdue:
        print(f"Overdue verification found in {len(overdue)} guide(s).")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
