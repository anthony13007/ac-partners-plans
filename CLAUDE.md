# AC Partners / AC Collection — règles de prospection, vente et marketing

Ces règles s'appliquent à tout message, séquence ou contenu commercial écrit pour Anthony.

## Faits à jour sur Anthony
- Hôte Airbnb depuis **10 ans**, **800+ avis** (Superhost). Formulation EN : « Airbnb Superhost for 10 years (800+ reviews) ».
- Ne plus utiliser les anciens chiffres (9 ans, 759 avis, 4,84★).
- Commission partenaires : **12 % sur les nuits vendues uniquement** (plus 10 %). Pas de frais de mise en place, pas d'exclusivité, pas de durée minimum. Ne l'annoncer qu'une fois le prospect engagé, jamais dans le 1er message.

## Réflexe avant d'écrire une ligne : penser high-ticket closer
Répondre à ces quatre questions, dans l'ordre, AVANT de rédiger :
1. **À qui je parle ?** (wedding planner, gestionnaire de villas, propriétaire, agence de séminaires, conciergerie…)
2. **Quel est SON objectif business ?** (ce qu'il vend à ses propres clients, ce qui le fait gagner de l'argent)
3. **Qu'est-ce qu'il va regarder me concernant ?** (ce qui prouve que je peux l'aider, lui — pas ce dont je suis fier)
4. **Quel est SON intérêt à me répondre ?** (argent, temps gagné, risque retiré, client servi)

Toute preuve de crédibilité doit être pertinente pour CE lecteur. Sinon elle dégage.

## Erreur à ne jamais refaire
Ne pas mettre « Airbnb Superhost / 800+ avis » partout par défaut.
- Pertinent : pour un **propriétaire ou un hôte** Airbnb (pair à pair, preuve de performance sur la plateforme).
- Hors sujet : pour un **wedding planner, une agence événementielle, une agence de séminaires**. Ils ne réservent pas sur Airbnb et se moquent des avis voyageurs.

## Grille par cible
**Wedding planners / event planners (Bali)**
- Leur objectif : livrer un événement parfait à leur client, protéger leur réputation, garder leur marge.
- Ce qu'ils regardent : la villa (photos, capacité en invités, chambres), l'autorisation d'événement (musique, horaire, banjar), la disponibilité sur leurs dates, la réactivité et la fiabilité de l'interlocuteur.
- Leur intérêt : un lieu sûr et prêt à réserver + une commission d'apporteur sur chaque réservation.
- Preuves à citer : les villas nommées (ex. The Dreamtime House, Umalas, 7 chambres), capacité, conditions événement, ac-collection.com.

**Propriétaires / gestionnaires de villas**
- Leur objectif : remplir le calendrier (surtout en basse saison) sans perdre le contrôle.
- Ce qu'ils regardent : la demande que j'apporte, qui je suis sur le marché, ce que ça leur coûte.
- Leur intérêt : réservations en plus, gestion et relation voyageur conservées, paiement seulement au résultat.
- Ici Superhost + avis EST pertinent.

## Règles de forme
- **Sonder d'abord.** Le 1er message pose une question sur SON besoin avant de pitcher. On présente l'offre seulement quand on sait ce qu'il cherche.
- Une seule villa en exemple (ex. The Dreamtime House), pas une liste. Pas de promesse de capacité événement.
- Anglais par défaut à Bali.
- **Signature : « Anthony » seulement**, jamais « Anthony Campana » ni de titre, dans tous les messages (WhatsApp, e-mail, Airbnb). Les PDF d'offre gardent leur bloc signature complet.
- Court, orienté vers le lecteur, une seule question facile à la fin.
- Ne jamais affirmer ce qui n'est pas vérifié (capacité événement, partenariats, demandes entrantes). Signaler à Anthony ce qu'il faut confirmer avant l'envoi.
- Aucun message envoyé automatiquement : on prépare, Anthony envoie.
- Airbnb : pas de lien ni de coordonnées dans le 1er message. WhatsApp : liens autorisés.

## Process « analyse + offre » (validé par Anthony le 24/11/2026, cas The Ridge Bali)
À utiliser dès qu'un prospect répond, demande « l'analyse » ou un rendez-vous (propriétaire, société de gestion, hôtel). Deux livrables envoyés ensemble : **une page d'analyse en ligne (lien Vercel) + une offre PDF en pièce jointe**, avec un message court.

1. **Recherche, sources réelles uniquement.** Annonces sur Airbnb, Booking.com, Expedia, Agoda, Mr & Mrs Smith, site du prospect : note et nombre d'avis, distinctions, tarif publié, canaux présents ou absents. Photos prises sur les OTA (Booking via Chromium headless si le site bloque). Coordonnées GPS sur la page Booking.
2. **Marché : PriceLabs Market Research (STR Index)**, zone et nombre de chambres du bien. Zone absente de `villa-site/market/bali.json` : l'ajouter avec `series` (occupation, ADR, délai de réservation, durée de séjour, annonces actives, mois par mois, et l'année précédente) et `pace` (déjà réservé pour les 3 prochains mois, même date l'an dernier, final l'an dernier).
3. **Page d'analyse** : `villa-site/villas/<slug>.json`, puis `python3 villa-site/market_report.py <slug>`. Rapport façon PriceLabs, minimaliste : 4 indicateurs, occupation et ADR sur 12 mois face à l'année précédente, réservations en cours, délai de réservation, **carte** de la zone mesurée, faits publics sur le bien, 3 lectures, tableau des données. Puis le **manque à gagner** (`report_keep_gap` + `gap_intro`), toujours présenté comme une projection « si le bien suivait son marché », jamais comme sa propre occupation.
   - Dans l'analyse : **ni commission, ni offre, ni nom de plateforme manquante** (écrire « some major OTAs are missing »). `hide_offer: true`.
   - Bandeau neutre (`owner_banner` : « Prepared for <nom> team · private »), jamais « for the owner » : le lecteur peut être une société de gestion. Lien en `?report`.
4. **Offre PDF** : `offer/partnership/<slug>/villa.json`, puis `python3 offer/partnership/build_partnership.py <slug>` (modèle Zeno Arete, 5 pages, leur logo en médaillon s'il existe).
   - Message central : **ils gardent tout ce qui est en place, AC distribue en parallèle**.
   - **Airbnb présenté dans l'offre** comme le canal qui a fait ses preuves (profil Superhost 10 ans, 800 avis). Autres plateformes **restées vagues**, pas de Marriott ni de Plum Guide (trop chers au mois), pas de ligne « reel Instagram ».
   - Commission par villa (`commission`), 12 % par défaut ; 15 % testé sur The Hideaway.
5. **Message** (anglais) : remerciement, présentation d'AC Collection en quelques lignes, lien de l'analyse, offre en pièce jointe, « tout ce qui est en place reste, j'ajoute des canaux », une question (un rendez-vous). Pas de commission dans le message.
6. **Avant l'envoi** : recouper les chiffres avec une deuxième source (AirROI, etc.), vérifier le rendu sur ordinateur et téléphone, ajouter la ligne `villa-site/funnel.csv`, lister à Anthony ce qu'il doit confirmer (partenaires cités, chiffres de preuve). **Publication sur `main` (donc en ligne) seulement avec son OK.**
- Dépôt public : jamais la signature ni les PDF générés dans Git (`offer/partnership/.gitignore`).
