"""
Builds the printable menu card (booklet) from assets/js/menu-data.js in three sizes:
    A3         297 x 420 mm   (the A4 layout scaled up x1.414 - big wall / counter menu)
    A4         210 x 297 mm
    A5         148 x 210 mm   (single-column layout so text stays readable)

Output (served at /qr/menucard/):
    qr/menucard/eastern-special-inihaw-menu-card-<size>.pdf
    qr/menucard/<size>/page-01.webp ...      previews
    qr/menucard/index.html                    download page

Run from the project root after changing prices or dishes:
    python tools/build_menu_card.py            # all sizes
    python tools/build_menu_card.py A5         # one size
Needs Google Chrome (or Edge) and Node.js; pip install pillow qrcode pymupdf
"""
import html as H
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from string import Template

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_qr_poster import BROWSERS, DOODLES, font_face, qr_svg  # noqa: E402

from PIL import Image  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "qr", "menucard")
IMG_TMP = os.path.join(tempfile.gettempdir(), "ei-menucard-img")
SITE = "inihaumenu.hizarc.com"
ADDRESS = "Villagio Mall · Gate #7 · First Floor"
PHONE = "053 562 7615"

# All sizes in mm / pt.  CONTENT_H is derived: H - (band + gap) - foot - pad
# All sizes in mm / pt.  CONTENT_H is derived: H - (band + gap) - foot - pad
# W/H are the layout canvas; "zoom" scales it onto the paper (A3 = A4 layout x 1.4142).
_A4 = dict(W=210, H=297, side=12, band=15, foot=11, gap=7, pad=12, cols=2, row=24, ph=22, clamp=4, head=18,
           sp_cols=4, sp_rows=3, cb_cols=1, cb_rows=3, free_h=13, cb_li=8.4,
           promo_img=40, feast_w=70, qr_promo=40, promo_h3=19, promo_max=64, cover_bar=18,
           brand_pt=14, sect_pt=7.5, foot_pt=7.8, h2_pt=21, list_px=300, list_src=360, sp_src=540, use_plan=True)
FORMATS = {
    "A3": dict(_A4, label="A3", size="297 × 420 mm", file="eastern-special-inihaw-menu-card-A3.pdf",
               zoom=1.41421, PW=297, PH=420, list_px=440, list_src=540, sp_src=720),
    "A4": dict(_A4, label="A4", size="210 × 297 mm", file="eastern-special-inihaw-menu-card-A4.pdf"),
    "A5": dict(label="A5", size="148 × 210 mm", file="eastern-special-inihaw-menu-card-A5.pdf", W=148, H=210,
               side=9, band=12, foot=9, gap=6, pad=8, cols=1, row=19, ph=17, clamp=2, head=16,
               sp_cols=2, sp_rows=2, cb_cols=1, cb_rows=3, free_h=14, cb_li=6.6,
               promo_img=28, feast_w=46, qr_promo=32, promo_h3=15, promo_max=50, cover_bar=14,
               brand_pt=10.5, sect_pt=6, foot_pt=6.5, h2_pt=18, list_px=240, list_src=360, sp_src=540, use_plan=False),
}
GAP = 2.5          # gap between list rows
AFTER = 5          # space after a category block

# Which categories share an A4 page (chosen so pages fill up nicely); leftover space gets a promo banner.
# Used only when it fits the page size; otherwise categories flow automatically.
PLAN = [
    ["inihaw", "sizzling", "@pitcher"],
    ["masarsang", "butter-garlic"],
    ["favorites", "probinsya", "@combos"],
    ["sabaw", "pancit"],
    ["gulay", "fried"],
    ["almusal", "sweet-sour", "@qr"],
    ["sinangag", "drinks"],
    ["indian", "@combos"],
    ["indonesian", "@pitcher", "@qr"],
]
FILLER_ROTATION = ["pitcher", "combos", "qr"]

e = H.escape


# ------------------------------------------------------------------ data & images
def menu():
    js = "global.window={};require(process.argv[1]);process.stdout.write(JSON.stringify(window.MENU))"
    out = subprocess.run(["node", "-e", js, os.path.join(ROOT, "assets", "js", "menu-data.js")],
                         capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(out.stdout)


def photo(slug, size, px=None):
    """WebP -> JPEG (Chrome keeps JPEG compressed inside the PDF). px = optional downscale (keeps aspect)."""
    os.makedirs(IMG_TMP, exist_ok=True)
    out = os.path.join(IMG_TMP, f"{slug}-{size}-{px or size}.jpg")
    if not os.path.exists(out):
        im = Image.open(os.path.join(ROOT, "assets", "img", "menu", f"{slug}-{size}.webp")).convert("RGB")
        if px and px < im.width:
            im = im.resize((px, round(im.height * px / im.width)), Image.LANCZOS)
        im.save(out, quality=84, optimize=True, progressive=True)
    return "file:///" + out.replace("\\", "/")


def price_html(it, cur):
    if it.get("prices"):
        return " / ".join(str(p["price"]) for p in it["prices"]) + f"<small>{cur}</small>"
    return f'{it["price"]}<small>{cur}</small>'


def sub_html(it):
    if it.get("prices"):
        return " / ".join(p["label"] for p in it["prices"])
    return f'{it["cal"]} kcal' if it.get("cal") not in (None, "") else ""


DOODLE_PATHS = (
    "<circle cx='32' cy='34' r='15'/><circle cx='32' cy='34' r='9'/>"
    "<path d='M104 18c10 4 14 16 8 26s-20 10-24 2 6-26 16-28z M96 44l14-22'/>"
    "<path d='M128 92v34 M122 92v10a6 6 0 0 0 12 0V92'/>"
    "<path d='M20 104c8-6 22-6 30 0 M22 112h26 M24 104l4-14 M46 104l-4-14'/>"
    "<path d='M70 140c6-10 18-12 26-4 M84 128c2-6 6-8 10-8'/>"
    "<path d='M74 78l3 6 6 1-4.5 4 1 6-5.5-3-5.5 3 1-6-4.5-4 6-1z'/>"
)


def doodles_svg(w_mm, h_mm, tile_mm=54):
    """Vector doodle background (CSS background patterns get rasterised at 72 dpi in PDFs)."""
    s = 160 / tile_mm
    uses = "".join(f'<use href="#dd" x="{x * 160}" y="{y * 160}"/>'
                   for y in range(math.ceil(h_mm / tile_mm) + 1) for x in range(math.ceil(w_mm / tile_mm) + 1))
    return (f'<svg class="doodles" viewBox="0 0 {w_mm * s:.1f} {h_mm * s:.1f}" preserveAspectRatio="xMinYMin slice">'
            f'<defs><g id="dd" fill="none" stroke="#fff" stroke-opacity=".14" stroke-width="2.2" '
            f'stroke-linecap="round" stroke-linejoin="round">{DOODLE_PATHS}</g></defs>{uses}</svg>')


# ------------------------------------------------------------------ builder
class Book:
    def __init__(self, F, M):
        self.F, self.M = F, M
        self.cur = M["restaurant"]["currency"]
        self.content_top = F["band"] + F["gap"]
        self.content_h = F["H"] - self.content_top - F["foot"] - F["pad"]
        self.capacity = self.content_h + AFTER
        self.pages = []
        self.fill_i = 0

    # ---- page chrome
    def inner(self, html, section):
        n = len(self.pages) + 1
        self.pages.append(
            f'<section class="page inner"><div class="top"><span class="brand"><b>EASTERN</b> SPECIAL INIHAW</span>'
            f'<span class="sect">{e(section)}</span></div><div class="content">{html}</div>'
            f'<div class="bottom"><span>{ADDRESS} · {PHONE}</span><span class="pn">{n:02d}</span></div></section>')

    def cover_frame(self, inner_html):
        """Cover-style page: artwork is designed on a 210 x 279 mm canvas and scaled to the page."""
        F = self.F
        s = min(F["W"] / 210, (F["H"] - F["cover_bar"]) / 279)
        left = (F["W"] - 210 * s) / 2
        return (f'<section class="page cover">{doodles_svg(F["W"], F["H"])}'
                # CSS zoom (not transform) so print layout really shrinks; zoom also scales "left", hence / s
                f'<div class="cv" style="zoom:{s:.4f};left:{left / s:.2f}mm">{inner_html}</div>'
                f'<div class="cfoot"><span>{ADDRESS}</span><i></i><span>Mob. {PHONE}</span></div></section>')

    def head(self, en, title):
        return (f'<div class="cat-h"><p class="en">{en}</p><h2>{title}</h2><span class="line"></span></div>')

    # ---- pages
    def cover(self):
        circles = [("chicken-inasal", 6, 116, 46), ("pancit-palabok", 160, 126, 46),
                   ("kare-kare", 12, 186, 40), ("halo-halo", 160, 194, 38)]
        small = "".join(f'<div class="dish" style="left:{x}mm;top:{y}mm;width:{d}mm;height:{d}mm">'
                        f'<img src="{photo(s, 540)}"></div>' for s, x, y, d in circles)
        self.pages.append(self.cover_frame(f"""
  <p class="kick"><span>FILIPINO GRILL · INDIAN · INDONESIAN</span></p>
  <h1 class="logo"><span class="e">EASTERN</span><span class="s">SPECIAL</span>Inihaw</h1>
  <p class="menuword"><i></i>MENU<i></i></p>
  <div class="hero"><img src="{photo('bulalo', 720)}"></div>
  {small}
  <div class="scanbox"><div class="q">{qr_svg()}</div>
    <div><b>Scan for our digital menu</b><span>{SITE}</span></div></div>"""))

    def back_cover(self):
        self.pages.append(self.cover_frame(f"""
  <p class="kick"><span>THANK YOU · SALAMAT PO</span></p>
  <h1 class="logo"><span class="e">EASTERN</span><span class="s">SPECIAL</span>Inihaw</h1>
  <div class="backcard"><p class="bk">Scan for our digital menu</p><div class="q">{qr_svg()}</div>
    <span class="url">{SITE}</span><p class="bs">Every dish with photos and prices — share it with family &amp; friends!</p><p class="np">We do not serve pork.</p></div>"""))

    def combos(self):
        F, M, cur = self.F, self.M, self.cur
        per = F["cb_cols"] * F["cb_rows"]
        ch = (self.content_h - F["head"] - F["free_h"] - 4 - (F["cb_rows"] - 1) * 3.5) / F["cb_rows"]
        combos = M["combos"]
        for p in range(0, len(combos), per):
            chunk = combos[p:p + per]
            ih = ch - 4.4
            cards = "".join(f"""<div class="combo" style="height:{ch:.2f}mm"><div class="cimg" style="width:{ih * 4 / 3:.2f}mm;height:{ih:.2f}mm"><img src="{photo(c['img'], 720, 640)}"><span class="serves">{e(c['serves'])}</span></div>
  <div class="cbody"><div class="chead"><h3>{e(c['name'].replace('Family ', ''))}</h3><span class="badge">{c['price']} {cur}</span></div>
  <ul>{''.join(f'<li><span>{e(d["n"])}</span><em>{e(d["q"])}</em></li>' for d in c['dishes'])}</ul>
  <p class="inc"><b>+ Included:</b> {e(", ".join(c['free']))}</p><p class="kc">{c['cal']} kcal</p></div></div>""" for c in chunk)
            title = "Family Combos" + (" <em>(continued)</em>" if p else "")
            rows = math.ceil(len(chunk) / F["cb_cols"])
            used = F["head"] + F["free_h"] + 4 + rows * ch + (rows - 1) * 3.5
            html = (self.head("Sharing feasts for family &amp; friends", title)
                    + f'<div class="free" style="height:{F["free_h"]}mm"><span class="ft">INCLUDED</span><p>Every combo comes with '
                    f'<b>rice, buko pandan, Pepsi, water, fruits, kropek &amp; free sabaw</b> — amounts per combo below.</p></div>'
                    + f'<div class="combos">{cards}</div>')
            html += self.maybe_filler(self.content_h - used - 4)
            self.inner(html, "Family Combos")

    def specials(self, cat):
        F, cur = self.F, self.cur
        per = F["sp_cols"] * F["sp_rows"]
        ch = (self.content_h - F["head"] - (F["sp_rows"] - 1) * 5) / F["sp_rows"]
        items = cat["items"]
        for p in range(0, len(items), per):
            cards = "".join(f"""<div class="sp" style="height:{ch:.2f}mm"><div class="spimg" style="height:{ch - 30:.2f}mm"><img src="{photo(it['img'], F['sp_src'], 450 if F['sp_src'] == 540 else 640)}"><span class="badge">{price_html(it, cur)}</span></div>
  <h3>{e(it['name'])}</h3><p>{e(it['desc'])}</p><span class="kc">{sub_html(it)}</span></div>""" for it in items[p:p + per])
            title = e(cat["name"]) + (" <em>(continued)</em>" if p else "")
            self.inner(self.head(f"{e(cat['en'])} · chef's favourites", title) + f'<div class="specials">{cards}</div>',
                       cat["name"])

    # ---- list pages
    def item(self, it):
        F = self.F
        return f"""<div class="it"><div class="ph"><img src="{photo(it['img'], F['list_src'], F['list_px'])}"></div>
  <div class="tx"><h4>{e(it['name'])}</h4><p>{e(it['desc'])}</p></div>
  <div class="pr"><b>{price_html(it, self.cur)}</b><span>{sub_html(it)}</span></div></div>"""

    def rows(self, n):
        return math.ceil(n / self.F["cols"])

    def block_h(self, rows):
        return self.F["head"] + rows * self.F["row"] + (rows - 1) * GAP + AFTER

    def cat_block(self, cat, items, cont=False):
        r = self.rows(len(items))
        title = e(cat["name"]) + (" <em>(continued)</em>" if cont else "")
        return (self.head(e(cat["en"]), title)
                + f'<div class="items" style="height:{r * self.F["row"] + (r - 1) * GAP}mm">'
                + "".join(self.item(it) for it in items) + "</div>")

    def planned(self, cats):
        by_id = {c["id"]: c for c in cats}
        if sorted(c for pg in PLAN for c in pg if not c.startswith("@")) != sorted(by_id):
            return None
        out = []
        for pg in PLAN:
            blocks, secs, used, fills = [], [], 0.0, []
            for cid in pg:
                if cid.startswith("@"):
                    fills.append(cid[1:])
                    continue
                cat = by_id[cid]
                blocks.append(self.cat_block(cat, cat["items"]))
                secs.append(cat["name"])
                used += self.block_h(self.rows(len(cat["items"])))
            if used > self.capacity:
                return None
            out.append((blocks, secs, self.capacity - used, fills))
        return out

    def greedy(self, cats):
        cols = self.F["cols"]
        out, blocks, used, secs = [], [], 0.0, []

        def flush():
            nonlocal blocks, used, secs
            if blocks:
                out.append((blocks, secs, self.capacity - used, []))
            blocks, used, secs = [], 0.0, []

        for cat in cats:
            items, idx, cont = cat["items"], 0, False
            while idx < len(items):
                fit = int((self.capacity - used - self.F["head"] - AFTER + GAP) // (self.F["row"] + GAP))
                rows_left = self.rows(len(items) - idx)
                if fit < min(2, rows_left):
                    flush()
                    continue
                take = min(fit, rows_left)
                blocks.append(self.cat_block(cat, items[idx: idx + take * cols], cont))
                secs.append(cat["name"])
                used += self.block_h(take)
                idx, cont = idx + take * cols, True
                if idx < len(items):
                    flush()
        flush()
        for pg in out:                      # promo banners wherever a page has room (different ones per page)
            rem = pg[2]
            while rem >= 45 and len(pg[3]) < len(FILLER_ROTATION):
                kind = FILLER_ROTATION[self.fill_i % len(FILLER_ROTATION)]
                self.fill_i += 1
                if kind in pg[3]:
                    continue
                pg[3].append(kind)
                rem -= min(rem - 4, self.F["promo_max"]) + 4
        return out

    def maybe_filler(self, free):
        if free < 45:
            return ""
        kind = FILLER_ROTATION[self.fill_i % len(FILLER_ROTATION)]
        self.fill_i += 1
        return self.filler(kind, free)

    def filler(self, kind, h):
        F, M, cur = self.F, self.M, self.cur
        h = min(h, F["promo_max"])
        if kind == "pitcher":
            items = {it["id"]: it for c in M["categories"] for it in c["items"]}
            pj, it_ = items.get("pineapple-juice"), items.get("iced-tea")
            if not (pj and it_ and pj.get("prices")):
                return ""
            single, pitcher = pj["prices"][0]["price"], pj["prices"][-1]["price"]
            return f"""<div class="promo pitcher" style="height:{h:.1f}mm"><div class="ptx"><span class="pk">PITCHER DEAL</span>
  <h3>Pineapple Juice &amp; Iced Tea</h3><p>Single <b>{single} {cur}</b> &nbsp;·&nbsp; Pitcher <b>{pitcher} {cur}</b> — made for sharing.</p></div>
  <div class="pimgs"><div class="pc"><img src="{photo('pineapple-juice', 540)}"></div><div class="pc"><img src="{photo('iced-tea', 540)}"></div></div></div>"""
        if kind == "combos":
            lo = min(c["price"] for c in M["combos"])
            return f"""<div class="promo combo-ad" style="height:{h:.1f}mm"><div class="ptx"><span class="pk">FOR FAMILY &amp; FRIENDS</span>
  <h3>Family Combos · from {lo} {cur}</h3><p>Feasts for 3 to 10 persons with rice, buko pandan, Pepsi, water, fruits &amp; sabaw included.</p></div>
  <div class="feast"><img src="{photo('combo-2', 720)}"></div></div>"""
        if kind == "qr":
            return f"""<div class="promo qrp" style="height:{h:.1f}mm"><div class="q">{qr_svg()}</div>
  <div class="ptx"><span class="pk">DIGITAL MENU</span><h3>Scan &amp; share with your friends</h3>
  <p>Every dish with photos and prices, right on your phone.</p><span class="url">{SITE}</span></div></div>"""
        return ""

    # ---- whole book
    def build(self):
        cats = self.M["categories"]
        special = next(c for c in cats if c["id"] == "special")
        rest = [c for c in cats if c["id"] != "special"]
        self.cover()
        self.combos()
        self.specials(special)
        pages = self.planned(rest) if self.F["use_plan"] else None
        if pages is None:
            pages = self.greedy(rest)
        for blocks, secs, free, fills in pages:
            extra, rem = "", free
            for k in fills:
                if rem < 40:
                    break
                h = min(rem - 4, self.F["promo_max"])
                extra += self.filler(k, h)
                rem -= h + 4
            self.inner("".join(blocks) + extra, " · ".join(dict.fromkeys(secs)))
        if len(self.pages) % 2:            # even page count for double-sided printing
            self.back_cover()
        return self.html()

    def html(self):
        F = self.F
        css = Template(CSS).substitute(
            W=F["W"], H=F["H"], PW=F.get("PW", F["W"]), PH=F.get("PH", F["H"]), ZOOM=F.get("zoom", 1), side=F["side"], band=F["band"], foot=F["foot"], ctop=self.content_top,
            ch=f"{self.content_h:.2f}", cols=" ".join(["1fr"] * F["cols"]), row=F["row"], ph=F["ph"],
            clamp=F["clamp"], head=F["head"], rh=F["row"] / 2, line_top=F["head"] - 6.5, sp_cols=F["sp_cols"], cb_cols=F["cb_cols"],
            cb_li=F["cb_li"], promo_img=F["promo_img"], feast_w=F["feast_w"], qr_promo=F["qr_promo"],
            promo_h3=F["promo_h3"], cover_bar=F["cover_bar"], brand_pt=F["brand_pt"], sect_pt=F["sect_pt"],
            foot_pt=F["foot_pt"], h2_pt=F["h2_pt"], cfoot_pt=round(10.5 * F["cover_bar"] / 18, 1),
            DOODLES=DOODLES)
        fonts = "".join([font_face("Fredoka", "Fredoka.ttf", "300 700"),
                         font_face("Poppins", "Poppins-Medium.ttf", 500),
                         font_face("Poppins", "Poppins-SemiBold.ttf", 600),
                         font_face("Poppins", "Poppins-Bold.ttf", 700)])
        return (f'<!doctype html><html><head><meta charset="utf-8"><style>{fonts}{css}</style></head>'
                f'<body>{"".join(self.pages)}</body></html>')


CSS = """
@page { size: ${PW}mm ${PH}mm; margin: 0; }
html { zoom: ${ZOOM}; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { -webkit-print-color-adjust: exact; print-color-adjust: exact; font-family: Poppins, sans-serif; color: #3B2110; }
.page { position: relative; width: ${W}mm; height: ${H}mm; overflow: hidden; break-after: page; background: #FBF6EE; }
.page:last-child { break-after: auto; }
img { display: block; width: 100%; height: 100%; object-fit: cover; }
.q svg { width: 100%; height: 100%; display: block; }

/* ---------- cover / back cover (artwork on a 210 x 279 mm canvas, scaled) ---------- */
.doodles { position: absolute; inset: 0; width: 100%; height: 100%; }
.cover { background: radial-gradient(150mm 90mm at 50% 100%, rgba(255,110,20,.30), transparent 70%),
  radial-gradient(130mm 80mm at 50% 0%, rgba(255,138,31,.12), transparent 70%),
  linear-gradient(180deg, #120D0A 0%, #1E1611 55%, #2A1C12 100%); }
.cv { position: absolute; top: 0; width: 210mm; height: 279mm; }
.cover .kick { position: absolute; top: 20mm; left: 0; right: 0; text-align: center; }
.cover .kick span { display: inline-block; font: 700 9pt Poppins; letter-spacing: .34em; color: #FDECD6;
  background: rgba(243,154,43,.2); padding: 2mm 6mm 2mm 7mm; border-radius: 10mm; }
.cover .logo { position: absolute; top: 30mm; left: 0; right: 0; text-align: center; color: #fff;
  font: 700 70pt/.95 Fredoka; text-shadow: 0 1.6mm 0 rgba(0,0,0,.25); }
.cover .logo .e { display: block; font: 700 30pt/1 Poppins; color: #38B64B; letter-spacing: .03em;
  -webkit-text-stroke: .7mm #fff; paint-order: stroke fill; text-shadow: none; }
.cover .logo .s { display: block; font: 700 14pt/1.5 Poppins; letter-spacing: .32em; padding-left: .32em; text-shadow: none; }
.menuword { position: absolute; top: 98mm; left: 0; right: 0; display: flex; align-items: center; justify-content: center;
  gap: 5mm; font: 700 17pt Fredoka; letter-spacing: .5em; color: #F39A2B; padding-left: .5em; }
.menuword i { width: 22mm; height: .7mm; background: #F39A2B; border-radius: 1mm; }
.hero { position: absolute; left: 44mm; top: 111mm; width: 122mm; height: 122mm; border-radius: 50%; overflow: hidden;
  border: 3mm solid #fff; box-shadow: 0 4mm 12mm rgba(0,0,0,.5); }
.dish { position: absolute; border-radius: 50%; overflow: hidden; border: 2mm solid #fff;
  box-shadow: 0 2.5mm 6mm rgba(57,34,20,.35); background: #EFE8DA; }
.dish img { transform: scale(1.3); }
.scanbox { position: absolute; left: 50%; transform: translateX(-50%); top: 240mm; display: flex; align-items: center; gap: 5mm;
  background: #fff; border-radius: 5mm; padding: 3mm 7mm 3mm 3mm; box-shadow: 0 2mm 6mm rgba(57,34,20,.25); white-space: nowrap; }
.scanbox .q { width: 25mm; height: 25mm; padding: 1.5mm; }
.scanbox b { display: block; font: 700 14pt Fredoka; color: #3B2110; }
.scanbox span { font: 600 9pt Poppins; color: #B9620C; }
.backcard { position: absolute; left: 35mm; right: 35mm; top: 112mm; background: #fff; border-radius: 8mm; text-align: center;
  padding: 9mm 10mm 10mm; box-shadow: 0 4mm 12mm rgba(57,34,20,.35); }
.backcard .bk { font: 700 19pt Fredoka; color: #3B2110; }
.backcard .q { width: 86mm; height: 86mm; margin: 6mm auto 5mm; }
.backcard .url { display: inline-block; font: 600 11pt Poppins; background: #FDECD6; padding: 1.5mm 5mm; border-radius: 8mm; }
.backcard .bs { font: 500 10pt/1.45 Poppins; color: #6E5A49; margin-top: 4mm; }
.backcard .np { font: 600 9pt Poppins; color: #23913A; margin-top: 3mm; }
.cfoot { position: absolute; left: 0; right: 0; bottom: 0; height: ${cover_bar}mm; background: #ED1C24; color: #fff;
  display: flex; align-items: center; justify-content: center; gap: 6mm; font: 600 ${cfoot_pt}pt Poppins; }
.cfoot i { width: .4mm; height: 45%; background: rgba(255,255,255,.5); }

/* ---------- inner page chrome ---------- */
.top { position: absolute; top: 0; left: 0; right: 0; height: ${band}mm; padding: 0 ${side}mm; display: flex; align-items: center;
  justify-content: space-between; gap: 4mm; background: url("${DOODLES}") 0 0 / 40mm 40mm, linear-gradient(180deg, #120D0A, #1E1611); }
.top .brand { flex: none; font: 700 ${brand_pt}pt Fredoka; color: #fff; letter-spacing: .06em; }
.top .brand b { color: #38B64B; font-weight: 700; }
.top .sect { font: 600 ${sect_pt}pt Poppins; letter-spacing: .14em; text-transform: uppercase; color: #3B2110;
  background: rgba(255,255,255,.92); padding: 1.2mm 3.5mm; border-radius: 6mm; min-width: 0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.bottom { position: absolute; bottom: 0; left: 0; right: 0; height: ${foot}mm; padding: 0 ${side}mm; background: #1E1611; color: #E9DCCB;
  display: flex; align-items: center; justify-content: space-between; font: 500 ${foot_pt}pt Poppins; }
.bottom .pn { font: 700 11pt Fredoka; color: #F39A2B; }
.bottom { border-top: .8mm solid #ED1C24; }
.inner .content { position: absolute; top: ${ctop}mm; left: ${side}mm; right: ${side}mm; height: ${ch}mm; }

.cat-h { position: relative; height: ${head}mm; padding-top: .5mm; }
.cat-h .en { font: 700 7.4pt Poppins; letter-spacing: .16em; text-transform: uppercase; color: #B9620C; }
.cat-h h2 { font: 700 ${h2_pt}pt/1.1 Fredoka; color: #3B2110; display: inline-block; background: #FBF6EE; padding-right: 4mm;
  position: relative; z-index: 1; }
.cat-h h2 em { font: 500 9pt Poppins; color: #7A6656; font-style: normal; }
.cat-h .line { position: absolute; left: 0; right: 0; top: ${line_top}mm; height: .6mm; background: linear-gradient(90deg, #F39A2B, rgba(243,154,43,.15)); }

/* ---------- list items ---------- */
.items { display: grid; grid-template-columns: ${cols}; grid-auto-rows: ${row}mm; column-gap: 8mm; row-gap: 2.5mm; margin-bottom: 5mm; }
.it { display: flex; align-items: center; gap: 3mm; background: #fff; border-radius: ${rh}mm 4mm 4mm ${rh}mm; padding: 1mm 3mm 1mm 1mm;
  border: .3mm solid #EDE1C8; }
.it .ph { flex: none; width: ${ph}mm; height: ${ph}mm; border-radius: 50%; overflow: hidden; background: #EFE8DA;
  box-shadow: 0 0 0 .8mm #FDECD6; }
.it .ph img { transform: scale(1.22); }
.it .tx { flex: 1; min-width: 0; }
.it h4 { font: 600 11.2pt/1.08 Fredoka; color: #3B2110; }
.it .tx p { font: 500 6.9pt/1.33 Poppins; color: #6E5A49; margin-top: .7mm;
  display: -webkit-box; -webkit-line-clamp: ${clamp}; -webkit-box-orient: vertical; overflow: hidden; }
.it .pr { flex: none; width: 17mm; text-align: right; align-self: stretch; display: flex; flex-direction: column; justify-content: center; }
.it .pr b { font: 700 15pt/1 Fredoka; color: #ED1C24; white-space: nowrap; }
.it .pr b small, .badge small { font: 700 6.5pt Poppins; margin-left: .6mm; }
.it .pr span { font: 500 6.2pt Poppins; color: #8C7867; margin-top: 1.2mm; }

/* ---------- combos ---------- */
.free { display: flex; align-items: center; gap: 3mm; background: #3B2110; color: #F1E6D6; border-radius: 4mm;
  padding: 0 4mm; margin-bottom: 4mm; font: 500 8.2pt/1.35 Poppins; }
.free b { color: #F39A2B; font-weight: 600; }
.ft { flex: none; background: #38B64B; color: #fff; font: 700 9pt Fredoka; letter-spacing: .1em; padding: 1.2mm 2.6mm; border-radius: 2mm; }
.combos { display: grid; grid-template-columns: repeat(${cb_cols}, 1fr); gap: 3.5mm 6mm; margin-bottom: 4mm; }
.combo { display: flex; gap: 3.5mm; background: #fff; border-radius: 4mm; padding: 2.2mm; overflow: hidden;
  box-shadow: 0 .8mm 2.5mm rgba(57,34,20,.14); }
.cimg { flex: none; border-radius: 3mm; overflow: hidden; position: relative; }
.cimg .serves { position: absolute; left: 1.6mm; bottom: 1.6mm; background: rgba(30,16,8,.85); color: #fff; font: 700 7pt Poppins; padding: .8mm 2.4mm; border-radius: 3mm; }
.cbody { flex: 1; min-width: 0; padding-top: .4mm; }
.chead { display: flex; align-items: center; justify-content: space-between; gap: 2mm; }
.chead h3 { font: 700 12.5pt Fredoka; color: #3B2110; white-space: nowrap; }
.badge { background: #ED1C24; color: #fff; font: 700 10pt Fredoka; padding: .8mm 2.4mm; border-radius: 2mm; white-space: nowrap; }
.combo ul { list-style: none; margin-top: 1mm; }
.combo li { font: 600 ${cb_li}pt/1.36 Poppins; color: #4D3A2C; padding-left: 3mm; position: relative; white-space: nowrap; display: flex; justify-content: space-between; gap: 2mm; }
.combo li span { overflow: hidden; text-overflow: ellipsis; }
.combo li em { font-style: normal; color: #8C7867; flex: none; }
.combo .inc { font: 500 calc(${cb_li}pt - 1pt)/1.35 Poppins; color: #6E5A49; margin-top: 1.2mm; }
.combo .inc b { color: #23913A; }
.combo li::before { content: ""; position: absolute; left: .3mm; top: 1.3mm; width: 1.5mm; height: 1.5mm; border-radius: 50%; background: #F39A2B; }
.combo .kc { font: 500 6.4pt Poppins; color: #8C7867; margin-top: .6mm; }

/* ---------- specials ---------- */
.specials { display: grid; grid-template-columns: repeat(${sp_cols}, 1fr); gap: 5mm 4mm; }
.sp { background: #fff; border-radius: 4mm; overflow: hidden; box-shadow: 0 .8mm 2.5mm rgba(57,34,20,.14);
  display: flex; flex-direction: column; }
.spimg { position: relative; flex: none; }
.spimg .badge { position: absolute; right: 2mm; top: 2mm; background: #ED1C24; font-size: 12pt; padding: 1mm 2.4mm;
  box-shadow: 0 1mm 2mm rgba(0,0,0,.25); }
.sp h3 { font: 600 11pt/1.1 Fredoka; color: #3B2110; padding: 2.4mm 2.6mm 0; }
.sp p { font: 500 6.5pt/1.36 Poppins; color: #6E5A49; padding: 1mm 2.6mm 0;
  display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }
.sp .kc { margin-top: auto; padding: 0 2.6mm 2.2mm; font: 600 6.3pt Poppins; color: #B9620C; }

/* ---------- promo banners (fill leftover space) ---------- */
.promo { position: relative; display: flex; align-items: center; gap: 5mm; border-radius: 5mm; overflow: hidden; padding: 0 0 0 7mm;
  box-shadow: 0 1mm 4mm rgba(57,34,20,.2); }
.promo + .promo { margin-top: 4mm; }
.promo .ptx { flex: 1; min-width: 0; }
.promo .pk { display: inline-block; font: 700 6.8pt Poppins; letter-spacing: .2em; padding: 1mm 3mm; border-radius: 5mm; }
.promo h3 { font: 700 ${promo_h3}pt/1.1 Fredoka; margin-top: 2mm; }
.promo p { font: 500 8.2pt/1.45 Poppins; margin-top: 1.5mm; max-width: 110mm; }
.pitcher { background: url("${DOODLES}") 0 0 / 40mm 40mm, linear-gradient(120deg, #F39A2B, #D9740F); color: #fff; }
.pitcher .pk { background: #ED1C24; color: #fff; }
.pitcher h3 { text-shadow: 0 .6mm 0 rgba(57,34,20,.2); }
.pitcher p b { color: #3B2110; font-weight: 700; }
.pimgs { flex: none; display: flex; padding-right: 6mm; }
.pc { width: ${promo_img}mm; height: ${promo_img}mm; border-radius: 50%; overflow: hidden; border: 1.6mm solid #fff; box-shadow: 0 1.5mm 4mm rgba(57,34,20,.35); }
.pc + .pc { margin-left: -9mm; }
.combo-ad { background: #3B2110; color: #F1E6D6; }
.combo-ad .pk { background: #F39A2B; color: #3B2110; }
.combo-ad h3 { color: #F39A2B; }
.combo-ad .feast { flex: none; align-self: stretch; width: ${feast_w}mm; clip-path: ellipse(100% 100% at 100% 50%); }
.qrp { background: #fff; padding-left: 5mm; border-left: 2.5mm solid #F39A2B; }
.qrp .q { flex: none; width: ${qr_promo}mm; height: ${qr_promo}mm; }
.qrp .pk { background: #FDECD6; color: #B9620C; }
.qrp h3 { color: #ED1C24; }
.qrp p { color: #4D3A2C; }
.qrp .url { display: inline-block; margin-top: 2mm; font: 600 8.2pt Poppins; color: #3B2110; background: #FDECD6; padding: 1mm 3.5mm; border-radius: 6mm; }
"""


# ------------------------------------------------------------------ render
def render(key, F, M, browser):
    book = Book(F, M)
    doc_html = book.build()
    n_pages = len(book.pages)
    pdf = os.path.join(OUT_DIR, F["file"])
    tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"_menu_card_build_{key}.html")
    open(tmp, "w", encoding="utf-8").write(doc_html)
    if os.path.exists(pdf):
        os.remove(pdf)
    try:
        subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--run-all-compositor-stages-before-draw", "--virtual-time-budget=15000",
                        "--allow-file-access-from-files", "--no-first-run", "--no-default-browser-check",
                        f"--user-data-dir={os.path.join(tempfile.gettempdir(), 'ei-menucard-profile')}",
                        f"--print-to-pdf={pdf}", "file:///" + tmp.replace("\\", "/")],
                       check=True, capture_output=True, timeout=300)
    finally:
        if "--keep-html" not in sys.argv and os.path.exists(tmp):
            os.remove(tmp)
    if not os.path.exists(pdf):
        sys.exit(f"Browser did not produce the {key} PDF.")

    import pymupdf
    doc = pymupdf.open(pdf)
    size_mm = [round(v / 72 * 25.4, 1) for v in doc[0].rect[2:]]
    print(f"{key:7s} -> {F['file']}  {len(doc)} pages, {size_mm[0]} x {size_mm[1]} mm, {os.path.getsize(pdf) // 1024} KB")
    if len(doc) != n_pages:
        print(f"  WARNING: expected {n_pages} pages, got {len(doc)} (something overflowed)")
    pdir = os.path.join(OUT_DIR, key.lower())
    shutil.rmtree(pdir, ignore_errors=True)
    os.makedirs(pdir)
    for i, pg in enumerate(doc, 1):
        pix = pg.get_pixmap(dpi=round(1000 / (F.get("PW", F["W"]) / 25.4)))  # ~1000 px wide previews
        Image.frombytes("RGB", (pix.w, pix.h), pix.samples).save(
            os.path.join(pdir, f"page-{i:02d}.webp"), "WEBP", quality=80, method=6)
    return dict(key=key, label=F["label"], size=F["size"], file=F["file"], pages=len(doc),
                mb=os.path.getsize(pdf) / 1024 / 1024, ratio=F["H"] / F["W"])


def web_page(results):
    tabs = "".join(
        f'<input type="radio" name="fmt" id="t-{r["key"]}"{" checked" if r["key"] == "A4" else ""}>'
        f'<label for="t-{r["key"]}">{e(r["label"].split(" (")[0])}<small>{e(r["size"])}</small></label>'
        for i, r in enumerate(results))
    downloads = "".join(
        f'<a class="dl" href="{r["file"]}" download><span class="ic">{e(r["key"].upper()[:6])}</span>'
        f'<span><span class="t">{e(r["label"])}</span><br><span class="d">{e(r["size"])} · {r["pages"]} pages · PDF {r["mb"]:.1f} MB</span></span>'
        f'<span class="ar">↓</span></a>' for r in results)
    panels = ""
    for i, r in enumerate(results):
        imgs = "\n".join(
            f'      <img src="{r["key"].lower()}/page-{p:02d}.webp" width="1000" height="{round(1000 * r["ratio"])}" '
            f'alt="{e(r["label"])} page {p}"' + (' loading="lazy"' if (r["key"] != "A4" or p > 1) else "") + ' decoding="async">'
            for p in range(1, r["pages"] + 1))
        panels += (f'\n    <div class="panel" id="p-{r["key"]}"><div class="bar"><a class="btn dark" href="{r["file"]}" download>'
                   f'⬇ Download {e(r["label"].split(" (")[0])} PDF</a><a class="btn ghost" href="{r["file"]}" target="_blank" rel="noopener">'
                   f'Open / Print</a></div>\n{imgs}\n    </div>')
    show = "\n".join(f'  #t-{r["key"]}:checked ~ .panels #p-{r["key"]} {{ display: grid; }}' for r in results)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Eastern Special Inihaw — Menu Card</title>
<meta name="robots" content="noindex">
<meta name="theme-color" content="#16100C">
<link rel="icon" href="../../assets/img/icon-192.png" type="image/png">
<style>
  :root {{ --gold:#FF8A1F; --gold-lt:#FDE6CC; --green:#3BBF55; --brown:#1E1611; --red:#E8262B; --cream:#F7F1EA; --muted:#7A6656; --line:#EAE0D4; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font: 15px/1.45 system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif; color: var(--brown); background: var(--cream); }}
  header {{ background: radial-gradient(70% 60% at 50% 110%, rgba(255,110,20,.35), transparent 70%), linear-gradient(180deg, #120D0A 0%, #1E1611 55%, #2A1C12 100%); color: #fff; text-align: center; padding: max(26px, env(safe-area-inset-top)) 20px 64px; }}
  .kick {{ display: inline-block; font-size: 11px; font-weight: 700; letter-spacing: .18em; color: #FFBF4D; background: rgba(255,138,31,.16); padding: 5px 12px; border-radius: 99px; }}
  h1 .e {{ color: var(--green); -webkit-text-stroke: 1px #fff; paint-order: stroke fill; }}
  h1 {{ font: 900 clamp(34px, 11vw, 52px)/.95 "Arial Rounded MT Bold", ui-rounded, system-ui, sans-serif; text-transform: uppercase; letter-spacing: .03em; margin-top: 10px; text-shadow: 0 3px 0 rgba(57,34,20,.18); }}
  header p {{ margin-top: 8px; font-weight: 600; }}
  main {{ max-width: 760px; margin: -44px auto 0; padding: 0 14px 40px; }}
  .card {{ background: #fff; border-radius: 18px; padding: 14px; box-shadow: 0 14px 30px -16px rgba(57,34,20,.5); }}
  .card h2 {{ margin: 2px 4px 10px; }}
  h2 {{ font-size: 13px; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin: 26px 4px 10px; }}
  .list {{ display: grid; gap: 10px; }}
  .dl {{ display: flex; align-items: center; gap: 14px; text-decoration: none; color: inherit; background: var(--cream); border: 1.5px solid var(--line); border-radius: 14px; padding: 12px 14px; }}
  .dl:first-child {{ background: var(--brown); color: #fff; border-color: var(--brown); }}
  .dl:first-child .d {{ color: #E9DCCB; }}
  .ic {{ flex: none; width: 50px; height: 44px; border-radius: 12px; display: grid; place-items: center; font-weight: 900; font-size: 12px; background: var(--gold-lt); color: var(--brown); }}
  .dl:first-child .ic {{ background: var(--red); color: #fff; }}
  .t {{ font-weight: 800; }} .d {{ font-size: 13px; color: var(--muted); }} .ar {{ margin-left: auto; font-size: 20px; opacity: .6; }}
  .links {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }}
  .btn {{ display: flex; align-items: center; justify-content: center; height: 46px; border-radius: 14px; text-decoration: none; font-weight: 800; font-size: 14px; }}
  .btn.dark {{ background: var(--brown); color: #fff; }}
  .btn.ghost {{ background: #fff; color: var(--brown); border: 1.5px solid var(--line); }}
  .btn.red {{ background: var(--red); color: #fff; }}
  .tabs {{ display: grid; grid-template-columns: repeat({len(results)}, 1fr); gap: 8px; }}
  .tabs > input {{ position: absolute; opacity: 0; pointer-events: none; }}
  .tabs > label {{ text-align: center; padding: 10px 6px; border-radius: 12px; background: #fff; border: 1.5px solid var(--line); font-weight: 800; cursor: pointer; line-height: 1.2; }}
  .tabs > label small {{ display: block; font-size: 11.5px; font-weight: 600; color: var(--muted); margin-top: 2px; }}
  .tabs > input:checked + label {{ background: var(--brown); color: #fff; border-color: var(--brown); }}
  .tabs > input:checked + label small {{ color: #E9DCCB; }}
  .tabs > input:focus-visible + label {{ outline: 3px solid var(--gold); }}
  .panels {{ grid-column: 1 / -1; margin-top: 8px; }}
  .panel {{ display: none; gap: 16px; }}
{show}
  .bar {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
  .panel img {{ display: block; width: 100%; height: auto; border-radius: 6px; background: #EFE8DA; box-shadow: 0 10px 24px -14px rgba(57,34,20,.6); }}
  footer {{ text-align: center; color: var(--muted); font-size: 12.5px; padding: 0 20px 30px; }}
</style>
</head>
<body>
<header>
  <span class="kick">PRINTABLE MENU CARD</span>
  <h1><span class="e">Eastern</span> Special Inihaw</h1>
  <p>Every dish with photo &amp; price · choose your paper size</p>
</header>
<main>
  <div class="card">
    <h2>Download</h2>
    <div class="list">{downloads}</div>
    <div class="links"><a class="btn red" href="../../">Digital menu →</a><a class="btn ghost" href="../">QR code &amp; poster</a></div>
  </div>
  <h2>Preview</h2>
  <div class="tabs">{tabs}
    <div class="panels">{panels}
    </div>
  </div>
</main>
<footer>Print at 100% / "Actual size" on the matching paper size. Prices in Saudi Riyal (SR).</footer>
</body>
</html>
"""


def main():
    keys = [a for a in sys.argv[1:] if not a.startswith("--")] or list(FORMATS)
    M = menu()
    browser = next((b for b in BROWSERS if os.path.exists(b)), None)
    if not browser:
        sys.exit("Google Chrome or Microsoft Edge is required.")
    os.makedirs(OUT_DIR, exist_ok=True)
    for f in os.listdir(OUT_DIR):                      # previews from the old single-size layout
        if f.startswith("page-") and f.endswith(".webp"):
            os.remove(os.path.join(OUT_DIR, f))
    results = [render(k, FORMATS[k], M, browser) for k in keys]
    if len(keys) == len(FORMATS):
        open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8").write(web_page(results))
        print("web page -> qr/menucard/index.html")
    shutil.rmtree(IMG_TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
