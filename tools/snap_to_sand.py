#!/usr/bin/env python3
"""Snap pins that landed on housing to the nearest beach sand.

Builds a small satellite mosaic around each pin, classifies water pixels,
finds the nearest land pixel, then steps a little further inland so the pin
sits on the beach or bank rather than the waterline.

Prints JSON: {name: {old: [lat,lon], new: [lat,lon], moved_m: float}}
"""
import io
import json
import math
import os
import sys
import urllib.request

from PIL import Image

TILE = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
CACHE = os.path.expanduser("~/.hermes/cache/scratch/tiles")
os.makedirs(CACHE, exist_ok=True)
Z = 16
SPAN = 7  # tiles across


def tile_xy(lat, lon, z):
    n = 2 ** z
    return (lon + 180.0) / 360.0 * n, (1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n


def get_tile(z, x, y):
    p = os.path.join(CACHE, f"esri_{z}_{x}_{y}.jpg")
    if not os.path.exists(p):
        req = urllib.request.Request(
            TILE.format(z=z, x=x, y=y), headers={"User-Agent": "auckland-fpv-pin-audit/1.0"}
        )
        open(p, "wb").write(urllib.request.urlopen(req, timeout=25).read())
    return Image.open(p).convert("RGB")


def mosaic(lat, lon):
    tx, ty = tile_xy(lat, lon, Z)
    cx, cy = int(tx), int(ty)
    off = SPAN // 2
    img = Image.new("RGB", (SPAN * 256, SPAN * 256))
    for i, gx in enumerate(range(cx - off, cx + off + 1)):
        for j, gy in enumerate(range(cy - off, cy + off + 1)):
            img.paste(get_tile(Z, gx, gy), (i * 256, j * 256))
    px = (tx - (cx - off)) * 256
    py = (ty - (cy - off)) * 256
    return img, px, py


def is_water(p):
    r, g, b = p
    return b > r + 12 and b > 55 and g > r


def is_sand(p):
    r, g, b = p
    return r > 150 and g > 138 and b > 108 and r >= b and (r - b) < 70


def main():
    pts = [a.split(",") for a in sys.argv[1:]]
    out = {}
    for name, la, lo in pts:
        lat, lon = float(la), float(lo)
        img, px, py = mosaic(lat, lon)
        w, h = img.size
        pix = img.load()
        start = (int(px), int(py))
        if is_sand(pix[start]):
            out[name] = {"old": [lat, lon], "new": [lat, lon], "moved_m": 0.0, "note": "already on sand"}
            continue
        best = None
        # spiral outward, nearest land pixel
        for radius in range(4, 300, 3):
            for ang in range(0, 360, 6):
                dx = int(radius * math.cos(math.radians(ang)))
                dy = int(radius * math.sin(math.radians(ang)))
                x, y = start[0] + dx, start[1] + dy
                if 0 <= x < w and 0 <= y < h and is_sand(pix[x, y]):
                    dist = math.hypot(dx, dy)
                    if best is None or dist < best[0]:
                        best = (dist, dx, dy)
            if best:
                break
        if not best:
            out[name] = {"old": [lat, lon], "new": [lat, lon], "moved_m": 0.0, "note": "no shore found"}
            continue
        dist, dx, dy = best
        # step ~12 px further inland from the shore point
        ux, uy = dx / (dist or 1), dy / (dist or 1)
        fx, fy = start[0] + dx + ux * 12, start[1] + dy + uy * 12
        lat_new = lat + (py - fy) * (360.0 / (256 * 2 ** Z)) * math.cos(math.radians(lat))
        lon_new = lon + (fx - px) * (360.0 / (256 * 2 ** Z))
        moved = math.hypot((fx - px) * 1.9, (fy - py) * 1.9)
        out[name] = {"old": [lat, lon], "new": [round(lat_new, 6), round(lon_new, 6)], "moved_m": round(moved)}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
