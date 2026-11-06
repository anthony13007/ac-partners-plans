#!/usr/bin/env python3
"""Prospection Bali en ligne de commande : qualifier une annonce Airbnb, creer sa page de diagnostic
sur ac-collection.com, sortir les 3 messages, suivre le funnel du site.

  python3 villa-site/diagnostic.py check  <url|id> [<url|id> ...] [--adr 650]     # ne cree rien
  python3 villa-site/diagnostic.py create <url|id> [--adr 650] [--rates-idr 10 16] [--first-name Ketut]
                                          [--contact "Ketut (owner)"] [--handle "+62 8xx"] [--commission 12]
  python3 villa-site/diagnostic.py funnel [--status sent]                         # le funnel du site
  python3 villa-site/diagnostic.py set <slug> sent --note "WhatsApp, message 1"
  python3 villa-site/diagnostic.py market                                         # occupation par zone, mois creux

check lit l'annonce et son calendrier public, applique les memes regles que le site (zone, mois creux,
nuits reellement libres) et donne un verdict. create fait la meme lecture, refuse ce qui ne doit pas
etre prospecte, puis demande la page au site (POST /api/diagnostics) et ecrit outreach/<slug>.md avec
les liens de la page. Le funnel est celui du site (table villa_funnel), pas funnel.csv.

Jeton de routine : ~/.local/share/ac-owner-diagnostic/config.json {"token", "base"} ; jamais affiche.
"""
import argparse, datetime, json, pathlib, re, sys, urllib.error, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_message, villa  # noqa: E402
from fetch_listing import fetch_listing  # noqa: E402
from find_leads import screen  # noqa: E402

CFG_PATH = pathlib.Path.home() / ".local/share/ac-owner-diagnostic/config.json"
STATUSES = ["draft", "sent", "replied", "call", "signed", "highlight", "refused", "dead"]
DAILY_CAP = 8  # envois par jour (regle d'Anthony)


def api(method, path, body=None):
    cfg = json.loads(CFG_PATH.read_text(encoding="utf-8"))
    req = urllib.request.Request(
        cfg["base"].rstrip("/") + "/api" + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"x-pdf-job-token": cfg["token"], "Content-Type": "application/json", "User-Agent": "ac-diagnostic-cli/1"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read().decode() or "{}")
        except Exception: return e.code, {"error": f"HTTP {e.code}"}  # noqa: BLE001


def listing_url(ref):
    ref = ref.strip()
    if ref.isdigit(): return f"https://www.airbnb.com/rooms/{ref}"
    m = re.search(r"airbnb\.[a-z.]+/(?:rooms|h)/(\d+)", ref)
    return f"https://www.airbnb.com/rooms/{m.group(1)}" if m else ref


def assess(ref, a):
    """-> dict(url, ok, verdict, cfg?, gap?). ok = une page peut etre creee et la villa peut etre contactee."""
    url = listing_url(ref); out = {"url": url, "ok": False}
    if "airbnb." not in url: return {**out, "verdict": "pas un lien Airbnb : le site ne lit que airbnb.com/rooms/<id>"}
    L = fetch_listing(url)
    if not L.get("title") or not L.get("photos"): return {**out, "verdict": "annonce illisible (en pause, privee ou retiree)"}
    keep, why = screen(L)
    if not keep: return {**out, "verdict": f"NE PAS PROSPECTER : {why}", "title": L.get("title")}
    if (L.get("bedrooms") or 0) < 2: return {**out, "verdict": "hors cible : moins de 2 chambres", "title": L.get("title")}
    ns = argparse.Namespace(name=getattr(a, "name", None), area=getattr(a, "area", None), slug=None, bedrooms=None, adr=a.adr,
                            rates_idr=getattr(a, "rates_idr", None), photos=None, first_name=getattr(a, "first_name", None),
                            contact=getattr(a, "contact", None), handle=getattr(a, "handle", None),
                            channel=getattr(a, "channel", "whatsapp"), fresh=True, calendar=None, no_calendar=False)
    try:
        _, cfg = villa.build_config(L, ns)
    except SystemExit as e:
        return {**out, "verdict": f"zone hors marche : {e}", "title": L.get("title")}
    g = make_message.gap(cfg)
    out.update(cfg=cfg, gap=g, title=L.get("title"), manager=why)
    if not cfg["low_season"]:
        return {**out, "verdict": f"pas de page : {cfg['area']} depasse le seuil d'occupation sur les 3 prochains mois (secteur plein)"}
    if g["real"] and g["empty"] == 0: return {**out, "verdict": "pas de page : calendrier complet sur les mois creux"}
    notes = []
    if not g["real"]: notes.append("calendrier illisible, nuits estimees d'apres le marche")
    elif g["empty"] == g["nights"]: notes.append("calendrier 100 % ouvert : souvent une annonce non synchronisee, a verifier avant d'envoyer")
    if g["real"] and g["own"] > g["occ"]: notes.append("plus remplie que son secteur : argument plus faible")
    if (cfg["bedrooms"] or 0) < 4: notes.append("moins de 4 chambres : hors du coeur de cible")
    if why: notes.append(f"geree par {why} : viser le gestionnaire")
    return {**out, "ok": True, "verdict": "OK" + (" — " + " ; ".join(notes) if notes else "")}


def show(r):
    print(f"\n{r.get('title') or r['url']}\n  {r['url']}")
    cfg, g = r.get("cfg"), r.get("gap")
    if cfg and g and cfg["low_season"]:
        months = ", ".join(f"{m['month'].split(' ')[0][:3]} {m['open'] if isinstance(m.get('open'), int) else '~' + str(round(m['days'] * (1 - m['market_occ'])))}/{m['days']}" for m in cfg["low_season"])
        rate = "prix du secteur" if str(cfg.get("adr_source", "")).startswith("market_p75") else "prix donne"
        print(f"  {cfg['area']} · {cfg['bedrooms']} ch · ${cfg['adr']}/nuit ({rate})")
        print(f"  nuits {'libres' if g['real'] else 'vides (estimation)'} : {g['empty']}/{g['nights']} ({months})")
        print(f"  occupation : villa {round(g['own'] * 100)} % · secteur {round(g['occ'] * 100)} %   |   ${g['loss']:,.0f} encore a vendre, cible {g['target']} nuits")
    print(f"  -> {r['verdict']}")


def cmd_check(a):
    for ref in a.urls: show(assess(ref, a))


def cmd_create(a):
    r = assess(a.url, a); show(r)
    if not r["ok"]: sys.exit(1)
    body = {"url": r["url"], "adr": a.adr, "ratesIdr": a.rates_idr, "name": a.name, "area": a.area,
            "firstName": a.first_name, "contact": a.contact, "handle": a.handle, "channel": a.channel, "commission": a.commission}
    code, j = api("POST", "/diagnostics", {k: v for k, v in body.items() if v is not None})
    if code != 201: sys.exit(f"  le site a refuse (HTTP {code}) : {j.get('error')}")
    cfg = r["cfg"]; cfg["slug"] = j["slug"]
    if a.commission: cfg["commission"] = a.commission / 100
    md, g = make_message.build(cfg, a.first_name, owner_url=j["ownerPage"], guest_url=j["guestPage"])
    out = HERE / "outreach" / f"{j['slug']}.md"; out.parent.mkdir(exist_ok=True); out.write_text(md, encoding="utf-8")
    print(f"\n  page proprietaire : {j['ownerPage']}\n  page voyageur     : {j['guestPage']}")
    print(f"  chiffres du site  : {j['emptyNights']} nuits, ${j['loss']:,.0f}" + ("" if (j["emptyNights"], j["loss"]) == (g["empty"], g["loss"]) else f"   (lecture locale : {g['empty']} nuits, ${g['loss']:,.0f} : le calendrier a bouge entre les deux lectures, la page fait foi)"))
    print(f"  messages          : {out.relative_to(HERE.parent)}\n  funnel            : statut draft. Apres l'envoi : python3 villa-site/diagnostic.py set {j['slug']} sent")


def cmd_funnel(a):
    code, j = api("GET", "/diagnostics/funnel")
    if code != 200: sys.exit(f"le site a refuse (HTTP {code}) : {j.get('error')}")
    rows = j.get("funnel", []); today = datetime.date.today().isoformat()
    sent_today = sum(1 for x in rows if str(x.get("sent") or "")[:10] == today)
    counts = {s: sum(1 for x in rows if x.get("status") == s) for s in STATUSES}
    print("funnel du site : " + " · ".join(f"{s} {n}" for s, n in counts.items() if n) + f"   |   envoyes aujourd'hui : {sent_today}/{DAILY_CAP}")
    for x in rows:
        if a.status and x.get("status") != a.status: continue
        print(f"\n{x.get('status', ''):9} {x.get('villa')} ({x.get('area')}, {x.get('bedrooms')} ch) · {x.get('empty_nights')} nuits · ${int(x.get('loss') or 0):,}")
        print(f"          {x.get('slug')} · {x.get('contact') or 'contact ?'} {x.get('handle') or ''} · {x.get('page_url')}")
        print(f"          a faire : {x.get('next_action') or '-'} · dernier contact {str(x.get('last_touch') or '')[:10]}" + (f" · {x.get('notes')}" if x.get("notes") else ""))


def cmd_set(a):
    code, j = api("PUT", f"/diagnostics/funnel/{a.slug}", {"status": a.status, "note": a.note or ""})
    if code != 200: sys.exit(f"le site a refuse (HTTP {code}) : {j.get('error')}")
    row = j.get("row", {}); print(f"{row.get('slug')} -> {row.get('status')} · a faire : {row.get('next_action') or '-'}")


def cmd_market(a):
    M = villa.MARKET; thr = round(M.get("peak_occ_threshold", 0.55) * 100)
    print(f"Occupation du marche (PriceLabs Market Research, releve du {M['pulled']}), seuil des mois creux {thr} %")
    for name, z in M["zones"].items():
        rows, annual, _ = villa.low_season(name)
        soft = ", ".join(f"{m['month']} {round(m['market_occ'] * 100)} %" for m in rows) or "aucun mois creux : pas de page automatique"
        print(f"  {z['label']:10} {z['br_band']:7} {z.get('area', ''):36} annee {annual} %  |  {soft}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("urls", nargs="+"); c.add_argument("--adr", type=float); c.set_defaults(fn=cmd_check)
    c = sub.add_parser("create"); c.add_argument("url"); c.add_argument("--adr", type=float)
    c.add_argument("--rates-idr", type=float, nargs=2, metavar=("LOW_M", "HIGH_M")); c.add_argument("--name"); c.add_argument("--area")
    c.add_argument("--first-name"); c.add_argument("--contact"); c.add_argument("--handle"); c.add_argument("--channel", default="whatsapp")
    c.add_argument("--commission", type=float, help="en pourcent ; 10 par defaut (societe de gestion), 12 pour un proprietaire"); c.set_defaults(fn=cmd_create)
    c = sub.add_parser("funnel"); c.add_argument("--status", choices=STATUSES); c.set_defaults(fn=cmd_funnel)
    c = sub.add_parser("set"); c.add_argument("slug"); c.add_argument("status", choices=STATUSES); c.add_argument("--note"); c.set_defaults(fn=cmd_set)
    c = sub.add_parser("market"); c.set_defaults(fn=cmd_market)
    a = ap.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
