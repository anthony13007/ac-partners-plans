#!/usr/bin/env python3
"""Prospection Bali — la cle cockpit « bali_prospects » (section « Bali — villas » de l'onglet Prospection).

  python3 villa-site/bali_prospects.py                 # calendriers + decouverte + push
  python3 villa-site/bali_prospects.py --no-discover   # seulement les villas deja suivies (rapide)
  python3 villa-site/bali_prospects.py --no-push       # ecrit le JSON sans l'envoyer au cockpit

Chaque matin (launchd com.acpartners.bali-prospects) :
  1. relit le calendrier Airbnb public de chaque villa suivie (bali_prospects.curated.json, tenu a la main),
     et compte ses nuits libres sur la fenetre M+1 → M+3 (hors fetes : decembre 1-20, janvier 6-31) ;
  2. cherche de nouvelles villas 5 ch.+ sur les zones (find_leads), ecarte AVOID / HOLD / BIG_PM / OURS,
     les exclusions a la main et tout ce qui est deja dans le funnel du site ; ne garde que les villas
     dont le calendrier est nettement plus vide que le secteur ;
  3. ecrit Dashboard/bali_prospects.json et le pousse dans le cockpit (PUT /api/cockpit/data/bali_prospects).

Regles : jamais d'envoi automatique (Anthony clique « Open » puis envoie lui-meme, 8 par jour) ; le message 1
pose une question, sans page ; Uluwatu est un secteur plein (> 55 %) : l'argument n'est pas la basse saison
mais « le marche est plein, pas votre calendrier », et on ne garde que les villas tres en dessous du secteur.
On ecrit toujours « your Airbnb calendar » : un calendrier presque vide peut etre non synchronise.
"""
import argparse, datetime, json, pathlib, re, sys, urllib.request, urllib.error

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import villa                                   # noqa: E402  (MARKET, zone_for, MONTHS, LONG, DAYS)
from fetch_listing import fetch_calendar       # noqa: E402
import find_leads                              # noqa: E402  (search_ids, fetch_cached, screen)
import diagnostic                              # noqa: E402  (api → funnel du site)

CURATED = HERE / "bali_prospects.curated.json"
DASH = pathlib.Path.home() / "Documents/Claude/Projects/AC Partners/Dashboard"
OUT = DASH / "bali_prospects.json"
PUSH_CFG = DASH / ".cockpit-push.json"
ZONE_KEY = {"Uluwatu": "uluwatu", "Canggu": "canggu", "Pererenan": "pererenan", "Berawa": "berawa", "Seminyak": "seminyak"}
# zone de prospection d'apres la ville Airbnb (Umalas, Kerobokan → Canggu ; Pecatu, Bingin → Uluwatu)
MIN_BR = 5
PAGES = 2
MAX_FETCH = 30


def window(today=None):
    """Les 3 mois qui suivent le mois en cours, fetes retirees (peak_windows du marche) : [{ym, from, to, days, month}].
    Meme decoupage que les pages diagnostic, mais SANS le seuil d'occupation : a Uluwatu le secteur est plein et
    c'est justement l'argument."""
    t = today or datetime.date.today()
    peak = villa.MARKET.get("peak_windows", {})
    rows = []
    for i in range(1, 4):
        y, m = t.year + (t.month + i - 1) // 12, (t.month + i - 1) % 12 + 1
        mon = villa.MONTHS[m - 1]
        w = peak.get(villa.LONG[mon], {}) if isinstance(peak.get(villa.LONG[mon]), dict) else {}
        rows.append({"ym": f"{y}-{m:02d}", "month": mon, "label": w.get("label", villa.LONG[mon]),
                     "from": w.get("from", 1), "to": w.get("to", villa.DAYS[mon]),
                     "days": w.get("to", villa.DAYS[mon]) - w.get("from", 1) + 1})
    return rows


def market_occ(zone_key, rows):
    """Occupation du secteur par mois de la fenetre (moyenne LY / annee precedente quand elle existe), en %."""
    z = villa.MARKET["zones"][zone_key]
    ly, prev = z["occ_ly"], z.get("occ_prev", {})
    return {r["month"]: round((ly[r["month"]] + prev[r["month"]]) / 2 if r["month"] in prev else ly[r["month"]]) for r in rows}


def read_calendar(lid, rows):
    """Nuits libres de la villa sur la fenetre, mois par mois : {month: {open, days}} ou None si illisible."""
    cal = fetch_calendar(lid)
    if not cal: return None
    by = {d["date"]: d["available"] for d in cal}
    out = {}
    for r in rows:
        days = [f"{r['ym']}-{d:02d}" for d in range(r["from"], r["to"] + 1)]
        if not all(d in by for d in days): return None  # calendrier qui ne couvre pas la fenetre
        out[r["month"]] = {"open": sum(1 for d in days if by[d]), "days": len(days)}
    return out


def assess(cal, rows, occ_area):
    """-> dict(free, nights, occ, month_empty, month_label, month_open, month_days, month_area) a partir du calendrier."""
    nights = sum(r["days"] for r in rows)
    free = sum(cal[r["month"]]["open"] for r in rows)
    # le mois le plus vide de la villa (en proportion), pour l'accroche
    worst = max(rows, key=lambda r: cal[r["month"]]["open"] / cal[r["month"]]["days"])
    return {"free": free, "nights": nights, "occ": round(100 * (1 - free / nights)),
            "month": worst["month"], "month_label": worst["label"], "month_open": cal[worst["month"]]["open"],
            "month_days": cal[worst["month"]]["days"], "month_area": occ_area[worst["month"]]}


def auto_message(v, a, hook):
    """Message 1 pour une villa sans message personnalise : accroche, un constat, une question, pas de page."""
    name = v.get("en") or v["name"].split(" (")[0]   # nom tel qu'il se dit en anglais, sans la note entre parentheses
    zone = v["zone"]
    if a["month_open"] >= a["month_days"] - 1:
        claim = (f"{zone} villas run at about {a['month_area']}% occupancy in {villa.LONG[a['month']]}, "
                 f"yet your Airbnb calendar is still open for the whole month.")
    else:
        claim = (f"it still shows {a['free']} open nights between December and February, "
                 f"while the area sits at about {round(sum(v['_occ_area'].values()) / len(v['_occ_area']))}%.")
    return f"{hook}\n\nI came across {name} while benchmarking {zone}: {claim}\n\nMind if I share what I'm seeing?"


def keep(zone, a, occ_area_avg):
    """Garde-fou : on ne propose que les villas nettement plus vides que leur secteur."""
    if zone == "Uluwatu":
        return a["occ"] <= occ_area_avg / 2        # secteur plein : il faut un calendrier TRES en dessous
    return a["occ"] < occ_area_avg - 10 and a["free"] >= 30


def funnel_index():
    """Statut reel du funnel du site par slug, plus les noms de villas deja suivies (pour ne pas les re-decouvrir)."""
    try:
        code, j = diagnostic.api("GET", "/diagnostics/funnel")
        rows = j.get("funnel", []) if code == 200 else []
    except Exception as e:  # noqa: BLE001
        print(f"  ! funnel illisible : {e}"); rows = []
    return {r["slug"]: r for r in rows}, {re.sub(r"\W+", " ", (r.get("villa") or "").lower()).strip() for r in rows}


def zone_of(L, area_hint):
    z = villa.zone_for(L.get("city") or "", area_hint, L.get("title") or "")
    label = {v: k for k, v in ZONE_KEY.items()}.get(z)
    return label or area_hint


def discover(cur, rows, known_ids, funnel_names):
    """Nouvelles villas 5 ch.+ sur les zones, filtrees comme find_leads, hors exclusions et funnel."""
    found = []
    ci, co = f"{rows[0]['ym']}-{rows[0]['from'] + 4:02d}", None
    d0 = datetime.date.fromisoformat(ci); co = (d0 + datetime.timedelta(days=5)).isoformat()
    for zone in cur["zones"]:
        seen = []
        for page in range(PAGES):
            try:
                seen += [i for i in find_leads.search_ids(zone, MIN_BR, ci, co, offset=page * 18) if i not in seen]
            except Exception as e:  # noqa: BLE001
                print(f"  ! {zone} p{page}: {e}")
        print(f"  {zone}: {len(seen)} annonces vues")
        for lid in seen[:MAX_FETCH]:
            if lid in known_ids: continue
            try:
                L = find_leads.fetch_cached(f"https://www.airbnb.com/rooms/{lid}", lid)
            except Exception as e:  # noqa: BLE001
                print(f"  ! {lid}: {e}"); continue
            if (L.get("bedrooms") or 0) < MIN_BR: continue
            ok, why = find_leads.screen(L)
            if not ok: print(f"  - {lid} ecartee : {why}"); continue
            name = re.sub(r"^\*?NEW\*?\s*", "", L.get("title") or "")[:60]
            if re.sub(r"\W+", " ", name.lower()).strip() in funnel_names: continue
            found.append({"id": lid, "name": name, "zone": zone_of(L, zone), "area": L.get("city") or zone, "br": L.get("bedrooms"),
                          "contact": f"hôte {L['host']}" if L.get("host") else "", "wa": "", "status": "contact_to_find",
                          "manager": why or "", "discovered": datetime.date.today().isoformat()})
            known_ids.add(lid)
    return found


def push(body):
    cfg = json.loads(PUSH_CFG.read_text())
    req = urllib.request.Request(f"{cfg['base']}/api/cockpit/data/bali_prospects", data=body, method="PUT",
                                 headers={"Content-Type": "application/json", "x-cockpit-token": cfg["token"], "User-Agent": "ac-cockpit-push"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-discover", action="store_true"); ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args()
    cur = json.loads(CURATED.read_text(encoding="utf-8"))
    rows = window()
    nights = sum(r["days"] for r in rows)
    print(f"fenetre : {' + '.join(r['label'] for r in rows)} = {nights} nuits")
    funnel, funnel_names = funnel_index()
    excluded_ids = {e["id"] for e in cur["excluded"]}
    known = {v["id"] for v in cur["villas"]} | excluded_ids
    for v in cur["villas"]:
        for x in v.get("extra", []):
            m = re.search(r"/rooms/(\d+)", x["url"]); known.add(m.group(1)) if m else None

    # villas decouvertes les jours precedents (gardees dans le JSON de sortie, pas dans le fichier a la main)
    prev = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    carried = [v for v in prev.get("villas", []) if v.get("discovered") and v["id"] not in known and v["id"] not in excluded_ids]
    known |= {v["id"] for v in carried}

    villas = [dict(v) for v in cur["villas"]] + carried
    if not a.no_discover:
        print("decouverte…")
        villas += discover(cur, rows, known, funnel_names)

    out, dropped = [], []
    for v in villas:
        zone = v["zone"] if v["zone"] in ZONE_KEY else "Canggu"
        occ_area = market_occ(ZONE_KEY[v.get("cal_zone", zone)], rows)
        occ_area_avg = round(sum(occ_area[r["month"]] * r["days"] for r in rows) / nights)
        v["_occ_area"] = occ_area
        cal = read_calendar(v.get("cal_id", v["id"]), rows)
        if cal:
            ass = assess(cal, rows, occ_area); src = "calendar"
        elif v.get("seed"):
            s = v["seed"]; ass = {"free": s["free"], "nights": nights, "occ": s["occ"], "month": "", "month_label": "", "month_open": 0, "month_days": 0, "month_area": occ_area_avg}; src = "seed"
        else:
            dropped.append((v["name"], "calendrier illisible")); continue
        curated = v["id"] in {c["id"] for c in cur["villas"]}
        if not curated and not keep(zone, ass, occ_area_avg):
            dropped.append((v["name"], f"{ass['occ']} % vs secteur {occ_area_avg} % : pas assez d'ecart")); continue
        msg = v["msg"] if v.get("msg") else auto_message(v, ass, cur["hook"]) if src == "calendar" else ""
        f = funnel.get(v.get("slug") or "")
        out.append({
            "id": v["id"], "name": v["name"], "zone": zone, "area": v.get("area") or zone, "br": v.get("br"),
            "url": f"https://www.airbnb.com/rooms/{v['id']}", "extra": v.get("extra", []),
            "occ": ass["occ"], "occ_area": occ_area_avg, "free": ass["free"], "nights": nights, "source": src,
            "month_empty": ass["month_label"], "month_open": ass["month_open"], "month_days": ass["month_days"],
            "contact": v.get("contact", ""), "lead": v.get("lead", ""), "wa": v.get("wa", ""), "wa_verify": bool(v.get("wa_verify")),
            "status": v.get("status", "contact_to_find"), "note": v.get("note", ""), "manager": v.get("manager", ""),
            "slug": v.get("slug"), "funnel": {"status": f["status"], "page": f.get("page_url"), "next": f.get("next_action"), "last": str(f.get("last_touch") or "")[:10]} if f else None,
            "msg": msg.replace("{hook}", cur["hook"]), "discovered": v.get("discovered"),
        })
        print(f"  {ass['occ']:3d} % / {occ_area_avg} %  {ass['free']:2d}/{nights}  {v['name'][:45]}  [{src}]")
    for name, why in dropped: print(f"  - {name[:45]} : {why}")

    order = {z: i for i, z in enumerate(cur["zones"])}
    out.sort(key=lambda v: (order.get(v["zone"], 9), v["occ"]))
    data = {"updated": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"), "prepared": cur["prepared"],
            "window": {"label": " + ".join(r["label"] for r in rows), "from": f"{rows[0]['ym']}-{rows[0]['from']:02d}",
                       "to": f"{rows[-1]['ym']}-{rows[-1]['to']:02d}", "nights": nights, "market_pulled": villa.MARKET["pulled"]},
            "hook": cur["hook"], "zones": cur["zones"], "villas": out, "excluded": cur["excluded"], "dropped": [{"name": n, "why": w} for n, w in dropped]}
    body = json.dumps(data, ensure_ascii=False, indent=1).encode()
    OUT.write_text(body.decode(), encoding="utf-8")
    print(f"{len(out)} villas -> {OUT}")
    if not a.no_push:
        try:
            r = push(body); print(f"  ✓ cockpit bali_prospects : {r.get('bytes', 0) // 1024} ko")
        except urllib.error.HTTPError as e:
            print(f"  ✗ cockpit : HTTP {e.code} {e.read().decode(errors='replace')[:120]}")
        except Exception as e:  # noqa: BLE001
            print(f"  ✗ cockpit : {e}")


if __name__ == "__main__":
    main()
