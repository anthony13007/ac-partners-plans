#!/usr/bin/env python3
"""Rental yield report for a villa FOR SALE — the buyer-facing page that answers "how much does it earn?".

  python3 rendement.py --zone canggu --br 5 --price-usd 750000 --lease-years 25 [--title "..."] [--slug x]
                       [--freehold] [--land-m2 800] [--build-m2 450] [--pool 15] [--adr-usd N] [--out file.html]

Market numbers come from market/bali.json (PriceLabs neighbourhood data, 350-listing compset per zone).
Three scenarios, all as RANGES, never a promise:
  market   = zone median ADR x zone occupancy (what an average listing does)
  ac       = zone p75 ADR x zone occupancy + AC uplift (what AC Collection's own portfolio does vs market)
  prudent  = market minus 15 %
Costs: operating 25 % of gross (staff, utilities, pool, maintenance, supplies), distribution 15 % (AC),
OTA blended 5 %, PPh final tax on rental income 10 % (Indonesia, on gross — buyer's advisor to confirm).
Leasehold: straight-line amortisation of the purchase price over the remaining years is shown next to the yield.
"""
import argparse, datetime, json, os, re, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.expanduser("~/Claude/ac-instagram/brand/LOGO-HORIZONTAL.png")   # charte ac-collection.com
MARKET = json.load(open(os.path.join(HERE, "market", "bali.json"), encoding="utf-8"))
AC_OCC_UPLIFT = 0.30   # AC's own Bali portfolio ran ~+40 pts above market on 30 days (11/09/2026); 30 pts kept as ceiling
OPEX, DISTRIB, OTA, TAX = 0.25, 0.15, 0.05, 0.10


def zone_key(z):
    z = (z or "").strip().lower()
    return MARKET["aliases"].get(z, z)


def money(n, cur="$"):
    n = round(n)
    return f"{cur}{n:,.0f}" if cur == "$" else f"{n:,.0f} {cur}"


def build(a):
    zk = zone_key(a.zone); Z = MARKET["zones"][zk]; fx = MARKET["usd_idr"]
    br = str(min(max(a.br, int(min(Z["adr_median_idr"]))), int(max(Z["adr_median_idr"]))))
    occ = statistics.mean(Z["occ_ly"].values()) / 100
    adr_med = a.adr_usd or Z["adr_median_idr"][br] / fx
    adr_p75 = Z["adr_p75_idr"][br] / fx if not a.adr_usd else a.adr_usd * 1.2
    lo_months = sorted(Z["occ_ly"].items(), key=lambda kv: kv[1])[:3]
    hi_months = sorted(Z["occ_ly"].items(), key=lambda kv: -kv[1])[:3]

    def scen(adr, o):
        gross = adr * 365 * o
        opex, dist, ota, tax = gross * OPEX, gross * DISTRIB, gross * OTA, gross * TAX
        net = gross - opex - dist - ota - tax
        return {"adr": adr, "occ": o, "nights": 365 * o, "gross": gross, "opex": opex, "dist": dist, "ota": ota, "tax": tax,
                "net": net, "yield": net / a.price_usd}
    S = {"prudent": scen(adr_med * 0.9, occ * 0.85), "market": scen(adr_med, occ), "ac": scen(adr_p75, min(occ + AC_OCC_UPLIFT, 0.85))}
    amort = 0 if a.freehold else a.price_usd / a.lease_years
    today = datetime.date.today().strftime("%d %B %Y")
    tenure = "Freehold (Hak Milik via PT PMA / HGB)" if a.freehold else f"Leasehold · {a.lease_years} years remaining"
    title = a.title or f"{a.br}-bedroom villa · {Z['label']}"
    slug = a.slug or re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")

    import base64
    LOGO = base64.b64encode(open(LOGO_PATH, "rb").read()).decode() if os.path.exists(LOGO_PATH) else ""

    def row(k, label):
        s = S[k]
        return (f"<tr><td>{label}</td><td class=n>{money(s['adr'])}</td><td class=n>{s['occ']*100:.0f} %</td><td class=n>{s['nights']:.0f}</td>"
                f"<td class=n>{money(s['gross'])}</td><td class=n><b>{money(s['net'])}</b></td><td class=n><b>{s['yield']*100:.1f} %</b></td></tr>")

    occ_bars = "".join(f"<div class=ob><i style='height:{v}%'></i><span>{m[:3]}</span><small>{v}</small></div>" for m, v in Z["occ_ly"].items())
    m = S["market"]; ac = S["ac"]
    html = f"""<title>{title}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=Montserrat:wght@300;400;500;600&display=swap">
<style>
:root{{--bg:#F8F2E8;--bg2:#EEE7DD;--ink:#3D2A1F;--ink2:#5C4A3D;--ink3:#8F6E56;--line:#E2D9CF;--card:#FEFDFB;--caramel:#C4794D;--terra:#A85F35;--vert:#4F7A52;--gold:#CBA14D;--shadow:0 10px 15px -3px rgba(0,0,0,.05),0 4px 6px -4px rgba(0,0,0,.05)}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:Montserrat,-apple-system,"Segoe UI",sans-serif;font-size:14.5px;line-height:1.6;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:980px;margin:0 auto;padding:36px 28px 70px}}
.brand{{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:26px;padding-bottom:18px;border-bottom:1px solid var(--line)}}.brand img{{height:52px;width:auto}}
.eyebrow{{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--terra);font-weight:600}}
h1{{font-family:"Cormorant Garamond",Georgia,serif;font-weight:500;font-size:clamp(34px,4.8vw,50px);line-height:1.02;margin:0 0 12px;text-wrap:balance}}
h1 em{{font-style:italic;font-weight:300;color:var(--ink2)}}
.lede{{color:var(--ink2);max-width:68ch;margin:0}}
h2{{font-family:"Cormorant Garamond",Georgia,serif;font-weight:600;font-size:27px;margin:44px 0 6px}}
.sub{{color:var(--ink2);margin:0 0 16px;max-width:70ch;font-size:13.5px}}
.facts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:0;border-top:1px solid var(--line);margin-top:26px}}
.fact{{padding:14px 18px 14px 0;border-bottom:1px solid var(--line)}}.fact .k{{font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--terra);font-weight:600}}
.fact b{{display:block;font-family:"Cormorant Garamond",Georgia,serif;font-weight:600;font-size:26px;margin-top:2px;line-height:1.1}}.fact span{{font-size:12px;color:var(--ink3)}}
.hero{{background:linear-gradient(135deg,#FFFFFF 0%,#FBF4E7 100%);border:1px solid var(--line);border-left:3px solid var(--caramel);border-radius:18px;padding:22px 26px;box-shadow:var(--shadow);display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:18px;margin-top:22px}}
.hero .k{{font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink3);font-weight:600}}
.hero b{{display:block;font-family:"Cormorant Garamond",Georgia,serif;font-weight:700;font-size:40px;line-height:1.02;margin:4px 0 2px;color:var(--ink)}}.hero span{{font-size:12.5px;color:var(--ink2)}}
.panel{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px 24px;box-shadow:var(--shadow)}}
table{{width:100%;border-collapse:collapse;font-size:13.5px;font-variant-numeric:tabular-nums}}
th{{text-align:left;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink3);font-weight:600;padding:0 10px 10px 0;border-bottom:1px solid var(--line)}}
td{{padding:10px 10px 10px 0;border-bottom:1px solid var(--line);vertical-align:top}}tr:last-child td{{border-bottom:0}}td.n{{text-align:right;white-space:nowrap}}td b{{font-weight:600}}
.scroll{{overflow-x:auto}}
.occ{{display:flex;gap:8px;align-items:flex-end;height:150px;padding-top:10px}}.ob{{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%}}
.ob i{{display:block;width:100%;max-width:38px;background:linear-gradient(180deg,var(--caramel),var(--terra));border-radius:6px 6px 0 0}}.ob span{{font-size:10px;letter-spacing:.06em;color:var(--ink3);margin-top:6px;text-transform:uppercase}}.ob small{{font-size:11px;color:var(--ink2)}}
.two{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:26px;align-items:start}}
ul{{margin:0;padding-left:18px;color:var(--ink2);font-size:13.5px}}li{{margin-bottom:7px}}li b{{color:var(--ink);font-weight:600}}
.note{{border-left:3px solid var(--caramel);background:rgba(196,121,77,.07);padding:12px 16px;border-radius:0 10px 10px 0;font-size:13px;color:var(--ink2);margin-top:18px}}
.foot{{margin-top:44px;padding-top:16px;border-top:1px solid var(--line);font-size:11.5px;color:var(--ink3);max-width:82ch;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;align-items:center}}
@media print{{body{{background:#fff}}.panel,.hero{{box-shadow:none}}}}
</style>
<div class=wrap>
<div class=brand><img src="data:image/png;base64,{LOGO}" alt="AC Collection"><div class=eyebrow>Rental yield report · {Z['label']}, Bali · {today}</div></div>
<h1>{title}<br><em>what it earns, on real market data</em></h1>
<p class=lede>Asking price {money(a.price_usd)} · {tenure}. Figures below are ranges built from {Z['compset']} comparable listings around this address, not a promise. The buyer's own advisor should confirm tax and tenure.</p>
<div class=facts>
  <div class=fact><span class=k>Tenure</span><b>{'Freehold' if a.freehold else str(a.lease_years)+' yrs'}</b><span>{'via PT PMA / HGB' if a.freehold else 'leasehold remaining'}</span></div>
  <div class=fact><span class=k>Bedrooms</span><b>{a.br}</b><span>rated against {Z['br_band']} comps</span></div>
  <div class=fact><span class=k>Market occupancy</span><b>{occ*100:.0f} %</b><span>12-month average, this zone</span></div>
  <div class=fact><span class=k>Market nightly rate</span><b>{money(adr_med)}</b><span>median, {a.br} BR · p75 {money(adr_p75)}</span></div>
  {'<div class=fact><span class=k>Land · build</span><b>'+str(a.land_m2)+' · '+str(a.build_m2)+' m²</b><span>'+(str(a.pool)+' m pool' if a.pool else '')+'</span></div>' if a.land_m2 else ''}
</div>
<div class=hero>
  <div><span class=k>Net yield, market scenario</span><b>{m['yield']*100:.1f} %</b><span>{money(m['net'])} net per year after all costs and tax</span></div>
  <div><span class=k>Net yield, AC-operated</span><b>{ac['yield']*100:.1f} %</b><span>{money(ac['net'])} net per year · {ac['occ']*100:.0f} % occupancy at p75 rates</span></div>
  <div><span class=k>{'Capital amortisation' if not a.freehold else 'Capital'}</span><b>{money(amort) if amort else 'kept'}</b><span>{'per year, straight line over the lease' if amort else 'freehold: no lease to amortise'}</span></div>
</div>

<h2>Three scenarios</h2>
<p class=sub>Gross revenue = nightly rate × nights sold. Net = gross minus operating costs ({OPEX*100:.0f} %), distribution ({DISTRIB*100:.0f} %), booking-platform fees ({OTA*100:.0f} %) and final rental tax ({TAX*100:.0f} %).</p>
<div class="panel scroll"><table><thead><tr><th>Scenario</th><th class=n>Rate / night</th><th class=n>Occupancy</th><th class=n>Nights</th><th class=n>Gross</th><th class=n>Net</th><th class=n>Net yield</th></tr></thead><tbody>
{row('prudent','Prudent · market minus 15 %')}{row('market','Market · zone median')}{row('ac','AC-operated · p75 rates, distribution on')}
</tbody></table>
<p class=sub style="margin:14px 0 0">The AC-operated line is what AC Collection's own Bali portfolio achieved against its market on the last reading: occupancy well above the zone average at above-median rates. It assumes the villa is distributed by AC from day one, priced daily and staffed to standard.</p></div>

<div class=two style="margin-top:26px">
<div><h2 style="margin-top:0">Occupancy through the year</h2><p class=sub>Final market occupancy, {Z['label']} {Z['br_band']}, last 12 months. Lowest: {', '.join(f'{k} {v} %' for k,v in lo_months)}. Highest: {', '.join(f'{k} {v} %' for k,v in hi_months)}.</p>
<div class=panel><div class=occ>{occ_bars}</div></div></div>
<div><h2 style="margin-top:0">What moves the number</h2><div class=panel><ul>
<li><b>Tenure first.</b> {'Freehold keeps the capital; yield is the whole story.' if a.freehold else f'On a {a.lease_years}-year lease the price is consumed over the term: {money(amort)} a year of amortisation sits next to the yield. Ask for the lease extension terms in writing before offering.'}</li>
<li><b>Bedrooms sell in groups.</b> {a.br} bedrooms places this villa in the {Z['br_band']} band, where demand is groups, weddings and retreats. Minimum stays and event rules decide the peak weeks.</li>
<li><b>Peak weeks carry the year.</b> Christmas to New Year and July to August run 15 to 20 % above surrounding dates in this zone. Daily pricing captures it; a flat rate gives it away.</li>
<li><b>Distribution is the lever.</b> The gap between the market and AC-operated lines is occupancy, not price. It comes from being sold on every channel plus direct group demand, which AC provides on a success fee only.</li>
</ul></div></div>
</div>

<h2>After the purchase</h2>
<p class=sub>AC Collection distributes the villa from the day of completion: listing on all channels, daily pricing, direct group and wedding demand, monthly statement. No setup fee, no retainer, {DISTRIB*100:.0f} % of nights sold. Operations stay with a local villa manager of the buyer's choice.</p>
<div class=note>This report uses PriceLabs neighbourhood data pulled on {MARKET['pulled']} for {Z['compset']} listings, at {fx:,.0f} IDR per USD. It is an estimate for discussion, not a guarantee of income. Indonesian rental income tax, land and building tax, and the legal form of ownership for foreign buyers must be confirmed by a licensed Indonesian advisor.</div>
<div class=foot><span>AC Collection · PT Anthony Campana Partners · Kerobokan, Bali · KBLI 68200 real estate on a fee or contract basis · ac-collection.com</span><span>report {slug}</span></div>
</div>
"""
    out = a.out or os.path.join(HERE, "yield", f"{slug}.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    print(f"{out}\n  market net {money(m['net'])} ({m['yield']*100:.1f} %) · AC net {money(ac['net'])} ({ac['yield']*100:.1f} %) · amortisation {money(amort)}/yr")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--zone", required=True); ap.add_argument("--br", type=int, required=True); ap.add_argument("--price-usd", type=float, required=True)
    ap.add_argument("--lease-years", type=int, default=25); ap.add_argument("--freehold", action="store_true")
    ap.add_argument("--title"); ap.add_argument("--slug"); ap.add_argument("--adr-usd", type=float)
    ap.add_argument("--land-m2", type=int); ap.add_argument("--build-m2", type=int); ap.add_argument("--pool", type=int); ap.add_argument("--out")
    build(ap.parse_args())
