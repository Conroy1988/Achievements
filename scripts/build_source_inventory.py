from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen
import argparse
import csv
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", "_site", "vendor"}
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\((https?://[^)\s]+)")


@dataclass(frozen=True)
class SourceRecord:
    url: str
    domain: str
    source_type: str
    stability: str
    reference_count: int
    files: tuple[str, ...]
    last_checked: str
    availability: str
    archive_lookup: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a repository-wide external source inventory.")
    parser.add_argument("--csv", type=Path, default=Path("source-inventory.csv"))
    parser.add_argument("--markdown", type=Path, default=Path("source-inventory.md"))
    parser.add_argument("--check-availability", action="store_true")
    parser.add_argument("--timeout", type=float, default=6.0)
    return parser.parse_args()


def markdown_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if not any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts)
    )


def normalise_url(raw: str) -> str:
    return raw.rstrip(".,;:").replace("&amp;", "&")


def classify(domain: str) -> tuple[str, str]:
    if domain in {"docs.github.com", "github.blog", "support.github.com"}:
        return "Official GitHub", "High"
    if domain == "web.archive.org":
        return "Archived source", "Archived"
    if domain == "github.com" or domain.endswith(".github.com"):
        return "GitHub-hosted source", "Medium"
    if domain.endswith(".gov") or domain.endswith(".gov.uk") or domain.endswith(".edu") or domain.endswith(".ac.uk"):
        return "Institutional source", "High"
    return "External source", "Review"


def availability(url: str, timeout: float) -> str:
    headers = {"User-Agent": "GitHub-Achievement-Encyclopedia-source-audit/1.0"}
    request = Request(url, headers=headers, method="HEAD")
    try:
        with urlopen(request, timeout=timeout) as response:
            return f"Reachable ({response.status})"
    except HTTPError as error:
        if error.code == 405:
            try:
                with urlopen(Request(url, headers=headers), timeout=timeout) as response:
                    return f"Reachable ({response.status})"
            except (HTTPError, URLError, TimeoutError) as fallback_error:
                return describe_error(fallback_error)
        if error.code in {401, 403, 429}:
            return f"Restricted ({error.code})"
        return f"Unavailable ({error.code})"
    except (URLError, TimeoutError) as error:
        return describe_error(error)


def describe_error(error: BaseException) -> str:
    reason = getattr(error, "reason", error)
    return f"Unreachable ({str(reason)[:80]})"


def collect(check: bool, timeout: float) -> list[SourceRecord]:
    references: dict[str, list[str]] = defaultdict(list)
    for path in markdown_files():
        relative = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        for raw in LINK_PATTERN.findall(text):
            references[normalise_url(raw)].append(relative)

    checked_on = date.today().isoformat() if check else "Not checked"
    records: list[SourceRecord] = []
    for url, uses in sorted(references.items()):
        domain = urlsplit(url).netloc.lower().split(":", 1)[0]
        source_type, stability = classify(domain)
        unique_files = tuple(sorted(set(uses)))
        status = availability(url, timeout) if check else "Not checked"
        records.append(
            SourceRecord(
                url=url,
                domain=domain,
                source_type=source_type,
                stability=stability,
                reference_count=len(uses),
                files=unique_files,
                last_checked=checked_on,
                availability=status,
                archive_lookup=f"https://web.archive.org/web/*/{quote(url, safe=':/?=&%#')}",
            )
        )
    return records


def output_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def write_csv(records: list[SourceRecord], path: Path) -> None:
    destination = output_path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "URL",
                "Domain",
                "Source type",
                "Stability",
                "Reference count",
                "Referencing files",
                "Last checked",
                "Availability",
                "Archive lookup",
            ]
        )
        for item in records:
            writer.writerow(
                [
                    item.url,
                    item.domain,
                    item.source_type,
                    item.stability,
                    item.reference_count,
                    "; ".join(item.files),
                    item.last_checked,
                    item.availability,
                    item.archive_lookup,
                ]
            )


def write_markdown(records: list[SourceRecord], path: Path) -> None:
    destination = output_path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    domains = len({item.domain for item in records})
    references = sum(item.reference_count for item in records)
    availability_counts: dict[str, int] = defaultdict(int)
    for item in records:
        availability_counts[item.availability.split(" ", 1)[0]] += 1

    lines = [
        "# External source inventory",
        "",
        f"Inventory contains **{len(records)} unique URLs** across **{domains} domains** and **{references} references**.",
        "",
        "## Availability summary",
        "",
    ]
    for label, count in sorted(availability_counts.items()):
        lines.append(f"- {label}: **{count}**")

    lines.extend(
        [
            "",
            "## Sources",
            "",
            "| Domain | Source type | Stability | References | Availability | URL |",
            "|---|---|---|---:|---|---|",
        ]
    )
    for item in records:
        lines.append(
            f"| {item.domain} | {item.source_type} | {item.stability} | {item.reference_count} | "
            f"{item.availability} | {item.url} |"
        )
    lines.append("")
    destination.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        records = collect(args.check_availability, args.timeout)
        write_csv(records, args.csv)
        write_markdown(records, args.markdown)
    except (OSError, ValueError) as error:
        print(f"Source inventory failed: {error}")
        return 1

    print(f"Inventoried {len(records)} unique external sources.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
