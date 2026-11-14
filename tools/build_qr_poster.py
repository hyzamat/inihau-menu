"""
Builds the printable A5 QR poster:  qr/eastern-special-inihaw-qr-poster-A5.pdf  (+ PNG preview)

Run from the project root:
    python tools/build_qr_poster.py
Needs Google Chrome (or Microsoft Edge) (used headless to print the PDF),
plus: pip install qrcode pymupdf opencv-python-headless   (last two only for the scan check)
"""
import base64
import os
import subprocess
import sys
import tempfile

import qrcode

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
OUT_PDF = os.path.join(ROOT, "qr", "eastern-special-inihaw-qr-poster-A5.pdf")
OUT_PNG = os.path.join(ROOT, "qr", "eastern-special-inihaw-qr-poster-A5.png")
URL = "https://inihaumenu.hizarc.com/"
SHOWN_URL = "inihaumenu.hizarc.com"

BROWSERS = [  # Chrome first: headless Edge silently skips --print-to-pdf on some PCs
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

BROWN, RED, GOLD, GREEN = "#1E1611", "#E8262B", "#FF8A1F", "#3BBF55"


# ---------------------------------------------------------------- QR code
def qr_svg():
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, border=0)
    q.add_data(URL)
    q.make(fit=True)
    m = q.get_matrix()
    n = len(m)
    finders = [(0, 0), (n - 7, 0), (0, n - 7)]

    def in_finder(r, c):
        return any(fr <= r < fr + 7 and fc <= c < fc + 7 for fc, fr in finders)

    logo = 9                              # modules kept clear for the centre logo
    lo = (n - logo) // 2

    def in_logo(r, c):
        return lo <= r < lo + logo and lo <= c < lo + logo

    parts = []
    for r in range(n):
        for c in range(n):
            if m[r][c] and not in_finder(r, c) and not in_logo(r, c):
                parts.append(f'<rect x="{c + .02:.2f}" y="{r + .02:.2f}" width=".96" height=".96" rx=".3"/>')
    eyes = []
    for fc, fr in finders:
        eyes.append(
            f'<path fill="{BROWN}" fill-rule="evenodd" d="M{fc + 2},{fr} h3 a2,2 0 0 1 2,2 v3 a2,2 0 0 1 -2,2 h-3 '
            f'a2,2 0 0 1 -2,-2 v-3 a2,2 0 0 1 2,-2 z M{fc + 2.3},{fr + 1} h2.4 a1.3,1.3 0 0 1 1.3,1.3 v2.4 '
            f'a1.3,1.3 0 0 1 -1.3,1.3 h-2.4 a1.3,1.3 0 0 1 -1.3,-1.3 v-2.4 a1.3,1.3 0 0 1 1.3,-1.3 z"/>'
            f'<rect x="{fc + 2}" y="{fr + 2}" width="3" height="3" rx="1" fill="{RED}"/>'
        )
    c0 = lo + .5
    size = logo - 1
    logo_svg = (
        f'<rect x="{c0}" y="{c0}" width="{size}" height="{size}" rx="2.2" fill="{BROWN}"/>'
        f'<text x="{n / 2}" y="{n / 2 + 1.3}" text-anchor="middle" font-family="Fredoka" font-weight="700" '
        f'font-size="3.8" letter-spacing=".1"><tspan fill="{GREEN}">E</tspan><tspan fill="#fff">I</tspan></text>'
        f'<rect x="{n / 2 - 1.6}" y="{n / 2 + 2.1}" width="3.2" height=".5" rx=".25" fill="{GOLD}"/>'
    )
    return (f'<svg viewBox="0 0 {n} {n}" xmlns="http://www.w3.org/2000/svg" shape-rendering="geometricPrecision">'
            f'<g fill="{BROWN}">{"".join(parts)}</g>{"".join(eyes)}{logo_svg}</svg>')


# ---------------------------------------------------------------- page
def font_face(family, file, weight):
    data = base64.b64encode(open(os.path.join(TOOLS, "fonts", file), "rb").read()).decode()
    return (f"@font-face{{font-family:'{family}';src:url(data:font/ttf;base64,{data}) format('truetype');"
            f"font-weight:{weight};font-display:block}}")


JPG_DIR = os.path.join(tempfile.gettempdir(), "ei-qr-poster-img")


def img(slug):
    # Chrome stores WebP losslessly in PDFs (~1 MB each); JPEG is passed through compressed.
    from PIL import Image
    os.makedirs(JPG_DIR, exist_ok=True)
    out = os.path.join(JPG_DIR, f"{slug}.jpg")
    Image.open(os.path.join(ROOT, "assets", "img", "menu", f"{slug}-720.webp")).convert("RGB").save(out, quality=90)
    return "file:///" + out.replace("\\", "/")


DOODLES = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 160 160' fill='none' "
    "stroke='white' stroke-opacity='.09' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'>"
    "<circle cx='32' cy='34' r='15'/><circle cx='32' cy='34' r='9'/>"
    "<path d='M104 18c10 4 14 16 8 26s-20 10-24 2 6-26 16-28z M96 44l14-22'/>"
    "<path d='M128 92v34 M122 92v10a6 6 0 0 0 12 0V92'/>"
    "<path d='M20 104c8-6 22-6 30 0 M22 112h26 M24 104l4-14 M46 104l-4-14'/>"
    "<path d='M70 140c6-10 18-12 26-4 M84 128c2-6 6-8 10-8'/>"
    "<path d='M74 78l3 6 6 1-4.5 4 1 6-5.5-3-5.5 3 1-6-4.5-4 6-1z'/>"
    "</svg>"
).replace("#", "%23").replace("<", "%3C").replace(">", "%3E")

TERRAZZO = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'>"
    "<g fill-opacity='.22'>"
    "<path fill='%23F39A2B' d='M12 14l5-2 3 4-4 4-5-1z'/><path fill='%2338B64B' d='M70 10l4 1 1 4-4 2-3-3z'/>"
    "<path fill='%23C2643E' d='M100 40l4-1 2 3-3 3-4-2z'/><path fill='%2338B64B' d='M30 64l3-2 3 2-1 4-4 0z'/>"
    "<path fill='%23F39A2B' d='M82 86l5 0 1 4-4 3-3-3z'/><path fill='%23C2643E' d='M18 100l3 0 2 3-3 2-3-2z'/>"
    "<path fill='%2338B64B' d='M58 108l3-1 2 2-2 3-3-1z'/><path fill='%23F39A2B' d='M108 104l3-1 2 3-3 2z'/>"
    "</g></svg>"
)


def html():
    fonts = "".join([
        font_face("Fredoka", "Fredoka.ttf", "300 700"),
        font_face("Poppins", "Poppins-Medium.ttf", 500),
        font_face("Poppins", "Poppins-SemiBold.ttf", 600),
        font_face("Poppins", "Poppins-Bold.ttf", 700),
    ])
    circles = [  # slug, left, top, diameter (mm), zoom
        ("bulalo", -9, 58, 42, 1.35),
        ("beef-sisig", 116, 70, 44, 1.3),
        ("kare-kare", -7, 112, 38, 1.3),
        ("halo-halo", 119, 122, 36, 1.25),
        ("chicken-inasal", -6, 15, 26, 1.3),
        ("pancit-palabok", 128, 22, 26, 1.3),
    ]
    circ = "".join(
        f'<div class="dish" style="left:{x}mm;top:{y}mm;width:{d}mm;height:{d}mm">'
        f'<img src="{img(s)}" style="transform:scale({z})"></div>'
        for s, x, y, d, z in circles
    )
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{fonts}
@page {{ size: 148mm 210mm; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 148mm; height: 210mm; }}
body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; font-family: Poppins, sans-serif; color: {BROWN}; }}
.page {{ position: relative; width: 148mm; height: 210mm; overflow: hidden;
  background: #FBF7EE url("{TERRAZZO}") 0 0 / 34mm 34mm; }}
.band {{ position: absolute; inset: 0 0 auto 0; height: 104mm;
  background: url("{DOODLES}") 0 0 / 46mm 46mm,
              radial-gradient(110mm 60mm at 50% 100%, rgba(255,110,20,.38), transparent 70%),
              radial-gradient(90mm 50mm at 50% 0%, rgba(255,138,31,.14), transparent 70%),
              linear-gradient(180deg, #120D0A 0%, #1E1611 55%, #2A1C12 100%); }}
.wave {{ position: absolute; left: 0; top: 92mm; width: 148mm; height: 14mm; }}
.kick {{ position: absolute; top: 11mm; left: 0; right: 0; text-align: center; }}
.kick span {{ display: inline-block; font: 700 7.4pt Poppins; letter-spacing: .32em; color: #FFBF4D;
  background: rgba(255,138,31,.16); padding: 1.5mm 4.5mm 1.5mm 5.5mm; border-radius: 10mm; }}
.logo {{ position: absolute; top: 18.5mm; left: 0; right: 0; text-align: center; color: #fff;
  font: 700 50pt/0.95 Fredoka; text-shadow: 0 1.1mm 0 rgba(0,0,0,.25); }}
.logo .e {{ display: block; font: 700 22pt/1 Poppins; color: {GREEN}; letter-spacing: .03em;
  -webkit-text-stroke: .5mm #fff; paint-order: stroke fill; text-shadow: none; }}
.logo .s {{ display: block; font: 700 11pt/1.4 Poppins; letter-spacing: .3em; padding-left: .3em; text-shadow: none; }}
.dish {{ position: absolute; border-radius: 50%; overflow: hidden; background: #EFE8DA;
  border: 1.6mm solid #fff; box-shadow: 0 2.2mm 5mm rgba(57,34,20,.32); }}
.dish img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.card {{ position: absolute; left: 50%; top: 62mm; width: 90mm; transform: translateX(-50%);
  background: #fff; border-radius: 7mm; padding: 6mm 6mm 5mm; text-align: center;
  box-shadow: 0 3mm 9mm rgba(0,0,0,.45), 0 0 0 .5mm rgba(255,138,31,.45); }}
.scan {{ font: 700 25pt/1 Fredoka; letter-spacing: .04em; color: {BROWN}; }}
.scan b {{ color: {RED}; font-weight: 700; }}
.sub {{ font: 500 8pt Poppins; color: #7A6656; margin-top: 1.6mm; }}
.qrbox {{ position: relative; width: 70mm; height: 70mm; margin: 3.5mm auto 0; padding: 7.6mm; }}
.qrbox svg {{ width: 100%; height: 100%; display: block; }}
.br {{ position: absolute; width: 9mm; height: 9mm; border: 1.3mm solid {GOLD}; }}
.br.tl {{ left: 0; top: 0; border-right: 0; border-bottom: 0; border-top-left-radius: 3.5mm; }}
.br.tr {{ right: 0; top: 0; border-left: 0; border-bottom: 0; border-top-right-radius: 3.5mm; }}
.br.bl {{ left: 0; bottom: 0; border-right: 0; border-top: 0; border-bottom-left-radius: 3.5mm; }}
.br.br2 {{ right: 0; bottom: 0; border-left: 0; border-top: 0; border-bottom-right-radius: 3.5mm; }}
.url {{ display: inline-flex; align-items: center; gap: 1.6mm; margin-top: 2.6mm;
  font: 600 8.6pt Poppins; color: {BROWN}; background: #FDECD6; padding: 1.4mm 4mm; border-radius: 10mm; }}
.url svg {{ width: 3.4mm; height: 3.4mm; fill: {GOLD}; }}
.promo {{ position: absolute; left: 10mm; right: 10mm; top: 172mm; height: 15mm;
  background: {BROWN}; border-radius: 4.5mm; display: flex; align-items: center; gap: 3.5mm; padding: 0 4mm 0 3mm;
  box-shadow: 0 2mm 5mm rgba(57,34,20,.25); }}
.price {{ flex: none; background: {RED}; color: #fff; border-radius: 3mm; text-align: center;
  padding: 1.2mm 2.6mm 1.4mm; font: 700 13pt/1 Fredoka; }}
.price small {{ display: block; font: 700 5.6pt Poppins; letter-spacing: .14em; margin-top: .6mm; opacity: .9; }}
.ptxt h3 {{ font: 700 12.5pt/1 Fredoka; letter-spacing: .05em; color: #FFBF4D; }}
.price em {{ display: block; font: 700 5.4pt Poppins; letter-spacing: .12em; font-style: normal; margin-bottom: .6mm; opacity: .9; }}
.ptxt p {{ font: 500 6.9pt/1.35 Poppins; color: #F1E6D6; margin-top: .9mm; }}
.foot {{ position: absolute; left: 0; right: 0; bottom: 0; height: 16mm; background: {RED};
  display: flex; align-items: center; justify-content: center; gap: 5mm; color: #fff; font: 600 8.6pt Poppins; }}
.foot span {{ display: inline-flex; align-items: center; gap: 1.5mm; }}
.foot svg {{ width: 3.6mm; height: 3.6mm; fill: #fff; }}
.foot i {{ width: .35mm; height: 6mm; background: rgba(255,255,255,.45); }}
</style></head><body><div class="page">
<div class="band"></div>
<svg class="wave" viewBox="0 0 148 14" preserveAspectRatio="none">
  <path d="M0 6 C 24 14, 48 0, 74 6 S 124 13, 148 4 V14 H0 Z" fill="#FBF7EE"/>
</svg>
{circ}
<p class="kick"><span>FILIPINO GRILL · INDIAN · INDONESIAN</span></p>
<h1 class="logo"><span class="e">EASTERN</span><span class="s">SPECIAL</span>Inihaw</h1>
<div class="card">
  <p class="scan">SCAN <b>FOR</b> MENU</p>
  <p class="sub">Open your phone camera and point it at the code</p>
  <div class="qrbox">
    <span class="br tl"></span><span class="br tr"></span><span class="br bl"></span><span class="br br2"></span>
    {qr_svg()}
  </div>
  <span class="url"><svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm6.9 6h-2.9a15.7 15.7 0 0 0-1.4-3.6A8 8 0 0 1 18.9 8zM12 4c.8 1.2 1.5 2.5 1.9 4h-3.8c.4-1.5 1.1-2.8 1.9-4zM4.3 14a8.2 8.2 0 0 1 0-4h3.4a16.5 16.5 0 0 0 0 4H4.3zm.8 2h2.9c.3 1.3.8 2.5 1.4 3.6A8 8 0 0 1 5.1 16zM8 8H5.1a8 8 0 0 1 4.3-3.6C8.8 5.5 8.3 6.7 8 8zm4 12c-.8-1.2-1.5-2.5-1.9-4h3.8c-.4 1.5-1.1 2.8-1.9 4zm2.3-6H9.7a14.7 14.7 0 0 1 0-4h4.6a14.7 14.7 0 0 1 0 4zm.3 5.6c.6-1.1 1.1-2.3 1.4-3.6h2.9a8 8 0 0 1-4.3 3.6zm1.7-5.6a16.5 16.5 0 0 0 0-4h3.4a8.2 8.2 0 0 1 0 4h-3.4z"/></svg>{SHOWN_URL}</span>
</div>
<div class="promo">
  <div class="price"><em>FROM</em>210<small>SR</small></div>
  <div class="ptxt"><h3>FAMILY COMBOS</h3>
  <p>Feasts for 3 to 10 persons · rice, buko pandan, Pepsi, water, fruits &amp; sabaw included</p></div>
</div>
<div class="foot">
  <span><svg viewBox="0 0 24 24"><path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg>Villagio Mall · Gate #7 · First Floor</span>
  <i></i>
  <span><svg viewBox="0 0 24 24"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>053 562 7615</span>
</div>
</div></body></html>"""


def main():
    browser = next((b for b in BROWSERS if os.path.exists(b)), None)
    if not browser:
        sys.exit("Microsoft Edge or Google Chrome is required to print the PDF.")
    tmp = os.path.join(TOOLS, "_qr_poster_build.html")
    profile = os.path.join(tempfile.gettempdir(), "ei-qr-poster-profile")
    if os.path.exists(OUT_PDF):
        os.remove(OUT_PDF)
    open(tmp, "w", encoding="utf-8").write(html())
    try:
        subprocess.run([
            browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw", "--virtual-time-budget=8000",
            "--allow-file-access-from-files", "--no-first-run", "--no-default-browser-check",
            f"--user-data-dir={profile}",  # separate profile so an open browser window doesn't interfere
            f"--print-to-pdf={OUT_PDF}", "file:///" + tmp.replace("\\", "/"),
        ], check=True, capture_output=True, timeout=120)
        if not os.path.exists(OUT_PDF):
            sys.exit("Browser did not produce the PDF.")
    finally:
        if os.path.exists(tmp) and "--keep-html" not in sys.argv:
            os.remove(tmp)
    print("PDF ->", OUT_PDF)

    # preview PNG + make sure the QR really scans
    try:
        import pymupdf
        import cv2
        import numpy as np
    except ImportError:
        print("(skip scan check: pip install pymupdf opencv-python-headless)")
        return
    doc = pymupdf.open(OUT_PDF)
    print("pages:", len(doc), "| size mm:", [round(v / 72 * 25.4, 1) for v in doc[0].rect[2:]])
    doc[0].get_pixmap(dpi=300).save(OUT_PNG)
    from PIL import Image  # small preview for the /qr/ web page
    prev = Image.open(OUT_PNG).convert("RGB")
    prev.resize((900, round(prev.height * 900 / prev.width)), Image.LANCZOS).save(
        os.path.join(ROOT, "qr", "poster-preview.webp"), "WEBP", quality=82, method=6)
    for dpi in (300, 150, 72):
        pix = doc[0].get_pixmap(dpi=dpi)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)[:, :, :3]
        cv = cv2.QRCodeDetector().detectAndDecode(cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))[0]
        try:
            import zxingcpp
            zx = next((r.text for r in zxingcpp.read_barcodes(arr)), "")
        except ImportError:
            zx = "(pip install zxing-cpp)"
        ok = URL in (cv, zx)
        print(f"scan @ {dpi:3d} dpi -> OpenCV: {cv!r}  ZXing: {zx!r}  {'OK' if ok else 'FAILED'}")


if __name__ == "__main__":
    main()
