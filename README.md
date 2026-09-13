# AC Partners - distribution plans

Landing pages personnalisees par operateur (genere par generate_pages.py). Prod Vercel :
https://ac-partners-plans-elvs.vercel.app (branche `main` ; les previews de branche sont proteges par login).

## villa-site/ — machine "site villa + manque a gagner + message" (Bali basse saison)

Une commande par villa, de l'URL au message pret a coller :

```
python3 villa-site/villa.py "https://www.airbnb.com/rooms/<id>" --adr 900 \
    --first-name Ketut --contact "Ketut Sudira" --handle "+62 8xx" --channel whatsapp [--clips] [--push]
```

Ce que ca fait (~1 min, 5 avec les clips) :

1. `fetch_listing.py` lit le listing (Airbnb : photos avec leur piece, chambres, voyageurs, note, description, equipements ; autre site : photos + titre). Marche depuis l'ordi, pas depuis le cloud.
2. Resout la zone (Kuta Utara -> Canggu, Tibubeneng -> Berawa...) et prend l'occupation marche PriceLabs des 3 mois les plus bas dans `market/bali.json` (cache par zone et gamme de chambres, releve du 11/09/2026, a rafraichir chaque trimestre via `get_neighbourhood_data` sur la villa de reference indiquee dans le fichier).
3. Choisit 8 photos (exterieurs d'abord, une par piece, pas de deco), ecrit `villas/<slug>.json`. ADR : `--adr` en USD, sinon p75 PriceLabs de la gamme (marque comme tel).
4. `generate_villa.py` construit `villa-site/<slug>.html` (servi en `/villa-site/<slug>`, `?owner` pour la section proprietaire).
5. `make_message.py` ecrit `outreach/<slug>.md` : accroche WhatsApp, variante Instagram, offre (etape 2), fallback highlight, relances J+3/7/14 datees. Rien n'est envoye.
6. `funnel.py add` ajoute la ligne dans `funnel.csv` (statut `draft`), puis commit.

Ensuite, a la main : coller l'etape 1 dans WhatsApp, `python3 villa-site/funnel.py set <slug> sent`, et chaque jour `funnel.py due` (relances) et `funnel.py stats` (taux de reponse / signature, kill criteria).

Re-lancer `villa.py` sur un slug existant garde les retouches manuelles du JSON (photos, textes) et ne rafraichit que la donnee marche, l'ADR et les sorties ; `--fresh` repart de zero. `"photos_locked": true` protege une selection de photos faite a la main.

### Film au scroll : photos animées en CSS, pas de vidéo générée

Le hero anime les photos du listing en pleine résolution (2560 px) directement en CSS, zoom et
pan différents par image, pilotés par le scroll. Net sur tout écran, ~3 Mo par villa, cadrage
correct sur téléphone. Les mp4 générés depuis des photos ont été abandonnés (2,5 à 9 Mo par clip
pour un rendu flou, et un 16:9 recadré à 25 % en portrait). `make_clips.py <slug> --from-video
tour.mp4` reste disponible pour de vraies images tournées par un propriétaire (drone, reel).
Vitesse du film : `scroll_vh_per_photo` dans le JSON (défaut 34).

### L'offre : une pile de valeur, une seule source

`config.json` → `offer.stack` : chaque ligne avec son prix seul barré puis "Included", le total
de valeur, puis un prix unique (10 % sur les nuits vendues), les conditions et la garantie. La
même liste alimente la section propriétaire de la page et le message 3. Côté guest : un seul
tarif généraliste (`--rates-idr 10 16` → "IDR 10M – 16M / night"), et "Check availability"
renvoie toujours chez le propriétaire (WhatsApp, sinon son annonce), jamais chez nous.

### Basse saison = les 3 prochains mois, pointes exclues

Fenêtre glissante à partir d'aujourd'hui, jamais "les 3 mois les plus creux de l'année".
`market/bali.json` → `peak_windows` retire Noël/Nouvel An (décembre s'arrête au 20, janvier
commence le 6) ; un mois au-dessus de 50 % d'occupation n'est jamais présenté comme creux.

**La référence complète du process, pour Bali et pour tout nouveau marché : [villa-site/SKILL.md](villa-site/SKILL.md)** (aussi installée comme skill `villa-prospect`).

### Fichiers

- `template.html` : le site (film au scroll, galerie, tarifs, WhatsApp) + section proprietaire (nuits vides, manque a gagner, package).
- `config.json` : URL Vercel, WhatsApp, stats Superhost, defauts (capture 35 %, commission 10 %, highlight 5 %, site seul $690 + $29/mois).
- `market/bali.json` : occupation marche par zone et par mois (12 derniers mois + annee precedente pour Canggu), ADR p50/p75/p90 par nombre de chambres, alias de localites.
- `villas/*.json` : une config par villa. `demo-seminyak` = demo, `the-dreamtime-house` = villa AC (test), `villa-soul-moon` et `villa-luja` = prospects reels.
- `outreach/*.md`, `funnel.csv`.

