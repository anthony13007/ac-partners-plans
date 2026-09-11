# AC Partners - distribution plans

Landing pages personnalisees par operateur (genere par generate_pages.py).

## villa-site/ — site villa "scroll film" + manque a gagner

Template de site pour une villa prospect (Bali basse saison), genere par `villa-site/generate_villa.py` :

- `villa-site/template.html` : le site (film au scroll a partir des photos du listing, galerie, tarifs, bouton WhatsApp) + section proprietaire (`owner_pitch: true` ou `?owner` dans l'URL) qui chiffre les nuits vides de basse saison et vend le package Site + Distribution AC Partners.
- `villa-site/villas/<slug>.json` : une config par villa (nom, zone, ADR, photos, saisons creuses, taux de capture, commission).
- `python3 villa-site/generate_villa.py` construit `villa-site/<slug>.html`, servi sur Vercel en `/villa-site/<slug>`.

Demo : `villa-site/demo-seminyak.html` (donnees marche PriceLabs Seminyak 4-10BR, photos d'emprunt a remplacer).

### Mode "scroll video" (comme le reel Webild)

Ajouter `tour_clips` dans le JSON de la villa : le scroll fait avancer la video (visite de la villa), le titre reste pose dessus, le site arrive a la fin. Sans `tour_clips`, la page retombe sur le film photo.

```json
"tour_clips": [
  {"src": "https://.../clip-01.mp4", "caption": "The drive in."},
  {"src": "https://.../clip-02.mp4", "caption": "The pool at dusk."}
]
```

Encodage des clips pour un scrub fluide (une image cle par frame, mp4 H.264, faststart) :

```
ffmpeg -i tour.mp4 -an -vf "scale=1280:-2,fps=24" -c:v libx264 -g 1 -keyint_min 1 -crf 23 -pix_fmt yuv420p -movflags +faststart clip-01.mp4
```

Les clips peuvent venir d'une video du proprietaire (drone, gimbal, reel Insta) ou etre generes photo par photo (image-to-video Higgsfield), puis heberges sur Vercel a cote de la page.
