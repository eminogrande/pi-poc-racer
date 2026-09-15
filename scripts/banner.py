#!/usr/bin/env python3
"""POC RACER banner: blue race queen | red testarossa | anime queen, above pixel logotype."""
from PIL import Image, ImageEnhance, ImageDraw

GIRL1 = "/var/folders/_q/02r_1y0n34960z0ghmm0kbvh0000gn/T/pi-clipboard-4d1de244-527b-4f0d-8f0a-14a4bb22ec42.png"  # anime, right
GIRL2 = "/var/folders/_q/02r_1y0n34960z0ghmm0kbvh0000gn/T/pi-clipboard-ed5231f2-abcd-4312-9dd4-f03349607e89.png"  # blue, left
CAR = "/var/folders/_q/02r_1y0n34960z0ghmm0kbvh0000gn/T/pi-clipboard-ef22f713-8ac3-4f93-a585-8ad17e251c6d.png"
OUT_ANSI, OUT_PNG = "themes/banner.ansi", "themes/banner-preview.png"
BG = (16, 16, 22)

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
TOP, BOT = (255, 30, 60), (163, 18, 43)

def load_rgb(src):
    img = Image.open(src)
    if "A" in img.getbands():
        img = Image.alpha_composite(Image.new("RGBA", img.size, (255,)*4), img.convert("RGBA"))
    return img.convert("RGB")

def fit(img, h):
    w = int(h * img.size[0] / img.size[1])
    return img.resize((w, h), Image.LANCZOS)

def flood(img, match):
    """Key border-connected pixels where match(px) is True -> BG."""
    w, h = img.size
    px = img.load()
    seen, stack = set(), [(x, y) for x in range(w) for y in (0, h-1)] + [(x, y) for y in range(h) for x in (0, w-1)]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h): continue
        seen.add((x, y))
        if match(px[x, y]):
            px[x, y] = BG
            stack += [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    return img

# anime queen: white bg -> flood-key near-white
g1 = fit(ImageEnhance.Color(load_rgb(GIRL1)).enhance(1.25), 72)
g1 = flood(g1, lambda p: p[0] > 225 and p[1] > 225 and p[2] > 225).quantize(32).convert("RGB")

# blue queen: dark garage bg -> global dark-threshold key
g2 = fit(ImageEnhance.Brightness(load_rgb(GIRL2)).enhance(1.35), 72)
px = g2.load()
for y in range(g2.size[1]):
    for x in range(g2.size[0]):
        if sum(px[x, y]) < 110: px[x, y] = BG
g2 = g2.quantize(32).convert("RGB")

# car: gray studio bg -> flood-key grayish pixels
car = fit(ImageEnhance.Color(load_rgb(CAR)).enhance(1.2), 64)
car = flood(car, lambda p: max(p) - min(p) < 28 and p[0] > 40).quantize(32).convert("RGB")

GAP = 8
CW = g2.size[0] + car.size[0] + g1.size[0] + GAP * 4
scene_h = 72
tw = sum(len(GLYPHS[c][0]) + 1 for c in TEXT) * TS - TS
CW = max(CW, tw + 8)
CH = scene_h + 7 * TS + 9
canvas = Image.new("RGB", (CW, CH), BG)
x = GAP
for part in (g2, car, g1):
    canvas.paste(part, (x, scene_h - part.size[1] + (72 - part.size[1]) // 2))
    x += part.size[0] + GAP
d = ImageDraw.Draw(canvas)
x = (CW - tw) // 2
for c in TEXT:
    g = GLYPHS[c]
    for ry, row in enumerate(g):
        col = TOP if ry < 4 else BOT
        for rx, v in enumerate(row):
            if v == "1":
                d.rectangle([x + rx*TS, scene_h + 5 + ry*TS, x + rx*TS + TS - 1, scene_h + 5 + ry*TS + TS - 1], fill=col)
    x += (len(g[0]) + 1) * TS

cw, chh = canvas.size
chh += chh % 2
canvas = canvas.resize((cw, chh))
px = canvas.load()
lines = []
for y in range(0, chh, 2):
    r = []
    for xx in range(cw):
        r1, gg1, b1 = px[xx, y]; r2, gg2, b2 = px[xx, y+1]
        r.append(f"\x1b[38;2;{r1};{gg1};{b1}m\x1b[48;2;{r2};{gg2};{b2}m▀")
    lines.append("".join(r) + "\x1b[0m")
open(OUT_ANSI, "w").write("\n".join(lines) + "\n")
canvas.resize((cw*6, chh*6), Image.NEAREST).save(OUT_PNG)
print(f"{OUT_ANSI}: {cw}x{chh//2} cells; preview: {OUT_PNG}")
