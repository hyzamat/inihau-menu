"""
Builds the QR code, printable table card and app icons.
(The link-preview picture is built by tools/build_share_image.py.)

Run from the project root:
    python tools/build_assets.py
Requires: pip install pillow "qrcode[pil]"
"""
import os

import qrcode
import qrcode.image.svg
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "https://inihaumenu.hizarc.com/"
IMG_DIR = os.path.join(ROOT, "assets", "img")
QR_DIR = os.path.join(ROOT, "qr")
FONT_DIR = os.path.join(ROOT, "tools", "fonts")

BROWN = (30, 22, 17)        # charcoal (site theme); QR modules use it too
CHAR = (22, 16, 12)
GREEN = (59, 191, 85)
RED = (232, 38, 43)
EMBER = (255, 138, 31)
AMBER = (255, 191, 77)
WHITE = (255, 255, 255)
SLUG = "eastern-special-inihaw"


def fredoka(size, weight="Bold"):
    f = ImageFont.truetype(os.path.join(FONT_DIR, "Fredoka.ttf"), size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def poppins(size, w="Bold"):
    return ImageFont.truetype(os.path.join(FONT_DIR, f"Poppins-{w}.ttf"), size)


def center_text(d, cx, y, text, f, fill, spacing=0, stroke=0, stroke_fill=None):
    w = d.textlength(text, font=f) + spacing * (len(text) - 1)
    x = cx - w / 2
    if spacing:
        for ch in text:
            d.text((x, y), ch, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
            x += d.textlength(ch, font=f) + spacing
    else:
        d.text((x, y), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)


def brand(d, cx, y, scale=1.0):
    """EASTERN (green, white outline) / SPECIAL / Inihaw — like the printed menu."""
    center_text(d, cx, y, "EASTERN", poppins(round(92 * scale)), GREEN, spacing=round(2 * scale),
                stroke=round(5 * scale), stroke_fill=WHITE)
    center_text(d, cx, y + round(120 * scale), "SPECIAL", poppins(round(52 * scale)), WHITE, spacing=round(8 * scale))
    center_text(d, cx, y + round(170 * scale), "Inihaw", fredoka(round(210 * scale)), WHITE)


def ember_glow(im, cy_frac=1.0, strength=0.42):
    """Warm grill glow rising from the bottom (cheap radial gradient)."""
    W, H = im.size
    glow = Image.new("L", (W // 8, H // 8), 0)
    gd = ImageDraw.Draw(glow)
    gw, gh = glow.size
    for r in range(max(gw, gh), 0, -1):
        a = int(255 * strength * (1 - r / max(gw, gh)) ** 2)
        gd.ellipse((gw / 2 - r * 1.2, gh * cy_frac - r * .7, gw / 2 + r * 1.2, gh * cy_frac + r * .7), fill=a)
    glow = glow.resize((W, H), Image.BILINEAR)
    return Image.composite(Image.new("RGB", (W, H), (255, 110, 20)), im, glow)


def make_qr():
    os.makedirs(QR_DIR, exist_ok=True)
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_Q, box_size=40, border=4)
    qr.add_data(URL)
    qr.make(fit=True)
    img = qr.make_image(fill_color=BROWN, back_color="white").convert("RGB")
    img.save(os.path.join(QR_DIR, f"{SLUG}-menu-qr.png"))
    # pure black SVG for professional printing
    svg = qrcode.make(URL, image_factory=qrcode.image.svg.SvgPathImage,
                      error_correction=qrcode.constants.ERROR_CORRECT_Q, border=4)
    svg.save(os.path.join(QR_DIR, f"{SLUG}-menu-qr.svg"))
    return img


def make_card(qr_img):
    # A6 portrait @ 300 dpi
    W, H = 1240, 1748
    card = ember_glow(Image.new("RGB", (W, H), CHAR), 0.62, 0.30)
    d = ImageDraw.Draw(card)
    cx = W // 2
    brand(d, cx, 70, 0.95)

    # QR on white rounded panel
    q = 760
    top = 560
    d.rounded_rectangle((cx - q // 2 - 40, top, cx + q // 2 + 40, top + q + 80), radius=48, fill=WHITE)
    card.paste(qr_img.resize((q, q), Image.NEAREST), (cx - q // 2, top + 40))

    center_text(d, cx, 1442, "SCAN FOR MENU", fredoka(84), AMBER, spacing=4)

    # red address bar like the printed cover
    d.rectangle((0, H - 170, W, H), fill=RED)
    center_text(d, cx, H - 150, "Villagio Mall - Gate #7 - First Floor", poppins(38, "SemiBold"), WHITE)
    center_text(d, cx, H - 92, "Mob.: 0535627615", poppins(38, "SemiBold"), WHITE)
    card.save(os.path.join(QR_DIR, f"{SLUG}-qr-table-card.png"), dpi=(300, 300))
    card.save(os.path.join(QR_DIR, f"{SLUG}-qr-table-card.pdf"), resolution=300)


def make_icons():
    os.makedirs(IMG_DIR, exist_ok=True)
    base = 1024
    im = ember_glow(Image.new("RGB", (base, base), CHAR), 1.05, 0.38)
    d = ImageDraw.Draw(im)
    f = fredoka(560)
    text = "EI"
    bbox = d.textbbox((0, 0), text, font=f)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x, y = (base - w) / 2 - bbox[0], (base - h) / 2 - bbox[1] - 40
    e_w = d.textlength("E", font=f)
    d.text((x, y), "E", font=f, fill=GREEN, stroke_width=14, stroke_fill=WHITE)
    d.text((x + e_w, y), "I", font=f, fill=WHITE)
    d.rounded_rectangle((base / 2 - 210, 800, base / 2 + 210, 836), radius=18, fill=EMBER)
    for size, name in ((192, "icon-192.png"), (512, "icon-512.png"), (180, "apple-touch-icon.png")):
        im.resize((size, size), Image.LANCZOS).save(os.path.join(IMG_DIR, name), optimize=True)


if __name__ == "__main__":
    qr_img = make_qr()
    make_card(qr_img)
    make_icons()
    print("QR ->", URL)
    print("done")
