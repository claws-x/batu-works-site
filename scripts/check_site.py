#!/usr/bin/env python3
"""Zero-dependency static-site preflight; fail closed on broken local links or feed."""
import json
import pathlib
import re
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

ROOT=pathlib.Path(__file__).resolve().parents[1]
PAGES=sorted(ROOT.glob("*.html"))
class Links(HTMLParser):
    def __init__(self): super().__init__();self.links=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "id" in a:self.ids.add(a["id"])
        if tag=="a" and "href" in a:self.links.append(a["href"])

def main():
    assert PAGES,"no pages"
    parsed={}
    for p in PAGES:
        obj=Links();obj.feed(p.read_text(encoding="utf-8"));parsed[p.name]=obj
    errors=[]
    for p in PAGES:
        for href in parsed[p.name].links:
            parts=urlsplit(href)
            if parts.scheme or parts.netloc or href.startswith("mailto:"):continue
            target=unquote(parts.path or p.name)
            if target.startswith("/") or ".." in pathlib.PurePosixPath(target).parts:
                errors.append(f"{p.name}: unsafe local href {href}");continue
            dest=ROOT/target
            if not dest.is_file():errors.append(f"{p.name}: missing {href}");continue
            if parts.fragment and dest.suffix==".html" and parts.fragment not in parsed.get(dest.name,Links()).ids:
                errors.append(f"{p.name}: missing anchor {href}")
    feed=json.loads((ROOT/"updates.json").read_text(encoding="utf-8"))
    if not isinstance(feed,list):errors.append("updates.json must be array")
    else:
        ids=set()
        for item in feed:
            if not isinstance(item,dict) or not all(k in item for k in ("id","date","kind","title","summary","url")):
                errors.append("invalid feed item");continue
            if item["id"] in ids:errors.append("duplicate feed ID")
            ids.add(item["id"])
            if urlsplit(item["url"]).scheme!="https":errors.append("non-HTTPS evidence URL")
    if errors:raise SystemExit("\n".join(errors))
    print(f"PASS: {len(PAGES)} pages, local links and {len(feed)} announcements")

if __name__=="__main__":main()
