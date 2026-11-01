"""Draws an original ZNexora Tech graphic (1200 x 630) for every post and category page.

Each content type has its own visual motif in the logo's colors:
  news                     broadcast rings
  weekly-recap             a 7-day grid of glowing squares
  exploited-vulnerabilities the CVSS score and a severity bar
  theory                   a network of connected nodes
  practical                a terminal window
These images also become the preview picture when a post is shared on social media.
"""
import hashlib
import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from common import ROOT

W, H = 1200, 630
NAVY = (4, 10, 31)
NAVY_2 = (8, 22, 58)
CYAN = (34, 199, 242)
ELECTRIC = (31, 107, 255)
SILVER = (214, 222, 235)
MUTED = (150, 166, 196)
SEVERITY = {"critical": (255, 77, 94), "high": (255, 154, 61), "medium": (240, 200, 70),
            "low": (90, 210, 140), "unscored": (150, 166, 196)}
LABEL = {"news": "LATEST NEWS", "weekly-recap": "WEEKLY RECAP", "exploited-vulnerabilities": "EXPLOITED VULNERABILITY",
         "theory": "ARTICLE", "practical": "TRAINING", "courses": "COURSE"}
FONT_FILE = ROOT / "brand" / "fonts" / "Archivo.ttf"
LOGO_FILE = ROOT / "assets" / "logo.png"
_logo_cache = {}


def font(size, weight=800, width=85):
    f = ImageFont.truetype(str(FONT_FILE), size)
    try:
        f.set_variation_by_axes([weight, width])
    except Exception:
        pass  # older systems: fall back to the default style
    return f


def rng_for(key):
    return random.Random(int(hashlib.sha1(key.encode()).hexdigest()[:8], 16))


def background(accent):
    img = Image.new("RGB", (W, H), NAVY)
    grad = Image.linear_gradient("L").resize((W, H))  # smooth top-to-bottom shading
    img = Image.composite(Image.new("RGB", (W, H), NAVY_2), img, grad.point(lambda v: int(v * 0.8)))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((620, -120, 1360, 620), fill=accent + (95,))
    ImageDraw.Draw(glow).ellipse((-260, 380, 420, 900), fill=ELECTRIC + (60,))
    img = img.convert("RGBA")
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    return img


def pixels(layer, r, x0, y0, color, count=16):
    """The scattered squares from the logo."""
    d = ImageDraw.Draw(layer)
    for _ in range(count):
        s = r.choice([10, 14, 18, 22])
        x, y = x0 + r.randint(0, 220), y0 + r.randint(0, 120)
        d.rectangle((x, y, x + s, y + s), fill=(color if r.random() > .3 else SILVER) + (r.randint(90, 220),))


def motif_news(layer, r, accent):
    d = ImageDraw.Draw(layer)
    cx, cy = 1080, 330
    for i, rad in enumerate(range(60, 520, 62)):
        d.arc((cx - rad, cy - rad, cx + rad, cy + rad), 120, 240, fill=accent + (max(30, 170 - i * 20),), width=6)
    d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=accent + (230,))


def motif_recap(layer, r, accent):
    d = ImageDraw.Draw(layer)
    x0, y0, s, g = 760, 150, 44, 14
    for row in range(5):
        for col in range(7):
            x, y = x0 + col * (s + g), y0 + row * (s + g)
            lit = r.random() < 0.45
            d.rounded_rectangle((x, y, x + s, y + s), 6, fill=(accent + (200,)) if lit else (SILVER + (28,)),
                                outline=SILVER + (60,), width=1)


def motif_vuln(layer, r, accent, score):
    d = ImageDraw.Draw(layer)
    text = str(score) if score else "?"
    f = font(230, 900, 70)
    d.text((1140, 300), text, font=f, fill=accent + (235,), anchor="rm")
    d.text((1140, 405), "CVSS", font=font(34, 700, 110), fill=SILVER + (190,), anchor="rm")
    d.rounded_rectangle((760, 450, 1140, 466), 8, fill=SILVER + (40,))
    try:
        frac = max(0.0, min(1.0, float(score) / 10))
    except (TypeError, ValueError):
        frac = 0.0
    if frac:
        d.rounded_rectangle((760, 450, 760 + int(380 * frac), 466), 8, fill=accent + (255,))


def motif_theory(layer, r, accent):
    d = ImageDraw.Draw(layer)
    nodes = [(r.randint(720, 1160), r.randint(70, 560)) for _ in range(13)]
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            if math.dist(a, b) < 230:
                d.line((a, b), fill=SILVER + (70,), width=2)
    for x, y in nodes:
        rad = r.choice([7, 10, 14])
        d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=accent + (220,))


def motif_practical(layer, r, accent):
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = 740, 140, 1150, 470
    d.rounded_rectangle((x0, y0, x1, y1), 16, fill=(3, 8, 24, 225), outline=accent + (160,), width=2)
    d.rectangle((x0 + 2, y0 + 2, x1 - 2, y0 + 40), fill=SILVER + (25,))
    for i, c in enumerate([(255, 95, 87), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((x0 + 18 + i * 26, y0 + 13, x0 + 32 + i * 26, y0 + 27), fill=c + (230,))
    mono = font(30, 600, 100)
    for i in range(4):
        y = y0 + 70 + i * 52
        d.text((x0 + 26, y), "$", font=mono, fill=accent + (230,))
        d.rounded_rectangle((x0 + 60, y + 10, x0 + 60 + r.randint(110, 290), y + 26), 6, fill=SILVER + (90,))
    d.text((x0 + 26, y0 + 70 + 4 * 52), ">_", font=font(34, 800, 100), fill=accent + (255,))


def motif_course(layer, r, accent):
    """Course modules with progress: a lesson plan."""
    d = ImageDraw.Draw(layer)
    x0, y0 = 760, 150
    done = r.randint(1, 3)
    for i in range(4):
        y = y0 + i * 82
        d.rounded_rectangle((x0, y, 1150, y + 62), 14, fill=(3, 8, 24, 210), outline=accent + (120,), width=2)
        cx, cy = x0 + 34, y + 31
        if i < done:
            d.ellipse((cx - 15, cy - 15, cx + 15, cy + 15), fill=accent + (255,))
            d.line((cx - 7, cy, cx - 2, cy + 6, cx + 8, cy - 6), fill=(255, 255, 255, 255), width=4)
        else:
            d.ellipse((cx - 15, cy - 15, cx + 15, cy + 15), outline=SILVER + (150,), width=3)
        d.text((x0 + 64, y + 13), f"Module {i + 1}", font=font(26, 700, 100), fill=SILVER + (230,))
        d.rounded_rectangle((x0 + 220, y + 25, 1120, y + 37), 6, fill=SILVER + (40,))
        width = 900 if i < done else (r.randint(0, 600) if i == done else 0)
        if width:
            d.rounded_rectangle((x0 + 220, y + 25, x0 + 220 + int((1120 - x0 - 220) * width / 900), y + 37), 6, fill=accent + (230,))


def wrap(draw, text, fnt, max_w):
    words, lines, line = text.split(), [], ""
    for w in words:
        trial = f"{line} {w}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            line = trial
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def logo(height):
    if height not in _logo_cache:
        lg = Image.open(LOGO_FILE).convert("RGBA")
        _logo_cache[height] = lg.resize((round(lg.width * height / lg.height), height), Image.LANCZOS)
    return _logo_cache[height]


def make_cover(path, title, category, score="", severity="", subtitle="", key=None):
    accent = SEVERITY.get(severity, CYAN) if category == "exploited-vulnerabilities" else CYAN
    if category == "theory":
        accent = (160, 140, 255)
    elif category == "practical":
        accent = (90, 220, 150)
    elif category == "courses":
        accent = (150, 165, 255)
    r = rng_for(key or title)
    img = background(accent)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    {"news": motif_news, "weekly-recap": motif_recap, "theory": motif_theory,
     "practical": motif_practical, "courses": motif_course}.get(category, lambda *a: None)(layer, r, accent)
    if category == "exploited-vulnerabilities":
        motif_vuln(layer, r, accent, score)
    if category != "weekly-recap":
        pixels(layer, r, 900, 24, CYAN, 12)
    # soften the motif so the title always stays readable
    img.alpha_composite(layer)
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shade).rectangle((0, 0, 760, H), fill=NAVY + (120,))
    img.alpha_composite(shade.filter(ImageFilter.GaussianBlur(80)))

    d = ImageDraw.Draw(img)
    if LOGO_FILE.is_file():  # skip the small logo if the file is missing, never crash
        img.alpha_composite(logo(84), (52, 40))
    label = LABEL.get(category, category.upper().replace("-", " "))
    lf = font(24, 750, 110)
    lw = d.textlength(label, font=lf)
    d.rounded_rectangle((60, 170, 60 + lw + 36, 214), 22, outline=accent, width=2)
    d.text((78, 192), label, font=lf, fill=accent, anchor="lm")

    max_w = 640 if category in ("exploited-vulnerabilities", "practical", "courses", "weekly-recap", "theory", "news") else 1000
    for size in (62, 56, 50, 44, 40):
        tf = font(size, 820, 82)
        lines = wrap(d, title, tf, max_w)
        if len(lines) <= 4:
            break
    lines = lines[:4]
    if len(lines) == 4 and d.textlength(lines[3], font=tf) > max_w - 40:
        lines[3] = lines[3].rsplit(" ", 1)[0] + "…"
    y = 240
    for line in lines:
        d.text((60, y), line, font=tf, fill=SILVER)
        y += int(size * 1.12)
    if subtitle:
        d.text((60, min(y + 14, 548)), subtitle, font=font(26, 500, 100), fill=MUTED)
    d.rectangle((60, 590, 220, 594), fill=accent)
    d.text((236, 592), "znexora tech", font=font(22, 700, 120), fill=MUTED, anchor="lm")
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path, "JPEG", quality=84, optimize=True, progressive=True)
