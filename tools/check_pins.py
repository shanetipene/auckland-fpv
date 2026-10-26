#!/usr/bin/env python3
"""Audit every spot pin against the named place in OpenStreetMap.

For each spot, search Nominatim for the spot name in Auckland, take the best
match, and report the distance between the stored pin and the matched place.
Results are cached so reruns are free.
"""
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(HERE, "pin_check.json")
UA = "auckland-fpv-pin-audit/1.0 (contact: cyn.ai.assistant@gmail.com)"
DATASETS = ["spots.json", "spots_west.json", "spots_north.json", "spots_south.json"]


def hav(a, b, c, d):
    r = 6371.0088
    p1, p2 = math.radians(a), math.radians(c)
    dp = p2 - p1
    dl = math.radians(d - b)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def query_for(spot):
    name = spot["name"]
    primary = name.split(" / ")[0]
    primary = re.sub(r"\s*\(.*?\)\s*", " ", primary).strip()
    return primary


def search(q):
    url = (
        "https://nominatim.openstreetmap.org/search?"
        + urllib.parse.urlencode({"q": q, "format": "json", "limit": 5, "countrycodes": "nz"})
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def main():
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    spots = []
    for fn in DATASETS:
        for s in json.load(open(os.path.join(ROOT, fn), encoding="utf-8")):
            s["_file"] = fn
            spots.append(s)

    out = []
    for s in sorted(spots, key=lambda x: x["short"]):
        key = s["short"]
        if key not in cache:
            q = query_for(s)
            try:
                res = search(q + ", Auckland, New Zealand")
                if not res:
                    res = search(q + ", New Zealand")
            except Exception as e:
                res = []
                print(f"  ! {key}: search failed {e}", file=sys.stderr)
            time.sleep(1.1)
            best = None
            for r in res:
                d = hav(s["lat"], s["lon"], float(r["lat"]), float(r["lon"]))
                if best is None or d < best["km"]:
                    best = {
                        "km": round(d, 2),
                        "osm": r["display_name"],
                        "lat": float(r["lat"]),
                        "lon": float(r["lon"]),
                        "type": r.get("type"),
                    }
            cache[key] = best
            json.dump(cache, open(CACHE, "w"), indent=1)

        b = cache[key]
        out.append(
            {
                "short": key,
                "file": s["_file"],
                "lat": s["lat"],
                "lon": s["lon"],
                "km": b["km"] if b else None,
                "osm": b["osm"] if b else None,
                "osm_lat": b["lat"] if b else None,
                "osm_lon": b["lon"] if b else None,
                "type": b["type"] if b else None,
            }
        )

    out.sort(key=lambda r: (r["km"] is None, -(r["km"] or 0)))
    for r in out:
        flag = "NO MATCH" if r["km"] is None else ("CHECK" if r["km"] > 0.6 else "ok")
        kms = "  n/a " if r["km"] is None else f"{r['km']:6.2f}"
        print(f"{flag:8} {kms}km  {r['short'][:26]:26} {r['file']:18} {str(r['osm'])[:70]}")

    print("\nflagged:", sum(1 for r in out if r["km"] is None or r["km"] > 0.6), "of", len(out))


if __name__ == "__main__":
    main()
