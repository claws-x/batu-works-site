#!/usr/bin/env python3
"""Check localized static pages, links, assets and the announcement feed."""
import json
import pathlib
import re
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAGES = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)
EXPECTED = ("index.html", "studio.html", "daily-quotes.html", "element-atlas.html", "faq.html", "privacy.html", "support.html")

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.alternates = []
        self.lang = None
    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "html":
            self.lang = data.get("lang")
        if "id" in data:
            self.ids.add(data["id"])
        if tag in ("a", "link") and "href" in data:
            self.links.append(data["href"])
            if tag == "link" and data.get("rel") == "alternate":
                self.alternates.append(data.get("hreflang"))

def main():
    parsed = {}
    errors = []
    for path in PAGES:
        doc = Page()
        doc.feed(path.read_text(encoding="utf-8"))
        parsed[path] = doc
    for prefix, lang in (("", "en"), ("ja/", "ja"), ("zh/", "zh-CN")):
        for page in EXPECTED:
            path = ROOT / prefix / page
            if path not in parsed:
                errors.append(f"missing translated page: {prefix}{page}")
            elif parsed[path].lang != lang:
                errors.append(f"wrong lang: {prefix}{page}")
            elif set(parsed[path].alternates) != {"en", "ja", "zh-Hans", "x-default"}:
                errors.append(f"missing hreflang alternate: {prefix}{page}")
    for path, doc in parsed.items():
        if len(doc.ids) != len(set(doc.ids)):
            errors.append(f"duplicate ID in {path}")
        for link in doc.links:
            parts = urlsplit(link)
            if parts.scheme or parts.netloc or link.startswith("mailto:"):
                if parts.scheme not in ("https", "mailto"):
                    errors.append(f"insecure external link {link}")
                continue
            if parts.path.startswith("/"):
                errors.append(f"absolute local link: {link}")
                continue
            target = (path.parent / unquote(parts.path or path.name)).resolve()
            if not target.is_relative_to(ROOT):
                errors.append(f"unsafe local link: {link}")
                continue
            if not target.is_file():
                errors.append(f"{path.relative_to(ROOT)}: missing {link}")
                continue
            if parts.fragment and target.suffix == ".html" and parts.fragment not in parsed.get(target, Page()).ids:
                errors.append(f"{path.relative_to(ROOT)}: missing anchor {link}")
    for name in EXPECTED:
        html = (ROOT/name).read_text(encoding="utf-8")
        if 'class="translations"' in html or "日本語：" in html or "中文：" in html:
            errors.append(f"old mixed-language snippet in {name}")
    feed = json.loads((ROOT/"updates.json").read_text(encoding="utf-8"))
    if not isinstance(feed, list):
        errors.append("updates.json must be an array")
    else:
        used = set()
        for item in feed:
            if not isinstance(item, dict) or not all(isinstance(item.get(k), str) and item[k] for k in ("id","date","kind","title","summary","url")):
                errors.append("invalid feed item")
                continue
            if item["id"] in used: errors.append("duplicate feed id")
            used.add(item["id"])
            if urlsplit(item["url"]).scheme != "https": errors.append("feed URL must use HTTPS")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"PASS: {len(PAGES)} localized pages, links, language switches and {len(feed)} announcements")

if __name__ == "__main__":
    main()
