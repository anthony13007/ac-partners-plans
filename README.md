# AC Partners - distribution plans

Landing pages personnalisees par operateur (genere par generate_pages.py).

## villa-site/ — site villa "scroll film" + manque a gagner

Template de site pour une villa prospect (Bali basse saison), genere par `villa-site/generate_villa.py` :

- `villa-site/template.html` : le site (film au scroll a partir des photos du listing, galerie, tarifs, bouton WhatsApp) + section proprietaire (`owner_pitch: true` ou `?owner` dans l'URL) qui chiffre les nuits vides de basse saison et vend le package Site + Distribution AC Partners.
- `villa-site/villas/<slug>.json` : une config par villa (nom, zone, ADR, photos, saisons creuses, taux de capture, commission).
- `python3 villa-site/generate_villa.py` construit `villa-site/<slug>.html`, servi sur Vercel en `/villa-site/<slug>`.

Demo : `villa-site/demo-seminyak.html` (donnees marche PriceLabs Seminyak 4-10BR, photos d'emprunt a remplacer).
