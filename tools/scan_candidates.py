#!/usr/bin/env python3
"""Geocode candidate spots and check them against the AirShare layers.

Prints a table of what is legal (no advisory polygons, no aerodrome inside
4 km) so we only write up sites that can actually be flown.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import airspace  # noqa: E402

UA = {"User-Agent": "auckland-fpv-spot-research/1.0 (shanetipene@github)"}
BBOX = (-37.60, 174.20, -36.05, 175.60)  # S, W, N, E


def geocode(q):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "json", "limit": 1, "countrycodes": "nz",
         "viewbox": f"{BBOX[1]},{BBOX[2]},{BBOX[3]},{BBOX[0]}", "bounded": 1}
    )
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        d = json.load(r)
    if not d:
        return None
    return float(d[0]["lat"]), float(d[0]["lon"]), d[0].get("display_name", "")


def main():
    cands = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else []
    out = []
    for c in cands:
        try:
            g = geocode(c["q"])
        except Exception as e:
            print(f"{c['short']:<22} GEOCODE FAIL {e}")
            continue
        time.sleep(1.1)
        if not g:
            print(f"{c['short']:<22} no geocode result")
            continue
        lat, lon, disp = g
        a = airspace.check(lat, lon)
        near = a["nearest_aerodromes"][0] if a["nearest_aerodromes"] else {"km": 99, "name": "-"}
        ring_ok = near["km"] >= 4.0
        ok = a["clean"] and ring_ok
        out.append({"short": c["short"], "region": c["region"], "q": c["q"],
                    "lat": round(lat, 6), "lon": round(lon, 6), "ok": ok,
                    "codes": a["codes"], "near_km": near["km"], "near": near["name"],
                    "disp": disp[:70]})
        flag = "OK  " if ok else "NO  "
        print(f"{flag}{c['short']:<22} {lat:.5f},{lon:.5f}  codes={','.join(a['codes']) or 'none':<12} "
              f"near={near['km']:.1f}km {near['name'][:26]:<26} | {disp[:44]}")
    json.dump(out, open(os.path.join(HERE, "candidates.json"), "w"), indent=1)

    legal = [c for c in out if c["ok"]]
    print(f"\n{len(legal)} legal of {len(out)} geocoded")


if __name__ == "__main__":
    main()
