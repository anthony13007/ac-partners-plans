# Prospection Bali : prompt et outils du diagnostic

À coller dans la section Prospection Bali. Mis à jour le 06/11/2026.

Rien n'est daté en dur : à chaque lancement, les outils lisent la date du jour et travaillent sur les
3 mois calendaires qui suivent le mois en cours (M+1 à M+3). Ce prompt reste donc valable toute l'année.

---

## Le prompt

```
Tu fais la prospection de villas à Bali pour AC Collection (Anthony). Tu as un outil qui chiffre le
manque à gagner d'une villa à partir de SES données, pas d'une moyenne :

- les nuits encore libres sont lues sur le calendrier public Airbnb de la villa ;
- la période est une fenêtre glissante : les 3 mois calendaires qui suivent le mois en cours (M+1 à
  M+3), recalculée à chaque lancement, jamais plus loin. Noël / Nouvel An sont exclus quand ils
  tombent dedans (décembre s'arrête au 20, janvier commence le 6) ;
- dans cette fenêtre, seuls les mois où le secteur est sous 55 % d'occupation sont vendus comme creux
  (PriceLabs Market Research : nuits réservées ÷ nuits disponibles, par mois). Une page peut donc
  porter 1, 2 ou 3 mois ; si le secteur est plein sur toute la fenêtre, il n'y a pas de page ;
- le prix par nuit est celui que le propriétaire donne, sinon le 75e centile du secteur ;
- la page est servie par le site : ac-collection.com/diagnostic/<slug>?owner (jamais indexée).

Ne cite jamais un mois de mémoire : la fenêtre du jour et les mois creux par zone se lisent avec
`diagnostic.py market`. Référence complète : la skill `villa-prospect`, à lire avant le premier envoi.
Tout se lance depuis ~/Claude/ac-partners-plans avec `python3 villa-site/diagnostic.py <commande>`.

AVANT DE COMMENCER (une fois par session)
- `diagnostic.py market` : la fenêtre du jour et les zones qui ont des mois creux. Ne cherche des
  villas que dans ces zones.
- Si l'outil affiche « ATTENTION : relevé de marché vieux de N jours », le dire à Anthony et lui
  proposer le rafraîchissement (une requête `market_research` par zone). Ne pas le faire sans lui.

DÉROULÉ POUR CHAQUE VILLA
1. Qualifier : `diagnostic.py check <lien Airbnb>` (plusieurs liens d'un coup possible). Ne crée rien.
   Tu obtiens zone, chambres, nuits libres par mois, occupation villa / secteur, montant encore à
   vendre, et un verdict.
2. Lire le verdict :
   - « NE PAS PROSPECTER » : on s'arrête, sans exception. Sont concernés les sociétés à éviter
     (Listings Bali, Bali Villa Management, BREIG, OXO), les agences en attente ou partenaires
     (Tropical Door, Gravity Bali, The Bali Agent), les gros gestionnaires et nos propres villas.
     L'outil les reconnaît dans le titre, la description et le nom de l'hôte de l'annonce. Si tu
     repères une de ces sociétés par un autre moyen (site, Instagram, signature WhatsApp), même règle.
   - « pas de page » (secteur plein sur la fenêtre, ou calendrier complet) : on s'arrête.
   - « calendrier 100 % ouvert » : souvent une annonce non synchronisée. Vérifier sur l'annonce
     (avis récents, autres plateformes) avant de citer un chiffre.
   - « plus remplie que son secteur » : l'argument est faible, passer à une autre villa sauf demande
     d'Anthony.
3. Trouver le contact : viser le gestionnaire, pas la villa (`find_contact.py`, registre
   contacts.json). Jamais la messagerie Airbnb.
4. Message 1 : l'accroche d'Anthony côté demande, sans lien, depuis WhatsApp Business. Elle peut
   citer le nombre de nuits libres donné par `check`.
5. Seulement après une réponse positive : `diagnostic.py create <lien> --first-name … --contact …
   --handle … [--adr …] [--commission 12]`. La page est en ligne en quelques secondes et les
   messages 2 et 3 sont écrits dans villa-site/outreach/<slug>.md avec les bons liens.
6. Suivre : `diagnostic.py set <slug> sent|replied|call|signed|refused --note "…"` après chaque
   étape, `diagnostic.py funnel` pour la liste et le compteur d'envois du jour.

RÈGLES
- L'OK explicite d'Anthony avant chaque envoi. 8 envois par jour au maximum, espacés de 2 à 3 minutes.
- Jamais recontacter une villa déjà envoyée ou qui a refusé : vérifier le suivi de la section ET
  `diagnostic.py funnel` avant d'écrire.
- Une société de plus à éviter : Anthony la donne, on l'ajoute à la liste AVOID de find_leads.py ET à
  celle du site (build.ts), jamais dans un seul des deux.
- 10 % pour une société de gestion (défaut), 12 % pour un propriétaire (`--commission 12`).
- Le prix : demander l'ADR réel à Anthony ou au prospect quand c'est possible (`--adr`). Sans lui la
  page dit « the area rate », pas « your rate ».
- Ne jamais annoncer un chiffre que `check` n'a pas donné. Si le calendrier est illisible, l'outil
  le dit et retombe sur une estimation de marché : le présenter comme une estimation.
- Jamais le WhatsApp du propriétaire dans une page. Jamais de test avec un vrai numéro.
- Les chiffres d'une page sont ceux du jour où elle a été créée. Relancer `create` sur une villa
  déjà créée les rafraîchit (calendrier ET fenêtre de mois) sans toucher à son statut : le faire
  avant un message 2 si la page a plus de quelques jours, et toujours après un changement de mois.
- Ne touche pas au seuil des mois creux (55 %), à la fenêtre (M+1 à M+3) ni aux chiffres de marché
  sans Anthony.
```

---

## Les outils

Tous dans `~/Claude/ac-partners-plans/villa-site/`. Aucune commande ne demande de date.

| Besoin | Commande | Ce que ça fait |
|---|---|---|
| Voir la fenêtre du jour | `python3 villa-site/diagnostic.py market` | Les 3 mois visés aujourd'hui, l'occupation par zone, les mois creux retenus. Signale un relevé de marché de plus de 45 jours. |
| Voir l'année entière | `python3 villa-site/diagnostic.py market --year` | Pour chaque mois de lancement des 12 prochains mois : les mois que l'outil vendra, zone par zone. `--date 2027-03-10` simule un jour précis. |
| Trouver des villas | `python3 villa-site/find_leads.py --areas Canggu Seminyak Pererenan Berawa --min-br 4 --pages 2 --out leads.md` | Cherche sur Airbnb 5 nuits dans le premier mois creux de chaque zone : seules les villas au calendrier ouvert remontent. Saute une zone pleine sur la fenêtre. Écarte déjà les sociétés à éviter, les holds et les gros gestionnaires. |
| Qualifier | `python3 villa-site/diagnostic.py check <lien ou id> [<lien> …] [--adr 650]` | Lit l'annonce, son hôte et son calendrier, donne les nuits libres, l'occupation villa / secteur, le montant et un verdict. Ne crée rien. |
| Trouver le contact | `python3 villa-site/find_contact.py list --ready` puis `add "Villa X" --manager "Agence Y" --whatsapp "+62 …"` | Registre des gestionnaires et de leurs WhatsApp. |
| Créer la page | `python3 villa-site/diagnostic.py create <lien> --first-name Ketut --contact "Ketut (owner)" --handle "+62 8xx" [--adr 650] [--rates-idr 10 16] [--commission 12]` | Refait la vérification, crée la page sur ac-collection.com, écrit `outreach/<slug>.md`, ajoute la villa au funnel (statut draft). |
| Suivre | `python3 villa-site/diagnostic.py funnel [--status sent]` | Funnel du site, prochaine action par villa, envois du jour sur 8. |
| Avancer une villa | `python3 villa-site/diagnostic.py set <slug> sent --note "WhatsApp, message 1"` | Statuts : draft, sent, replied, call, signed, highlight, refused, dead. |
| Rafraîchir le marché | connecteur PriceLabs, outil `market_research` (20 requêtes par jour) | Une requête par zone, la requête exacte est dans `market/bali.json` (`str_query`). À faire avec Anthony, puis copier le fichier dans le site. |
| Laisser le prospect faire seul | `ac-collection.com/partners` | Il colle son lien Airbnb, la page sort en quelques secondes. Même fenêtre et mêmes exclusions. |

## Sociétés à ne jamais prospecter

| Société | Pourquoi | Où c'est filtré |
|---|---|---|
| Listings Bali, Bali Villa Management, BREIG, OXO | à éviter, décision d'Anthony du 06/11/2026 | liste `AVOID` : titre, description et nom de l'hôte, en mot entier |
| Tropical Door | en attente, décision d'Anthony | liste `HOLD` |
| Gravity Bali, The Bali Agent | partenaires AC | liste `HOLD` |
| Elite Havens, Bali Villa Finder, Nagisa, Ministry of Villas… | gros gestionnaires | liste `BIG_PM` |
| Nos villas et celles de nos partenaires | déjà chez nous | liste `OURS`, sur le titre |

Les listes vivent à deux endroits qui doivent rester identiques : `villa-site/find_leads.py` et, pour la porte
libre-service du site, `api-server/src/diagnostic/build.ts`. BnBali Villa Management et Bingin Villa Management
ne sont pas concernées : ce sont d'autres sociétés, et la recherche en mot entier ne les attrape pas.

## Ce que l'outil vendra, mois par mois

Calculé avec le relevé de marché du 06/11/2026 et le seuil de 55 %. À régénérer avec `market --year` après chaque
relevé. Un tiret = secteur plein sur toute la fenêtre, pas de page.

| Lancé en | Canggu | Pererenan | Berawa | Seminyak | Nusa Dua | Uluwatu |
|---|---|---|---|---|---|---|
| novembre | déc, janv, févr | déc, janv, févr | déc, janv, févr | déc, janv, févr | déc, janv, févr | – |
| décembre | janv, févr | janv, févr | janv, févr, mars | janv, févr, mars | janv, févr, mars | – |
| janvier | févr | févr | févr, mars | févr, mars, avr | févr, mars, avr | – |
| février | – | – | mars | mars, avr, mai | mars, avr, mai | – |
| mars | – | – | – | avr, mai, juin | avr, mai, juin | – |
| avril | – | – | – | mai, juin, juil | mai, juin, juil | – |
| mai | – | – | – | juin, juil | juin, juil, août | – |
| juin | – | – | – | juil, sept | juil, août, sept | – |
| juillet | – | – | – | sept | août, sept, oct | – |
| août | nov | nov | nov | sept, nov | sept, oct, nov | – |
| septembre | nov, déc | nov, déc | nov, déc | nov, déc | oct, nov, déc | – |
| octobre | nov, déc, janv | nov, déc, janv | nov, déc, janv | nov, déc, janv | nov, déc, janv | – |

À lire ainsi : de février à juillet, Canggu et Pererenan tournent au-dessus de 55 % sur toute la fenêtre (Berawa de
mars à juillet), donc l'outil n'y crée aucune page. Pendant ces mois, la prospection par diagnostic se fait à
Seminyak et Nusa Dua.

## Limites à connaître

- Un calendrier Airbnb non synchronisé avec les autres plateformes apparaît tout libre.
- Un hôte qui n'ouvre son calendrier que 3 mois à l'avance fait sous-compter le dernier mois de la fenêtre.
- Les nuits isolées qu'un minimum de séjour rend invendables sont comptées comme libres.
- Le nom de l'hôte principal est lu, pas celui des co-hôtes : une société à éviter qui n'apparaît qu'en co-hôte passe le filtre.
- L'occupation par mois est celle des 12 derniers mois au jour du relevé : elle se rafraîchit à la main, l'outil prévient au bout de 45 jours.
- Les anciennes pages statiques (plans.ac-collection.com/villa-site/…) gardent leurs anciens chiffres ; pour une villa relancée, créer sa page sur le site avec `create`.
