#!/usr/bin/env python3
"""Source villa leads straight from Airbnb search, qualified and ranked.

  python3 find_leads.py --areas Canggu Seminyak Pererenan --min-br 5 \
      --checkin 2026-11-05 --checkout 2026-11-10 [--pages 3] [--out leads.md]

Searching WITH low-season dates is the qualification: Airbnb only returns villas whose
calendar is open then, i.e. exactly the gaps we sell. Each hit is fetched, sized up
(bedrooms, guests, rating, reviews, photos) and screened:
  - out if fewer than --min-br bedrooms
  - out if the description names a big property manager (we do not poach their inventory)
  - out if it is one of ours (AC Collection / partner portfolio)
Scores favour big, well-reviewed, photogenic villas: those convert.

Only reads public listing pages. Contacts are NOT on Airbnb — Anthony gets those himself;
this produces the shortlist and the ready-to-build slugs.
"""
import re, sys, json, base64, argparse, pathlib, datetime, urllib.parse
from fetch_listing import fetch, fetch_listing

HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / ".leads-cache"

def fetch_cached(url, lid):
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f"{lid}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    L = fetch_listing(url, tries=2)
    f.write_text(json.dumps(L, ensure_ascii=False), encoding="utf-8")
    return L

# on hold / never contact (Anthony's standing rules), plus the big aggregators we avoid
HOLD = ["tropical door", "thetropicaldoor"]
BIG_PM = ["elite havens", "bali villa finder", "nagisa", "villa-bali.com", "villabali",
          "bvi ", "bali villa escapes", "ministry of villas", "villa finder", "asia villas",
          "propertidepo", "bali management villas", "vila-bali"]
# matched on the TITLE only, and distinctive enough not to fire on prose:
# "ultimate retreat"/"ultimate relaxation" appear in half the listings in Bali.
OURS = ["ac collection", "ac partners", "dreamtime", "breig", "oxo black", "aquamarine",
        "villa ultimate", "lataliana", "rock coco", "villa daria", "casa de playa",
        "palm house", "nanuku", "azul ", "saraya", "calesma", "villa cahya", "villa capella",
        "villa larona", "bali forest", "peak villa", "the bali agent", "belle oasis", "ikebana"]

def search_ids(area, min_br, checkin, checkout, offset=0, adults=10):
    q = urllib.parse.quote(f"{area}--Bali--Indonesia")
    url = (f"https://www.airbnb.com/s/{q}/homes?adults={adults}&min_bedrooms={min_br}"
           f"&room_types%5B%5D=Entire%20home%2Fapt&checkin={checkin}&checkout={checkout}"
           + (f"&items_offset={offset}" if offset else ""))
    html = fetch(url, timeout=45)
    c = html.replace("\\u002F", "/").replace("\\/", "/")
    ids = []
    for tok in set(re.findall(r'"([A-Za-z0-9+/=]{20,60}==?)"', c)):
        try:
            d = base64.b64decode(tok).decode("utf-8", "ignore")
        except Exception:
            continue
        m = re.match(r"(?:Demand)?StayListing:(\d+)", d)
        if m:
            ids.append(m.group(1))
    return list(dict.fromkeys(ids))

def screen(L):
    """-> (ok, reason). Keeps the judgement in one place so the rules stay auditable."""
    title = (L.get("title") or "").lower()
    desc = (L.get("description") or "").lower()
    for h in HOLD:
        if h in title or h in desc: return False, f"on hold, do not contact ({h})"
    for pm in BIG_PM:
        if pm in title or pm in desc: return False, f"managed by a big PM ({pm.strip()})"
    for own in OURS:
        if own in title: return False, f"ours / partner ({own.strip()})"
    m = re.search(r"managed by ([A-Z][\w &'-]{2,40})", L.get("description") or "")
    manager = m.group(1).strip() if m else ""
    return True, manager

def score(L):
    br = L.get("bedrooms") or 0
    rating = L.get("rating") or 0
    reviews = L.get("reviews") or 0
    if reviews > 500: reviews = 0  # host-level total, not this listing
    photos = len(L.get("photos") or [])
    return round(br * 10 + rating * 6 + min(reviews, 150) * 0.12 + min(photos, 60) * 0.25, 1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--areas", nargs="+", default=["Canggu", "Seminyak"])
    ap.add_argument("--min-br", type=int, default=5)
    ap.add_argument("--checkin", required=True); ap.add_argument("--checkout", required=True)
    ap.add_argument("--pages", type=int, default=2)
    ap.add_argument("--max-fetch", type=int, default=40)
    ap.add_argument("--out", default="leads.md")
    a = ap.parse_args()

    seen, found = set(), []
    for area in a.areas:
        for page in range(a.pages):
            try:
                ids = search_ids(area, a.min_br, a.checkin, a.checkout, offset=page * 18)
            except Exception as e:
                print(f"  ! {area} p{page}: {e}"); continue
            new = [i for i in ids if i not in seen]
            seen.update(new); found += [(area, i) for i in new]
            print(f"  {area} p{page}: {len(ids)} ids, {len(new)} new")

    print(f"\n{len(found)} candidates, fetching up to {a.max_fetch}…")
    rows = []
    for area, lid in found[: a.max_fetch]:
        url = f"https://www.airbnb.com/rooms/{lid}"
        try:
            L = fetch_cached(url, lid)
        except Exception as e:
            print(f"  ! {lid}: {e}"); continue
        if (L.get("bedrooms") or 0) < a.min_br:
            print(f"  - {lid} {str(L.get('bedrooms'))}BR < {a.min_br}"); continue
        ok, note = screen(L)
        name = re.sub(r"^\*?NEW\*?\s*", "", L.get("title") or "")[:60]
        row = dict(area=area, id=lid, url=url, name=name, br=L.get("bedrooms"),
                   guests=L.get("guests"), rating=L.get("rating"), reviews=L.get("reviews"),
                   photos=len(L.get("photos") or []), city=L.get("city"), ok=ok, note=note,
                   score=score(L))
        rows.append(row)
        print(f"  {'OK ' if ok else 'skip'} {lid} {row['br']}BR {row['rating']}★ "
              f"{row['reviews']}rev — {name[:42]} {('(' + note + ')') if note else ''}")

    keep = sorted([r for r in rows if r["ok"]], key=lambda r: -r["score"])
    out = HERE / a.out
    md = [f"# Leads — {', '.join(a.areas)}, {a.min_br}BR+, disponibles {a.checkin} → {a.checkout}",
          f"\nGénéré {datetime.date.today().isoformat()} par find_leads.py. "
          f"{len(seen)} annonces vues, {len(rows)} qualifiées sur la taille, {len(keep)} retenues.\n",
          "| # | Villa | Zone | BR | Pers. | Note | Avis | Photos | Score | Manager | Annonce |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(keep, 1):
        md.append(f"| {i} | {r['name']} | {r['city'] or r['area']} | {r['br']} | {r['guests']} | "
                  f"{r['rating']} | {r['reviews']} | {r['photos']} | {r['score']} | {r['note'] or '—'} | {r['url']} |")
    rejected = [r for r in rows if not r["ok"]]
    if rejected:
        md += ["\n## Écartées", "", "| Villa | Raison |", "|---|---|"]
        md += [f"| {r['name']} | {r['note']} |" for r in rejected]
    md += ["\n## Étape suivante", "",
           "```bash",
           "python3 villa-site/villa.py \"<url>\" --name \"Villa X\" --adr <usd> --rates-idr <low> <high> \\",
           "    --contact \"<nom>\" --handle \"+62 8xx\" --channel whatsapp",
           "```",
           "",
           "Airbnb ne donne pas le téléphone de l'hôte : le contact vient d'Anthony (visite, Instagram, site de la villa)."]
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\n{len(keep)} leads retenus -> {out.relative_to(HERE.parent)}")

if __name__ == "__main__":
    main()
