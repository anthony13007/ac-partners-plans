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

### Mode "scroll video" sans Higgsfield

`python3 villa-site/make_clips.py <slug>` rend un clip Ken Burns par photo avec ffmpeg (zoom / pan, une image cle par frame, ~1-2 Mo par clip, $0), les depose dans `media/<slug>/` et ecrit `tour_clips` dans le JSON ; le scroll fait avancer la video, le titre reste pose dessus, le site arrive a la fin. Avec une vraie video du proprio (drone, reel) : `make_clips.py <slug> --from-video fichier.mp4` la decoupe en plans de 3 s scrubbables. Sans `tour_clips`, la page retombe sur le film photo.

Alternatives gratuites a Higgsfield pour de la vraie image-to-video : Kling et Hailuo (MiniMax) donnent des credits quotidiens gratuits, Luma Dream Machine un quota mensuel ; exporter en mp4 puis `--from-video`.

### Fichiers

- `template.html` : le site (film au scroll, galerie, tarifs, WhatsApp) + section proprietaire (nuits vides, manque a gagner, package).
- `config.json` : URL Vercel, WhatsApp, stats Superhost, defauts (capture 35 %, commission 10 %, highlight 5 %, site seul $690 + $29/mois).
- `market/bali.json` : occupation marche par zone et par mois (12 derniers mois + annee precedente pour Canggu), ADR p50/p75/p90 par nombre de chambres, alias de localites.
- `villas/*.json` : une config par villa. `demo-seminyak` = demo (photos d'emprunt), `the-dreamtime-house` = test reel (8 photos Airbnb, 8 clips).
- `outreach/*.md`, `funnel.csv`.

Encodage manuel d'un clip si besoin : `ffmpeg -i tour.mp4 -an -vf "scale=1024:-2,fps=24" -c:v libx264 -g 1 -keyint_min 1 -crf 27 -pix_fmt yuv420p -movflags +faststart clip-01.mp4`.
