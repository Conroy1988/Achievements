from __future__ import annotations

from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json
import sys

from scripts.collect_live_backlog_evidence import milestone_candidates, normalize_html, request_headers

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "research" / "live-backlog-sweep.json"

CANDIDATES = {
    "balloob": "home-assistant/core",
    "antirez": "redis/redis",
    "dhh": "rails/rails",
    "gaearon": "facebook/create-react-app",
    "yyx990803": "vuejs/core",
    "tiangolo": "fastapi/fastapi",
    "mitsuhiko": "pallets/flask",
    "visionmedia": "expressjs/express",
}


def fetch(url: str) -> tuple[int, str, str]:
    request = Request(url, headers=request_headers(url))
    with urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8", errors="replace")
        return response.status, response.headers.get("Content-Type", ""), body


def main() -> int:
    payload = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    records: list[dict] = []
    for login, expected_repo in CANDIDATES.items():
        url = f"https://github.com/users/{login}/achievements/starstruck/detail?hovercard=1"
        record: dict[str, object] = {
            "login": login,
            "expected_transferred_or_organization_repo": expected_repo,
            "url": url,
        }
        try:
            status, content_type, body = fetch(url)
        except (HTTPError, URLError, TimeoutError) as error:
            record.update({"status": "fetch-failed", "error": str(error)})
            records.append(record)
            continue
        text, links = normalize_html(url, body)
        record.update({
            "status": "fetched",
            "http_status": status,
            "content_type": content_type,
            "normalized_text": text,
            "github_links": links,
            "milestone_candidates": milestone_candidates(text),
            "expected_repo_linked": f"https://github.com/{expected_repo}" in links,
        })
        records.append(record)

    payload["starstruck_transfer_candidates"] = records
    payload["starstruck_transfer_summary"] = {
        "candidate_count": len(records),
        "fetched_count": sum(item.get("status") == "fetched" for item in records),
        "expected_organization_repo_linked_count": sum(item.get("expected_repo_linked") is True for item in records),
        "automatic_canonical_mutation": False,
    }
    SNAPSHOT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Collected {len(records)} Starstruck transfer candidates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
