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

- **Mois de basse saison = fenêtre glissante M+1 à M+3** : les 3 mois calendaires qui suivent le mois
  en cours, recalculés à chaque lancement, jamais "les 3 plus creux de l'année" et **jamais plus loin
  que M+3** (06/11/2026 : avant, l'outil avançait jusqu'à 12 mois pour trouver 3 mois creux ; en février
  il aurait vendu novembre, où tous les calendriers sont vides). Dans la fenêtre, seuls les mois sous
  le seuil sont gardés : la page peut donc porter 1, 2 ou 3 mois, ou ne pas exister (secteur plein).
  `diagnostic.py market --year` montre l'année entière. Rien n'est daté en dur dans les outils.
  Les fenêtres de pointe sont exclues via `market/bali.json` → `peak_windows`
  (décembre s'arrête au 20, janvier commence le 6) ; un mois où le secteur dépasse 55 % d'occupation
  (`peak_occ_threshold`, 50 % jusqu'au 06/11/2026) n'est jamais vendu comme creux. Le message dit "early December" quand le tableau dit "December (1–20)".
- **Occupation marché** = PriceLabs Market Research (`market_research`, STR Index) : nuits réservées ÷
  nuits disponibles des 12 derniers mois terminés, sur le périmètre et la gamme de chambres de la zone
  (`area`, `br_band`, requête dans `str_query`). Jamais l'occupation de `get_neighbourhood_data` : c'est
  un échantillon mouvant d'annonces voisines, le même mois passé y change d'un relevé à l'autre.
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
  secteur au-dessus de 55 % sur les mois visés. Uluwatu 3-5BR tourne à 58-64 % de décembre à février
  (70 % sur l'année) : pas un marché basse saison.

## Diagnostic côté serveur et porte d'entrée propriétaire (05/11/2026)

Le diagnostic tourne maintenant **dans l'API du site** (`~/Claude/ac-collection-site/app/artifacts/api-server/src/diagnostic/`),
plus dans ce dépôt : `lib/airbnbListing.ts` (portage de `fetch_listing.py`, Railway lit Airbnb sans
blocage, testé le 05/11), `diagnostic/build.ts` (calcul de `villa.py`, résultats identiques au Python
sur 8 cas), `diagnostic/template.html` (ce gabarit, embarqué tel quel). Page dynamique
**ac-collection.com/diagnostic/<slug>** lue en base (`villa_diagnostics`), funnel dans `villa_funnel`.
**Plus de push Vercel** pour les nouvelles pages ; les anciennes restent sur plans.ac-collection.com.

- Libre-service : `ac-collection.com/partners` → formulaire (lien Airbnb, prénom, WhatsApp) → page
  prête en quelques secondes sur `/partners/diagnostic/<token>`. **12 % propriétaire, 10 % société de
  gestion**, rien d'avance, sans exclusivité, en parallèle (texte voulu par Anthony pour cette porte ;
  ne pas le reporter dans le PDF Owner).
- **En ligne de commande (06/11/2026) : `villa-site/diagnostic.py`.** `check <url|id>…` qualifie sans rien
  créer (zone, nuits libres par mois, villa vs secteur, verdict : OK / ne pas prospecter / pas de page) ;
  `create <url> [--adr --first-name --contact --handle --commission]` refait la lecture, demande la page au
  site et écrit `outreach/<slug>.md` avec les liens ac-collection.com ; `funnel [--status]` et
  `set <slug> <statut> --note` pilotent le funnel du site (compteur d'envois du jour sur 8) ;
  `market [--date AAAA-MM-JJ] [--year]` affiche l'occupation par zone et les mois creux de la fenêtre du
  jour, simule un autre jour ou toute l'année, et signale un relevé de marché de plus de 45 jours. Le jeton de routine est lu dans la config, jamais affiché.
- À la main (remplace `villa.py`) : `POST /api/diagnostics` avec la session admin ou le jeton de
  routine (`x-pdf-job-token`) : `{url, adr?, ratesIdr?: [10,16], name?, area?, firstName?, contact?, handle?, commission?}`.
  Sans `adr` : 75e centile PriceLabs de la zone. Funnel : `GET /api/diagnostics/funnel`,
  `PUT /api/diagnostics/funnel/<slug> {status, note}`.
- Jamais le WhatsApp du propriétaire dans la page : il vit dans `villa_funnel.handle`.
- Passe « à voir » (Anthony traite, le visiteur lit « Anthony is on it personally ») : lien non
  Airbnb, annonce illisible, hold / gros gestionnaires / nos villas, moins de 2 chambres, zone hors
  `market/bali.json`, aucun mois creux à venir (Uluwatu), plus de 15 demandes en 24 h.
- Secours : si Airbnb refuse le serveur, la demande passe en file ; `villa-site/owner_diagnostic.py`
  (launchd `com.acpartners.owner-diagnostic`, fichier dans `villa-site/launchd/`) lit l'annonce sur
  le Mac et la renvoie au site. Config `~/.local/share/ac-owner-diagnostic/config.json`.
- Mettre à jour le marché : modifier `market/bali.json` ici ET sa copie `src/diagnostic/market-bali.json`
  dans le site (même chose pour `config.json` et `template.html`), puis pousser le site.
- `villa.py --commission N` existe toujours pour une page statique à l'ancienne.
- **Nuits vides = le vrai calendrier de la villa (05/11/2026).** Le site (`lib/airbnbCalendar.ts`,
  `readAirbnbDays`) et `villa.py` (`fetch_calendar`) lisent le calendrier public Airbnb de l'annonce et
  comptent les nuits encore réservables dans chaque mois creux (`low_season[].open`, fenêtres de pointe
  exclues via `peak_windows.from/to`). La page dit alors « still has N open nights », la colonne
  « Open nights », et compare l'occupation de la villa à celle du marché. Calendrier illisible →
  ancienne estimation nuits × (1 − occupation du marché). Calendrier plein sur les mois creux → pas de
  page (« à voir »). `villa.py --no-calendar` force l'estimation. L'occupation du marché ne sert plus
  qu'à choisir les mois creux (seuil de 55 %) et à situer la villa.
- **Occupation du marché = STR Index (06/11/2026).** Market Research est activé sur le compte PriceLabs.
  `occ_ly` = relevé du 06/11/2026 (nov. 2025 → oct. 2026) : Canggu déc. 50 / janv. 55 / févr. 51, Pererenan
  54 / 52 / 51, Berawa 51 / 52 / 52, Seminyak 42 / 43 / 38, Nusa Dua 32 / 38 / 35, Uluwatu 58 / 63 / 64.
  Avec le seuil à 55 % (décision d'Anthony), toutes les zones ont leurs 3 mois creux sauf Uluwatu (secteur
  plein, pas de page automatique). Anciens relevés gardés dans `occ_nd_*`. Rafraîchir : une requête
  `market_research` par zone (20 par jour), en vérifiant le périmètre renvoyé (un nom de lieu seul peut
  retomber sur un cercle de 15 km). Les prix (`adr_*_idr`) restent les centiles de `get_neighbourhood_data`.

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
  AC en cours, 40+ villas pour Gravity) — filtrés dans `find_leads.py` (`HOLD`).
- **Sociétés à éviter (Anthony, 06/11/2026)** : **Listings Bali, Bali Villa Management, BREIG, OXO** —
  liste `AVOID` de `find_leads.py`, reprise dans `screenListing` du site. Cherchées en mot entier dans
  le titre, la description **et le nom de l'hôte** (« Hosted by Alpha By Listings Bali ») : une société
  n'écrit presque jamais son nom dans le texte de l'annonce, c'est l'hôte qui la trahit. Mot entier
  pour ne pas attraper BnBali Villa Management ni Bingin Villa Management, qui sont d'autres sociétés.
  `HOLD` et `BIG_PM` regardent aussi le nom de l'hôte. Ajouter une société = l'ajouter aux DEUX listes
  (`find_leads.py` et `api-server/src/diagnostic/build.ts`). Quand un
  partenariat d'agence se signe, ses villas entrent par la porte partenaire : on génère les pages
  avec `villa.py` pour l'onboarding, pas la séquence de prospection.

## Sourcing de leads

```bash
python3 villa-site/find_leads.py --areas Canggu Seminyak Pererenan Berawa --min-br 5 --pages 2 --out leads.md
```

Sans `--checkin / --checkout`, les dates sont choisies seules pour chaque zone : 5 nuits dans le
premier mois creux de sa fenêtre M+1 à M+3. La même commande reste juste toute l'année ; une zone
pleine sur toute la fenêtre est sautée. Les dates restent forçables à la main.

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
   localités, `peak_windows`, `usd_<devise>`. Source : PriceLabs MCP — occupation par `market_research`
   (STR Index, périmètre officiel ou rayon autour d'un point), prix par
   `get_neighbourhood_data(listing_id, pms_name)` sur une villa de référence de la zone
   (`get_listings` pour l'id).
2. Pointer `villa.py` sur ce fichier (`MARKET`), adapter `defaults.island`, la devise et la
   preuve sociale (`sender.proof`) dans `config.json`.
3. Même commande, même pile, même funnel. Les 10 pages "Distribution Plan" à la racine du repo
   (Dubai, Phuket, Tulum, Mykonos) sont le même playbook.

## Fichiers

`template.html` (site + section owner), `villa.py` (orchestrateur), `fetch_listing.py`,
`generate_villa.py` (injecte `offer` de config.json), `make_message.py`, `funnel.py`,
`make_clips.py` (vidéo réelle seulement), `config.json`, `market/bali.json`, `villas/*.json`,
`outreach/*.md`, `funnel.csv`. Docs : `README.md`, `BUSINESS-PLAN.md`, `COLD-APPROACH.md`.
