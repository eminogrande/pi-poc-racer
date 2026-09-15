#!/usr/bin/env python3
"""POC RACER banner: pixelated anime race queen centered above pixel logotype -> ANSI + preview."""
from PIL import Image, ImageEnhance, ImageDraw

SRC = "/var/folders/_q/02r_1y0n34960z0ghmm0kbvh0000gn/T/pi-clipboard-4d1de244-527b-4f0d-8f0a-14a4bb22ec42.png"
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

img = Image.open(SRC)
if "A" in img.getbands():
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    img = Image.alpha_composite(bg, img.convert("RGBA"))
img = img.convert("RGB")
pw, ph = img.size
gh = 72  # girl height in px (= 36 rows)
gw = int(gh * pw / ph)
girl = img.resize((gw, gh), Image.LANCZOS)
girl = ImageEnhance.Color(girl).enhance(1.25)
# flood-key white background from borders -> BG (keeps white suit interior)
px = girl.load()
seen, stack = set(), [(x, y) for x in range(gw) for y in (0, gh-1)] + [(x, y) for y in range(gh) for x in (0, gw-1)]
while stack:
    x, y = stack.pop()
    if (x, y) in seen or not (0 <= x < gw and 0 <= y < gh): continue
    seen.add((x, y))
    r, g, b = px[x, y]
    if r > 225 and g > 225 and b > 225:
        px[x, y] = BG
        stack += [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
girl = girl.quantize(32).convert("RGB")

tw = sum(len(GLYPHS[c][0]) + 1 for c in TEXT) * TS - TS
CW = max(tw + 8, gw + 8)
CH = gh + 7 * TS + 9
canvas = Image.new("RGB", (CW, CH), BG)
canvas.paste(girl, ((CW - gw) // 2, 2))
d = ImageDraw.Draw(canvas)
x = (CW - tw) // 2
for c in TEXT:
    g = GLYPHS[c]
    for ry, row in enumerate(g):
        col = TOP if ry < 4 else BOT
        for rx, v in enumerate(row):
            if v == "1":
                d.rectangle([x + rx*TS, gh + 5 + ry*TS, x + rx*TS + TS - 1, gh + 5 + ry*TS + TS - 1], fill=col)
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
