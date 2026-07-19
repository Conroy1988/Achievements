from __future__ import annotations

from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
import argparse
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data" / "official-document-monitor.json"
PAGE_PATH = ROOT / "docs" / "official-document-monitor.md"
USER_AGENT = "GitHub-Achievement-Encyclopedia/1.0 (+https://github.com/Conroy1988/Achievements)"


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "svg", "nav", "footer"}:
            self.skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "svg", "nav", "footer"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)


def normalized_text(payload: bytes) -> str:
    parser = VisibleTextParser()
    parser.feed(payload.decode("utf-8", errors="replace"))
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def fingerprint(url: str) -> tuple[str, int]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    with urlopen(request, timeout=30) as response:
        payload = response.read()
    text = normalized_text(payload)
    if len(text) < 200:
        raise ValueError("normalized page content is unexpectedly short")
    return hashlib.sha256(text.encode("utf-8")).hexdigest(), len(text)


def validate_config(config: dict) -> list[str]:
    failures: list[str] = []
    documents = config.get("documents")
    if not isinstance(documents, list) or not documents:
        return ["documents must be a non-empty array"]
    ids: set[str] = set()
    urls: set[str] = set()
    for index, document in enumerate(documents, start=1):
        prefix = f"document {index}"
        document_id = document.get("id")
        url = document.get("url")
        if not isinstance(document_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", document_id):
            failures.append(f"{prefix}: invalid id")
        elif document_id in ids:
            failures.append(f"{prefix}: duplicate id {document_id}")
        ids.add(document_id)
        if not isinstance(url, str) or not url.startswith("https://docs.github.com/"):
            failures.append(f"{prefix}: URL must be an official docs.github.com HTTPS URL")
        elif url in urls:
            failures.append(f"{prefix}: duplicate URL")
        urls.add(url)
        affected = document.get("affected_achievements")
        if not isinstance(affected, list) or not affected or not all(isinstance(item, str) and item for item in affected):
            failures.append(f"{prefix}: affected_achievements must be a non-empty string array")
        baseline = document.get("baseline_sha256")
        if baseline is not None and not re.fullmatch(r"[0-9a-f]{64}", baseline):
            failures.append(f"{prefix}: invalid baseline SHA-256")
    return failures


def render_page(config: dict) -> str:
    lines = [
        "---",
        "layout: default",
        "title: Official documentation monitor",
        "description: Monitored GitHub documentation and the achievement guides affected by material changes.",
        "permalink: /official-doc-monitor/",
        "---",
        "",
        "## Official documentation monitor",
        "",
        "This monitor fingerprints normalized visible content from selected official GitHub documentation. A changed fingerprint is a review signal, not automatic proof that an achievement rule changed.",
        "",
        "| Document | Affected achievements | Baseline checked | Fingerprint |",
        "|---|---|---|---|",
    ]
    for document in config["documents"]:
        affected = ", ".join(document["affected_achievements"])
        checked = document.get("baseline_checked_at") or "Not initialised"
        digest = document.get("baseline_sha256") or "Not initialised"
        lines.append(f"| [{document['id']}]({document['url']}) | {affected} | {checked} | `{digest[:12]}` |")
    lines.extend([
        "",
        "## Change handling",
        "",
        "1. Scheduled checks compare current normalized content with the committed baseline.",
        "2. Material differences produce a dated report and an open review issue.",
        "3. A maintainer inspects the official wording and identifies affected guide claims.",
        "4. Baselines change only through a reviewed pull request after the guide impact is resolved.",
        "",
        "Navigation, footer, style, script, and SVG content are excluded before hashing to reduce cosmetic noise.",
        "",
    ])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitor selected official GitHub documentation pages.")
    parser.add_argument("--initialise", action="store_true")
    parser.add_argument("--report", default="official-doc-monitor-report.md")
    parser.add_argument("--json", default="official-doc-monitor-report.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    failures = validate_config(config)
    if failures:
        print("\n".join(failures))
        return 1

    checked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    results: list[dict] = []
    changed: list[dict] = []
    errors: list[dict] = []

    for document in config["documents"]:
        try:
            current_sha, text_length = fingerprint(document["url"])
            previous_sha = document.get("baseline_sha256")
            result = {
                "id": document["id"],
                "url": document["url"],
                "affected_achievements": document["affected_achievements"],
                "baseline_sha256": previous_sha,
                "current_sha256": current_sha,
                "normalized_characters": text_length,
                "changed": previous_sha is not None and previous_sha != current_sha,
            }
            results.append(result)
            if args.initialise:
                document["baseline_sha256"] = current_sha
                document["baseline_checked_at"] = checked_at
            elif result["changed"]:
                changed.append(result)
        except Exception as error:  # noqa: BLE001
            item = {"id": document.get("id"), "url": document.get("url"), "error": str(error)}
            errors.append(item)

    if args.initialise and not errors:
        CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        PAGE_PATH.write_text(render_page(config), encoding="utf-8")

    status = "error" if errors else "changed" if changed else "unchanged"
    payload = {
        "schema_version": "1.0.0",
        "checked_at": checked_at,
        "status": status,
        "documents_checked": len(results),
        "changes": changed,
        "errors": errors,
        "results": results,
    }
    (ROOT / args.json).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Official documentation monitor report",
        "",
        f"- Checked at: {checked_at}",
        f"- Status: {status}",
        f"- Documents checked: {len(results)}",
        f"- Material fingerprint changes: {len(changed)}",
        f"- Errors: {len(errors)}",
    ]
    if changed:
        lines.extend(["", "## Changed documents", ""])
        for item in changed:
            affected = ", ".join(item["affected_achievements"])
            lines.append(f"- [{item['id']}]({item['url']}) — affected guides: {affected}")
    if errors:
        lines.extend(["", "## Errors", ""])
        for item in errors:
            lines.append(f"- {item['id']}: {item['error']}")
    (ROOT / args.report).write_text("\n".join(lines) + "\n", encoding="utf-8")

    if errors:
        return 1
    if changed:
        return 2
    print(f"Official documentation monitor passed across {len(results)} pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
