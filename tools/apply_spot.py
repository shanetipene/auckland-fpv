#!/usr/bin/env python3
"""Add an approved community spot to the site and redeploy.

Usage:
    python3 tools/apply_spot.py spot.json [--dry-run] [--no-deploy]

The JSON file needs:
    short, name, region (central|east|north|west|south), lat, lon,
    secl, traffic, fly   (0-5, traffic = crowd level, higher = busier)
    status (clear|permit|restricted), kind, best, hazards, note,
    access, land, quiet_time, quiet_days, avoid

drive_min / drive_km and fpv_score are computed here.
"""
import json
import math
import os
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CBD = (-36.8489, 174.7652)
DATASETS = {
    "central": "spots.json",
    "east": "spots.json",
    "west": "spots_west.json",
    "north": "spots_north.json",
    "south": "spots_south.json",
}
REQUIRED = [
    "short", "name", "region", "lat", "lon", "secl", "traffic", "fly",
    "status", "kind", "best", "hazards", "note", "access", "launch", "land",
    "quiet_time", "quiet_days", "avoid",
]


def haversine_km(a, b, c, d):
    r = 6371.0088
    p1, p2 = math.radians(a), math.radians(c)
    dp = p2 - p1
    dl = math.radians(d - b)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def drive(lat, lon):
    """Road distance/time from the CBD via OSRM, with a straight-line fallback."""
    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{CBD[1]},{CBD[0]};{lon},{lat}?overview=false"
    )
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            d = json.load(r)
        route = d["routes"][0]
        return int(round(route["duration"] / 60)), int(round(route["distance"] / 1000))
    except Exception:
        km = haversine_km(CBD[0], CBD[1], lat, lon) * 1.45
        return int(round(km / 45 * 60)), int(round(km))


def score(secl, traffic, fly, status):
    base = 1.0 + 0.8 * fly + 0.6 * secl + 0.4 * (5 - traffic)
    if status == "permit":
        base -= 1.0
    elif status == "restricted":
        base -= 1.5
    return round(max(0.0, min(10.0, base)), 1)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    deploy = "--no-deploy" not in sys.argv
    if not args:
        raise SystemExit(__doc__)

    spec = json.load(open(args[0], encoding="utf-8"))
    missing = [k for k in REQUIRED if not spec.get(k) and spec.get(k) != 0]
    if missing:
        raise SystemExit("Missing fields: " + ", ".join(missing))

    region = spec["region"].lower()
    if region not in DATASETS:
        raise SystemExit("Unknown region: " + region)

    lat, lon = float(spec["lat"]), float(spec["lon"])
    mins, km = drive(lat, lon)
    spec["drive_min"] = mins
    spec["drive_km"] = km
    spec["maps_url"] = spec.get("maps_url") or f"https://maps.google.com/?q={lat:.5f},{lon:.5f}"
    spec["fpv_score"] = spec.get("fpv_score") or score(
        float(spec["secl"]), float(spec["traffic"]), float(spec["fly"]), spec["status"]
    )

    print(json.dumps({k: spec[k] for k in ("short", "region", "drive_min", "drive_km", "fpv_score")}, indent=2))
    if dry:
        print("dry run — nothing written")
        return

    path = os.path.join(ROOT, DATASETS[region])
    spots = json.load(open(path, encoding="utf-8"))
    if any(s["short"].lower() == spec["short"].lower() for s in spots):
        raise SystemExit(f"A spot called {spec['short']} already exists in {DATASETS[region]}")

    spots.append(spec)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(spots, f, indent=1, ensure_ascii=False)
    print(f"added to {DATASETS[region]} (now {len(spots)} spots)")

    gen = subprocess.run([sys.executable, "gen_html.py"], cwd=ROOT, capture_output=True, text=True)
    if gen.returncode != 0:
        raise SystemExit("generator failed:\n" + gen.stdout + gen.stderr)
    print(gen.stdout.strip())

    if deploy:
        subprocess.run([os.path.join(ROOT, "deploy-cloudflare.sh")], cwd=ROOT)
    print("done:", spec["short"])


if __name__ == "__main__":
    main()
