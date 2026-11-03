#!/usr/bin/env python3
"""Publish a verified, owner-authored GitHub issue to the public website feed."""
import datetime as dt
import json
import os
import pathlib
import re
import sys
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
FEED = ROOT / "updates.json"
KINDS = {"company", "product", "release", "news"}
MAX_ITEMS = 60

def fail(msg):
    raise SystemExit("Publish rejected: " + msg)

def main():
    event = json.loads(pathlib.Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    issue = event.get("issue") or {}
    if event.get("action") not in {"opened", "edited", "labeled"}:
        return
    # Only owner-authored issues are accepted; never run issue text as code.
    if issue.get("author_association") != "OWNER":
        fail("issue must be authored by repository owner")
    if not str(issue.get("title", "")).startswith("[publish] "):
        return
    body = issue.get("body") or ""
    match = re.fullmatch(r"\s*```json\s*(\{.*?\})\s*```\s*", body, flags=re.S)
    if not match:
        fail("body must contain one JSON code block")
    try:
        data = json.loads(match.group(1))
    except ValueError as exc:
        fail("invalid JSON: " + str(exc))
    if not isinstance(data, dict) or set(data) != {"kind", "title", "summary", "url", "approved"}:
        fail("expected kind, title, summary, url, approved")
    if data["approved"] is not True:
        fail("approved must be true")
    if data["kind"] not in KINDS:
        fail("invalid kind")
    if not isinstance(data["title"], str) or not 4 <= len(data["title"]) <= 110:
        fail("invalid title")
    if not isinstance(data["summary"], str) or not 12 <= len(data["summary"]) <= 500:
        fail("invalid summary")
    if not isinstance(data["url"], str) or len(data["url"]) > 500:
        fail("invalid URL")
    parsed = urlparse(data["url"])
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        fail("public HTTPS evidence URL required")
    if data["kind"] == "release" and not (parsed.netloc.lower() in {"apps.apple.com", "play.google.com", "github.com"}):
        fail("release must link to a verifiable public store or GitHub release")
    existing = json.loads(FEED.read_text(encoding="utf-8"))
    if not isinstance(existing, list):
        fail("feed format invalid")
    issue_id = int(issue["number"])
    item = {
        "id": "issue-" + str(issue_id),
        "date": dt.datetime.now(dt.timezone.utc).date().isoformat(),
        "kind": data["kind"],
        "title": data["title"].strip(),
        "summary": data["summary"].strip(),
        "url": data["url"]
    }
    updated = [item] + [x for x in existing if x.get("id") != item["id"]]
    FEED.write_text(json.dumps(updated[:MAX_ITEMS], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Published", item["id"], item["title"])

if __name__ == "__main__":
    main()
