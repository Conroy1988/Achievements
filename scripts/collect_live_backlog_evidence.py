from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
import json
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research" / "live-backlog-sweep.json"
USER_AGENT = "Mozilla/5.0 (compatible; GitHub-Achievement-Encyclopedia/1.0)"


@dataclass(frozen=True)
class Target:
    id: str
    kind: str
    url: str
    achievement_slug: str | None = None
    subject_login: str | None = None


TARGETS = [
    Target("PAIR-X4-RONGRONGGG9", "achievement-fragment", "https://github.com/users/Rongronggg9/achievements/pair-extraordinaire/detail?hovercard=1", "pair-extraordinaire", "Rongronggg9"),
    Target("PAIR-X4-TORVALDS", "achievement-fragment", "https://github.com/users/torvalds/achievements/pair-extraordinaire/detail?hovercard=1", "pair-extraordinaire", "torvalds"),
    Target("PAIR-X3-SCHWEINEPRIESTER", "achievement-fragment", "https://github.com/users/Schweinepriester/achievements/pair-extraordinaire/detail?hovercard=1", "pair-extraordinaire", "Schweinepriester"),
    Target("YOLO-SCHWEINEPRIESTER", "achievement-fragment", "https://github.com/users/Schweinepriester/achievements/yolo/detail?hovercard=1", "yolo", "Schweinepriester"),
    Target("STARSTRUCK-X4-TORVALDS", "achievement-fragment", "https://github.com/users/torvalds/achievements/starstruck/detail?hovercard=1", "starstruck", "torvalds"),
    Target("STARSTRUCK-X4-SCHWEINEPRIESTER", "achievement-fragment", "https://github.com/users/Schweinepriester/achievements/starstruck/detail?hovercard=1", "starstruck", "Schweinepriester"),
    Target("STARSTRUCK-X3-RONGRONGGG9", "achievement-fragment", "https://github.com/users/Rongronggg9/achievements/starstruck/detail?hovercard=1", "starstruck", "Rongronggg9"),
    Target("YOLO-REFERENCE-PR", "github-api", "https://api.github.com/repos/Schweinepriester/achievement-testarea/pulls/4"),
    Target("YOLO-REFERENCE-REVIEWS", "github-api", "https://api.github.com/repos/Schweinepriester/achievement-testarea/pulls/4/reviews"),
]


class FragmentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.text: list[str] = []
        self.links: list[str] = []

    def handle_data(self, data: str) -> None:
        value = " ".join(data.split())
        if value:
            self.text.append(value)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)


def request_headers(url: str) -> dict[str, str]:
    host = urlparse(url).netloc
    if host == "api.github.com":
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": "2022-11-28",
        }
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    return {
        "Accept": "text/html, */*;q=0.1",
        "Accept-Language": "en-GB,en;q=0.9",
        "Referer": "https://github.com/",
        "User-Agent": USER_AGENT,
        "X-Requested-With": "XMLHttpRequest",
    }


def fetch(url: str) -> tuple[int, str, str]:
    request = Request(url, headers=request_headers(url))
    with urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8", errors="replace")
        return response.status, response.headers.get("Content-Type", ""), body


def normalize_html(url: str, body: str) -> tuple[str, list[str]]:
    parser = FragmentParser()
    parser.feed(body)
    text = " ".join(unescape(" ".join(parser.text)).split())
    links: list[str] = []
    for href in parser.links:
        absolute = urljoin(url, href)
        parsed = urlparse(absolute)
        if parsed.scheme == "https" and parsed.netloc == "github.com" and absolute not in links:
            links.append(absolute)
    return text, links


def milestone_candidates(text: str) -> list[int]:
    values: list[int] = []
    pattern = r"(?:1st|2nd|3rd|4th|5th|8th|10th|16th|24th|32nd|48th|128th|512th|1024th|4096th)|\b(?:1|2|4|5|8|10|16|24|32|48|128|512|1024|4096)\b"
    for match in re.findall(pattern, text, flags=re.IGNORECASE):
        digits = re.sub(r"\D", "", match)
        if digits and int(digits) not in values:
            values.append(int(digits))
    return values


def compact_api(value: object) -> object:
    if isinstance(value, list):
        return [compact_api(item) for item in value]
    if not isinstance(value, dict):
        return value
    allowed = {
        "id", "number", "state", "user", "login", "html_url", "submitted_at",
        "author_association", "merged", "merged_at", "merged_by", "merge_commit_sha",
        "requested_reviewers", "head", "base", "sha", "ref", "repo", "full_name",
        "owner", "type", "fork", "archived", "stargazers_count", "name",
    }
    return {key: compact_api(item) for key, item in value.items() if key in allowed}


def collect_target(target: Target) -> dict:
    record: dict[str, object] = {
        "id": target.id,
        "kind": target.kind,
        "url": target.url,
        "achievement_slug": target.achievement_slug,
        "subject_login": target.subject_login,
    }
    try:
        status, content_type, body = fetch(target.url)
    except (HTTPError, URLError, TimeoutError) as error:
        record.update({"status": "fetch-failed", "error": str(error)})
        return record

    record.update({
        "status": "fetched",
        "http_status": status,
        "content_type": content_type,
        "body_sha256": sha256(body.encode("utf-8")).hexdigest(),
    })
    if target.kind == "achievement-fragment":
        text, links = normalize_html(target.url, body)
        record.update({
            "normalized_text": text,
            "normalized_text_sha256": sha256(text.encode("utf-8")).hexdigest(),
            "github_links": links,
            "milestone_candidates": milestone_candidates(text),
        })
    else:
        record["api_payload"] = compact_api(json.loads(body))
    return record


def main() -> int:
    records = [collect_target(target) for target in TARGETS]
    payload = {
        "schema_version": "1.0.0",
        "observed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "purpose": "First-party evidence sweep for CLM-006 and contradictions CTR-002, CTR-004, and CTR-006.",
        "automatic_canonical_mutation": False,
        "records": records,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    failures = [str(record["id"]) for record in records if record.get("status") != "fetched"]
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(records)} records.")
    if failures:
        print("Fetch failures: " + ", ".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
