#!/usr/bin/env python3
"""Move existing pins to new coordinates, rebuilding the map and streetview links.

Usage: python3 tools/apply_pin_fixes.py fixes.json
where fixes.json is {"Spot short name": [lat, lon], ...}

Prints what moved and by how far; does not regenerate or deploy.
"""
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ("spots.json", "spots_west.json", "spots_north.json", "spots_south.json")


def km(a, b, c, d):
    r = 6371.0088
    p1, p2 = math.radians(a), math.radians(c)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(d - b) / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def main():
    fixes = json.load(open(sys.argv[1], encoding="utf-8"))
    missing = set(fixes)
    for fn in FILES:
        path = os.path.join(ROOT, fn)
        data = json.load(open(path, encoding="utf-8"))
        changed = False
        for s in data:
            if s["short"] in fixes:
                lat, lon = fixes[s["short"]]
                moved = km(s["lat"], s["lon"], lat, lon)
                s["lat"], s["lon"] = lat, lon
                s["maps_url"] = f"https://maps.google.com/?q={lat:.6f},{lon:.6f}"
                s["sv_url"] = (f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={lat:.6f},{lon:.6f}")
                print(f"{s['short']:<18} moved {moved*1000:>5.0f} m -> {lat:.6f},{lon:.6f}")
                missing.discard(s["short"])
                changed = True
        if changed:
            json.dump(data, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    if missing:
        print("NOT FOUND:", ", ".join(sorted(missing)))


if __name__ == "__main__":
    main()
