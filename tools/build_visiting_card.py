"""
Builds the shop's visiting card (business card), front + back:
    qr/eastern-special-inihaw-visiting-card.pdf          print file: 2 pages, 96 x 56 mm = 90 x 50 mm + 3 mm bleed
    qr/eastern-special-inihaw-visiting-card-front.png    90 x 50 mm @ 600 dpi (for WhatsApp / social media)
    qr/eastern-special-inihaw-visiting-card-back.png
    qr/visiting-card-preview.webp                        both sides, for the /qr/ page

Run from the project root:
    python tools/build_visiting_card.py
Needs Google Chrome (or Edge) and: pip install qrcode pymupdf pillow   (+ zxing-cpp for the scan check)
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_qr_poster import BROWSERS, URL, SHOWN_URL, font_face, qr_svg  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QR_DIR = os.path.join(ROOT, "qr")
SLUG = "eastern-special-inihaw-visiting-card"
PDF = os.path.join(QR_DIR, f"{SLUG}.pdf")

TRIM_W, TRIM_H, BLEED = 90, 50, 3
PAGE_W, PAGE_H = TRIM_W + 2 * BLEED, TRIM_H + 2 * BLEED

ADDRESS_1, ADDRESS_2 = "Villagio Mall · Gate #7", "First Floor"
PHONE = "053 562 7615"
WHATSAPP = "+966 53 562 7615"

ICONS = {
    "pin": '<path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/>',
    "phone": '<path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/>',
    "wa": '<path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38a9.9 9.9 0 0 0 4.74 1.21c5.46 0 9.91-4.45 9.91-9.91S17.5 2 12.04 2zm0 18.15c-1.48 0-2.93-.4-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.2 8.2 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.24-8.24 4.54 0 8.23 3.7 8.23 8.24 0 4.54-3.7 8.24-8.22 8.24zm4.52-6.16c-.25-.12-1.47-.72-1.69-.81-.23-.08-.39-.12-.56.12-.16.25-.64.81-.78.97-.14.17-.29.19-.54.06-.25-.12-1.05-.39-1.99-1.23-.74-.66-1.230-1.47-1.38-1.72-.14-.25-.02-.38.11-.51.11-.11.25-.29.37-.43.13-.15.17-.25.25-.41.08-.17.04-.31-.02-.43-.06-.12-.56-1.34-.76-1.84-.2-.48-.41-.42-.56-.43h-.48c-.17 0-.43.06-.66.31-.22.25-.86.85-.86 2.07 0 1.22.89 2.4 1.01 2.56.12.17 1.75 2.67 4.23 3.74.59.26 1.05.41 1.41.52.59.19 1.13.16 1.56.1.48-.07 1.47-.6 1.67-1.18.21-.58.21-1.07.14-1.18-.06-.11-.22-.17-.47-.29z"/>',
    "web": '<path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm6.9 6h-2.9a15.7 15.7 0 0 0-1.4-3.6A8 8 0 0 1 18.9 8zM12 4c.8 1.2 1.5 2.5 1.9 4h-3.8c.4-1.5 1.1-2.8 1.9-4zM4.3 14a8.2 8.2 0 0 1 0-4h3.4a16.5 16.5 0 0 0 0 4H4.3zm.8 2h2.9c.3 1.3.8 2.5 1.4 3.6A8 8 0 0 1 5.1 16zM8 8H5.1a8 8 0 0 1 4.3-3.6C8.8 5.5 8.3 6.7 8 8zm4 12c-.8-1.2-1.5-2.5-1.9-4h3.8c-.4 1.5-1.1 2.8-1.9 4zm2.3-6H9.7a14.7 14.7 0 0 1 0-4h4.6a14.7 14.7 0 0 1 0 4zm.3 5.6c.6-1.1 1.1-2.3 1.4-3.6h2.9a8 8 0 0 1-4.3 3.6zm1.7-5.6a16.5 16.5 0 0 0 0-4h3.4a8.2 8.2 0 0 1 0 4h-3.4z"/>',
}

DOODLE_PATHS = (
    "<circle cx='32' cy='34' r='15'/><circle cx='32' cy='34' r='9'/>"
    "<path d='M104 18c10 4 14 16 8 26s-20 10-24 2 6-26 16-28z M96 44l14-22'/>"
    "<path d='M128 92v34 M122 92v10a6 6 0 0 0 12 0V92'/>"
    "<path d='M20 104c8-6 22-6 30 0 M22 112h26 M24 104l4-14 M46 104l-4-14'/>"
    "<path d='M70 140c6-10 18-12 26-4 M84 128c2-6 6-8 10-8'/>"
)


def icon(name, cls=""):
    return f'<svg class="ic {cls}" viewBox="0 0 24 24">{ICONS[name]}</svg>'


def doodles():
    tile = 30  # mm
    uses = "".join(f'<use href="#dd" x="{x * 160}" y="{y * 160}"/>' for y in range(3) for x in range(5))
    s = 160 / tile
    return (f'<svg class="doodles" viewBox="0 0 {PAGE_W * s:.1f} {PAGE_H * s:.1f}" preserveAspectRatio="xMinYMin slice">'
            f'<defs><g id="dd" fill="none" stroke="#fff" stroke-opacity=".07" stroke-width="2.2" stroke-linecap="round" '
            f'stroke-linejoin="round">{DOODLE_PATHS}</g></defs>{uses}</svg>')


def html():
    wordmark = open(os.path.join(ROOT, "assets", "img", "wordmark.svg"), encoding="utf-8").read()
    fonts = "".join([font_face("Fredoka", "Fredoka.ttf", "300 700"), font_face("Poppins", "Poppins-Medium.ttf", 500),
                     font_face("Poppins", "Poppins-SemiBold.ttf", 600), font_face("Poppins", "Poppins-Bold.ttf", 700)])
    B = BLEED
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{fonts}
@page {{ size: {PAGE_W}mm {PAGE_H}mm; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; font-family: Poppins, sans-serif; }}
.page {{ position: relative; width: {PAGE_W}mm; height: {PAGE_H}mm; overflow: hidden; break-after: page; color: #F8EFE5;
  background: radial-gradient(70mm 26mm at 50% 104%, rgba(255,110,20,.42), transparent 70%),
              radial-gradient(60mm 22mm at 50% -6%, rgba(255,138,31,.14), transparent 70%),
              linear-gradient(180deg, #120D0A 0%, #1E1611 60%, #2A1C12 100%); }}
.page:last-child {{ break-after: auto; }}
.doodles {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
.trim {{ position: absolute; left: {B}mm; top: {B}mm; width: {TRIM_W}mm; height: {TRIM_H}mm; }}
.ember {{ position: absolute; left: 0; right: 0; bottom: 0; height: .9mm;
  background: linear-gradient(90deg, transparent, #FF8A1F 18%, #FFBF4D 50%, #FF8A1F 82%, transparent); }}

/* front */
.front .wm {{ position: absolute; left: 50%; top: 8.2mm; width: 50mm; transform: translateX(-50%); }}
.front .wm svg {{ width: 100%; height: auto; display: block; filter: drop-shadow(0 .5mm 0 rgba(0,0,0,.35)); }}
.front .tag {{ position: absolute; left: 0; right: 0; top: 36.6mm; text-align: center; font: 700 5.6pt Poppins;
  letter-spacing: .26em; padding-left: .26em; color: #FFBF4D; }}
.front .rule {{ position: absolute; left: 50%; top: 34.4mm; width: 16mm; height: .35mm; transform: translateX(-50%);
  background: linear-gradient(90deg, transparent, #FF8A1F, transparent); }}

/* back */
.back .qr {{ position: absolute; left: 4.5mm; top: 5mm; width: 29mm; height: 36mm; background: #fff; border-radius: 3mm;
  padding: 2.2mm 2.2mm 0; text-align: center; box-shadow: 0 .8mm 2.4mm rgba(0,0,0,.45); }}
.back .qr svg {{ width: 24.6mm; height: 24.6mm; display: block; }}
.back .qr b {{ display: block; margin-top: 1.7mm; font: 700 6.4pt/1 Fredoka; letter-spacing: .06em; color: #1E1611; }}
.back .qr b em {{ font-style: normal; color: #E8262B; }}
.back .qr small {{ display: block; margin-top: .9mm; font: 600 4.3pt Poppins; color: #7A6656; }}
.back .info {{ position: absolute; left: 37.5mm; right: 4mm; top: 5mm; }}
.back .name {{ font: 700 7.6pt/1 Poppins; letter-spacing: .02em; color: #fff; white-space: nowrap; }}
.back .name b {{ color: #3BBF55; }}
.back .name span {{ display: block; margin-top: 1mm; font: 600 4.6pt Poppins; letter-spacing: .14em; color: #FFBF4D; }}
.back ul {{ list-style: none; margin-top: 3.2mm; display: grid; gap: 1.85mm; }}
.back li {{ display: flex; align-items: center; gap: 1.8mm; font: 600 6.3pt/1.2 Poppins; color: #F8EFE5; white-space: nowrap; }}
.back li small {{ display: block; font: 500 5pt/1.2 Poppins; color: #C9B8A6; }}
.ic {{ flex: none; width: 4.4mm; height: 4.4mm; padding: .85mm; border-radius: 50%; fill: #1A0D03; background: #FF8A1F; }}
.ic.wa {{ background: #25D366; fill: #fff; padding: .7mm; }}
.back .bar {{ position: absolute; left: 0; right: 0; bottom: 0; height: {5.2 + B}mm; padding-bottom: {B}mm; background: #E8262B; display: flex;
  align-items: center; justify-content: center; gap: 1.4mm; font: 700 5.5pt Poppins; letter-spacing: .08em; color: #fff; }}
.back .bar svg {{ width: 3mm; height: 3mm; fill: #fff; }}
</style></head><body>

<section class="page front">{doodles()}<div class="trim">
  <div class="wm">{wordmark}</div>
  <span class="rule"></span>
  <p class="tag">FILIPINO GRILL · INDIAN · INDONESIAN</p>
</div><span class="ember"></span></section>

<section class="page back">{doodles()}<div class="trim">
  <div class="qr">{qr_svg()}<b>SCAN <em>FOR</em> MENU</b><small>Order on WhatsApp inside</small></div>
  <div class="info">
    <p class="name"><b>EASTERN</b> SPECIAL INIHAW<span>RESTAURANT</span></p>
    <ul>
      <li>{icon("pin")}<span>{ADDRESS_1}<small>{ADDRESS_2}</small></span></li>
      <li>{icon("phone")}<span>{PHONE}</span></li>
      <li>{icon("wa", "wa")}<span>{WHATSAPP}<small>WhatsApp orders</small></span></li>
      <li>{icon("web")}<span>{SHOWN_URL}</span></li>
    </ul>
  </div>
</div><div class="bar"><svg viewBox="0 0 24 24">{ICONS["wa"]}</svg>ORDER ON WHATSAPP · PICKUP · DELIVERY</div></section>
</body></html>"""


def main():
    browser = next((b for b in BROWSERS if os.path.exists(b)), None)
    if not browser:
        sys.exit("Google Chrome or Microsoft Edge is required to print the PDF.")
    tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_visiting_card_build.html")
    open(tmp, "w", encoding="utf-8").write(html())
    if os.path.exists(PDF):
        os.remove(PDF)
    try:
        subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--run-all-compositor-stages-before-draw", "--virtual-time-budget=8000",
                        "--allow-file-access-from-files", "--no-first-run", "--no-default-browser-check",
                        f"--user-data-dir={os.path.join(tempfile.gettempdir(), 'ei-card-profile')}",
                        f"--print-to-pdf={PDF}", "file:///" + tmp.replace("\\", "/")],
                       check=True, capture_output=True, timeout=120)
    finally:
        if "--keep-html" not in sys.argv and os.path.exists(tmp):
            os.remove(tmp)
    if not os.path.exists(PDF):
        sys.exit("Browser did not produce the PDF.")

    import pymupdf
    from PIL import Image
    doc = pymupdf.open(PDF)
    print("PDF ->", PDF, "|", len(doc), "pages,", [round(v / 72 * 25.4, 1) for v in doc[0].rect[2:]], "mm")
    sides = []
    for i, name in enumerate(("front", "back")):
        pix = doc[i].get_pixmap(dpi=600)
        im = Image.frombytes("RGB", (pix.w, pix.h), pix.samples)
        b = round(BLEED / 25.4 * 600)
        im = im.crop((b, b, im.width - b, im.height - b))            # trimmed 90 x 50 mm
        im.save(os.path.join(QR_DIR, f"{SLUG}-{name}.png"), dpi=(600, 600), optimize=True)
        sides.append(im)
    w = 900
    prev = [s.resize((w, round(w * s.height / s.width)), Image.LANCZOS) for s in sides]
    sheet = Image.new("RGB", (w, prev[0].height * 2 + 30), (247, 241, 234))
    sheet.paste(prev[0], (0, 0)); sheet.paste(prev[1], (0, prev[0].height + 30))
    sheet.save(os.path.join(QR_DIR, "visiting-card-preview.webp"), "WEBP", quality=84, method=6)

    try:  # scan check on the back
        import numpy as np
        import zxingcpp
        for dpi in (600, 300, 150):
            pix = doc[1].get_pixmap(dpi=dpi)
            arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)[:, :, :3]
            got = next((r.text for r in zxingcpp.read_barcodes(arr)), "")
            print(f"scan @ {dpi} dpi -> {got!r} {'OK' if got == URL else 'FAILED'}")
    except ImportError:
        print("(skip scan check: pip install zxing-cpp numpy)")


if __name__ == "__main__":
    main()
