"""Airspace lookup against the cached AirShare layer dump.

Used by the daily submission review. Returns every advisory polygon the point
falls inside, plus the nearest aerodromes with distances in km.
"""
import json
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_LAYERS = json.load(open(os.path.join(_HERE, "layers.json"), encoding="utf-8"))


def _rings(geom):
    if geom is None:
        return []
    t = geom.get("type")
    c = geom.get("coordinates")
    if t == "Polygon":
        return [c]
    if t == "MultiPolygon":
        return c
    return []


def _pip(lon, lat, ring):
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if ((yi > lat) != (yj > lat)) and (
            lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-15) + xi
        ):
            inside = not inside
        j = i
    return inside


def _in_feature(lon, lat, feat):
    for poly in _rings(feat.get("geometry")):
        if _pip(lon, lat, poly[0]) and not any(_pip(lon, lat, h) for h in poly[1:]):
            return True
    return False


def haversine_km(a, b, c, d):
    r = 6371.0088
    p1, p2 = math.radians(a), math.radians(c)
    dp = p2 - p1
    dl = math.radians(d - b)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def check(lat, lon):
    hits = []
    for f in _LAYERS["features"]:
        p = f.get("properties", {})
        if f.get("geometry") is None:
            continue
        try:
            if _in_feature(lon, lat, f):
                hits.append(
                    {
                        "code": p.get("mapCode"),
                        "name": p.get("name"),
                        "lower_ft": p.get("lowerLimitFeet"),
                    }
                )
        except Exception:
            continue

    ads = []
    for f in _LAYERS["features"]:
        p = f.get("properties", {})
        if p.get("mapCode") != "ad" or not p.get("lat"):
            continue
        try:
            dist = haversine_km(lat, lon, float(p["lat"]), float(p["lng"]))
        except Exception:
            continue
        ads.append({"km": round(dist, 2), "name": p.get("name")})
    ads.sort(key=lambda a: a["km"])

    # de-duplicate by name, keep first
    seen, nearest = set(), []
    for a in ads:
        if a["name"] in seen:
            continue
        seen.add(a["name"])
        nearest.append(a)
        if len(nearest) == 4:
            break

    codes = sorted({h["code"] for h in hits})
    return {
        "lat": lat,
        "lon": lon,
        "hits": hits,
        "codes": codes,
        "nearest_aerodromes": nearest,
        "clean": len(hits) == 0,
    }


if __name__ == "__main__":
    import sys

    lat, lon = float(sys.argv[1]), float(sys.argv[2])
    print(json.dumps(check(lat, lon), indent=2))
