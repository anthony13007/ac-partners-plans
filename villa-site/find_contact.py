#!/usr/bin/env python3
"""Find who to talk to for a villa — the manager's WhatsApp, not the villa's.

Airbnb strips every phone number and email, so contacts come from the web. The pattern that
works in Bali, found the hard way: villa name -> the small agency that manages it -> the
agency's own site, which publishes a WhatsApp. One agency usually runs several villas, so a
single conversation can put 3-5 villas on our channels (this is exactly how GORO went).

This script keeps the register of what has been found, so the searching (done with WebSearch /
WebFetch in the session) is never repeated:

  python3 find_contact.py add "Villa Mila" --manager "Elld Property" \
      --whatsapp "+62 819 866 392" --email info@elldproperty.com \
      --site https://www.elldproperty.com --listing https://www.airbnb.com/rooms/xxx
  python3 find_contact.py add "Villa Ora" --manager "The Tropical Door" --status hold \
      --note "en hold cote AC, ne pas contacter"
  python3 find_contact.py list [--ready]

Statuses: found (usable), hold (do not contact), none (searched, nothing published),
big-pm (out of target).
"""
import json, argparse, pathlib, datetime, re

HERE = pathlib.Path(__file__).resolve().parent
REG = HERE / "contacts.json"

def load(): return json.loads(REG.read_text(encoding="utf-8")) if REG.exists() else {}
def save(d): REG.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

def wa_link(handle):
    digits = re.sub(r"\D", "", handle or "")
    return f"https://wa.me/{digits}" if len(digits) >= 9 else None

def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add"); a.add_argument("villa")
    a.add_argument("--manager", default=""); a.add_argument("--whatsapp", default="")
    a.add_argument("--email", default=""); a.add_argument("--site", default="")
    a.add_argument("--listing", default=""); a.add_argument("--status", default="found")
    a.add_argument("--note", default=""); a.add_argument("--also", nargs="*", default=[],
                   help="other villas the same manager runs")
    l = sub.add_parser("list"); l.add_argument("--ready", action="store_true")
    args = ap.parse_args()
    d = load()
    if args.cmd == "add":
        d[args.villa] = {k: v for k, v in dict(
            manager=args.manager, whatsapp=args.whatsapp, wa_link=wa_link(args.whatsapp),
            email=args.email, site=args.site, listing=args.listing, status=args.status,
            note=args.note, also_manages=args.also, found=datetime.date.today().isoformat()
        ).items() if v}
        save(d); print(json.dumps(d[args.villa], ensure_ascii=False, indent=1))
    else:
        rows = [(k, v) for k, v in d.items() if not args.ready or v.get("status") == "found"]
        for k, v in sorted(rows, key=lambda x: x[1].get("status", "")):
            print(f"{v.get('status','?'):8} {k[:26].ljust(26)} {v.get('manager','—')[:22].ljust(22)} "
                  f"{v.get('whatsapp','—').ljust(18)} {v.get('note','')}")
        print(f"\n{sum(1 for _, v in rows if v.get('status')=='found')} contactable / {len(d)} registered")

if __name__ == "__main__":
    main()
