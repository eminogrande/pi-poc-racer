#!/usr/bin/env python3
"""Generate ANSI half-block pixel banner from an image. Usage: banner.py <img> <out> [width]"""
import sys
from PIL import Image

src, out, w = sys.argv[1], sys.argv[2], int(sys.argv[3] if len(sys.argv) > 3 else 72)
img = Image.open(src).convert("RGB")
pw, ph = img.size
band = img.crop((0, int(ph * 0.08), pw, int(ph * 0.58)))  # horizontal pit-garage band
h = int(w * (band.size[1] / band.size[0]))
h += h % 2
px = band.resize((w, h), Image.LANCZOS).load()

lines = []
for y in range(0, h, 2):
    row = []
    for x in range(w):
        r1, g1, b1 = px[x, y]
        r2, g2, b2 = px[x, y + 1]
        row.append(f"\x1b[38;2;{r1};{g1};{b1}m\x1b[48;2;{r2};{g2};{b2}m▀")
    lines.append("".join(row) + "\x1b[0m")
open(out, "w").write("\n".join(lines) + "\n")
print(f"{out}: {w}x{h // 2} cells")
