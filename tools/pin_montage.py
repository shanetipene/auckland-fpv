#!/usr/bin/env python3
"""Render satellite crops around a list of coordinates with a crosshair,
combined into a single montage for visual pin verification."""
import io
import math
import os
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFont

TILE = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
CACHE = os.path.expanduser("~/.hermes/cache/scratch/tiles")
os.makedirs(CACHE, exist_ok=True)

W, H = 320, 240
Z = 16


def tile_xy(lat, lon, z):
    n = 2 ** z
    x = (lon + 180.0) / 360.0 * n
    y = (1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n
    return x, y


def get_tile(z, x, y):
    path = os.path.join(CACHE, f"esri_{z}_{x}_{y}.jpg")
    if not os.path.exists(path):
        url = TILE.format(z=z, x=x, y=y)
        req = urllib.request.Request(url, headers={"User-Agent": "auckland-fpv-pin-audit/1.0"})
        data = urllib.request.urlopen(req, timeout=25).read()
        open(path, "wb").write(data)
    return Image.open(path).convert("RGB")


def crop(lat, lon):
    tx, ty = tile_xy(lat, lon, Z)
    txi, tyi = int(tx), int(ty)
    px = (tx - txi) * 256
    py = (ty - tyi) * 256
    canvas = Image.new("RGB", (W, H))
    x0 = txi * 256 + px - W / 2
    y0 = tyi * 256 + py - H / 2
    for gx in range(int(x0 // 256), int((x0 + W) // 256) + 1):
        for gy in range(int(y0 // 256), int((y0 + H) // 256) + 1):
            t = get_tile(Z, gx, gy)
            canvas.paste(t, (int(gx * 256 - x0), int(gy * 256 - y0)))
    d = ImageDraw.Draw(canvas)
    cx, cy = W // 2, H // 2
    d.line([(cx - 13, cy), (cx + 13, cy)], fill=(255, 40, 40), width=2)
    d.line([(cx, cy - 13), (cx, cy + 13)], fill=(255, 40, 40), width=2)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], outline=(255, 255, 255), width=2)
    return canvas


def main():
    pts = [p.split(",") for p in sys.argv[2:]]
    out = sys.argv[1]
    cells = []
    for p in pts:
        name, lat, lon = p[0], float(p[1]), float(p[2])
        im = crop(lat, lon)
        d = ImageDraw.Draw(im)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
        except Exception:
            font = ImageFont.load_default()
        d.rectangle([0, 0, W, 24], fill=(0, 0, 0))
        d.text((7, 4), name[:34], fill=(255, 255, 255), font=font)
        cells.append(im)
    cols = 3
    rows = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * W, rows * H), (12, 14, 18))
    for i, im in enumerate(cells):
        sheet.paste(im, ((i % cols) * W, (i // cols) * H))
    sheet.save(out, quality=88)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
