from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic, sleep
from typing import Iterator
from urllib.error import URLError
from urllib.request import urlopen
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = ROOT / "audit-artifacts"
SEMVER_NOTE = re.compile(r"^v\d+\.\d+\.\d+\.md$")


@dataclass
class AuditResult:
    name: str
    category: str
    status: str
    duration_seconds: float
    command: list[str] | None
    log: str | None
    summary: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the complete GitHub Achievement Encyclopedia audit.")
    parser.add_argument("--markdown", type=Path, default=Path("repository-audit.md"))
    parser.add_argument("--json", type=Path, default=Path("repository-audit.json"))
    parser.add_argument("--artifacts", type=Path, default=Path("audit-artifacts"))
    parser.add_argument("--skip-browser", action="store_true", help="skip Playwright search and visual checks")
    return parser.parse_args()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def tail(text: str, lines: int = 8) -> str:
    values = [line for line in text.splitlines() if line.strip()]
    return " | ".join(values[-lines:])[:800] or "No output."


def command_result(
    name: str,
    category: str,
    command: list[str],
    artifact_dir: Path,
    *,
    env: dict[str, str] | None = None,
    timeout: int = 900,
) -> AuditResult:
    started = monotonic()
    combined_env = os.environ.copy()
    if env:
        combined_env.update(env)
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=combined_env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        output = completed.stdout + ("\n" if completed.stdout and completed.stderr else "") + completed.stderr
        status = "passed" if completed.returncode == 0 else "failed"
        summary = tail(output)
    except subprocess.TimeoutExpired as error:
        output = (error.stdout or "") + "\n" + (error.stderr or "")
        status = "failed"
        summary = f"Timed out after {timeout} seconds. {tail(output)}"
    except OSError as error:
        output = str(error)
        status = "failed"
        summary = f"Could not execute command: {error}"

    log_path = artifact_dir / f"{slug(name)}.log"
    log_path.write_text(output.rstrip() + "\n", encoding="utf-8")
    return AuditResult(
        name=name,
        category=category,
        status=status,
        duration_seconds=round(monotonic() - started, 3),
        command=command,
        log=log_path.relative_to(ROOT).as_posix(),
        summary=summary,
    )


def internal_result(name: str, category: str, errors: list[str], artifact_dir: Path) -> AuditResult:
    log_path = artifact_dir / f"{slug(name)}.log"
    if errors:
        log_path.write_text("\n".join(f"- {error}" for error in errors) + "\n", encoding="utf-8")
        return AuditResult(name, category, "failed", 0.0, None, log_path.relative_to(ROOT).as_posix(), "; ".join(errors))
    log_path.write_text("All checks passed.\n", encoding="utf-8")
    return AuditResult(name, category, "passed", 0.0, None, log_path.relative_to(ROOT).as_posix(), "All checks passed.")


def site_contract(artifact_dir: Path) -> AuditResult:
    errors: list[str] = []
    required = [
        ROOT / "_config.yml",
        ROOT / "_layouts" / "default.html",
        ROOT / "assets" / "css" / "style.scss",
        ROOT / "assets" / "social-card.svg",
    ]
    for path in required:
        if not path.exists():
            errors.append(f"Missing required site file: {path.relative_to(ROOT)}")
    if errors:
        return internal_result("Site metadata and accessibility contract", "site", errors, artifact_dir)

    config = (ROOT / "_config.yml").read_text(encoding="utf-8")
    for key in ("title:", "description:", "url:", "baseurl:", "lang:", "author:"):
        if key not in config:
            errors.append(f"_config.yml does not define {key[:-1]}")

    layout = (ROOT / "_layouts" / "default.html").read_text(encoding="utf-8")
    layout_requirements = {
        "language declaration": '<html lang="{{ site.lang',
        "responsive viewport": 'name="viewport"',
        "SEO metadata": "{% seo %}",
        "labelled primary navigation": 'aria-label="Primary navigation"',
        "main landmark": 'role="main"',
        "repository footer": "site.github.repository_url",
    }
    for label, marker in layout_requirements.items():
        if marker not in layout:
            errors.append(f"Default layout lacks {label}.")

    style = (ROOT / "assets" / "css" / "style.scss").read_text(encoding="utf-8")
    if ":focus-visible" not in style:
        errors.append("Global stylesheet lacks visible keyboard focus styling.")
    if "prefers-reduced-motion" not in style:
        errors.append("Global stylesheet lacks reduced-motion handling.")

    search = ROOT / "search.md"
    if search.exists():
        text = search.read_text(encoding="utf-8")
        for marker in ('role="search"', 'aria-live="polite"', '<label for="search-query">'):
            if marker not in text:
                errors.append(f"Search page lacks required accessibility marker: {marker}")

    return internal_result("Site metadata and accessibility contract", "site", errors, artifact_dir)


def release_contract(artifact_dir: Path) -> AuditResult:
    errors: list[str] = []
    policy = ROOT / "RELEASES.md"
    changelog = ROOT / "CHANGELOG.md"
    notes_dir = ROOT / "docs" / "releases"
    if not policy.exists() or "semantic versioning" not in policy.read_text(encoding="utf-8").lower():
        errors.append("Release policy does not declare semantic versioning.")
    if not changelog.exists() or "semantic versioning" not in changelog.read_text(encoding="utf-8").lower():
        errors.append("Changelog does not declare semantic versioning.")
    notes = sorted(notes_dir.glob("v*.md")) if notes_dir.exists() else []
    if not notes:
        errors.append("No versioned release notes exist.")
    for note in notes:
        if not SEMVER_NOTE.fullmatch(note.name):
            errors.append(f"Invalid release-note filename: {note.relative_to(ROOT)}")
        text = note.read_text(encoding="utf-8")
        for heading in ("## Added", "## Verification", "## Known limitations"):
            if heading not in text:
                errors.append(f"{note.relative_to(ROOT)} lacks {heading}.")
    return internal_result("Release policy compliance", "release", errors, artifact_dir)


@contextmanager
def static_server(directory: Path, port: int, readiness_path: str, log_path: Path) -> Iterator[None]:
    with log_path.open("w", encoding="utf-8") as log_handle:
        process = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(port), "--directory", str(directory)],
            cwd=ROOT,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
        )
    try:
        deadline = monotonic() + 30
        url = f"http://127.0.0.1:{port}{readiness_path}"
        while monotonic() < deadline:
            try:
                with urlopen(url, timeout=2) as response:
                    if 200 <= response.status < 400:
                        break
            except (URLError, TimeoutError):
                sleep(0.5)
        else:
            raise RuntimeError(f"Static server did not become ready: {url}")
        yield
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def browser_results(artifact_dir: Path) -> list[AuditResult]:
    results: list[AuditResult] = []
    site = ROOT / "_site"
    serve = ROOT / "_audit-serve"
    shutil.rmtree(serve, ignore_errors=True)
    serve.mkdir(parents=True)
    project_path = serve / "Achievements"
    try:
        project_path.symlink_to(site, target_is_directory=True)
    except OSError:
        shutil.copytree(site, project_path)

    search_server_log = artifact_dir / "search-server.log"
    try:
        with static_server(serve, 4173, "/Achievements/search/", search_server_log):
            results.append(
                command_result(
                    "Search browser behaviour",
                    "browser",
                    ["npm", "run", "search:test"],
                    artifact_dir,
                    env={"SEARCH_BASE_URL": "http://127.0.0.1:4173/Achievements"},
                )
            )
    except (OSError, RuntimeError) as error:
        results.append(internal_result("Search browser behaviour", "browser", [str(error)], artifact_dir))

    visual_server_log = artifact_dir / "visual-server.log"
    try:
        with static_server(site, 4174, "/", visual_server_log):
            results.append(
                command_result(
                    "Visual regression",
                    "browser",
                    ["npm", "run", "visual:test"],
                    artifact_dir,
                    env={"VISUAL_BASE_URL": "http://127.0.0.1:4174"},
                )
            )
    except (OSError, RuntimeError) as error:
        results.append(internal_result("Visual regression", "browser", [str(error)], artifact_dir))
    return results


def report_payload(results: list[AuditResult], started_at: datetime, duration: float) -> dict:
    passed = sum(result.status == "passed" for result in results)
    failed = len(results) - passed
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "started_at": started_at.isoformat().replace("+00:00", "Z"),
        "duration_seconds": round(duration, 3),
        "status": "passed" if failed == 0 else "failed",
        "summary": {"total": len(results), "passed": passed, "failed": failed},
        "results": [asdict(result) for result in results],
    }


def markdown_report(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Repository audit report",
        "",
        f"**Overall result:** {payload['status'].upper()}",
        "",
        f"Generated at **{payload['generated_at'].replace('T', ' ').replace('Z', ' UTC')}** in **{payload['duration_seconds']} seconds**.",
        "",
        f"- Controls: **{summary['total']}**",
        f"- Passed: **{summary['passed']}**",
        f"- Failed: **{summary['failed']}**",
        "",
        "## Control results",
        "",
        "| Control | Category | Result | Duration | Log |",
        "|---|---|---|---:|---|",
    ]
    for result in payload["results"]:
        log = f"`{result['log']}`" if result["log"] else "—"
        lines.append(
            f"| {result['name']} | {result['category']} | {result['status'].upper()} | "
            f"{result['duration_seconds']:.3f}s | {log} |"
        )
    lines.extend(["", "## Failure summaries", ""])
    failures = [result for result in payload["results"] if result["status"] != "passed"]
    if failures:
        lines.extend(f"- **{result['name']}:** {result['summary']}" for result in failures)
    else:
        lines.append("No failures were recorded.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    started_wall = datetime.now(timezone.utc).replace(microsecond=0)
    started = monotonic()
    artifact_dir = resolve(args.artifacts)
    shutil.rmtree(artifact_dir, ignore_errors=True)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    python = sys.executable
    results = [
        command_result(
            "Repository-wide Markdown",
            "content",
            ["npx", "--yes", "markdownlint-cli2@0.18.1", "**/*.md"],
            artifact_dir,
        ),
        command_result("Achievement catalogue", "content", [python, "scripts/check_achievement_catalog.py"], artifact_dir),
        command_result(
            "Achievement data contract",
            "data",
            [python, "scripts/validate_achievement_data.py", "--report", str(artifact_dir / "achievement-data.md")],
            artifact_dir,
        ),
        command_result(
            "Verification freshness",
            "evidence",
            [
                python,
                "scripts/check_verification_dates.py",
                "--strict-staleness",
                "--output",
                str(artifact_dir / "verification-dates.md"),
            ],
            artifact_dir,
        ),
        command_result("Full repository links", "content", [python, "scripts/check_links.py", "--all"], artifact_dir),
        command_result(
            "Source resilience inventory",
            "sources",
            [
                python,
                "scripts/build_source_inventory.py",
                "--csv",
                str(artifact_dir / "source-inventory.csv"),
                "--markdown",
                str(artifact_dir / "source-inventory.md"),
            ],
            artifact_dir,
        ),
        command_result(
            "Repository health generation",
            "operations",
            [
                python,
                "-m",
                "scripts.build_health_dashboard",
                "--markdown",
                str(artifact_dir / "health-dashboard.md"),
                "--json",
                str(artifact_dir / "status.json"),
            ],
            artifact_dir,
        ),
        site_contract(artifact_dir),
        release_contract(artifact_dir),
        command_result(
            "GitHub Pages production build",
            "site",
            ["bundle", "exec", "jekyll", "build", "--source", ".", "--destination", "_site"],
            artifact_dir,
            timeout=1200,
        ),
    ]

    if not args.skip_browser:
        if results[-1].status == "passed":
            results.extend(browser_results(artifact_dir))
        else:
            results.append(internal_result("Search browser behaviour", "browser", ["Skipped because Jekyll build failed."], artifact_dir))
            results.append(internal_result("Visual regression", "browser", ["Skipped because Jekyll build failed."], artifact_dir))

    payload = report_payload(results, started_wall, monotonic() - started)
    markdown_path = resolve(args.markdown)
    json_path = resolve(args.json)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(markdown_report(payload), encoding="utf-8")
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        f"Repository audit {payload['status']}: "
        f"{payload['summary']['passed']}/{payload['summary']['total']} controls passed."
    )
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
