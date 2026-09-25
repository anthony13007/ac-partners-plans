---
name: villa-prospect
description: Machine de prospection AC Partners — d'une URL de villa (Airbnb ou site) à une page Vercel personnalisée (film au scroll + manque à gagner + offre en pile Hormozi), la séquence de 3 messages et la ligne de funnel, en une commande. Référence pour Bali et pour tout marché (Dubai, Phuket, Tulum, Mykonos…). Déclencheurs — "prospecte cette villa", URL Airbnb + "fais la page", "relance", "funnel", "nouveau marché".
---

# Villa prospect — la référence (validée par Anthony, 11-13/09/2026)

Repo `~/Claude/ac-partners-plans` (GitHub `anthony13007/ac-partners-plans`), dossier `villa-site/`.
Prod : **https://plans.ac-collection.com/villa-site/<slug>** (branche `main` uniquement ; les
previews de branche sont derrière un login Vercel). `?owner` révèle la section propriétaire.

## Deux modèles de présentation (décision d'Anthony, 25/09/2026) — ne jamais les mélanger

| | **Modèle Owner** (lancement de villa) | **Modèle B2B** (management company) |
|---|---|---|
| Cible | propriétaire qui lance / confie sa villa | société de gestion (3 à 40 villas) |
| Rôle d'Anthony | marketing only, seul distributeur, sous son profil Superhost | distribution en parallèle, ils gardent tout |
| Argument | profil : 795 avis, 4,8★, 10 ans d'hôte → la villa ne part pas de zéro | la douleur : nuits vides chiffrées, analyse marché PriceLabs |
| Prix | **Lifetime 12 %** des nuits vendues | 10 % des nuits vendues |
| Support | PDF `offer/build_offer.py --villa "Nom" --cover … --photos …` | page diagnostic `villa.py` + 3 messages + funnel |
| Interdits | iCal, « in parallel », low season, garantie, « only one marketing », « we » | — |
| Commun | équipe opérationnelle (villa manager + staff) inchangée ; site direct + ac-collection.com = 17 % de frais OTA économisés | idem |

## La commande (5 min par villa, tout compris)

```bash
cd ~/Claude/ac-partners-plans && python3 villa-site/villa.py "<url airbnb ou site>" \
  --name "Villa X" --area Canggu --adr 625 --rates-idr 10 16 \
  --first-name Ketut --contact "Ketut (owner)" --handle "+62 8xx" --channel whatsapp
```

Sort : `villas/<slug>.json` → `<slug>.html` → `outreach/<slug>.md` (3 messages + fallback +
relances datées) → ligne `funnel.csv` (statut `draft`) → commit. Puis :

```bash
git checkout main && git merge --no-edit claude/ac-partners-bali-villas-6cjfpl && git push origin main
```

(Vercel redéploie `main` en ~30 s ; attendre avec `until curl -s <url> | grep -q "<marqueur du dernier commit>"`.)
Re-lancer sur un slug existant garde les retouches manuelles ; `--fresh` repart de zéro ;
`"photos_locked": true` protège une sélection de photos faite à la main.

## Ce qu'il faut demander à Anthony avant d'envoyer

1. **L'ADR réel** (`--adr`, USD) et si possible la fourchette IDR (`--rates-idr 10 16`). Sans
   ADR, le script prend le p75 PriceLabs de la zone et le marque comme tel.
2. **Le contact** : prénom + WhatsApp (`--handle`). Sans handle, le bouton guest "Check
   availability" renvoie vers **l'annonce du proprio** ; jamais vers notre numéro.
3. **Son OK explicite** pour chaque envoi. Cap 8 envois/jour. Jamais recontacter un refus.

## Règles gravées (chacune a coûté une correction)

- **Mois de basse saison = les 3 prochains mois calendaires** à partir d'aujourd'hui, jamais
  "les 3 plus creux de l'année" (en septembre on parle d'oct/nov/déc, pas de fév/mars).
  Les fenêtres de pointe sont exclues via `market/bali.json` → `peak_windows`
  (décembre s'arrête au 20, janvier commence le 6) ; un mois > 50 % d'occupation n'est jamais
  vendu comme creux. Le message dit "early December" quand le tableau dit "December (1–20)".
- **Occupation marché** = `occupancy.monthly.market_occupancy_ly` de PriceLabs (final de l'an
  dernier), jamais `market_occupancy` (on-the-books, décroît avec l'horizon).
- **L'offre est une pile Hormozi**, une seule source : `config.json` → `offer.stack`
  (7 lignes, prix barré + "Included", total "worth $2,674 → $0", puis UN prix : 10 % sur les
  nuits vendues, 3 conditions, garantie = 50 % de la cible). Elle alimente la page ET le
  message 3. Le site n'est qu'une ligne de la pile, jamais la vedette ; le bandeau final parle de
  la basse saison, pas du site.
- **Séquence** : 3 messages courts, l'offre seulement en 3e. Message 1 = qui je suis + une
  question. Message 2 = le chiffre + le lien `?owner` + le lien guest **de la même villa**
  (jamais une autre villa en vitrine). Message 3 = la pile. Fallback = highlight 5 %.
- **Côté guest** : un seul tarif généraliste ("IDR 10M – 16M / night" ou "From $X"), jamais
  de grille par saison. "Check availability" → WhatsApp du proprio, sinon son annonce.
- **Film au scroll** : les photos (2560 px, `url_hd`) sont animées en CSS (zoom/pan par
  image). **Pas de mp4 générés depuis des photos** : 2,5-9 Mo par clip pour du flou, et un
  16:9 recadré à 25 % sur un téléphone vertical. `make_clips.py --from-video` seulement pour
  de vraies images tournées par un proprio. Vitesse : `scroll_vh_per_photo` (défaut 34).
- **Mobile / WebKit** : `100svh` sur le hero ; tableau du manque à gagner empilé en cartes,
  avec `table, tbody, tr, td {display:block}` (Safari garde l'algorithme de tableau si la
  `table` reste en `display:table` → page 2x plus large, dézoom, fond crème à moitié) ;
  Ne JAMAIS mettre   `html,body{overflow-x:hidden}` (Safari en fait un conteneur de défilement et `position:sticky` cesse de coller :
  le hero défile, le rail du film apparaît en noir) → `overflow-x:clip` sur html/body, `hidden` sur body seul en repli.
  **Les captures headless Chrome à 393 px mentent** (layout 980 px recadré) et Chrome tolère
  ce que Safari casse : la vérification finale se fait sur l'iPhone d'Anthony.
- **Photos** : extérieurs d'abord (nuit/piscine en hero), une par pièce, pas de déco ni
  d'assiettes ; les labels Airbnb ("Pool image 2", "Exterior") guident la sélection
  (`PHOTO_PLAN`, 2 passes). Airbnb sert parfois une page sans photos : `fetch_listing.py`
  réessaie 5 fois ; trois formats d'URL photo existent (`miso/`, `hosting/`, `prohost-api/`).
- **Hors cible** : villa "Managed by" un gros PM (le signaler, Anthony décide), 1-3BR,
  > 60 % en basse saison. Uluwatu 3-5BR tourne à 78 % : pas un marché basse saison.

## Trouver le contact (le vrai goulot)

Airbnb ne publie jamais téléphone ni e-mail, et la plupart des villas n'ont aucun site propre :
6 recherches web sur les villas les mieux notées ont donné 0 numéro. **Ce qui marche : viser le
gestionnaire, pas la villa.** Nom de la villa → recherche web → la petite agence qui la gère →
son site publie un WhatsApp. Une agence gère en général 3 à 5 villas, donc une conversation
peut en amener plusieurs : c'est exactement le schéma GORO (Villa Luja).

```bash
python3 villa-site/find_contact.py add "Villa X" --manager "Agence Y" \
    --whatsapp "+62 8xx" --site https://… --listing https://airbnb.com/rooms/…
python3 villa-site/find_contact.py list --ready     # ceux qu'on peut contacter
```

Registre : `villa-site/contacts.json`. Statuts : `found`, `hold` (ne pas contacter),
`none` (cherché, rien de publié), `big-pm`. Pistes par ordre de rendement : site de l'agence
gestionnaire, Instagram de la villa (WhatsApp en bio, demande une session connectée),
Google Maps si la villa est enregistrée comme établissement. **Tropical Door est en hold**
(règle permanente d'Anthony, filtrée dans `find_leads.py`).

- **Ne jamais prospecter** : Tropical Door (hold), The Bali Agent et **Gravity Bali** (partenariats
  AC en cours, 40+ villas pour Gravity) — filtrés dans `find_leads.py` (`HOLD`). Quand un
  partenariat d'agence se signe, ses villas entrent par la porte partenaire : on génère les pages
  avec `villa.py` pour l'onboarding, pas la séquence de prospection.

## Sourcing de leads

```bash
python3 villa-site/find_leads.py --areas Canggu Seminyak Pererenan Umalas --min-br 5 \
    --checkin 2026-11-05 --checkout 2026-11-10 --pages 2 --out leads-nov.md
```

Décode les id d'annonces (base64 `StayListing:…`) des pages de recherche Airbnb. **Chercher
avec des dates de basse saison est la qualification** : seules les villas au calendrier ouvert
remontent, donc le trou se qualifie tout seul. Chaque annonce est récupérée (cache
`.leads-cache/`), filtrée (taille, gros gestionnaire, hold, notre propre portefeuille) et
classée. 40 leads obtenus pour Canggu/Seminyak/Pererenan/Umalas en 5BR+.

## Funnel

`python3 villa-site/funnel.py set <slug> sent|replied|call|signed|highlight|refused --note "…"`,
`funnel.py due` (relances J+3/7/14), `funnel.py stats` (kill criteria à 30/60/100 envois).
`funnel.py add` ne touche jamais au statut d'une villa déjà avancée (bug corrigé le 13/09).

## Nouveau marché (Dubai, Phuket, Tulum, Mykonos…)

1. Créer `villa-site/market/<marché>.json` sur le modèle de `bali.json` : par zone
   `occ_ly` (12 mois), `adr_median/p75/p90_idr` (ou devise locale + taux), `aliases` de
   localités, `peak_windows`, `usd_<devise>`. Source : PriceLabs MCP
   `get_neighbourhood_data(listing_id, pms_name, include_occupancy=true)` sur une villa de
   référence de la zone (`get_listings` pour l'id) — ou `market_research` si Market Research est
   activé sur le compte.
2. Pointer `villa.py` sur ce fichier (`MARKET`), adapter `defaults.island`, la devise et la
   preuve sociale (`sender.proof`) dans `config.json`.
3. Même commande, même pile, même funnel. Les 10 pages "Distribution Plan" à la racine du repo
   (Dubai, Phuket, Tulum, Mykonos) sont le même playbook.

## Fichiers

`template.html` (site + section owner), `villa.py` (orchestrateur), `fetch_listing.py`,
`generate_villa.py` (injecte `offer` de config.json), `make_message.py`, `funnel.py`,
`make_clips.py` (vidéo réelle seulement), `config.json`, `market/bali.json`, `villas/*.json`,
`outreach/*.md`, `funnel.csv`. Docs : `README.md`, `BUSINESS-PLAN.md`, `COLD-APPROACH.md`.
