#!/usr/bin/env python3
"""Relais du Mac pour la porte d'entree proprietaire (ac-collection.com/partners).

Depuis le 05/11/2026 le diagnostic est produit par le site lui-meme : il lit l'annonce Airbnb, calcule
le manque a gagner et sert la page sur ac-collection.com/diagnostic/<slug>. Plus de push Vercel.

Ce script ne sert que de secours : si Airbnb refuse la lecture au serveur (Railway), la demande passe
en file ; le Mac lit alors l'annonce avec fetch_listing.py et la renvoie au site, qui fait le reste.
Meme principe et meme jeton que pdf_jobs.

  python3 villa-site/owner_diagnostic.py            # une passe sur la file
  python3 villa-site/owner_diagnostic.py --dry-run  # liste ce qui serait traite, ne touche a rien

Config (hors ~/Documents, macOS bloque launchd dessus) : ~/.local/share/ac-owner-diagnostic/config.json
  {"token": "<PDF_JOB_TOKEN du site>", "base": "https://www.ac-collection.com"}
Les alertes (WhatsApp, e-mail, Telegram, cockpit) partent du site, pas d'ici.
"""
import fcntl, json, pathlib, sys, time, traceback, urllib.error, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

CFG_PATH = pathlib.Path.home() / ".local/share/ac-owner-diagnostic/config.json"
LOCK_PATH = pathlib.Path.home() / ".local/share/ac-owner-diagnostic/run.lock"


def log(msg):
    print(time.strftime("%Y-%m-%d %H:%M:%S"), msg, flush=True)


def api(cfg, method, path, body=None):
    req = urllib.request.Request(
        cfg["base"].rstrip("/") + "/api" + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"x-pdf-job-token": cfg["token"], "Content-Type": "application/json", "User-Agent": "ac-owner-diagnostic/2"},
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode() or "{}")


def process(cfg, lead):
    lid, url = lead["id"], lead["listing_url"]
    log(f"lead {lid} {lead['first_name']} ({lead['profile']}) {url}")
    try:
        from fetch_listing import fetch_listing

        listing = fetch_listing(url, tries=5)
        if not listing.get("title") or not listing.get("photos"):
            api(cfg, "POST", f"/owner-leads-queue/{lid}/review",
                {"reason": "Annonce illisible depuis le serveur ET depuis le Mac (en pause, privee, ou retiree)."})
            log("  -> a voir : annonce illisible")
            return
        out = api(cfg, "POST", f"/owner-leads-queue/{lid}/listing", listing)
        log(f"  -> {out.get('status')} {out.get('pageUrl') or out.get('note') or ''}")
    except urllib.error.HTTPError as e:
        log(f"  site : HTTP {e.code} (la demande reste en file, le filet du site la reprendra)")
    except Exception as e:  # noqa: BLE001
        log(traceback.format_exc())
        try:
            api(cfg, "POST", f"/owner-leads-queue/{lid}/review", {"reason": f"Erreur du relais Mac : {type(e).__name__}: {str(e)[:200]}"})
        except Exception:  # noqa: BLE001
            log("impossible de prevenir le site")


def main():
    dry = "--dry-run" in sys.argv
    if not CFG_PATH.exists():
        sys.exit(f"config manquante : {CFG_PATH}")
    cfg = json.loads(CFG_PATH.read_text(encoding="utf-8"))
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    lock = open(LOCK_PATH, "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        log("une autre passe tourne, on sort")
        return
    try:
        leads = api(cfg, "GET", "/owner-leads-queue/pending").get("leads", [])
    except urllib.error.HTTPError as e:
        log(f"file indisponible : HTTP {e.code}")
        return
    except Exception as e:  # noqa: BLE001
        log(f"file indisponible : {e}")
        return
    if dry:
        log(f"[dry-run] {len(leads)} demande(s) en file pour le Mac")
    for lead in leads:
        if dry:
            log(f"[dry-run] lead {lead['id']} {lead['first_name']} {lead['listing_url']} ({lead['profile']})")
            continue
        process(cfg, lead)


if __name__ == "__main__":
    main()
