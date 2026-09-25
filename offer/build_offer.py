#!/usr/bin/env python3
"""MODÈLE OWNER (lancement de villa, marketing only) : offre AC Partners en PDF, à la première personne, charte AC.
Le MODÈLE B2B (management company, douleur chiffrée, en parallèle, 10 %) = villa-site/villa.py, pas ce script.

  python3 build_offer.py                                  # version générique
  python3 build_offer.py --villa "Palm Spring Villa" --area Canggu \
      --cover img-mcm/29.jpg --photos img-mcm/01.jpg img-mcm/04.jpg --out AC-Partners-Offer-Palm-Spring-Villa

Règles d'Anthony (25/09/2026) : pas de « low season », pas de pourcentage dans le titre,
« I » et jamais « we », preuves = profil Airbnb réel (795 avis, 4.8★, 10 ans, Superhost).
"""
import argparse, html, os, subprocess, json
HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(HERE, "..", "experiences", "img")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
COMMISSION = "12%"
HOST = {"reviews": 795, "rating": "4.8", "years": 10, "villas": "~30"}

STACK = [
  ("Distribution under my profile", "Your villa listed on my Airbnb profile (Superhost, 795 reviews, 4.8★, 10 years of hosting), then Booking.com, Expedia, VRBO and Marriott Homes & Villas. A villa that goes live on a profile guests already trust books faster than a listing starting from zero. My own playbook, a nightly pricing strategy set together with you, one calendar, no double bookings.", None, None),
  ("Your direct-booking site", "A site for your villa on your own domain: scroll film, gallery, enquiry button. Every booking it brings saves the 17% of OTA fees.", 690, 29),
  ("Highlight on ac-collection.com", "Featured on ac-collection.com and in my guest emails: repeat guests, groups and retreats looking for large villas. Bookings made there carry no OTA fees: 17% saved.", None, 29),
  ("Monthly report + market insights", "On the 1st of every month: channel mix, occupancy, ADR, PriceLabs market data and my pricing recommendations.", None, 19.99),
  ("PriceLabs strategy tool", "The dynamic-pricing engine behind my own villas, running on yours: seasonality, events, lead time, minimum stays.", None, 15),
  ("Guest app", "Digital guidebook and concierge chat for every guest I send: check-in, house manual, local recommendations.", None, 39),
  ("Instagram reel of the villa", "Shot from your photos, published on @acpartners.collection.", 290, None),
  ("Pricing set-up + listing audit", "PriceLabs configured for your villa; photos, title and text reviewed in the first week.", 290, None),
]
TERMS = ["Nothing on the nights you sell yourself", "No set-up fee, no minimum term", "Stop whenever you want"]

def fu(p): return "file://" + os.path.abspath(p)

def build(a):
    villa = a.villa
    worth = sum((p or 0) + (m or 0) * 12 for _, _, p, m in STACK)
    def was(p, m):
        parts = ([f"${p:,}"] if p else []) + ([f"${m:g}/mo"] if m else [])
        return " + ".join(parts)
    rows = "".join(f'<tr><td class="n">{i+1:02d}</td><td><b>{html.escape(t)}</b><p>{html.escape(d)}</p></td><td class="w">{("<s>"+was(p,m)+"</s>") if (p or m) else ""}<span>Included</span></td></tr>' for i, (t, d, p, m) in enumerate(STACK))
    terms = "".join(f"<li>{t}</li>" for t in TERMS)
    kicker = f"AC Collection · Bali · Prepared for {html.escape(villa)}" if villa else "AC Partners · Distribution partnership · Bali"
    intro = (f"<b>{html.escape(villa)}</b> meets the criteria to join my portfolio of villas in Bali. Here is what I can do for you: " if villa
             else "Here is what I can do for your villa: ")
    intro += "I bring you the bookings. Listed under my Superhost profile, your villa starts with the trust of 795 reviews instead of starting from zero, which is what fills a calendar quickly. Your villa manager and your staff stay exactly the same. No set-up fee, no subscription."
    who = html.escape(villa) if villa else "your villa"
    cover = fu(a.cover)
    gallery = "".join(f'<img src="{fu(x)}">' for x in a.photos[:3])
    ncol = min(3, len(a.photos))
    logo, photo = fu(os.path.join(HERE, "logo-horizontal-transparent.png")), fu(os.path.join(HERE, "host-photo.jpg"))
    css = open(os.path.join(HERE, "offer.css"), encoding="utf-8").read()
    page = f'''<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=Montserrat:wght@300;400;500;600&display=swap">
<style>{css}</style></head><body>
<section class="pg cover">
  <div class="ph"><img src="{cover}"><div class="t"><div class="k">{kicker}</div>
    <h1>Everything your villa needs to sell <em>more nights.</em></h1></div></div>
  <div class="body">
    <p class="lead">{intro}</p>
    <div class="host">
      <img class="av" src="{photo}">
      <div class="who"><b>Anthony</b><span class="sh">◆ Airbnb Superhost</span><span class="sub">Founder, AC Collection</span></div>
      <div class="st"><b>{HOST['reviews']}</b><span>Reviews</span></div>
      <div class="st"><b>{HOST['rating']}★</b><span>Rating</span></div>
      <div class="st"><b>{HOST['years']}</b><span>Years hosting</span></div>
      <div class="st"><b>{HOST['villas']}</b><span>Villas in Bali</span></div>
    </div>
    <p class="hostcap">Your villa goes live on this profile: guests book it with the confidence of 795 reviews from day one.</p>
  </div>
  <div class="foot"><img class="logo" src="{logo}"><span>ac-collection.com</span></div>
</section>
<section class="pg"><div class="in">
  <div class="k">What I do for you</div>
  <h2>Everything included, <em>from day one.</em></h2>
  <p class="lead">Every line below is included the day your villa goes live. The crossed-out prices are what each one costs on its own.</p>
  <table>{rows}</table>
  <div class="price"><div><div class="life">Lifetime</div><div class="big">{COMMISSION}</div></div><div><div class="line">on the nights I sell. Nothing else.</div><ul>{terms}</ul></div></div>
</div><div class="foot"><img class="logo" src="{logo}"><span>02</span></div></section>
<section class="pg"><div class="in">
  <div class="k">How it works</div>
  <h2>Live within <em>a week.</em></h2>
  <div class="steps" style="grid-template-columns:repeat(3,1fr)">
    <div class="step"><div class="n">01</div><h3>Onboarding</h3><p>I write and photograph the listing to convert, map every amenity, set up one calendar across all channels and set pricing with you.</p></div>
    <div class="step"><div class="n">02</div><h3>Go live</h3><p>Your villa goes live under my Superhost profile on Airbnb, then Booking.com and every other channel, with your direct-booking site and the AC Collection highlight, all on the same day.</p></div>
    <div class="step"><div class="n">03</div><h3>Every month</h3><p>I bring the bookings, your team hosts the guests as today, and every booking goes straight to you. On the 1st, your report: channel mix, occupancy, rates, market data and my pricing recommendations.</p></div>
  </div>
  <div class="duo" style="grid-template-columns:repeat({ncol},1fr)">{gallery}</div>
  <div class="two" style="margin-top:5mm">
    <div><h3>You keep</h3><ul><li>Your operations team: villa manager and staff stay the same</li><li>Your direct guests</li><li>Your rate floor, and your own stays blocked whenever you want</li><li>Every booking, paid to you</li></ul></div>
    <div><h3>I need</h3><ul><li>Your photos</li><li>House rules and check-in details</li><li>Your net rates or rate floor per season</li></ul></div>
  </div>
  <div class="cta"><div class="c" style="text-align:left">Anthony Campana · <b>+62 851 9018 1610</b> · ac-collection.com</div></div>
</div><div class="foot"><img class="logo" src="{logo}"><span>PT Anthony Campana Partners · Bali</span></div></section>
</body></html>'''
    src = os.path.join(HERE, a.out + ".html"); open(src, "w", encoding="utf-8").write(page)
    pdf = os.path.join(HERE, a.out + ".pdf")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--allow-file-access-from-files", "--virtual-time-budget=8000",
                    "--no-pdf-header-footer", f"--print-to-pdf={pdf}", "file://" + src], capture_output=True)
    low = open(src, encoding="utf-8").read().lower()
    assert "ical" not in low.split("<body")[1] and "in parallel" not in low and "diagnostic" not in low.split("<body")[1] and "low season" not in low and "low-season" not in low and " we " not in low.replace("<", " "), "règle de discours violée"
    print(pdf)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--villa", default=""); ap.add_argument("--area", default="")
    ap.add_argument("--cover", default=os.path.join(EXP, "close.jpg"))
    ap.add_argument("--photos", nargs="+", default=[os.path.join(EXP, "dinner.jpg"), os.path.join(EXP, "drone-2.jpg")])
    ap.add_argument("--out", default="AC-Partners-Offer")
    build(ap.parse_args())
