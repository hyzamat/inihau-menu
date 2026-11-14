"""
Builds the "ORDER NOW" QR poster (scan -> digital menu -> order on WhatsApp):

  qr/order-now/eastern-special-inihaw-order-now-A4.pdf
  qr/order-now/eastern-special-inihaw-order-now-A5.pdf     (same design, scaled to A5)
  qr/order-now/eastern-special-inihaw-order-now.png        (for WhatsApp / Instagram / screens)
  qr/order-now/preview.webp                                (for the /qr/ page)

Phone, address and order types come from assets/js/menu-data.js. Run from the project root:
    python tools/build_order_poster.py
Needs Google Chrome or Microsoft Edge, Node.js, and: pip install qrcode pymupdf pillow zxing-cpp
"""
import html as H
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_qr_poster import BROWSERS, SHOWN_URL, URL, font_face, img, qr_svg  # noqa: E402
from build_visiting_card import ICONS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "qr", "order-now")
NAME = "eastern-special-inihaw-order-now"
PW, PH = 210, 297                                    # designed on A4 (mm); A5 = same layout at 1/sqrt(2)
SIZES = {"A4": (210, 297), "A5": (148, 210)}
e = H.escape

STEP_ICON = {
    "scan": "M9.5 6.5v3h-3v-3h3M11 5H5v6h6V5zm-1.5 9.5v3h-3v-3h3M11 13H5v6h6v-6zm6.5-6.5v3h-3v-3h3M19 5h-6v6h6V5zm-6 8h1.5v1.5H13V13zm1.5 1.5H16V16h-1.5v-1.5zM16 13h1.5v1.5H16V13zm-3 3h1.5v1.5H13V16zm1.5 1.5H16V19h-1.5v-1.5zM16 16h1.5v1.5H16V16zm1.5-1.5H19V16h-1.5v-1.5zm0 3H19V19h-1.5v-1.5zM22 7h-2V4h-3V2h5v5zm0 15v-5h-2v3h-3v2h5zM2 22h5v-2H4v-3H2v5zM2 2v5h2V4h3V2H2z",
    "add": "M11 9h2V6h3V4h-3V1h-2v3H8v2h3v3zm-4 9c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zm10 0c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2zm-9.83-3.25.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.86-7.01L19.42 4h-.01l-1.1 2-2.76 5H8.53l-.13-.27L6.16 6l-.95-2-.94-2H1v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.13 0-.25-.11-.25-.25z",
}
DOODLE = ("<g id='dd' fill='none' stroke='#fff' stroke-opacity='.07' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'>"
          "<circle cx='32' cy='34' r='15'/><circle cx='32' cy='34' r='9'/>"
          "<path d='M104 18c10 4 14 16 8 26s-20 10-24 2 6-26 16-28z M96 44l14-22'/>"
          "<path d='M128 92v34 M122 92v10a6 6 0 0 0 12 0V92'/>"
          "<path d='M20 104c8-6 22-6 30 0 M22 112h26 M24 104l4-14 M46 104l-4-14'/>"
          "<path d='M70 140c6-10 18-12 26-4 M84 128c2-6 6-8 10-8'/></g>")


def restaurant():
    js = "global.window={};require(process.argv[1]);process.stdout.write(JSON.stringify(window.MENU.restaurant))"
    out = subprocess.run(["node", "-e", js, os.path.join(ROOT, "assets", "js", "menu-data.js")],
                         capture_output=True, text=True, encoding="utf-8", check=True)
    return json.loads(out.stdout)


def pretty_phone(p):
    d = "".join(ch for ch in p if ch.isdigit())
    return f"{d[:3]} {d[3:6]} {d[6:]}" if len(d) == 10 else p


def svg(path):
    return f'<svg viewBox="0 0 24 24"><path d="{path}"/></svg>'


def icon(name):
    return f'<svg viewBox="0 0 24 24">{ICONS[name]}</svg>'


def doodles(w, h, tile=40):
    k = tile / 160
    uses = "".join(f'<use href="#dd" transform="translate({x * tile} {y * tile}) scale({k})"/>'
                   for y in range(int(h // tile) + 1) for x in range(int(w // tile) + 1))
    return f'<svg class="pat" viewBox="0 0 {w} {h}" style="width:{w}mm;height:{h}mm"><defs>{DOODLE}</defs>{uses}</svg>'


def page(R):
    phone = pretty_phone(R["phone"])
    addr = R["address"].replace(" - ", " · ")
    types = " · ".join(R.get("orderTypes") or ["Pickup", "Delivery"])
    wordmark = open(os.path.join(ROOT, "assets", "img", "wordmark.svg"), encoding="utf-8").read()
    dishes = [  # slug, left, top, size (mm)
        ("bulalo", -15, 6, 54), ("chicken-tikka", 171, 10, 52),
        ("halo-halo", -9, 66, 36), ("chicken-inasal", 182, 70, 36),
    ]
    circ = "".join(f'<div class="dish" style="left:{x}mm;top:{y}mm;width:{d}mm;height:{d}mm"><img src="{img(s)}"></div>'
                   for s, x, y, d in dishes)
    steps = [("scan", "Scan", "the QR code"), ("add", "Add", "your favourite dishes"), ("wa", "Send", "your order on WhatsApp")]
    steps_html = '<i class="arr"></i>'.join(
        f'<div class="st"><span class="num">{i}</span><span class="sic">{icon("wa") if k == "wa" else svg(STEP_ICON[k])}</span>'
        f'<b>{t}</b><small>{e(s)}</small></div>' for i, (k, t, s) in enumerate(steps, 1))
    return f"""<div class="page">
  <div class="band">{doodles(PW, 118)}</div>
  <svg class="wave" viewBox="0 0 210 16" preserveAspectRatio="none"><path d="M0 7 C 34 16, 70 0, 105 7 S 176 15, 210 5 V16 H0 Z" fill="#F7F1EA"/></svg>
  {circ}
  <p class="kick"><span>FILIPINO GRILL · INDIAN · INDONESIAN</span></p>
  <div class="wm">{wordmark}</div>
  <div class="card">
    <p class="wa-pill">{icon("wa")}ORDER ON WHATSAPP</p>
    <h2 class="order">ORDER NOW</h2>
    <p class="types">{e(types)}</p>
    <div class="qrbox">
      <span class="br tl"></span><span class="br tr"></span><span class="br bl"></span><span class="br br2"></span>
      {qr_svg()}
    </div>
    <p class="scan">Point your phone camera here</p>
    <span class="url">{icon("web")}{SHOWN_URL}</span>
  </div>
  <div class="steps">{steps_html}</div>
  <div class="foot">
    <span>{icon("pin")}{e(addr)}</span><i></i>
    <span>{icon("phone")}{e(phone)}</span><i></i>
    <span class="w">{icon("wa")}{e(phone)}</span>
  </div>
</div>"""


CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: #F7F1EA; }
body { -webkit-print-color-adjust: exact; print-color-adjust: exact; font-family: Poppins, sans-serif; color: #1E1611; }
.page { position: relative; width: 210mm; height: 297mm; overflow: hidden; background: #F7F1EA; zoom: ZOOM_; }
.pat { position: absolute; left: 0; top: 0; }
.band { position: absolute; left: 0; top: 0; width: 210mm; height: 118mm; overflow: hidden;
  background: radial-gradient(140mm 70mm at 50% 100%, rgba(255,110,20,.40), transparent 70%),
              radial-gradient(110mm 60mm at 50% 0%, rgba(255,138,31,.14), transparent 70%),
              linear-gradient(180deg, #120D0A 0%, #1E1611 55%, #2A1C12 100%); }
.wave { position: absolute; left: 0; top: 104mm; width: 210mm; height: 16mm; }
.dish { position: absolute; border-radius: 50%; overflow: hidden; background: #EFE8DA;
  border: 2mm solid #fff; box-shadow: 0 2.5mm 6mm rgba(0,0,0,.4); }
.dish img { width: 100%; height: 100%; object-fit: cover; display: block; transform: scale(1.3); }
.kick { position: absolute; top: 12mm; left: 0; right: 0; text-align: center; }
.kick span { display: inline-block; font: 700 8.6pt Poppins; letter-spacing: .3em; color: #FFBF4D;
  background: rgba(255,138,31,.18); padding: 1.8mm 5mm 1.8mm 6mm; border-radius: 10mm; }
.wm { position: absolute; left: 50%; top: 21mm; width: 98mm; transform: translateX(-50%); }
.wm svg { width: 100%; height: auto; display: block; filter: drop-shadow(0 1mm 0 rgba(0,0,0,.35)); }
.card { position: absolute; left: 24mm; right: 24mm; top: 80mm; text-align: center;
  background: #fff; border-radius: 9mm; padding: 7.5mm 0 6.5mm;
  box-shadow: 0 4mm 12mm rgba(0,0,0,.30), 0 0 0 .6mm rgba(255,138,31,.45); }
.wa-pill { display: inline-flex; align-items: center; gap: 2mm; font: 700 9pt Poppins; letter-spacing: .16em;
  color: #fff; background: #25D366; padding: 1.8mm 5mm 1.8mm 3.6mm; border-radius: 10mm; }
.wa-pill svg { width: 5mm; height: 5mm; fill: #fff; }
.order { font: 700 54pt/1 Fredoka; letter-spacing: .04em; color: #E8262B; margin-top: 3mm;
  text-shadow: 0 1.2mm 0 rgba(232,38,43,.16); }
.types { font: 600 11pt Poppins; color: #7A6656; margin-top: 1mm; letter-spacing: .02em; }
.qrbox { position: relative; width: 86mm; height: 86mm; margin: 4mm auto 0; padding: 8.5mm; }
.qrbox svg { width: 100%; height: 100%; display: block; }
.br { position: absolute; width: 12mm; height: 12mm; border: 1.8mm solid #FF8A1F; }
.br.tl { left: 0; top: 0; border-right: 0; border-bottom: 0; border-top-left-radius: 5mm; }
.br.tr { right: 0; top: 0; border-left: 0; border-bottom: 0; border-top-right-radius: 5mm; }
.br.bl { left: 0; bottom: 0; border-right: 0; border-top: 0; border-bottom-left-radius: 5mm; }
.br.br2 { right: 0; bottom: 0; border-left: 0; border-top: 0; border-bottom-right-radius: 5mm; }
.scan { font: 500 9.5pt Poppins; color: #7A6656; margin-top: 2.5mm; }
.url { display: inline-flex; align-items: center; gap: 2mm; margin-top: 2.5mm;
  font: 600 11pt Poppins; color: #1E1611; background: #FDE6CC; padding: 1.8mm 5mm; border-radius: 10mm; }
.url svg { width: 4.4mm; height: 4.4mm; fill: #FF8A1F; }
.steps { position: absolute; left: 14mm; right: 14mm; top: 249mm; display: flex; align-items: flex-start; justify-content: center; }
.st { position: relative; width: 52mm; text-align: center; }
.sic { display: grid; place-items: center; width: 15mm; height: 15mm; margin: 0 auto; border-radius: 50%;
  background: #fff; box-shadow: 0 1mm 3mm rgba(0,0,0,.18), 0 0 0 .5mm rgba(255,138,31,.55); }
.sic svg { width: 8mm; height: 8mm; fill: #1E1611; }
.st:last-child .sic { background: #25D366; box-shadow: 0 1mm 3mm rgba(7,94,84,.35); }
.st:last-child .sic svg { fill: #fff; }
.num { position: absolute; left: calc(50% + 4.2mm); top: -1.4mm; z-index: 1; width: 6.4mm; height: 6.4mm; border-radius: 50%;
  background: #E8262B; color: #fff; font: 700 9pt/6.4mm Fredoka; border: .6mm solid #fff; box-sizing: content-box; }
.st b { display: block; font: 700 15pt/1 Fredoka; letter-spacing: .03em; margin-top: 2.4mm; color: #1E1611; }
.st small { display: block; font: 500 8.6pt/1.3 Poppins; color: #7A6656; margin-top: .8mm; }
.arr { flex: none; width: 8mm; height: 15mm; position: relative; }
.arr::before { content: ""; position: absolute; left: 1.5mm; top: 5mm; width: 4mm; height: 4mm;
  border-top: 1.2mm solid #FF8A1F; border-right: 1.2mm solid #FF8A1F; transform: rotate(45deg); border-radius: .5mm; }
.foot { position: absolute; left: 0; right: 0; bottom: 0; height: 17mm; background: #1E1611; color: #fff;
  border-top: 1mm solid #E8262B;
  display: flex; align-items: center; justify-content: center; gap: 4.5mm; font: 600 9.6pt Poppins; }
.foot span { display: inline-flex; align-items: center; gap: 1.8mm; white-space: nowrap; }
.foot svg { width: 4.4mm; height: 4.4mm; fill: #FF8A1F; }
.foot span.w svg { fill: #25D366; }
.foot i { width: .35mm; height: 6.5mm; background: rgba(255,255,255,.3); }
"""


def document(R, size):
    w, h = SIZES[size]
    fonts = "".join([font_face("Fredoka", "Fredoka.ttf", "300 700"),
                     font_face("Poppins", "Poppins-Medium.ttf", 500),
                     font_face("Poppins", "Poppins-SemiBold.ttf", 600),
                     font_face("Poppins", "Poppins-Bold.ttf", 700)])
    css = CSS.replace("ZOOM_", f"{w / PW:.5f}")
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{fonts}
@page {{ size: {w}mm {h}mm; margin: 0; }}{css}</style></head><body>{page(R)}</body></html>"""


def chrome_pdf(browser, html_text, pdf, tag):
    tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"_order_poster_{tag}.html")
    open(tmp, "w", encoding="utf-8").write(html_text)
    if os.path.exists(pdf):
        os.remove(pdf)
    try:
        subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--run-all-compositor-stages-before-draw", "--virtual-time-budget=8000",
                        "--allow-file-access-from-files", "--no-first-run", "--no-default-browser-check",
                        f"--user-data-dir={os.path.join(tempfile.gettempdir(), 'ei-order-poster-profile')}",
                        f"--print-to-pdf={pdf}", "file:///" + tmp.replace("\\", "/")],
                       check=True, capture_output=True, timeout=120)
    finally:
        if "--keep-html" not in sys.argv and os.path.exists(tmp):
            os.remove(tmp)
    if not os.path.exists(pdf):
        sys.exit(f"Browser did not produce {pdf}")


def main():
    browser = next((b for b in BROWSERS if os.path.exists(b)), None)
    if not browser:
        sys.exit("Google Chrome or Microsoft Edge is required.")
    R = restaurant()
    os.makedirs(OUT, exist_ok=True)
    import pymupdf
    import zxingcpp
    from PIL import Image
    ok = True
    for size in SIZES:
        pdf = os.path.join(OUT, f"{NAME}-{size}.pdf")
        chrome_pdf(browser, document(R, size), pdf, size)
        d = pymupdf.open(pdf)
        mm = [round(v / 72 * 25.4, 1) for v in d[0].rect[2:]]
        good = len(d) == 1
        print(f"{size}: {len(d)} page(s), {mm[0]} x {mm[1]} mm, {os.path.getsize(pdf) // 1024} KB")
        for dpi in (300, 150, 72):
            pix = d[0].get_pixmap(dpi=dpi)
            found = [r.text for r in zxingcpp.read_barcodes(Image.frombytes("RGB", (pix.w, pix.h), pix.samples))]
            good &= found == [URL]
            print(f"   scan @ {dpi:3d} dpi -> {found}")
        ok &= good
        if size == "A4":
            pix = d[0].get_pixmap(dpi=150)                       # 1240 x 1754
            im = Image.frombytes("RGB", (pix.w, pix.h), pix.samples)
            im.save(os.path.join(OUT, f"{NAME}.png"), optimize=True)
            im.resize((900, round(im.height * 900 / im.width)), Image.LANCZOS).save(
                os.path.join(OUT, "preview.webp"), "WEBP", quality=82, method=6)
    print("ALL OK" if ok else "CHECK FAILED")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
