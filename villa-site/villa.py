#!/usr/bin/env python3
"""One command per villa: listing URL -> villas/<slug>.json -> <slug>.html -> outreach/<slug>.md -> funnel.csv -> git commit.

  python3 villa.py <airbnb-or-site-url> --adr 1300 [--name "Villa X"] [--area Canggu] [--slug villa-x]
                   [--first-name Ketut --contact "Ketut Sudira" --handle "+62..." --channel whatsapp]
                   [--photos 8] [--clips] [--no-commit] [--push] [--fresh]

Re-running on an existing slug keeps your hand edits (photos, texts) and only refreshes
the market data, the ADR if given, the HTML, the message and the funnel row. --fresh rebuilds all.
--adr is in USD; without it the ADR falls back to the PriceLabs 75th percentile of the zone (flagged).
"""
import json, re, sys, pathlib, argparse, subprocess, datetime, unicodedata
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fetch_listing import fetch_listing
import generate_villa, make_message, funnel

HERE = pathlib.Path(__file__).resolve().parent
CFG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
MARKET = json.loads((HERE / "market" / "bali.json").read_text(encoding="utf-8"))
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
LONG = {"Jan": "January", "Feb": "February", "Mar": "March", "Apr": "April", "May": "May", "Jun": "June", "Jul": "July", "Aug": "August", "Sep": "September", "Oct": "October", "Nov": "November", "Dec": "December"}
DAYS = {"Jan": 31, "Feb": 28, "Mar": 31, "Apr": 30, "May": 31, "Jun": 30, "Jul": 31, "Aug": 31, "Sep": 30, "Oct": 31, "Nov": 30, "Dec": 31}

# photo selection: (label prefix, max per category), exteriors first — the rule of the listing-pdf skill
PHOTO_PLAN = [("Exterior", 2), ("Swimming pool", 2), ("Pool", 2), ("Terrace", 1), ("Outdoor", 1), ("Patio", 1), ("Garden", 1), ("Rooftop", 1), ("Lounge", 1),
              ("Hot tub", 1), ("Living room", 2), ("Dining area", 1), ("Kitchen", 1), ("Bedroom 1", 1), ("Bedroom 2", 1), ("Gym", 1), ("Cinema", 1), ("Bathroom 1", 1), ("Full bathroom 1", 1)]
SKIP = ("Additional", "Workspace", "single bed", "double bed", "queen bed", "king bed",
        "Interior details", "Parking", "Bedroom view")
# host-written captions: never put safety kit, storage or signage on a client-facing page
JUNK = ("extinguisher", "first aid", "smoke alarm", "alarm", "towel", "toilet", "sink",
        "wifi", "password", "router", "switch", "meter", "washing machine", "laundry",
        "safe box", "storage", "cupboard", "wardrobe", "closet", "sign", "note", "rules",
        "instruction", "manual", "key", "lock", "trash", "bin", "detergent", "aircon remote")
CAPTIONS = {
    "Exterior": ["{name}, {area}.", "The estate from above."], "Swimming pool": ["The pool at first light.", "Pool deck, late afternoon."], "Pool": ["The pool at first light.", "Pool deck, late afternoon."],
    "Terrace": ["The terrace, breakfast hour."], "Outdoor": ["The garden, all yours."], "Patio": ["The terrace, breakfast hour."], "Garden": ["The garden pavilion."], "Rooftop": ["Rooftop, sunset hour."],
    "Lounge": ["The outdoor lounge, evening."], "Hot tub": ["Hot tub and spa, off the garden."], "Living room": ["The living pavilion, open to the garden.", "Lounge, evening."],
    "Dining area": ["Dinner for {guests}, chef on request."], "Kitchen": ["The kitchen, professional grade."],
    "Bedroom 1": ["Master suite, garden light."], "Bedroom 2": ["Second suite, ensuite."], "Gym": ["Home gym and wellness."],
    "Cinema": ["Private cinema."], "Bathroom 1": ["Garden bathroom."], "Full bathroom 1": ["Garden bathroom."]}

def _cat(label):
    """category of a photo label like 'Swimming pool,Exterior image 3' -> first plan prefix contained in it"""
    for prefix, _ in PHOTO_PLAN:
        if prefix.lower() in label.lower(): return prefix
    return ""

def wa_link(handle):
    """+62 895 3470 07195 -> https://wa.me/62895347007195. None if no digits."""
    import re as _re
    digits = _re.sub(r"\D", "", handle or "")
    return f"https://wa.me/{digits}" if digits else None

def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "villa"

def clean_name(title, description="", area="", bedrooms=None):
    # "Villa Only 400m to the Beach" is not a name: reject ordinary words after Villa
    STOP = {"only", "with", "in", "near", "for", "and", "at", "by", "is", "has", "of", "to",
            "from", "the", "a", "an", "just", "steps", "walk", "minutes", "min", "close",
            "beach", "villa", "luxury", "private", "new", "modern", "spacious", "stunning"}
    for pat in (r"Welcome to (?:the )?([A-Z][\w'&-]+(?:\s+[A-Z][\w'&-]+){0,3})",
                r"\b(Villa\s+[A-Z][\w'&-]+(?:\s+[A-Z][\w'&-]+)?)",
                r"\b([A-Z][\w'&-]+\s+(?:House|Residence|Estate|Retreat|Lodge|Compound))\b"):
        for src in (title, description or ""):
            m = re.search(pat, src)
            if m:
                n = re.sub(r"\s{2,}", " ", m.group(1).strip(" -—:,"))
                words = n.split()
                if len(n) > 3 and not re.match(r"^(The|This|Our|Your|A)\b", n) \
                   and not any(w.lower() in STOP for w in words[1:]):
                    return n
    # no real name on the listing: an honest, clean generic beats a mangled title
    if area and bedrooms: return f"{area} {bedrooms}-Bedroom Villa"
    t = re.sub(r"^\*?NEW\*?\s*", "", title, flags=re.I)
    t = re.sub(r"\b\d+\s*BR\b|\b\d+[- ]?bed(?:room)?s?\b", "", t, flags=re.I)
    t = re.sub(r"\s{2,}", " ", t)
    t = re.sub(r"\s*[-–|·]\s*$", "", t)
    m = re.search(r"(?:The\s+)?([A-Z][\w']+(?:\s+[A-Z][\w']+){0,3}\s+(?:House|Villa|Estate|Residence|Retreat|Lodge))", t)
    if m: return m.group(0).strip()
    m = re.search(r"(Villa\s+[A-Z][\w']+(?:\s+[A-Z][\w']+)?)", t)
    return (m.group(1) if m else t.split(" - ")[0].split("|")[0]).strip()[:60]

def zone_for(city, area):
    key = (area or city or "").lower().strip()
    for alias, z in MARKET["aliases"].items():
        if alias in key: return z
    return None

def low_season(zone, n=3, from_date=None):
    """The next n calendar months from today (rolling), not a global lowest-occupancy pick —
    the pitch must talk about the gap that is actually coming up, not a distant Feb/Mar
    mentioned in September. Falls back to whichever months genuinely have data."""
    z = MARKET["zones"][zone]; ly = z["occ_ly"]; prev = z.get("occ_prev", {})
    blend = {m: (ly[m] + prev[m]) / 2 if m in prev else ly[m] for m in MONTHS}
    today = from_date or datetime.date.today()
    start = today.month  # 0-based index of NEXT month (Jan=index0=month1, so month m -> index m)
    peak = MARKET.get("peak_windows", {})
    threshold = MARKET.get("peak_occ_threshold", 0.50) * 100
    rows = []
    for i in range(12):  # walk forward until n genuinely soft months are found
        if len(rows) >= n: break
        m = MONTHS[(start + i) % 12]
        if blend[m] > threshold: continue  # a busy month is not a low season, never pitch it as one
        window = peak.get(LONG[m], {})
        rows.append({"month": window.get("label", LONG[m]),
                     "days": window.get("days", DAYS[m]),
                     "market_occ": round(blend[m] / 100, 2)})
    annual = round(sum(ly.values()) / 12)
    return rows, annual, blend

def pick_photos(photos, n, name, area, guests):
    if not photos: return []
    chosen = []
    clean = [p for p in photos if not any(j in p["label"].lower() for j in JUNK)]
    if not clean: clean = photos
    photos = clean
    categorised = sum(1 for p in photos if _cat(p["label"]))
    if photos[0]["label"] and categorised >= 4:
        ok = lambda p: not any(s.lower() in p["label"].lower() for s in SKIP) and p not in chosen
        # pass 1: one photo per category (exteriors first, then each room); pass 2: the extra exterior/pool shots
        for cap_pass in (1, 2):
            for prefix, cap in PHOTO_PLAN:
                if cap < cap_pass or len(chosen) >= n: continue
                have = sum(1 for p in chosen if _cat(p["label"]) == prefix)
                for p in photos:
                    if have >= cap_pass: break
                    if _cat(p["label"]) == prefix and ok(p): chosen.append(p); have += 1
        if len(chosen) < n:  # fill up, but one photo per distinct caption: no triple living room
            used = {re.sub(r"[^a-z]", "", p["label"].lower())[:28] for p in chosen}
            for p in photos:
                if len(chosen) >= n: break
                if p in chosen or any(s.lower() in p["label"].lower() for s in SKIP): continue
                k = re.sub(r"[^a-z]", "", p["label"].lower())[:28]
                if k in used: continue
                used.add(k); chosen.append(p)
            chosen += [p for p in photos if p not in chosen][: n - len(chosen)]
    else:
        # free-text captions: take the listing's own order (hosts put their best first)
        # but never three near-identical shots — one per distinct caption.
        seen_lbl = set()
        for p in photos:
            key = re.sub(r"[^a-z]", "", p["label"].lower())[:28]
            if key in seen_lbl: continue
            seen_lbl.add(key); chosen.append(p)
            if len(chosen) >= n: break
        if len(chosen) < n:
            chosen += [p for p in photos if p not in chosen][: n - len(chosen)]
    chosen = chosen[:n]
    out, used = [], {}
    for p in chosen:
        cat = _cat(p["label"])
        caps = CAPTIONS.get(cat, [""]); i = used.get(cat, 0); used[cat] = i + 1
        cap = caps[min(i, len(caps) - 1)].format(name=name, area=area, guests=guests or "twelve")
        out.append({"url": p["url"], "url_hd": p.get("url_hd", p["url"]), "caption": cap, "label": p["label"]})
    return out

def build_config(L, a):
    d = CFG["defaults"]; existing = None
    _area_guess = a.area or (MARKET["zones"].get(zone_for(L.get("city"), a.area), {}) or {}).get("label", "")
    name = a.name or clean_name(L.get("title") or "Villa", L.get("description", ""), _area_guess, L.get("bedrooms"))
    slug = a.slug or slugify(name)
    cfg_path = HERE / "villas" / f"{slug}.json"
    if cfg_path.exists() and not a.fresh:
        existing = json.loads(cfg_path.read_text(encoding="utf-8"))
    zone = zone_for(L.get("city"), a.area) or (existing or {}).get("zone")
    if not zone: sys.exit(f"zone not recognised for city '{L.get('city')}' — pass --area Canggu|Seminyak|Pererenan|Berawa|Uluwatu")
    Z = MARKET["zones"][zone]; area = a.area or Z["label"]
    br = a.bedrooms or L.get("bedrooms") or (existing or {}).get("bedrooms") or 4
    guests = L.get("guests") or (existing or {}).get("guests") or br * 2
    ls, annual, blend = low_season(zone, d["low_season_months"])
    if a.adr: adr, adr_src = int(a.adr), "owner/listing"
    elif existing and existing.get("adr"): adr, adr_src = existing["adr"], existing.get("adr_source", "existing")
    else:
        p75 = Z["adr_p75_idr"].get(str(min(max(br, min(map(int, Z["adr_p75_idr"]))), max(map(int, Z["adr_p75_idr"])))))
        adr, adr_src = int(round(p75 / MARKET["usd_idr"] / 50) * 50), "market_p75 (PriceLabs, no ADR given)"
    months_txt = ", ".join(m["month"][:3] for m in ls)
    photos = pick_photos(L.get("photos", []), a.photos or d["max_photos"], name, area, guests)
    desc = (L.get("description") or "").strip()
    first_para = next((p.strip() for p in re.split(r"\n\s*\n", desc) if len(p.strip()) > 80), desc[:300])
    amen = [x for x in L.get("amenities", []) if x.lower() not in ("essentials", "hot water", "hair dryer", "shampoo", "body soap", "cleaning products", "cooking basics", "dishes and silverware")][:10]
    facts = [{"n": str(br), "l": "Bedrooms"}, {"n": str(guests), "l": "Guests"}]
    if L.get("rating"): facts.append({"n": f'{L["rating"]}★', "l": f'{L.get("reviews") or ""} reviews'.strip()})
    facts.append({"n": area, "l": "Bali"})
    cfg = {
        "slug": slug, "name": name, "area": area, "zone": zone, "island": d["island"], "bedrooms": br, "guests": guests,
        "currency": d["currency"], "adr": adr, "adr_source": adr_src,
        "source_url": L.get("url"), "listing_id": L.get("listing_id"), "city_raw": L.get("city"),
        "hero_title": f"{name}.<br><em>{area},</em> {d['island']}.",
        "photos": photos,
        "story_title": f"{br} bedrooms, one pool, <em>the whole group under one roof.</em>",
        "story_lead": first_para[:420],
        "story_points": [f"{br} ensuite bedrooms for up to {guests} guests", "Private pool, garden and open living pavilion",
                         "Full-time staff, daily housekeeping, private chef on request", f"{area}'s beaches, cafés and beach clubs within minutes"],
        "facts": facts[:4],
        "book_lead": "Rates include staff, daily housekeeping and airport transfers. Minimum three nights; five over Christmas and New Year.",
        "rate_range": ({"currency": "IDR", "low": a.rates_idr[0] * 1e6, "high": a.rates_idr[1] * 1e6, "usd_low": round(a.rates_idr[0] * 1e6 / MARKET["usd_idr"]), "usd_high": round(a.rates_idr[1] * 1e6 / MARKET["usd_idr"])} if a.rates_idr else None),
        "amenities": amen or ["Private pool", "Chef on request", "Daily housekeeping", "Airport transfers", "Fast Wi-Fi", "Air-conditioned bedrooms"],
        "book_url": wa_link(a.handle) or (existing or {}).get("book_url") or L.get("url"),  # "Check availability" always goes to THEM: their WhatsApp, else their own listing — never our number
        "owner_pitch": True,
        "low_season": ls, "annual_market_occ": annual,
        "capture_rate": d["capture_rate"], "commission": d["commission"],
        "site_price": f"Included · {d['currency']}{d['site_price_oneoff']} + {d['currency']}{d['site_price_monthly']}/mo on its own",
        "gap_source": f"Source: PriceLabs market data, {Z['label']}, {Z['br_band']} villas ({Z['compset']} listings), pulled {MARKET['pulled']}: last-year market occupancy by month, lowest in {months_txt}; annual average {annual}%.",
        "market": {"zone": zone, "compset": Z["compset"], "br_band": Z["br_band"], "occ_ly": Z["occ_ly"], "pulled": MARKET["pulled"]},
        "cta_title": "Your low season, filled. <em>10% on the nights we sell,</em> nothing else.",
        "cta_text": "Fifteen minutes on WhatsApp to walk through the numbers for your villa. We take a handful of villas per area for the low season.",
        "whatsapp": CFG["whatsapp"],
        "contact": {"name": a.contact or "", "first_name": a.first_name or "", "handle": a.handle or "", "channel": a.channel},
        "generated": datetime.date.today().isoformat(),
    }
    if existing:  # keep hand edits: everything except the refreshed market/adr/contact blocks
        keep = {k: v for k, v in existing.items() if k not in ("low_season", "annual_market_occ", "gap_source", "market", "generated", "adr", "adr_source")}
        if a.photos and not existing.get("photos_locked"): keep.pop("photos", None)
        for k in ("name", "first_name", "handle") if a.contact or a.first_name or a.handle else (): keep.get("contact", {}).pop(k, None)
        merged = {**cfg, **keep}
        if keep.get("contact") is not None: merged["contact"] = {**cfg["contact"], **{k: v for k, v in keep["contact"].items() if v}}
        cfg = merged
    return cfg_path, cfg

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url"); ap.add_argument("--adr", type=float); ap.add_argument("--name"); ap.add_argument("--area"); ap.add_argument("--slug")
    ap.add_argument("--rates-idr", type=float, nargs=2, metavar=("LOW_M", "HIGH_M"), help="nightly range in millions of IDR, e.g. 10 16"); ap.add_argument("--bedrooms", type=int); ap.add_argument("--photos", type=int); ap.add_argument("--first-name"); ap.add_argument("--contact"); ap.add_argument("--handle")
    ap.add_argument("--channel", default="whatsapp"); ap.add_argument("--clips", action="store_true"); ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--no-commit", action="store_true"); ap.add_argument("--push", action="store_true"); ap.add_argument("--days", nargs=2, default=("Tuesday", "Thursday"))
    a = ap.parse_args()
    print("1/6 fetching listing…"); L = fetch_listing(a.url)
    print(f"    {L.get('title')!r} | {L.get('city')} | {L.get('bedrooms')}BR / {L.get('guests')} guests | {len(L.get('photos', []))} photos | rating {L.get('rating')} ({L.get('reviews')} reviews)")
    cfg_path, cfg = build_config(L, a)
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"2/6 config -> {cfg_path.relative_to(HERE.parent)} | zone {cfg['zone']} | ADR ${cfg['adr']} ({cfg['adr_source']}) | low season {[m['month'][:3] + ' ' + str(int(m['market_occ']*100)) + '%' for m in cfg['low_season']]}")
    if a.clips:
        print("3/6 clips…"); subprocess.run([sys.executable, str(HERE / "make_clips.py"), cfg["slug"]], check=True)
    else: print("3/6 clips skipped (--clips to render Ken Burns tour clips)")
    out = generate_villa.build(cfg_path); print(f"4/6 page -> {out.relative_to(HERE.parent)}")
    msg, g = make_message.write(cfg["slug"], a.first_name, tuple(a.days)); print(f"5/6 message -> {msg.relative_to(HERE.parent)} | {g['empty']} empty nights, ${g['loss']:,.0f} not earned, target +{g['target']} nights")
    funnel.add(cfg["slug"], a.contact or "", a.handle or "", a.channel); print("6/6 funnel row added/updated (status draft)")
    if not a.no_commit:
        root = HERE.parent
        subprocess.run(["git", "-C", str(root), "add", "villa-site"], check=True)
        r = subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", f"villa-site: {cfg['name']} ({cfg['area']}, {cfg['bedrooms']}BR) page + outreach\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"])
        print("    committed" if r.returncode == 0 else "    nothing to commit")
        if a.push: subprocess.run(["git", "-C", str(root), "push"], check=False)
    print(f"\nOwner page : {CFG['base_url']}/villa-site/{cfg['slug']}?owner   (public once the branch is on main)")
    print(f"Guest site : {CFG['base_url']}/villa-site/{cfg['slug']}")
    print(f"Message    : open {msg.relative_to(HERE.parent)}, copy step 1, then  python3 funnel.py set {cfg['slug']} sent")

if __name__ == "__main__":
    main()
