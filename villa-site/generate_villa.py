#!/usr/bin/env python3
"""Generate a villa site from template.html + villas/<slug>.json.

Usage:
  python3 generate_villa.py                # build every villas/*.json -> ../villa-site/<slug>.html
  python3 generate_villa.py villas/x.json  # build one

Config keys: see villas/demo-seminyak.json. Photos are plain URLs (paste them
from the listing / PDF-listing flow); the page turns them into scroll-film frames
and the gallery. Set "owner_pitch": true for the version you send to the owner,
false once the villa signs and the site becomes theirs (or append ?owner to the URL).
"""
import json, sys, html, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = (HERE / "template.html").read_text(encoding="utf-8")

def build(cfg_path: pathlib.Path) -> pathlib.Path:
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    slug = cfg.get("slug") or cfg_path.stem
    title = f"{cfg['name']} — {cfg['area']}, {cfg['island']}"
    page = (TEMPLATE
            .replace("{{TITLE}}", html.escape(title))
            .replace("{{OG_IMAGE}}", html.escape(cfg["photos"][0]["url"] if cfg.get("photos") else ""))
            .replace("{{CONFIG}}", json.dumps(cfg, ensure_ascii=False, indent=2).replace("</", "<\\/")))
    out = HERE / f"{slug}.html"
    out.write_text(page, encoding="utf-8")
    return out

if __name__ == "__main__":
    targets = [pathlib.Path(a) for a in sys.argv[1:]] or sorted((HERE / "villas").glob("*.json"))
    for t in targets:
        print("built", build(t).relative_to(HERE.parent))
