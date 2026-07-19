from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
import argparse
import json
import os
import sys

from scripts.build_source_inventory import collect as collect_sources
from scripts.check_verification_dates import inspect_guides

ROOT = Path(__file__).resolve().parents[1]
RELEVANT_WORKFLOWS = {
    "Content quality",
    "Link check",
    "Source inventory",
    "Visual regression",
    "Verification release",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the public repository health dashboard.")
    parser.add_argument("--markdown", type=Path, default=Path("docs/health-dashboard.md"))
    parser.add_argument("--json", type=Path, default=Path("api/status.json"))
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "Conroy1988/Achievements"))
    return parser.parse_args()


def api_get(path: str, token: str | None) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-achievement-encyclopedia-health/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"https://api.github.com{path}", headers=headers)
    with urlopen(request, timeout=20) as response:
        return json.load(response)


def search_count(repository: str, kind: str, token: str | None) -> int:
    query = quote(f"repo:{repository} is:{kind} is:open")
    return int(api_get(f"/search/issues?q={query}&per_page=1", token)["total_count"])


def workflow_state(repository: str, token: str | None) -> tuple[dict[str, str], str | None]:
    payload = api_get(f"/repos/{repository}/actions/runs?branch=main&status=completed&per_page=100", token)
    states: dict[str, str] = {}
    latest_audit: datetime | None = None
    for run in payload.get("workflow_runs", []):
        name = run.get("name", "")
        if name not in RELEVANT_WORKFLOWS or name in states:
            continue
        states[name] = run.get("conclusion") or "unknown"
        updated = run.get("updated_at")
        if updated and run.get("conclusion") == "success":
            value = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            latest_audit = max(latest_audit, value) if latest_audit else value
    for name in sorted(RELEVANT_WORKFLOWS):
        states.setdefault(name, "unknown")
    return states, latest_audit.isoformat().replace("+00:00", "Z") if latest_audit else None


def latest_release(repository: str, token: str | None) -> dict[str, str | None]:
    try:
        item = api_get(f"/repos/{repository}/releases/latest", token)
    except HTTPError as error:
        if error.code == 404:
            return {"tag": None, "published_at": None, "url": None}
        raise
    return {
        "tag": item.get("tag_name"),
        "published_at": item.get("published_at"),
        "url": item.get("html_url"),
    }


def repository_metrics() -> dict:
    guides = inspect_guides(date.today())
    freshness = Counter(item.status for item in guides)
    sources = collect_sources(False, 0)
    stability = Counter(item.stability for item in sources)
    markdown_files = [
        path
        for path in ROOT.rglob("*.md")
        if not any(part in {".git", "_site", "vendor", "node_modules"} for part in path.relative_to(ROOT).parts)
    ]
    baselines = list((ROOT / "tests" / "visual" / "baselines").glob("*.png"))
    return {
        "guides": len(guides),
        "freshness": dict(sorted(freshness.items())),
        "sources": len(sources),
        "source_stability": dict(sorted(stability.items())),
        "markdown_files": len(markdown_files),
        "visual_baselines": len(baselines),
    }


def score_health(metrics: dict, workflows: dict[str, str], open_issues: int, open_prs: int) -> tuple[int, str]:
    score = 100
    score -= 12 * sum(status != "success" for status in workflows.values())
    freshness = metrics["freshness"]
    score -= 3 * freshness.get("Review due soon", 0)
    score -= 8 * freshness.get("Overdue", 0)
    score -= 15 * freshness.get("Invalid", 0)
    score -= min(20, open_issues * 5)
    score -= min(10, open_prs * 2)
    score = max(0, score)
    if score >= 95:
        label = "Excellent"
    elif score >= 85:
        label = "Healthy"
    elif score >= 70:
        label = "Watch"
    else:
        label = "Action required"
    return score, label


def build_payload(repository: str) -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    metrics = repository_metrics()
    try:
        open_issues = search_count(repository, "issue", token)
        open_prs = search_count(repository, "pr", token)
        workflows, latest_audit = workflow_state(repository, token)
        release = latest_release(repository, token)
        api_status = "live"
    except (HTTPError, URLError, TimeoutError, KeyError, ValueError) as error:
        print(f"GitHub API data unavailable: {error}", file=sys.stderr)
        open_issues = 0
        open_prs = 0
        workflows = {name: "unknown" for name in sorted(RELEVANT_WORKFLOWS)}
        latest_audit = None
        release = {"tag": None, "published_at": None, "url": None}
        api_status = "fallback"

    score, label = score_health(metrics, workflows, open_issues, open_prs)
    return {
        "schema_version": "1.0.0",
        "repository": repository,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "api_status": api_status,
        "health": {"score": score, "label": label},
        "release": release,
        "latest_successful_audit": latest_audit,
        "open": {"issues": open_issues, "pull_requests": open_prs},
        "workflows": workflows,
        "metrics": metrics,
    }


def display_time(value: str | None) -> str:
    return value.replace("T", " ").replace("Z", " UTC") if value else "Not available"


def build_markdown(payload: dict) -> str:
    health = payload["health"]
    metrics = payload["metrics"]
    release = payload["release"]
    freshness = metrics["freshness"]
    workflow_rows = "\n".join(
        f"| {name} | {status.title()} |" for name, status in sorted(payload["workflows"].items())
    )
    stability_rows = "\n".join(
        f"| {label} | {count} |" for label, count in sorted(metrics["source_stability"].items())
    )
    release_text = f"[{release['tag']}]({release['url']})" if release.get("tag") and release.get("url") else "Not available"
    lines = [
        "---",
        "layout: default",
        "title: Repository health dashboard",
        "permalink: /health/",
        "description: Live operational health, verification freshness, automation status, source resilience, and maintenance backlog.",
        "---",
        "",
        "## Repository health dashboard",
        "",
        f"**Overall health:** {health['score']}/100 — **{health['label']}**",
        "",
        f"Generated at **{display_time(payload['generated_at'])}** from repository data and the GitHub API.",
        "",
        "## Current operating state",
        "",
        "| Measure | Value |",
        "|---|---:|",
        f"| Canonical achievement guides | {metrics['guides']} |",
        f"| Fresh guides | {freshness.get('Fresh', 0)} |",
        f"| Review due soon | {freshness.get('Review due soon', 0)} |",
        f"| Overdue guides | {freshness.get('Overdue', 0)} |",
        f"| Invalid verification records | {freshness.get('Invalid', 0)} |",
        f"| Tracked Markdown files | {metrics['markdown_files']} |",
        f"| External source URLs | {metrics['sources']} |",
        f"| Visual baselines | {metrics['visual_baselines']} |",
        f"| Open issues | {payload['open']['issues']} |",
        f"| Open pull requests | {payload['open']['pull_requests']} |",
        "",
        "## Automation status",
        "",
        "| Workflow | Latest completed result |",
        "|---|---|",
        workflow_rows,
        "",
        f"Latest successful tracked audit: **{display_time(payload['latest_successful_audit'])}**.",
        "",
        "## Source resilience",
        "",
        "| Stability classification | Unique URLs |",
        "|---|---:|",
        stability_rows,
        "",
        "## Release baseline",
        "",
        f"Latest formal release: **{release_text}**.",
        "",
        "## Scoring model",
        "",
        "The score starts at 100 and applies transparent deductions for failed or unknown tracked workflows, stale or invalid verification metadata, open issues, and open pull requests. It is an operational signal, not a substitute for evidence review.",
        "",
        "## Related controls",
        "",
        "- [Verification methodology](verification-methodology.md)",
        "- [Maintenance policy](../MAINTENANCE.md)",
        "- [Release and version policy](../RELEASES.md)",
        "- [Achievement index](achievement-index.md)",
        "",
    ]
    return "\n".join(lines)


def output_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    args = parse_args()
    payload = build_payload(args.repository)
    markdown = output_path(args.markdown)
    status_json = output_path(args.json)
    markdown.parent.mkdir(parents=True, exist_ok=True)
    status_json.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text(build_markdown(payload), encoding="utf-8")
    status_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Health dashboard: {payload['health']['score']}/100 ({payload['health']['label']}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
