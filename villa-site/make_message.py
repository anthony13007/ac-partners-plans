#!/usr/bin/env python3
"""Generate the outreach sequence for one villa from villas/<slug>.json.

  python3 make_message.py <slug> [--first-name Name] [--days "Tuesday" "Thursday"]

Writes outreach/<slug>.md (step 1 hook, IG variant, step 2 offer, step 3 fallback,
follow-ups J+3 / J+7 / J+14) with the numbers of the owner page. Nothing is sent.
"""
import json, sys, pathlib, argparse, datetime

HERE = pathlib.Path(__file__).resolve().parent
CFG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))

def money(n, cur="$"):
    return f"{cur}{int(round(n)):,}"

def gap(cfg):
    """Same maths as template.html owner section."""
    adr = cfg["adr"]; rows = []
    tot_n = tot_e = tot_l = 0
    for m in cfg["low_season"]:
        e = round(m["days"] * (1 - m["market_occ"])); l = e * adr
        rows.append((m["month"], m["days"], m["market_occ"], e, l)); tot_n += m["days"]; tot_e += e; tot_l += l
    occ = 1 - tot_e / tot_n if tot_n else 0
    target = round(tot_e * cfg.get("capture_rate", CFG["defaults"]["capture_rate"]))
    added = target * adr
    fee = added * cfg.get("commission", CFG["defaults"]["commission"])
    return dict(rows=rows, nights=tot_n, empty=tot_e, loss=tot_l, occ=occ, target=target, added=added, fee=fee)

def build(cfg, first_name=None, days=("Tuesday", "Thursday")):
    s = CFG["sender"]; d = CFG["defaults"]
    g = gap(cfg)
    cur = cfg.get("currency", "$")
    first = first_name or cfg.get("contact", {}).get("first_name") or "there"
    villa = cfg["name"]; area = cfg["area"]; br = cfg["bedrooms"]
    months = [m["month"].split(" ")[0] for m in cfg["low_season"]]
    months_txt = ", ".join(months[:-1]) + " and " + months[-1] if len(months) > 1 else months[0]
    url = f'{CFG["base_url"]}/villa-site/{cfg["slug"]}?owner'
    site_url = f'{CFG["base_url"]}/villa-site/{cfg["slug"]}'
    adr = money(cfg["adr"], cur); loss = money(g["loss"], cur); occ = round(g["occ"] * 100)
    guarantee = max(5, round(g["target"] * d.get("guarantee_nights_share", 0.5)))
    compset = cfg.get("market", {}).get("compset", 350)
    site_price = f'{cur}{d["site_price_oneoff"]} + {cur}{d["site_price_monthly"]}/month'

    step1 = f"""Hi {first}, Anthony here — Airbnb Superhost for {s['superhost_years']} years ({s['reviews']} reviews, {s['rating']}★), I run {s['brand']}, ~{s['villas']} luxury villas in Canggu, Seminyak and Uluwatu.

I came across {villa} while benchmarking {area} and ran it through our PriceLabs market data. {br}-bedroom villas around you sit at ~{occ}% occupancy in {months_txt}. At your ~{adr}/night that is about {g['empty']} empty nights and {loss} not earned per low season.

I put the numbers on a private page for you, with a site for the villa built from your photos (4-min scroll). Want the link?"""

    step1_ig = f"""Hi {first} — Superhost here, {s['villas']} villas in Bali. Ran {villa} through our low-season data: about {loss} left on the table in {months_txt}. Made you a 4-min page + a site for the villa, want it?"""

    step2 = f"""Here it is: {url}

Two things on that page:
1. The gap: {g['empty']} empty low-season nights at {adr}, from PriceLabs data on {compset} villas around you.
2. What we do about it: we co-list {villa} on our channels (Airbnb Superhost profile, Booking.com, Expedia, VRBO, Marriott Homes & Villas, plus our {s['brand']} guest base: repeat guests, groups, retreats), one synced calendar, dynamic pricing. You keep the management, the staff and the ops.

The deal, all of it:
• {round(cfg.get('commission', d['commission'])*100)}% on the nights we sell. Nothing on the nights you sell yourself.
• No set-up fee, no exclusivity, no minimum term. Stop whenever you want.
• The site you just scrolled is yours, on your own domain, the day we go live ({site_price} on its own, {cur}0 for partners).
• One-page report on the 1st of every month: channel mix, occupancy, ADR, incremental revenue.
• If we have not sold {guarantee} nights by the end of the first low season, you keep the site and walk away. Nothing owed.

For reference, {s['proof']}. Same playbook.

15 minutes on WhatsApp this week? I have {days[0]} and {days[1]} open."""

    step3 = f"""Understood, no problem. One lighter option, zero commitment:
we feature {villa} as a highlight on the {s['brand']} guest site and in our guest emails (repeat guests, groups, retreats looking for large villas). You handle the booking directly. We take {round(d['highlight_commission']*100)}% on a booking we send you, nothing otherwise.

If a low-season enquiry lands, you'll be glad it was there. Shall I add it?"""

    fu3 = f"""Hi {first}, did the page load OK on your side? {url}
Happy to walk you through the {g['empty']} nights in 10 min, or send the calc as a PDF."""
    fu7 = f"""{first}, one number from our side: {s['proof']}.
Same channels, same pricing engine, for {villa}. The site stays yours either way. 10 min this week?"""
    fu14 = f"""Last one from me, {first}. We're closing the Bali low-season partner list this month (a handful of villas, one per street). Want the spot for {villa}, or shall I pass?
Either way, the site is here whenever you want it: {site_url}"""

    today = datetime.date.today()
    md = f"""# Outreach — {villa} ({area}, {br}BR)

Generated {today.isoformat()} · owner page: {url} · guest site: {site_url}
Numbers: {g['empty']} empty nights / {g['nights']} in {months_txt} (market {occ}%), {loss} not earned at {adr}/night; we target +{g['target']} nights = {money(g['added'], cur)} added, our fee {money(g['fee'], cur)}.
Contact: {cfg.get('contact', {}).get('name', '')} {cfg.get('contact', {}).get('handle', '')} via {cfg.get('contact', {}).get('channel', 'whatsapp')}

## Step 1 — hook (WhatsApp)
```
{step1}
```

## Step 1 — Instagram DM variant
```
{step1_ig}
```

## Step 2 — the page + the offer (send after a "yes")
```
{step2}
```

## Step 3 — fallback highlight (send after a "no")
```
{step3}
```

## Follow-up J+3 ({(today + datetime.timedelta(days=3)).isoformat()})
```
{fu3}
```

## Follow-up J+7 ({(today + datetime.timedelta(days=7)).isoformat()}) — attach a PriceLabs screenshot of one of our villas at 100% vs market
```
{fu7}
```

## Follow-up J+14 ({(today + datetime.timedelta(days=14)).isoformat()}) — last
```
{fu14}
```
"""
    return md, g

def write(slug, first_name=None, days=("Tuesday", "Thursday")):
    cfg = json.loads((HERE / "villas" / f"{slug}.json").read_text(encoding="utf-8"))
    md, g = build(cfg, first_name, days)
    out = HERE / "outreach" / f"{slug}.md"; out.parent.mkdir(exist_ok=True)
    out.write_text(md, encoding="utf-8")
    return out, g

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("slug"); ap.add_argument("--first-name"); ap.add_argument("--days", nargs=2, default=("Tuesday", "Thursday"))
    a = ap.parse_args()
    out, g = write(a.slug, a.first_name, tuple(a.days))
    print("wrote", out.relative_to(HERE.parent), "| empty nights", g["empty"], "| loss", money(g["loss"]))
