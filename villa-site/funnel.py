#!/usr/bin/env python3
"""Funnel tracker: villa-site/funnel.csv (one row per villa).

  python3 funnel.py add <slug> [--contact "Name" --handle "+62..." --channel whatsapp]
  python3 funnel.py set <slug> <status> [--note "..."]     statuses: draft sent replied call signed highlight refused dead
  python3 funnel.py list
  python3 funnel.py due            # follow-ups due today (J+3 / J+7 / J+14 after 'sent' with no reply)
  python3 funnel.py stats          # response / call / signature rates + kill criteria of BUSINESS-PLAN.md
"""
import csv, sys, json, pathlib, datetime, argparse

HERE = pathlib.Path(__file__).resolve().parent
CSV = HERE / "funnel.csv"
FIELDS = ["slug", "villa", "area", "bedrooms", "adr", "empty_nights", "loss", "contact", "handle", "channel",
          "page_url", "status", "created", "sent", "replied", "call", "closed", "last_touch", "next_action", "notes"]
STATUSES = ["draft", "sent", "replied", "call", "signed", "highlight", "refused", "dead"]

def load():
    if not CSV.exists(): return []
    with CSV.open(encoding="utf-8", newline="") as f: return list(csv.DictReader(f))

def save(rows):
    with CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
        for r in rows: w.writerow({k: r.get(k, "") for k in FIELDS})

def today(): return datetime.date.today().isoformat()

def add(slug, contact="", handle="", channel="whatsapp", status="draft"):
    from make_message import gap, CFG
    cfg = json.loads((HERE / "villas" / f"{slug}.json").read_text(encoding="utf-8"))
    g = gap(cfg); rows = load()
    row = next((r for r in rows if r["slug"] == slug), None)
    new = {"slug": slug, "villa": cfg["name"], "area": cfg["area"], "bedrooms": cfg["bedrooms"], "adr": cfg["adr"],
           "empty_nights": g["empty"], "loss": int(g["loss"]), "contact": contact or cfg.get("contact", {}).get("name", ""),
           "handle": handle or cfg.get("contact", {}).get("handle", ""), "channel": channel or cfg.get("contact", {}).get("channel", "whatsapp"),
           "page_url": f'{CFG["base_url"]}/villa-site/{slug}?owner', "status": status, "created": today(), "last_touch": today(),
           "next_action": "send step 1"}
    if row: row.update({k: v for k, v in new.items() if v not in ("", None)})
    else: rows.append(new)
    save(rows); return new

def set_status(slug, status, note=""):
    assert status in STATUSES, f"status must be one of {STATUSES}"
    rows = load(); row = next((r for r in rows if r["slug"] == slug), None)
    if not row: sys.exit(f"{slug} not in funnel, run add first")
    row["status"] = status; row["last_touch"] = today()
    stamp = {"sent": "sent", "replied": "replied", "call": "call", "signed": "closed", "highlight": "closed", "refused": "closed", "dead": "closed"}.get(status)
    if stamp and not row.get(stamp): row[stamp] = today()
    row["next_action"] = {"sent": "J+3 follow-up", "replied": "send step 2 (page + offer)", "call": "call, then contract", "signed": "onboarding (channels, calendar, pricing)",
                          "highlight": "add to AC Collection site", "refused": "", "dead": "", "draft": "send step 1"}[status]
    if note: row["notes"] = (row.get("notes", "") + " | " if row.get("notes") else "") + f"{today()} {note}"
    save(rows); return row

def due():
    out = []; t = datetime.date.today()
    for r in load():
        if r["status"] != "sent" or not r.get("sent"): continue
        d = (t - datetime.date.fromisoformat(r["sent"])).days
        step = "J+3" if d >= 3 and d < 7 else "J+7" if d >= 7 and d < 14 else "J+14" if d >= 14 else None
        if step: out.append((r["slug"], r["villa"], d, step))
    return out

def stats():
    rows = load(); n = len(rows)
    sent = [r for r in rows if r["status"] != "draft"]
    replied = [r for r in sent if r["status"] in ("replied", "call", "signed", "highlight", "refused")]
    calls = [r for r in sent if r["status"] in ("call", "signed", "highlight")]
    signed = [r for r in sent if r["status"] == "signed"]; hl = [r for r in sent if r["status"] == "highlight"]
    pct = lambda a, b: f"{(100*len(a)/len(b)):.0f}%" if b else "–"
    lines = [f"villas: {n} | sent: {len(sent)} | replied: {len(replied)} ({pct(replied, sent)}) | calls: {len(calls)} ({pct(calls, sent)}) | signed: {len(signed)} ({pct(signed, sent)}) | highlights: {len(hl)}",
             f"pipeline value (signed, fee on targeted nights): see outreach/*.md; kill criteria (BUSINESS-PLAN §6):"]
    if len(sent) >= 30:
        rr = len(replied) / len(sent); sr = len(signed) / len(sent)
        lines.append(f"  response rate {rr:.0%} -> {'OK' if rr >= 0.10 else 'BELOW 10%: change the hook or the channel'}")
        lines.append(f"  signature rate {sr:.1%} -> {'OK' if sr >= 0.02 or len(sent) < 100 else 'BELOW 2% at 100 sent: lead with the free site'}")
    else:
        lines.append(f"  kill criteria evaluated from 30 sent (now {len(sent)}); hard stop at 100 sent: <10% replies or <2 signatures")
    return "\n".join(lines)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("add"); p.add_argument("slug"); p.add_argument("--contact", default=""); p.add_argument("--handle", default=""); p.add_argument("--channel", default="whatsapp")
    p = sub.add_parser("set"); p.add_argument("slug"); p.add_argument("status"); p.add_argument("--note", default="")
    sub.add_parser("list"); sub.add_parser("due"); sub.add_parser("stats")
    a = ap.parse_args()
    if a.cmd == "add": print(add(a.slug, a.contact, a.handle, a.channel))
    elif a.cmd == "set": print(set_status(a.slug, a.status, a.note))
    elif a.cmd == "list":
        for r in load(): print(f'{r["slug"]:28} {r["status"]:10} sent={r.get("sent","")} last={r.get("last_touch","")} next={r.get("next_action","")}')
    elif a.cmd == "due":
        for slug, villa, d, step in due(): print(f"{step:5} {slug} ({villa}) sent {d} days ago")
    elif a.cmd == "stats": print(stats())
