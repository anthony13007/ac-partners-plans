#!/usr/bin/env python3
"""Market report for a villa page: the « analysis » block, PriceLabs style, measured data only.

  python3 villa-site/market_report.py the-ridge-bali

Reads villas/<slug>.json (zone, name, report_position, report_map) and the zone's monthly series in
market/bali.json (series, pace), writes `report_html` back into the villa JSON and rebuilds its page.
The template shows the report instead of the gap table when `report_html` is present.

Rule: nothing here is an estimate of the property's own occupancy or lost revenue. Every figure is
either read from PriceLabs Market Research for the area, or a public fact about the property
(rating, published rate, channels) given in `report_position`.
"""
import datetime, html, json, pathlib, statistics, sys

HERE = pathlib.Path(__file__).resolve().parent
MARKET = json.loads((HERE / "market" / "bali.json").read_text(encoding="utf-8"))
C1, C2 = "#c4794d", "#2a78a8"   # last 12 months, year before — validated on the #f8f2e8 surface (dataviz validate_palette.js)
INK, MUT, GRID, SURF = "#372115", "#8a7768", "#e3d7c5", "#fffdf9"
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
LONG = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

CSS = """<style>
.rep{margin-top:34px}
.rep h3{font-family:var(--serif);font-weight:500;font-size:24px;color:#372115;margin:0 0 4px}
.rep .sub{font-size:13px;color:#8a7768;margin:0 0 12px;max-width:none}
.rep .kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.rep .kpi{background:#fffdf9;border:1px solid #e3d7c5;border-radius:14px;padding:20px 22px}
.rep .kpi .l{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:#8a7768;font-weight:600}
.rep .kpi .n{font-family:var(--serif);font-size:38px;line-height:1;color:#372115;margin-top:12px}
.rep .kpi .d{font-size:12.5px;color:#8a7768;margin-top:8px}
.rep .grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px}
.rep .card{background:#fffdf9;border:1px solid #e3d7c5;border-radius:14px;padding:22px 22px 16px;min-width:0}
.rep .card>svg{display:block;width:100%;height:auto;overflow:visible}
.rep .card>svg text{font-family:var(--sans);font-size:11px;fill:#8a7768}
.rep .card>svg text.v{fill:#372115;font-weight:600}
.rep .col line.x,.rep .col circle{opacity:0}
.rep .col:hover line.x,.rep .col:hover circle{opacity:1}
.rep .legend{display:flex;gap:18px;flex-wrap:wrap;font-size:12.5px;color:#5a463a;margin-bottom:6px}
.rep .legend i{display:inline-block;width:14px;height:3px;border-radius:2px;vertical-align:middle;margin-right:7px}
.rep table.pace{width:100%;border-collapse:collapse;margin:6px 0 0;font-size:14px;background:none;border:0}
.rep table.pace th{background:none;font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:#8a7768;font-weight:600;padding:8px 10px 8px 0;border-bottom:1px solid #e3d7c5;text-align:left}
.rep table.pace td{padding:12px 10px 12px 0;border-bottom:1px solid #efe6d8;color:#372115;vertical-align:middle}
.rep table.pace tr:last-child td{border-bottom:0}
.rep table.pace td.n{font-family:var(--serif);font-size:19px}
.rep .track{position:relative;height:8px;border-radius:4px;background:#f0e3d5;min-width:90px}
.rep .track b{position:absolute;left:0;top:0;bottom:0;border-radius:4px;background:#c4794d}
.rep .track u{position:absolute;top:-3px;bottom:-3px;width:2px;background:#372115}
.rep .rfacts{margin:8px 0 0}
.rep .rfacts .f{display:flex;justify-content:space-between;gap:18px;padding:11px 0;border-bottom:1px solid #efe6d8;font-size:14px;color:#372115}
.rep .rfacts .f:last-child{border-bottom:0}
.rep .rfacts .f span:first-child{color:#8a7768;flex:0 0 38%}
.rep .rfacts .f span:last-child{text-align:right}
.rep #report-map{height:330px;border-radius:10px;overflow:hidden;background:#efe6d8;margin-top:8px}
.rep #report-map .leaflet-tile{filter:grayscale(1) sepia(.18) contrast(.92) brightness(1.04)}
.rep #report-map .leaflet-tooltip{font-family:var(--sans);font-size:12px;color:#372115;font-weight:600}
.rep .reads{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:14px}
.rep .reads .card h4{font-family:var(--serif);font-weight:500;font-size:21px;color:#372115;margin:0 0 6px}
.rep .reads .card p{font-size:14px;margin:0;color:#8a7768}
.rep details{margin-top:18px;font-size:13px;color:#8a7768}
.rep details summary{cursor:pointer;color:#a45d33;font-weight:600;letter-spacing:.04em}
.rep details table{width:100%;border-collapse:collapse;margin-top:10px;font-size:13px;background:#fffdf9;border:1px solid #e3d7c5}
.rep details th,.rep details td{padding:7px 10px;border-bottom:1px solid #efe6d8;text-align:right;color:#372115}
.rep details th:first-child,.rep details td:first-child{text-align:left}
.rep details th{font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:#8a7768;background:#f2e9db}
.rep .src{font-size:12.5px;color:#9c8a78;margin-top:18px;max-width:78ch}
#rep-tip{position:fixed;z-index:50;pointer-events:none;background:#372115;color:#f8f2e8;font-size:12.5px;line-height:1.45;padding:8px 11px;border-radius:8px;white-space:pre-line;display:none;max-width:240px}
@media(max-width:820px){.rep .card>svg text{font-size:15px}.rep .card>svg text.mh{display:none}.rep .kpis{grid-template-columns:1fr 1fr}.rep .grid2,.rep .reads{grid-template-columns:1fr}.rep .kpi .n{font-size:32px}}
</style>"""


def ym_label(ym, long=False, year=True):
    y, m = ym.split("-"); name = (LONG if long else MON)[int(m) - 1]
    return f"{name} {y}" if year else name


def line_chart(series, key, key_ly, fmt, ticks, tip_unit):
    """Two lines over 12 months: last 12 months and the year before. One axis, hairline grid, end labels."""
    W, H, L, R, T, B = 520, 250, 44, 62, 12, 30
    lo, hi = ticks[0], ticks[-1]; n = len(series)
    x = lambda i: L + i * (W - L - R) / (n - 1)
    y = lambda v: T + (hi - v) / (hi - lo) * (H - T - B)
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{html.escape(tip_unit)} by month, last 12 months against the year before">']
    for t in ticks:
        o.append(f'<line x1="{L}" x2="{W - R}" y1="{y(t):.1f}" y2="{y(t):.1f}" stroke="{GRID}" stroke-width="1"/><text x="{L - 8}" y="{y(t) + 4:.1f}" text-anchor="end">{fmt(t)}</text>')
    for i, s in enumerate(series):
        lab = MON[int(s["ym"][5:]) - 1] + (f" '{s['ym'][2:4]}" if i in (0, n - 1) else "")
        o.append(f'<text{" class=mh" if i % 2 and i != n - 1 or i == n - 2 else ""} x="{x(i):.1f}" y="{H - 8}" text-anchor="middle">{lab}</text>')
    for k, c in ((key_ly, C2), (key, C1)):
        pts = " ".join(f"{x(i):.1f},{y(s[k]):.1f}" for i, s in enumerate(series))
        o.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
    a, b = series[-1][key], series[-1][key_ly]   # end labels, pushed apart if they would collide
    ya, yb = y(a), y(b)
    if abs(ya - yb) < 13: ya, yb = (ya - 7, yb + 7) if ya < yb else (ya + 7, yb - 7)
    for v, yy, c, yv in ((a, ya, C1, y(a)), (b, yb, C2, y(b))):
        o.append(f'<circle cx="{x(n - 1):.1f}" cy="{yv:.1f}" r="4" fill="{c}" stroke="{SURF}" stroke-width="2"/><text class="v" x="{x(n - 1) + 9:.1f}" y="{yy + 4:.1f}">{fmt(v)}</text>')
    step = (W - L - R) / (n - 1)
    for i, s in enumerate(series):   # hover columns: crosshair + dots (CSS), tooltip (data-tip)
        tip = f"{ym_label(s['ym'])}\n{tip_unit}: {fmt(s[key])}\nYear before: {fmt(s[key_ly])}"
        o.append(f'<g class="col" data-tip="{html.escape(tip)}"><rect x="{x(i) - step / 2:.1f}" y="{T}" width="{step:.1f}" height="{H - T - B}" fill="transparent"/>'
                 f'<line class="x" x1="{x(i):.1f}" x2="{x(i):.1f}" y1="{T}" y2="{H - B}" stroke="{MUT}" stroke-width="1"/>'
                 f'<circle cx="{x(i):.1f}" cy="{y(s[key_ly]):.1f}" r="4" fill="{C2}" stroke="{SURF}" stroke-width="2"/><circle cx="{x(i):.1f}" cy="{y(s[key]):.1f}" r="4" fill="{C1}" stroke="{SURF}" stroke-width="2"/></g>')
    o.append("</svg>")
    return "".join(o)


def bar_chart(series, key, unit, ticks):
    """One series, 12 columns from a zero baseline; the highest and the lowest are labelled."""
    W, H, L, R, T, B = 520, 250, 44, 14, 18, 30
    hi = ticks[-1]; n = len(series); band = (W - L - R) / n; bw = min(24, band - 8)
    y = lambda v: T + (hi - v) / hi * (H - T - B)
    vals = [s[key] for s in series]; imax, imin = vals.index(max(vals)), vals.index(min(vals))
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Median booking window by month, in days">']
    for t in ticks:
        o.append(f'<line x1="{L}" x2="{W - R}" y1="{y(t):.1f}" y2="{y(t):.1f}" stroke="{GRID}" stroke-width="1"/><text x="{L - 8}" y="{y(t) + 4:.1f}" text-anchor="end">{t}</text>')
    for i, s in enumerate(series):
        cx = L + band * (i + .5); v = s[key]; top = y(v); h = H - B - top
        lab = MON[int(s["ym"][5:]) - 1] + (f" '{s['ym'][2:4]}" if i in (0, n - 1) else "")
        path = f"M{cx - bw / 2:.1f},{H - B} v{-(h - 4):.1f} q0,-4 4,-4 h{bw - 8:.1f} q4,0 4,4 v{h - 4:.1f} z"
        o.append(f'<g data-tip="{html.escape(ym_label(s["ym"]))}&#10;Booked {v} {unit} ahead (median)"><rect x="{cx - band / 2:.1f}" y="{T}" width="{band:.1f}" height="{H - T - B}" fill="transparent"/><path d="{path}" fill="{C1}"/></g>')
        o.append(f'<text{" class=mh" if i % 2 and i != n - 1 or i == n - 2 else ""} x="{cx:.1f}" y="{H - 8}" text-anchor="middle">{lab}</text>')
        if i in (imax, imin): o.append(f'<text class="v" x="{cx:.1f}" y="{top - 6:.1f}" text-anchor="middle">{v}</text>')
    o.append("</svg>")
    return "".join(o)


def build(slug):
    vp = HERE / "villas" / f"{slug}.json"; v = json.loads(vp.read_text(encoding="utf-8"))
    Z = MARKET["zones"][v["zone"]]; S = Z["series"]; P = Z["pace"]
    name = v.get("short_name") or v["name"]
    read = datetime.date.fromisoformat(Z.get("pulled", MARKET["pulled"])); read_txt = f"{read.day} {LONG[read.month - 1]} {read.year}"
    occ, occ_ly = statistics.mean(s["occ"] for s in S), statistics.mean(s["occ_ly"] for s in S)
    adr, adr_ly = statistics.mean(s["adr"] for s in S), statistics.mean(s["adr_ly"] for s in S)
    bws = [s["bw"] for s in S]; loss = [s["los"] for s in S]
    hi3 = sorted(S, key=lambda s: -s["occ"])[:3]; lo3 = sorted(S, key=lambda s: s["occ"])[:3]
    mfmt = lambda n: f"{n / 1e6:.2f}M"
    pct = lambda n: f"{n:.0f}%"
    kpis = [("Market occupancy", pct(occ), f"12-month average · {occ - occ_ly:+.1f} pts vs the year before".replace("-", "−")),
            ("Average daily rate", "IDR " + mfmt(adr), f"12-month average · {(adr / adr_ly - 1) * 100:+.0f}% vs the year before".replace("-", "−")),
            ("Booking window", f"{statistics.median(bws):.0f} days", f"median, from {min(bws)} to {max(bws)} days by month"),
            ("Length of stay", f"{min(loss)} to {max(loss)} nights", f"median by month · about {round(statistics.mean(s['listings'] for s in S), -2):,.0f} active listings")]
    k_html = "".join(f'<div class="kpi"><div class="l">{a}</div><div class="n">{b}</div><div class="d">{c}</div></div>' for a, b, c in kpis)
    period = f"{ym_label(S[0]['ym'])} – {ym_label(S[-1]['ym'])}"
    legend = f'<div class="legend"><span><i style="background:{C1}"></i>{period}</span><span><i style="background:{C2}"></i>Year before</span></div>'
    occ_chart = line_chart(S, "occ", "occ_ly", lambda n: f"{n:.0f}%", [30, 40, 50, 60, 70], "Occupancy")
    adr_chart = line_chart(S, "adr", "adr_ly", lambda n: f"{n / 1e6:.2f}M", [1.0e6, 1.2e6, 1.4e6, 1.6e6], "Average daily rate (IDR)")
    bw_chart = bar_chart(S, "bw", "days", [0, 5, 10, 15, 20, 25])
    scale = max(r["final_ly"] for r in P["rows"]) * 1.05
    pace_rows = "".join(
        f'<tr><td data-l="Month">{ym_label(r["ym"], long=True)}</td><td class="n" data-l="Today">{r["otb"]:.0f}%</td><td class="n" data-l="Same date last year">{r["otb_stly"]:.0f}%</td><td class="n" data-l="Final last year">{r["final_ly"]:.0f}%</td>'
        f'<td style="width:34%" data-l="Progress"><div class="track" style="width:{r["final_ly"] / scale * 100:.0f}%" data-tip="{ym_label(r["ym"], long=True)}&#10;On the books today: {r["otb"]}%&#10;Same date last year: {r["otb_stly"]}%&#10;Final last year: {r["final_ly"]}%"><b style="width:{r["otb"] / r["final_ly"] * 100:.0f}%"></b><u style="left:{r["otb_stly"] / r["final_ly"] * 100:.0f}%"></u></div></td></tr>'
        for r in P["rows"])
    pos = v.get("report_position") or {}
    facts = "".join(f'<div class="f"><span>{html.escape(a)}</span><span>{html.escape(b)}</span></div>' for a, b in pos.get("facts", []))
    r0 = P["rows"][0]
    reads = [
        ("A clear season", f"The area peaks in {', '.join(LONG[int(s['ym'][5:]) - 1] for s in sorted(hi3, key=lambda s: s['ym']))} ({min(s['occ'] for s in hi3):.0f} to {max(s['occ'] for s in hi3):.0f}% occupancy) and is softest in {', '.join(LONG[int(s['ym'][5:]) - 1] for s in sorted(lo3, key=lambda s: s['ym']))} ({min(s['occ'] for s in lo3):.0f} to {max(s['occ'] for s in lo3):.0f}%)."),
        ("Guests book late", f"Depending on the month, the median booking is made {min(bws)} to {max(bws)} days before arrival. On {read.day} {LONG[read.month - 1]}, {r0['otb']:.0f}% of the area's {ym_label(r0['ym'], long=True, year=False)} nights were booked; last {ym_label(r0['ym'], long=True, year=False)} finished at {r0['final_ly']:.0f}%. Most of the coming months is still to be sold."),
        ("More choice for guests", f"Over twelve months the average rate booked in the area was {abs((adr / adr_ly - 1) * 100):.0f}% {'lower' if adr < adr_ly else 'higher'} than the year before, and occupancy {abs(occ - occ_ly):.1f} points {'lower' if occ < occ_ly else 'higher'}. With this much supply, visibility and reputation decide who gets the booking."),
    ] + [tuple(x) for x in pos.get("readings", [])]
    reads_html = "".join(f'<div class="card"><h4>{html.escape(a)}</h4><p>{html.escape(b)}</p></div>' for a, b in reads[:3 if not pos.get("readings") else 6])
    tbl = "".join(f"<tr><td data-l='Month'>{ym_label(s['ym'])}</td><td data-l='Occupancy'>{s['occ']:.1f}%</td><td data-l='Year before'>{s['occ_ly']:.1f}%</td><td data-l='ADR (IDR)'>{s['adr']:,.0f}</td><td data-l='ADR, year before'>{s['adr_ly']:,.0f}</td><td data-l='Booking window (days)'>{s['bw']}</td><td data-l='Stay (nights)'>{s['los']}</td><td data-l='Active listings'>{s['listings']:,}</td></tr>" for s in S)
    has_map = bool(v.get("report_map"))
    position_card = (f'<div class="card"><h3>{html.escape(name)} in this market</h3><p class="sub">{html.escape(pos.get("sub", "Public information, read on the same day."))}</p><div class="rfacts">{facts}</div></div>' if facts else "")
    map_card = (f'<div class="card"><h3>The area measured</h3><p class="sub">{html.escape(Z["br_band"].replace(" BR", "-bedroom"))} villas within {Z["radius_m"] / 1000:.0f} km of Sayan{html.escape(Z.get("area_note", ""))}. The dot is {html.escape(name)}.</p><div id="report-map"></div></div>' if has_map else "")
    out = f"""{CSS}<div class="rep">
<div class="kpis">{k_html}</div>
<div class="grid2">
  <div class="card"><h3>Occupancy by month</h3><p class="sub">Booked nights ÷ available nights, {html.escape(Z["br_band"].replace(" BR", "-bedroom"))} villas in the area.</p>{legend}{occ_chart}</div>
  <div class="card"><h3>Average daily rate by month</h3><p class="sub">In IDR, across the same villas.</p>{legend}{adr_chart}</div>
</div>
<div class="grid2">
  <div class="card"><h3>On the books for the coming months</h3><p class="sub">Share of the area's nights already booked on {read_txt}. Bar: today, against where the month finished last year. Tick: the same date last year.</p>
    <table class="pace"><thead><tr><th>Month</th><th>Today</th><th>Same date last year</th><th>Final last year</th><th></th></tr></thead><tbody>{pace_rows}</tbody></table></div>
  <div class="card"><h3>How far ahead guests book</h3><p class="sub">Median days between booking and arrival, by month of stay.</p>{bw_chart}</div>
</div>
<div class="grid2">{map_card}{position_card}</div>
<div class="reads">{reads_html}</div>
<details><summary>View the data</summary><table><thead><tr><th>Month</th><th>Occupancy</th><th>Year before</th><th>ADR (IDR)</th><th>Year before</th><th>Booking window (days)</th><th>Stay (nights)</th><th>Active listings</th></tr></thead><tbody>{tbl}</tbody></table></details>
<p class="src">Source: PriceLabs Market Research, {html.escape(Z["br_band"].replace(" BR", "-bedroom"))} villas within {Z["radius_m"] / 1000:.0f} km of Sayan, Ubud (about {Z["compset"]:,} listings), read on {read_txt}. Headline figures are the average of the twelve monthly values. Occupancy counts the nights open for booking (nights blocked by owners are left out), and the set of active listings changes from month to month. This report describes the market around {html.escape(name)}: it does not measure {html.escape(name)}'s own occupancy or revenue.{" " + html.escape(pos["note"]) if pos.get("note") else ""}</p>
</div><div id="rep-tip"></div>"""
    v["report_html"] = out
    vp.write_text(json.dumps(v, ensure_ascii=False, indent=2), encoding="utf-8")
    import generate_villa
    print("report ->", generate_villa.build(vp).relative_to(HERE.parent))


if __name__ == "__main__":
    build(sys.argv[1])
