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

Photos for the Indian and Indonesian sections (and a few others) are free-licensed; their sources,
authors and licenses are listed in `tools/photo-credits.json` and on `/credits.html`.

## Rebuilding assets

```bash
pip install pillow "qrcode[pil]" pymupdf opencv-python-headless zxing-cpp
python tools/build_images.py      # menu photos + combo collages -> assets/img/menu
python tools/build_wordmark.py    # EASTERN SPECIAL Inihaw wordmark -> assets/img/wordmark.svg + index.html
python tools/build_assets.py      # QR code, table card, icons, share image
python tools/build_qr_poster.py   # A5 poster PDF/PNG + scan check (needs Chrome; fonts in tools/fonts, SIL OFL)
python tools/build_menu_card.py   # menu card PDFs (A3, A4, A5) + previews + /qr/menucard/ page (needs Chrome + Node)
```
