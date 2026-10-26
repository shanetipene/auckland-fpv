#!/usr/bin/env python3
"""Snap a pin to the nearest real beach sand (erosion-filtered).

Classifies sand pixels, requires a full 3x3 block of sand (so pale roofs and
concrete can't match), then returns the nearest surviving sand pixel nudged a
few pixels inland.

Usage: python3 tools/snap_sand2.py "Name,lat,lon" [...]
"""
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
SPAN = 7


def tile_xy(lat, lon, z):
    n = 2 ** z
    return ((lon + 180.0) / 360.0 * n,
            (1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n)


def get_tile(z, x, y):
    p = os.path.join(CACHE, f"esri_{z}_{x}_{y}.jpg")
    if not os.path.exists(p):
        req = urllib.request.Request(TILE.format(z=z, x=x, y=y),
                                     headers={"User-Agent": "auckland-fpv/1.0"})
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
    return img, (tx - (cx - off)) * 256, (ty - (cy - off)) * 256


def is_sand(p):
    r, g, b = p
    return r > 150 and g > 140 and b > 112 and r >= b and (r - b) < 55


def main():
    out = {}
    for arg in sys.argv[1:]:
        name, la, lo = arg.split(",")
        lat, lon = float(la), float(lo)
        img, px, py = mosaic(lat, lon)
        w, h = img.size
        pix = img.load()
        sx, sy = int(px), int(py)

        best = None
        for radius in range(6, 300, 6):
            for ang in range(0, 360, 8):
                dx = int(radius * math.cos(math.radians(ang)))
                dy = int(radius * math.sin(math.radians(ang)))
                x, y = sx + dx, sy + dy
                if not (2 <= x < w - 2 and 2 <= y < h - 2):
                    continue
                if all(is_sand(pix[x + i, y + j]) for i in (-1, 0, 1) for j in (-1, 0, 1)):
                    d = math.hypot(dx, dy)
                    if best is None or d < best[0]:
                        best = (d, dx, dy)
            if best:
                break

        if not best:
            out[name] = {"new": [round(lat, 6), round(lon, 6)], "moved_m": 0, "note": "no sand found"}
            continue

        d, dx, dy = best
        ux, uy = dx / (d or 1), dy / (d or 1)
        fx, fy = sx + dx + ux * 6, sy + dy + uy * 6
        lat_new = lat + (py - fy) * (360.0 / (256 * 2 ** Z)) * math.cos(math.radians(lat))
        lon_new = lon + (fx - px) * (360.0 / (256 * 2 ** Z))
        out[name] = {"new": [round(lat_new, 6), round(lon_new, 6)],
                     "moved_m": round(d * 1.9), "note": "snapped"}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
