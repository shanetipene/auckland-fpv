#!/usr/bin/env python3
"""List pending community submissions with an airspace verdict attached.

Reads the D1 table through wrangler, so it needs CLOUDFLARE_API_TOKEN in the
environment (or the token file used by deploy-cloudflare.sh).

Usage:
    python3 tools/review_pending.py            # human readable
    python3 tools/review_pending.py --json     # machine readable
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import airspace  # noqa: E402

CBD = (-36.8489, 174.7652)
DATASETS = {
    "west": "spots_west.json",
    "north": "spots_north.json",
    "south": "spots_south.json",
}
# spots.json holds central + east together
CENTRAL = {
    "Coyle Park", "Monte Cecilia", "Waiatarua", "Stonefields",
    "Panmure Basin", "Pt England", "Orakei Basin", "Glendowie",
}


def token():
    tok = os.environ.get("CLOUDFLARE_API_TOKEN")
    if tok:
        return tok
    path = os.path.expanduser("~/.config/wrangler/pages-token")
    if os.path.exists(path):
        return open(path).read().strip()
    raise SystemExit("No Cloudflare token available.")


def d1(sql):
    env = dict(os.environ, CLOUDFLARE_API_TOKEN=token())
    env["PATH"] = os.path.expanduser("~/.npm-global/bin") + ":" + env.get("PATH", "")
    out = subprocess.run(
        ["wrangler", "d1", "execute", "fpv-community", "--remote",
         "--command", sql, "--json"],
        cwd=ROOT, capture_output=True, text=True, env=env, timeout=120,
    )
    txt = out.stdout
    start = txt.find("[")
    if start == -1:
        raise SystemExit("D1 query failed: " + (out.stderr or txt)[:400])
    data = json.loads(txt[start:])
    return data[0]["results"]


def existing_shorts():
    names = set()
    for fn in ("spots.json", "spots_west.json", "spots_north.json", "spots_south.json"):
        path = os.path.join(ROOT, fn)
        if not os.path.exists(path):
            continue
        for s in json.load(open(path, encoding="utf-8")):
            names.add(s["short"].lower())
            names.add(s["name"].lower())
    return names


def main():
    rows = d1(
        "SELECT id,name,region,lat,lon,maps_url,access,why,hazards,submitter,created_at "
        "FROM submissions WHERE status='pending' ORDER BY created_at"
    )
    known = existing_shorts()
    out = []
    for r in rows:
        lat, lon = r.get("lat"), r.get("lon")
        verdict = airspace.check(lat, lon) if lat is not None and lon is not None else None
        dup = r["name"].strip().lower() in known
        out.append(
            {
                "id": r["id"],
                "name": r["name"],
                "region": r["region"],
                "lat": lat,
                "lon": lon,
                "km_from_cbd": round(airspace.haversine_km(CBD[0], CBD[1], lat, lon), 1)
                if lat is not None else None,
                "possible_duplicate": dup,
                "airspace": verdict,
                "access": r.get("access"),
                "why": r.get("why"),
                "hazards": r.get("hazards"),
                "submitter": r.get("submitter"),
                "maps_url": r.get("maps_url"),
                "created_at": r.get("created_at"),
            }
        )

    if "--json" in sys.argv:
        print(json.dumps(out, indent=2))
        return

    if not out:
        print("No pending submissions.")
        return

    for s in out:
        print(f"\n#{s['id']}  {s['name']}  [{s['region']}]  {s['km_from_cbd']} km from CBD")
        print(f"  coords: {s['lat']}, {s['lon']}")
        if s["possible_duplicate"]:
            print("  !! name matches an existing spot")
        if s["airspace"]:
            a = s["airspace"]
            if a["clean"]:
                print("  airspace: CLEAN")
            else:
                codes = ", ".join(
                    f"{h['code']}:{h['name']}" for h in a["hits"]
                )
                print(f"  airspace: RESTRICTED -> {codes}")
            if a["nearest_aerodromes"]:
                n = a["nearest_aerodromes"][0]
                print(f"  nearest aerodrome: {n['name']} {n['km']} km")
        print(f"  access: {s['access'] or '-'}")
        print(f"  why: {s['why']}")
        print(f"  hazards: {s['hazards'] or '-'}")
        print(f"  from: {s['submitter'] or 'anonymous'}")


if __name__ == "__main__":
    main()
