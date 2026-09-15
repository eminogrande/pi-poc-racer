#!/usr/bin/env python3
"""POC RACER banner: pixel logotype only, two-tone, ANSI half-blocks + preview."""
from PIL import Image, ImageDraw

OUT_ANSI, OUT_PNG = "themes/banner.ansi", "themes/banner-preview.png"

GLYPHS = {
 "P": ["11110","10001","10001","11110","10000","10000","10000"],
 "O": ["01110","10001","10001","10001","10001","10001","01110"],
 "C": ["01110","10001","10000","10000","10000","10001","01110"],
 "R": ["11110","10001","10001","11110","10100","10010","10001"],
 "A": ["01110","10001","10001","11111","10001","10001","10001"],
 "E": ["11111","10000","10000","11110","10000","10000","11111"],
 " ": ["00000"]*7,
}
TEXT, TS = "POC RACER", 2
TOP, BOT, BG = (255, 30, 60), (163, 18, 43), (16, 16, 22)

tw = sum(len(GLYPHS[c][0]) + 1 for c in TEXT) * TS - TS
th = 7 * TS
CW = tw + 8
canvas = Image.new("RGB", (CW, th + 6), BG)
d = ImageDraw.Draw(canvas)
x = 4
for c in TEXT:
    g = GLYPHS[c]
    for ry, row in enumerate(g):
        col = TOP if ry < 4 else BOT
        for rx, v in enumerate(row):
            if v == "1":
                d.rectangle([x + rx*TS, 3 + ry*TS, x + rx*TS + TS - 1, 3 + ry*TS + TS - 1], fill=col)
    x += (len(g[0]) + 1) * TS

cw, chh = canvas.size
chh += chh % 2
canvas = canvas.resize((cw, chh))
px = canvas.load()
lines = []
for y in range(0, chh, 2):
    r = []
    for xx in range(cw):
        r1, g1, b1 = px[xx, y]; r2, g2, b2 = px[xx, y+1]
        r.append(f"\x1b[38;2;{r1};{g1};{b1}m\x1b[48;2;{r2};{g2};{b2}m▀")
    lines.append("".join(r) + "\x1b[0m")
open(OUT_ANSI, "w").write("\n".join(lines) + "\n")
canvas.resize((cw*6, chh*6), Image.NEAREST).save(OUT_PNG)
print(f"{OUT_ANSI}: {cw}x{chh//2} cells; preview: {OUT_PNG}")
