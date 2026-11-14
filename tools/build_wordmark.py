"""
Builds the "EASTERN / SPECIAL / Inihaw" wordmark (as on the printed menu) as vector paths:
    assets/img/wordmark.svg            (standalone file, used by print tools)
    index.html                         (inlined between <!--wordmark--> markers: no font download, instant paint)

Run from the project root:
    python tools/build_wordmark.py
Requires: pip install fonttools
Fonts: tools/fonts/Poppins-Bold.ttf, tools/fonts/Fredoka.ttf (SIL OFL)
"""
import os
import re

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "tools", "fonts")
GREEN, WHITE = "#38B64B", "#FFFFFF"


def load(name, wght=None):
    f = TTFont(os.path.join(FONTS, name))
    if wght and "fvar" in f:
        f = instantiateVariableFont(f, {"wght": wght})
    return f


def line(font, text, size, tracking=0.0):
    """Returns (svg path d, width) for text at font size `size`, baseline at y=0."""
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm
    scale = size / upm
    pen = SVGPathPen(gs)
    x = 0.0
    names = [cmap[ord(ch)] for ch in text]
    for i, gname in enumerate(names):
        tp = TransformPen(pen, (scale, 0, 0, -scale, x, 0))
        gs[gname].draw(tp)
        x += gs[gname].width * scale + (tracking * size if i < len(names) - 1 else 0)
    d = re.sub(r"(\d+\.\d{2})\d+", r"\1", pen.getCommands())
    return d, x


def build():
    poppins = load("Poppins-Bold.ttf")
    fredoka = load("Fredoka.ttf", 700)
    e_d, e_w = line(poppins, "EASTERN", 64, 0.02)
    s_d, s_w = line(poppins, "SPECIAL", 26, 0.32)
    i_d, i_w = line(fredoka, "Inihaw", 150)
    W = max(e_w, s_w, i_w) + 16
    cx = W / 2
    y_e, y_s, y_i = 62, 104, 222
    H = 240
    svg = (
        f'<svg class="wordmark" viewBox="0 0 {W:.0f} {H}" role="img" aria-label="Eastern Special Inihaw" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<path transform="translate({cx - e_w / 2:.1f} {y_e})" d="{e_d}" fill="{GREEN}" stroke="{WHITE}" '
        f'stroke-width="5" stroke-linejoin="round" paint-order="stroke fill"/>'
        f'<path transform="translate({cx - s_w / 2:.1f} {y_s})" d="{s_d}" fill="{WHITE}"/>'
        f'<path transform="translate({cx - i_w / 2:.1f} {y_i})" d="{i_d}" fill="{WHITE}"/>'
        f'</svg>'
    )
    return svg


def main():
    svg = build()
    os.makedirs(os.path.join(ROOT, "assets", "img"), exist_ok=True)
    open(os.path.join(ROOT, "assets", "img", "wordmark.svg"), "w", encoding="utf-8").write(svg)
    idx = os.path.join(ROOT, "index.html")
    html = open(idx, encoding="utf-8").read()
    new = re.sub(r"<!--wordmark-->.*?<!--/wordmark-->", lambda m: f"<!--wordmark-->{svg}<!--/wordmark-->", html, flags=re.S)
    if new != html:
        open(idx, "w", encoding="utf-8").write(new)
    print(f"wordmark: {len(svg) / 1024:.1f} KB", "(inlined in index.html)" if "<!--wordmark-->" in html else "")


if __name__ == "__main__":
    main()
