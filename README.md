# Eastern Special Inihaw — QR Menu

Mobile-first digital menu for Eastern Special Inihaw (Villagio Mall, Gate #7, First Floor), live at **https://inihaumenu.hizarc.com/**.
Plain HTML/CSS/JS (no frameworks, no build step needed to deploy), ~15 KB of gzipped code plus lazy-loaded WebP photos.

## What's in here

| Path | What it is |
| --- | --- |
| `index.html` | The page |
| `assets/js/menu-data.js` | **All dishes, prices, calories, combos.** Edit this to change the menu. |
| `assets/js/app.js` | Rendering, search, category bar, dish pop-up |
| `assets/css/style.css` | Styles (brand brown `#3B2110`, green `#38B64B`, red `#ED1C24`, ember `#F39A2B`) |
| `assets/img/menu/` | Optimized photos, 3 sizes each (360/540/720 px WebP). Combo pictures are collages of the exact dishes in each combo. |
| `assets/img/wordmark.svg` | The EASTERN SPECIAL Inihaw wordmark as vector paths (also inlined in `index.html`) |
| `qr/` | QR code (PNG + SVG), **A5 poster** (PDF + PNG), simple A6 table card, and a download page served at `/qr/` |
| `qr/eastern-special-inihaw-visiting-card.pdf` | **Visiting card** 90 × 50 mm, front + back, 3 mm bleed (+ PNG images of each side) |
| `qr/order-now/` | **ORDER NOW poster** (A4, A5 PDF + PNG): scan, add dishes, send on WhatsApp |
| `qr/menucard/` | **Printable menu card** in **A3, A4 and A5** (PDF + page previews), served at `/qr/menucard/` |
| `sw.js` | Service worker: instant repeat visits, works on weak signal |
| `CNAME`, `.nojekyll` | GitHub Pages custom domain settings |
| `tools/` | Scripts that rebuild the photos, QR/icons, poster and menu cards |

Not uploaded (see `.gitignore`): `Menu Item IMage/` (full-size original photos) and the 1080p intro videos.

## Publish on GitHub Pages

1. Create a GitHub repository and push this folder to the `main` branch.
2. Repository **Settings → Pages → Build and deployment**: Source = *Deploy from a branch*, Branch = `main`, folder `/ (root)`.
3. Custom domain: `inihaumenu.hizarc.com` (already set by the `CNAME` file).
4. At the DNS provider for `hizarc.com`, add a record:
   `CNAME   inihaumenu   <your-github-username>.github.io`
5. Once the DNS check passes in Settings → Pages, tick **Enforce HTTPS**.

The QR code points to `https://inihaumenu.hizarc.com/` and will work as soon as the site is live there.

- Menu: **https://inihaumenu.hizarc.com/**
- QR code & poster: **https://inihaumenu.hizarc.com/qr/**
- Printable menu cards (A3, A4, A5): **https://inihaumenu.hizarc.com/qr/menucard/**
- ORDER NOW poster (A4): **https://inihaumenu.hizarc.com/qr/order-now/eastern-special-inihaw-order-now-A4.pdf**

## WhatsApp ordering

Guests tap the red **+** on a dish photo (or **Add to order** inside a dish for size + quantity), then the green
**View order** button. With an empty order that button shows the 3 steps and **Start ordering**, which scrolls to
the dishes and points at the **+** buttons. The order popup has the basket, an **Add to your order** row
(`extras` in `menu-data.js`), order type (Pickup / Delivery, Delivery pre-selected), delivery address,
**Share my location**, name and a kitchen note. **Send order on WhatsApp** opens WhatsApp to `+966 53 562 7615`
with the whole order typed out.

- Delivery charge by distance (`restaurant.delivery.zones`): the customer must pick one before sending.
  Within 3 km **10 SR** · within 5 km **15 SR** · within 10 km **20 SR** · above 10 km **30 SR**.
  The chosen distance and charge go into the WhatsApp message. Without `zones`, `restaurant.delivery.fee` is one
  fixed charge (`0` = free, `null` = confirmed on WhatsApp). Optional minimum order: `restaurant.delivery.minOrder`.
- Order types and the pre-selected one: `restaurant.orderTypes`, `restaurant.defaultOrderType`.
- Links: `/#order` opens the order popup, `/?order=pickup#order` pre-selects Pickup.

## Link preview (WhatsApp, Facebook, iMessage)

Pasting the site link shows the big **ORDER NOW** picture `assets/img/og-order-now.jpg` (1200 x 630, under 100 KB),
set by the `og:` tags at the top of `index.html`. Chat apps keep old previews for a while: after changing the picture,
give it a new file name (and update the tags) so the new one is fetched. In WhatsApp, paste the link and wait a moment
for the big preview to appear before sending.

## Changing the menu

- **Price / name / description:** edit `assets/js/menu-data.js`, commit, push. Live in about a minute.
  Then run `python tools/build_menu_card.py` so the printable menu cards (PDFs) match.
- **New dish:** put the photo in `Menu Item IMage/`, add `"slug": "file name.jpg"` to `SOURCES` in
  `tools/build_images.py`, run `python tools/build_images.py slug`, then add the item in `menu-data.js` with `img: "slug"`.
- **Replaced a photo but kept the same slug?** Change `VERSION` in `sw.js` (e.g. `ei-v2`) so phones fetch the new one.

Each dish can be linked directly, e.g. `https://inihaumenu.hizarc.com/#bulalo`.

No pork: dishes that are traditionally pork (Crispy Pata, Patatin, Dinuguan, Bopis, Chicharon Bulaklak, Lechon Kawali, Sisig…)
are listed as their beef/chicken versions, with matching non-pork photos.

## Photos

All dish photos share the same top-view terrazzo style. Budget Meal has no photo of its own yet:
it shows an example-meal collage (see `SQUARE_COLLAGES` in `tools/build_images.py`) until one is added.

## Rebuilding assets

```bash
pip install pillow "qrcode[pil]" pymupdf opencv-python-headless zxing-cpp
python tools/build_images.py      # menu photos + combo collages -> assets/img/menu
python tools/build_wordmark.py    # EASTERN SPECIAL Inihaw wordmark -> assets/img/wordmark.svg + index.html
python tools/build_assets.py      # QR code, table card, icons
python tools/build_share_image.py # link-preview picture for WhatsApp etc. (needs Chrome + Node)
python tools/build_qr_poster.py   # A5 poster PDF/PNG + scan check (needs Chrome; fonts in tools/fonts, SIL OFL)
python tools/build_menu_card.py   # menu card PDFs (A3, A4, A5) + previews + /qr/menucard/ page (needs Chrome + Node)
python tools/build_visiting_card.py   # visiting card PDF + PNGs (needs Chrome)
python tools/build_order_poster.py    # ORDER NOW poster, A4 + A5 PDF + PNG (needs Chrome + Node)
```
