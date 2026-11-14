"""
Builds /credits.html (photo attributions for the free-licensed photos).

Reads "Menu Item IMage/credits.json" when present (and keeps a copy in tools/photo-credits.json so the
page can be rebuilt without the source photos). Only slugs actually used by build_images.py are listed.

    python tools/build_credits.py
"""
import ast
import html
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "Menu Item IMage", "credits.json")
KEEP = os.path.join(ROOT, "tools", "photo-credits.json")
OUT = os.path.join(ROOT, "credits.html")


def used_slugs():
    src = open(os.path.join(ROOT, "tools", "build_images.py"), encoding="utf-8").read()
    start = src.index("SOURCES = {") + len("SOURCES = ")
    sources = ast.literal_eval(src[start: src.index("}\n", start) + 1])
    return {slug: name for slug, name in sources.items()}


def main():
    if os.path.exists(SRC):
        shutil.copyfile(SRC, KEEP)
    data = json.load(open(KEEP, encoding="utf-8"))
    used = used_slugs()
    rows = []
    for slug, c in sorted(data.items()):
        if used.get(slug) != c.get("file"):
            continue
        e = html.escape
        rows.append(
            f'<li><img src="assets/img/menu/{e(slug)}-360.webp" width="64" height="64" alt="" loading="lazy">'
            f'<span><b>{e(slug.replace("-", " ").title())}</b><br>'
            f'<a href="{e(c["source"])}" rel="nofollow noopener" target="_blank">{e(c.get("title") or "Source")}</a>'
            f' — {e(c.get("author") or "unknown author")} · {e(c.get("license") or "")}</span></li>')
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Photo credits — Eastern Special Inihaw</title>
<meta name="robots" content="noindex">
<link rel="icon" href="assets/img/icon-192.png" type="image/png">
<style>
  body {{ margin: 0; font: 15px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif; color: #2A1708; background: #FBF6EE; }}
  header {{ background: #3B2110; color: #fff; padding: 22px 18px; }}
  h1 {{ margin: 0; font-size: 22px; }}
  main {{ max-width: 760px; margin: 0 auto; padding: 16px; }}
  ul {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }}
  li {{ display: flex; gap: 12px; align-items: center; background: #fff; border: 1px solid #EEE2CF; border-radius: 12px; padding: 8px; font-size: 13.5px; }}
  li img {{ border-radius: 8px; flex: none; }}
  a {{ color: #B9620C; }}
  p {{ color: #7A6656; }}
</style></head><body>
<header><h1>Photo credits</h1></header>
<main>
<p>These menu photos are used under free licenses (Creative Commons / public domain); they are cropped and resized.
<a href="./">← Back to the menu</a></p>
<ul>
{chr(10).join(rows)}
</ul>
</main></body></html>
"""
    open(OUT, "w", encoding="utf-8").write(page)
    print(f"credits.html: {len(rows)} photos")


if __name__ == "__main__":
    main()
