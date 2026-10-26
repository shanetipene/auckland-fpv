#!/usr/bin/env python3
"""Find the nearest point on a beach or park polygon to a given coordinate.

Used to repair pins that landed on housing instead of the coast.
"""
import json
import math
import sys
import time
import urllib.parse
import urllib.request

EPS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]


def overpass(q):
    last = None
    for ep in EPS:
        for attempt in range(2):
            try:
                req = urllib.request.Request(
                    ep,
                    data=urllib.parse.urlencode({"data": q}).encode(),
                    headers={"User-Agent": "auckland-fpv-pin-audit/1.0"},
                )
                return json.load(urllib.request.urlopen(req, timeout=60))["elements"]
            except Exception as e:
                last = e
                time.sleep(2)
    print("  ! overpass failed:", last, file=sys.stderr)
    return []


def hav(a, b, c, d):
    r = 6371.0088
    p1, p2 = math.radians(a), math.radians(c)
    dp = p2 - p1
    dl = math.radians(d - b)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def nearest_on_segment(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return ax, ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return ax + t * dx, ay + t * dy


def nearest_point(lat, lon, ways, want_name=None):
    best = None
    for el in ways:
        tags = el.get("tags", {})
        if want_name and want_name.lower() not in tags.get("name", "").lower():
            continue
        geom = el.get("geometry")
        if not geom:
            continue
        for i in range(len(geom) - 1):
            a, b = geom[i], geom[i + 1]
            q = nearest_on_segment(lon, lat, a["lon"], a["lat"], b["lon"], b["lat"])
            d = hav(lat, lon, q[1], q[0])
            if best is None or d < best["km"]:
                best = {"km": round(d, 3), "lat": round(q[1], 6), "lon": round(q[0], 6),
                        "name": tags.get("name", "?"), "kind": tags.get("natural") or tags.get("leisure")}
    return best


def main():
    lat, lon, query = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
    q = (
        f"[out:json][timeout:50];"
        f'(way(around:3000,{lat},{lon})["natural"="beach"];'
        f'way(around:3000,{lat},{lon})["leisure"~"park|reserve"]["name"];);'
        "out geom tags;"
    )
    ways = overpass(q)
    print(json.dumps({"query": query, "candidates": nearest_point(lat, lon, ways)}, indent=2))


if __name__ == "__main__":
    main()
