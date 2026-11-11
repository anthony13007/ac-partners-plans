#!/usr/bin/env python3
"""Proposition de partenariat AC (modèle « A VIP clientele for … », 5 pages, 12 % en parallèle).

Reproduit le PDF envoyé à Zeno Arete (Nusa Nova Group) le 11/11/2026. Une villa = un dossier :
  partnership/<slug>/villa.json   textes propres à la villa (voir the-hideaway/villa.json)
  partnership/<slug>/cover.jpg    photo de couverture
  partnership/<slug>/header.jpg   photo en tête de la page villa (nom libre, donné dans villa.json)
  partnership/<slug>/logo.png     logo du partenaire, en médaillon sur la couverture (optionnel)

  python3 offer/partnership/build_partnership.py the-hideaway
  -> offer/partnership/<slug>/AC-Partnership-<Nom>.html et .pdf

Dépôt public : la signature (assets/signature.png) et les PDF/HTML générés ne sont pas versionnés
(voir .gitignore du dossier). Sans signature.png, la page 5 sort sans signature.

Règles : « I », jamais « we » ; preuves = profil Airbnb réel (800 avis, 4.8★, 10 ans) ;
pas de « low season » ni de garantie dans le PDF.
"""
import html, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
CHROME = os.environ.get("CHROME") or next((c for c in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/opt/pw-browsers/chromium"] if os.path.exists(c)), "chromium")
PHONE = "+62 851 9018 1610"
HOST = {"reviews": "800", "rating": "4.8", "years": "10"}

STACK = [
    ("An additional Airbnb listing under my profile", "Listing written to rank, photos sorted room by room, you as co-host. Alongside your own listing, never instead of it.", None),
    ("Distribution on 8+ channels", "The major booking platforms worldwide, the leading Asian platforms and travel search engines, reaching guests in Europe, the Americas, Australia and Asia. Every listing built and managed by me, on one synced calendar.", "$390 + $49/mo"),
    ("Highlight on ac-collection.com", "On the homepage for three months, then in the Asia portfolio and my guest emails. Bookings made there carry no OTA fees: 15% saved.", "$29/mo"),
    ("Landing page for direct booking + payment collection", "A dedicated page for {villa} where guests book direct and pay online: scroll film, gallery, rates, secure payment collected at booking. Every booking it brings saves around 15% of platform fees.", "$490"),
    ("Private VIP concierge + guest app", "For every guest I send: stay confirmed, experiences curated, digital guidebook and concierge chat, at the standard your villa deserves.", "$39/mo"),
    ("My worldwide clientele and network", "Families, founders and private groups from Europe, the Americas, the Middle East, Australia and Asia, and the travel designers who place their clients with me.", None),
    ("PriceLabs strategy tool", "The dynamic-pricing engine behind my own villas, running on yours, above your rates: seasonality, events, lead time, minimum stays.", "$15/mo"),
    ("Monthly report + market insights", "On the 1st of every month: occupancy, ADR, PriceLabs market data and my pricing recommendations.", "$19.99/mo"),
    ("Pricing set-up + listing audit", "PriceLabs configured for {villa}; photos, title and text reviewed in the first week.", "$290"),
]
CHANNELS = [("Airbnb · my Superhost profile", False), ("Major booking platforms worldwide", False), ("Leading Asian platforms", False),
            ("Travel search engines", False), ("My private clientele and network", False), ("ac-collection.com · direct", True)]
TERMS = ["Your own listing stays live, untouched", "Nothing on the nights you sell yourself", "No set-up fee, no exclusivity, no minimum term", "Stop whenever you want, confirmed stays honoured"]

CSS = """
@page{size:A4;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
body{background:#F8F1E8;color:#2B1D14;font-family:'Montserrat',Arial,sans-serif;font-weight:300;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.pg{width:210mm;height:297mm;position:relative;overflow:hidden;page-break-after:always;background:#F8F1E8}
.in{padding:14mm 17mm 0}
.k{font-size:7.6pt;letter-spacing:.32em;text-transform:uppercase;color:#C4794D;font-weight:400;margin-bottom:4mm}
h1,h2,h3,.serif{font-family:'Cormorant Garamond',Georgia,serif;font-weight:400}
h2{font-size:27pt;line-height:1.08;color:#2B1D14}
h2 em,h1 em{color:#C4794D;font-style:italic}
p{font-size:9.4pt;line-height:1.56;color:#4A3A2E;margin-bottom:3mm}
p b{font-weight:600;color:#2B1D14}
.rule{border-top:1px solid #E4D6C6;margin:4mm 0}
.foot{position:absolute;left:17mm;right:17mm;bottom:9mm;display:flex;justify-content:space-between;align-items:center}
.foot img{height:8.5mm}
.foot span{font-size:7pt;letter-spacing:.24em;color:#9A8676;text-transform:uppercase}
/* couverture */
.cover .ph{height:132mm;position:relative}
.cover .ph img{width:100%;height:100%;object-fit:cover}
.cover .ph:after{content:"";position:absolute;left:0;right:0;bottom:0;height:42mm;background:linear-gradient(180deg,rgba(248,241,232,0),#F8F1E8)}
.cover .seal{position:absolute;left:50%;top:116mm;transform:translateX(-50%);width:33mm;height:33mm;border-radius:50%;background:#F8F1E8;border:1px solid #E4D6C6;padding:1.6mm;z-index:3}
.cover .seal img{width:100%;height:100%;border-radius:50%;object-fit:cover}
.cover .txt{text-align:center;padding-top:26mm}
.cover .kk{font-size:7.8pt;letter-spacing:.34em;color:#C4794D;text-transform:uppercase;margin-bottom:4mm}
.cover h1{font-size:37pt;line-height:1.05}
.cover .bar{width:30mm;border-top:1.4px solid #C4794D;margin:6mm auto}
.cover .sub{font-size:9pt;color:#7A6656;letter-spacing:.02em}
.cover .tag{font-family:'Cormorant Garamond',serif;font-size:16pt;margin-top:9mm}
.cover .tag em{color:#C4794D;font-style:italic}
.cover .who{margin-top:10mm;font-size:8.6pt;color:#7A6656;line-height:1.7}
.cover .who b{display:block;letter-spacing:.28em;font-weight:600;color:#2B1D14;font-size:8.4pt;margin-bottom:.6mm}
.cover .who a{color:#C4794D;text-decoration:none}
/* page 2 */
.stats{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid #E4D6C6;border-bottom:1px solid #E4D6C6;margin:5mm 0}
.stats>div{text-align:center;padding:4mm 0;border-left:1px solid #E4D6C6}
.stats>div:first-child{border-left:0}
.stats b{display:block;font-family:'Cormorant Garamond',serif;font-weight:400;font-size:21pt;color:#2B1D14}
.stats span{font-size:6.6pt;letter-spacing:.24em;color:#9A8676;text-transform:uppercase}
.card{background:#FBF8F3;border:1px solid #E4D6C6;border-radius:4mm;padding:5mm 6mm;display:flex;gap:7mm;align-items:center;margin-top:5mm}
.card img{width:30mm;height:30mm;border-radius:50%;object-fit:cover}
.card .k{margin-bottom:2mm}
.card b{font-weight:600;font-size:11pt;display:block;margin-bottom:1mm}
.card .s{font-size:8.4pt;color:#9A8676;margin-bottom:2mm;display:block}
/* page 3 */
.hero{height:100mm;position:relative}
.hero img{width:100%;height:100%;object-fit:cover}
.hero:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(26,15,8,.62),rgba(26,15,8,.15) 60%,rgba(26,15,8,0))}
.hero .t{position:absolute;left:17mm;top:14mm;z-index:2}
.hero .k{color:#F4E3D2}
.hero h2{color:#FBF6EE;font-size:26pt}
.hero h2 em{color:#FBF6EE}
.quote{border-left:2px solid #C4794D;padding:1mm 0 1mm 5mm;margin:5mm 0;font-family:'Cormorant Garamond',serif;font-size:14.5pt;line-height:1.38;color:#2B1D14}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:5mm;margin-top:3mm}
.cards>div{background:#FBF8F3;border:1px solid #E4D6C6;border-radius:3.4mm;padding:5mm}
.cards h3{font-size:15pt;margin-bottom:2mm}
.cards p{font-size:8.3pt;line-height:1.55;margin:0}
/* page 4 */
table{width:100%;border-collapse:collapse;margin-top:3mm}
td{border-top:1px solid #E4D6C6;padding:1.9mm 0;vertical-align:top}
tr:last-child td{border-bottom:1px solid #E4D6C6}
td.n{width:10mm;font-family:'Cormorant Garamond',serif;font-size:13pt;color:#C4794D}
td b{font-weight:600;font-size:9.4pt;color:#2B1D14;display:block;margin-bottom:.8mm}
td p{font-size:7.9pt;line-height:1.5;margin:0;max-width:125mm}
td.w{text-align:right;width:40mm;font-size:7pt;letter-spacing:.2em;color:#C4794D;font-weight:600}
td.w s{display:block;font-family:'Cormorant Garamond',serif;font-size:11.5pt;letter-spacing:0;color:#9A8676;font-weight:400;margin-bottom:1mm;white-space:nowrap}
.yr{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:2px solid #2B1D14;padding:3.5mm 0 1.6mm}
.yr span{font-family:'Cormorant Garamond',serif;font-size:17pt}
.yr .w{text-align:right;font-size:7pt;letter-spacing:.2em;color:#C4794D;font-weight:600;font-family:'Montserrat',sans-serif}
.yr .w s{display:block;font-family:'Cormorant Garamond',serif;font-size:19pt;letter-spacing:0;color:#2B1D14;font-weight:400}
.price{background:#2B1D14;border-radius:3.4mm;margin-top:4mm;padding:5mm 9mm;display:grid;grid-template-columns:44mm 1fr;align-items:center;color:#F8F1E8}
.price .l{font-size:7pt;letter-spacing:.3em;color:#E8A87C;font-weight:600}
.price .big{font-family:'Cormorant Garamond',serif;font-size:36pt;color:#E8A87C;line-height:1;margin-top:3mm}
.price .line{font-family:'Cormorant Garamond',serif;font-size:16pt;margin-bottom:2mm}
.price li{font-size:8.4pt;color:#E9DED2;margin:1.3mm 0 0 4mm}
.price li::marker{color:#E8A87C}
/* page 5 */
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:5mm;margin-top:3mm}
.steps>div{background:#FBF8F3;border:1px solid #E4D6C6;border-radius:3.4mm;padding:6mm;min-height:46mm}
.steps .n{font-family:'Cormorant Garamond',serif;font-size:14pt;color:#C4794D}
.steps h3{font-size:16pt;margin:1.4mm 0 2.4mm}
.steps p{font-size:8.4pt;margin:0}
.chips{display:flex;flex-wrap:wrap;gap:2.4mm}
.chips span{font-size:8.2pt;padding:2.2mm 4.4mm;border:1px solid #E4D6C6;border-radius:20mm;background:#FBF8F3;color:#2B1D14}
.chips span.lux{border-color:#C4794D;color:#C4794D;font-weight:600}
.sign{text-align:center;margin-top:16mm}
.sign .q{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:21pt;color:#C4794D}
.sign img{height:24mm;margin:7mm 0 1mm}
.sign b{display:block;letter-spacing:.24em;font-weight:600;font-size:8.6pt}
.sign span{display:block;font-size:8.4pt;color:#7A6656;margin-top:1.4mm}
.sign span a{color:#C4794D;text-decoration:none}
"""


def fu(p):
    return "file://" + os.path.abspath(p)


def esc(t):
    """Échappe le texte et garde *mot* en italique (accent terracotta dans les titres)."""
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", html.escape(t))


def build(slug):
    d = os.path.join(HERE, slug)
    v = json.load(open(os.path.join(d, "villa.json"), encoding="utf-8"))
    name = v["villa"]
    foot = f'<div class="foot"><img src="{fu(os.path.join(ASSETS, "ac-collection-footer.png"))}"><span>AC Partners | AC Collection · {{n}}</span></div>'
    logo = os.path.join(d, "logo.png")
    seal = fu(logo) if os.path.exists(logo) else fu(os.path.join(ASSETS, "ac-seal.png"))
    paras = "".join(f"<p>{esc(x)}</p>" if not x.startswith("**") else f"<p><b>{esc(x.split('**')[1])}</b>{esc(x.split('**', 2)[2])}</p>" for x in v["why"])
    cards = "".join(f"<div><h3>{esc(t)}</h3><p>{esc(x)}</p></div>" for t, x in v["guests"])
    rows = "".join(
        f'<tr><td class="n">{i + 1:02d}</td><td><b>{esc(t)}</b><p>{esc(x.format(villa=name))}</p></td>'
        f'<td class="w">{f"<s>{p}</s>" if p else ""}INCLUDED</td></tr>' for i, (t, x, p) in enumerate(STACK))
    terms = "".join(f"<li>{t}</li>" for t in TERMS)
    def yearly(p):  # "$29/mo" -> 348 ; "$490" -> 490 ; "$390 + $49/mo" -> 978
        if not p:
            return 0
        tot = 0
        for part in p.split("+"):
            part = part.strip(); n = float(part.strip("$").split("/")[0].replace(",", ""))
            tot += n * 12 if part.endswith("/mo") else n
        return tot
    worth = sum(yearly(p) for _, _, p in STACK)
    chips = "".join(f"<span{' class=lux' if lux else ''}>{c}</span>" for c, lux in CHANNELS)
    # Signature hors Git (dépôt public) : assets/signature.png, à poser à la main sur le Mac.
    sigp = os.path.join(ASSETS, "signature.png")
    sig = f'<img src="{fu(sigp)}">' if os.path.exists(sigp) else '<div style="height:12mm"></div>'
    page = f"""<!doctype html><html><head><meta charset="utf-8"><title>AC Partnership · {html.escape(name)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&family=Montserrat:wght@300;400;600&display=swap">
<style>{CSS}</style></head><body>

<section class="pg cover">
  <div class="ph"><img src="{fu(os.path.join(d, v['cover']))}"></div>
  <div class="seal"><img src="{seal}"></div>
  <div class="txt">
    <div class="kk">Partnership proposal</div>
    <h1>A VIP clientele<br><em>for {html.escape(name)}.</em></h1>
    <div class="bar"></div>
    <div class="sub">{html.escape(v['area'])} · Luxury distribution partnership</div>
    <div class="tag">An additional channel, <em>alongside yours.</em></div>
    <div class="who"><b>ANTHONY CAMPANA</b>Founder · PT Anthony Campana Partners<br>AC Partners | AC Collection<br><a>ac-collection.com</a></div>
  </div>
</section>

<section class="pg"><div class="in">
  <div class="k">Who I am</div>
  <h2>Ten years of hosting,<br><em>at the high end of the market.</em></h2>
  <p style="margin-top:6mm">I am Anthony Campana, founder of PT Anthony Campana Partners, the Indonesian company behind AC Partners and AC Collection, a curated collection of premium villas in Bali and across Asia.</p>
  <p>My work is focused on the very top of the market. I host a VIP clientele of families, founders and private groups who book villas and estates for extended stays, and who expect a level of service that goes well beyond the keys: a private concierge before arrival, curated experiences during the stay, and someone who knows them when they come back.</p>
  <div class="stats"><div><b>{HOST['reviews']}</b><span>Guest reviews</span></div><div><b>{HOST['rating']}★</b><span>Rating</span></div><div><b>{HOST['years']}</b><span>Years hosting</span></div><div><b>Worldwide</b><span>VIP clientele</span></div></div>
  <p>These numbers are not a vanity metric. On booking platforms, review volume and rating directly drive search ranking and conversion, and a listing created under this profile inherits that history from day one. Behind them is a clientele from Europe, the Americas, the Middle East, Australia and Asia, who travel several times a year and book through someone they trust.</p>
  <div class="rule"></div>
  <div class="k">A registered Indonesian company</div>
  <p>I operate through PT Anthony Campana Partners, a PT PMA incorporated in Indonesia, holding a valid NIB and the KBLI classifications required for villa rental, real-estate intermediation and advertising. Every booking is invoiced through the company, with proper documentation on both sides.</p>
  <p>{esc(v['company_note'])}</p>
  <div class="rule"></div>
  <div class="k">Portfolio</div>
  <p>AC Collection is a private portfolio of luxury villas and estates in Bali and across Asia, from beachfront houses to a fifteen-bedroom estate, presented on ac-collection.com to a VIP clientele that books direct. I work with a recurring international clientele of families, founders and private groups, and with a network of travel designers, wedding planners and concierges who place their most demanding clients with me.</p>
  <div class="card"><img src="{fu(os.path.join(ASSETS, 'host.jpg'))}"><div><div class="k">My Airbnb profile</div><b>Anthony · Airbnb Superhost</b><span class="s">Founder, AC Collection · {HOST['reviews']} reviews · {HOST['rating']}★ · {HOST['years']} years of hosting</span><p style="margin:0">Families, founders and private groups book through this profile, and come back.</p></div></div>
</div>{foot.format(n=2)}</section>

<section class="pg">
  <div class="hero"><img src="{fu(os.path.join(d, v['header']))}" style="object-position:{v.get('header_position', '50% 60%')}"><div class="t"><div class="k">Why {html.escape(name)}</div><h2>{esc(v['why_title'])}</h2></div></div>
  <div class="in" style="padding-top:9mm">
    {paras}
    <div class="quote">A villa inside my portfolio can be promoted. A one-off request cannot. Within my collection, {html.escape(name)} is featured to my international clientele, to my network of travel designers and concierges, and on ac-collection.com.</div>
    <p><b>What I bring is a clientele, not another middleman.</b>{esc(v.get('closing', ''))}</p>
    <div class="k" style="margin-top:5mm">What my guests would book here</div>
    <div class="cards">{cards}</div>
  </div>{foot.format(n=3)}</section>

<section class="pg"><div class="in">
  <div class="k">What I bring</div>
  <h2>Everything included, <em>from day one.</em></h2>
  <p style="margin-top:3mm;margin-bottom:1mm">Every line below is included the day {html.escape(name)} goes live. The crossed-out prices are what each one costs on its own.</p>
  <table>{rows}</table>
  <div class="yr"><span>Total per year</span><div class="w"><s>${worth:,.0f}</s>INCLUDED</div></div>
  <div class="price"><div><div class="l">IN PARALLEL</div><div class="big">{v.get("commission", 12)}%</div></div><div><div class="line">on the nights I sell. Nothing else.</div><ul>{terms}</ul></div></div>
</div>{foot.format(n=4)}</section>

<section class="pg"><div class="in">
  <div class="k">Next step</div>
  <h2>Let's begin <em>with {html.escape(name)}.</em></h2>
  <div class="k" style="margin-top:8mm">How it works</div>
  <div class="steps">
    <div><div class="n">01</div><h3>Onboarding</h3><p>Photos, rates, calendars, pricing. <b>48 hours.</b></p></div>
    <div><div class="n">02</div><h3>Go live</h3><p>My listing goes live alongside yours, with you as co-host, and {html.escape(name)} on ac-collection.com, the same day. Your own listing does not change.</p></div>
    <div><div class="n">03</div><h3>Every month</h3><p>I bring the guests, your team hosts, every booking is paid to you. On the 1st, your statement.</p></div>
  </div>
  <div class="k" style="margin-top:9mm">Where {html.escape(name)} goes live</div>
  <div class="chips">{chips}</div>
  <div class="sign"><div class="q">“Let's win the market together.”</div>{sig}<b>ANTHONY CAMPANA</b><span>Founder · PT Anthony Campana Partners · AC Partners | AC Collection</span><span><a>ac-collection.com</a> · {PHONE}</span></div>
</div>{foot.format(n=5)}</section>
</body></html>"""
    out = os.path.join(d, "AC-Partnership-" + re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-"))
    open(out + ".html", "w", encoding="utf-8").write(page)
    body = page.split("<body>")[1].lower()
    assert " we " not in re.sub(r"<[^>]+>", " ", body) and "low season" not in body and "guarantee" not in body, "règle de discours violée"
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--allow-file-access-from-files", "--virtual-time-budget=10000",
                    "--no-pdf-header-footer", f"--print-to-pdf={out}.pdf", "file://" + out + ".html"], capture_output=True, check=True)
    print(out + ".pdf")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "the-hideaway")
