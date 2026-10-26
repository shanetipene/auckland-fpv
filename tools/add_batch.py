#!/usr/bin/env python3
"""Add several spots in one pass, with an airspace gate on every one.

Usage: python3 tools/add_batch.py tools/new_spots.json [--dry-run] [--no-deploy]

Each spec needs the fields apply_spot.py expects. Anything inside an AirShare
advisory polygon, or within 4 km of an aerodrome, is refused rather than added.
drive_min / drive_km / fpv_score / maps_url / sv_url are computed here, and
gen_html.py runs once at the end.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import airspace  # noqa: E402

DATASETS = {
    "central": "spots.json", "east": "spots.json",
    "west": "spots_west.json", "north": "spots_north.json", "south": "spots_south.json",
}


def haversine_km(a, b, c, d):
    import math
    r = 6371.0088
    p1, p2 = math.radians(a), math.radians(c)
    dp, dl = p2 - p1, math.radians(d - b)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


CBD = (-36.8489, 174.7652)


def drive(lat, lon):
    import urllib.request
    url = (f"https://router.project-osrm.org/route/v1/driving/"
           f"{CBD[1]},{CBD[0]};{lon},{lat}?overview=false")
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            route = json.load(r)["routes"][0]
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
    specs = json.load(open(args[0], encoding="utf-8"))

    # keyed by FILE, not region: central and east share spots.json and must
    # not be loaded as two separate lists or one overwrites the other
    files = {}
    for _f in set(DATASETS.values()):
        files[_f] = json.load(open(os.path.join(ROOT, _f), encoding="utf-8"))
    seen = {s["short"].lower() for data in files.values() for s in data}

    added, refused = [], []
    for spec in specs:
        name = spec["short"]
        if name.lower() in seen:
            refused.append((name, "already on the site"))
            continue
        lat, lon = float(spec["lat"]), float(spec["lon"])
        a = airspace.check(lat, lon)
        near = a["nearest_aerodromes"][0]
        if a["hits"] or near["km"] < 4.0:
            refused.append((name, f"airspace: codes={a['codes']} nearest={near['name']} {near['km']}km"))
            continue
        minutes, km = drive(lat, lon)
        spec["drive_min"], spec["drive_km"] = minutes, km
        spec["dist_cbd_km"] = round(haversine_km(CBD[0], CBD[1], lat, lon), 1)
        spec["fpv_score"] = score(float(spec["secl"]), float(spec["traffic"]),
                                  float(spec["fly"]), spec["status"])
        spec["maps_url"] = f"https://maps.google.com/?q={lat:.6f},{lon:.6f}"
        spec["sv_url"] = f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={lat:.6f},{lon:.6f}"
        spec["region"] = spec["region"].lower()
        files[DATASETS[spec["region"]]].append(spec)
        seen.add(name.lower())
        added.append(spec)
        print(f"added  {name:<16} {spec['region']:<8} {spec['fpv_score']:>4}/10  {minutes} min {km} km")

    for name, why in refused:
        print(f"REFUSED {name:<15} {why}")

    print(f"\n{len(added)} added, {len(refused)} refused")
    if dry:
        print("dry run — nothing written")
        return

    for fname, data in files.items():
        json.dump(data, open(os.path.join(ROOT, fname), "w", encoding="utf-8"),
                  indent=1, ensure_ascii=False)

    gen = subprocess.run([sys.executable, "gen_html.py"], cwd=ROOT, capture_output=True, text=True)
    if gen.returncode != 0:
        raise SystemExit("generator failed:\n" + gen.stdout + gen.stderr)
    print(gen.stdout.strip()[-400:])

    if deploy:
        subprocess.run([os.path.join(ROOT, "deploy-cloudflare.sh")], cwd=ROOT)


if __name__ == "__main__":
    main()
