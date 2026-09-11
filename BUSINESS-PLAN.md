# AC Partners — plan "villa site + gap + distribution" (Bali basse saison)

Date : 11 sept. 2026. Donnees PriceLabs du jour (cache `villa-site/market/bali.json`), hypotheses
marquees comme telles. Deux decisions prises par defaut, a valider par Anthony (§ 9).

## 1. Le marche, chiffre (PriceLabs, compset de 350 villas autour de chaque villa de reference)

Occupation marche **finale** du mois, sur les 12 derniers mois (sept. 2025 -> aout 2026) :

| Zone / gamme | Moy. annuelle | 3 mois les plus bas | ADR median (p50) de la gamme | p75 |
|---|---|---|---|---|
| Canggu 4-10BR (ref. Dreamtime) | **44 %** | fev 41 % (34 % en 2025), nov 39 %, jan 40 % | 7BR : IDR 11.5M (~$720) | $910 |
| Seminyak 4-10BR (ref. LaTaLiana) | **53 %** | fev 45 %, dec 47 %, nov/jan 49 % | 7BR : IDR 15.8M (~$990) | $1,575 |
| Pererenan 4-6BR (ref. BREIG River) | 65 % | nov/jan/fev 60 % | 5BR : IDR 8.5M (~$530) | $900 |
| Berawa 3-5BR (ref. OXO) | 61 % | nov 51 %, jan/fev 55 % | 4BR : IDR 6.8M (~$425) | $575 |
| Uluwatu 3-5BR (ref. Bali Forest) | 78 % | dec 68 %, nov/jan/fev 72 % | 4BR : IDR 6.7M (~$420) | $600 |

Portefeuille AC Collection sur les 30 prochains jours : Dreamtime 80 %, BREIG River 100 %, Lot 8B 100 %,
OXO 97 %, Ultimate 83 %, Aquamarine 100 % contre 29-48 % de marche (releve du 11/09).

Lecture : **le probleme n'est pas seulement la basse saison, c'est la gamme.** Les 4BR+ de Canggu et
Seminyak tournent a 44-53 % toute l'annee, soit 170 a 205 nuits vides par an et par villa, quand
les 3-5BR d'Uluwatu sont a 78 %. La cible se resserre donc : **Canggu et Seminyak, 5BR+, ADR > $700**,
Pererenan en second rideau. Uluwatu n'est pas un marche "basse saison" pour cette offre.

## 2. L'offre (3 niveaux)

1. **Co-listing (coeur)** : 10 % sur les nuits vendues par nous, site offert, pas d'exclusivite,
   pas de duree minimum, garantie de nuits (50 % de la cible affichee) sinon le proprio garde le site.
2. **Site seul** : $690 one-off + $29/mois (hebergement, mises a jour). Sert surtout d'ancre de
   valeur dans l'offre ; on ne le pousse pas.
3. **Highlight AC Collection** : 0 upfront, 5 % sur les reservations envoyees.

## 3. Economie par villa signee

Calcul de la page (identique dans `make_message.py`) : nuits vides = jours x (1 - occ. marche),
sur les 3 mois les plus bas ; cible = 35 % des nuits vides ; fee = 10 % du revenu cible.

| Villa type | ADR | Nuits vides basse saison (3 mois) | Cible +35 % | Revenu ajoute | Fee AC |
|---|---|---|---|---|---|
| Canggu 7BR (Dreamtime, exemple reel) | $1,300 | 54 | 19 | $24,700 | $2,470 |
| Canggu 5BR | $800 | 54 | 19 | $15,200 | $1,520 |
| Seminyak 6BR | $1,000 | 47 | 16 | $16,000 | $1,600 |

C'est la promesse **prudente** faite au proprio (basse saison seule). Le vrai potentiel annuel,
qu'on chiffre en petit sur la page : Canggu 44 % = 204 nuits vides/an ; si on en capte 20-30 %
(40-60 nuits, ce que fait notre propre portefeuille a +40 pts du marche), a $800-1,300 :

| Scenario (nuits/an vendues par AC) | ADR $800 | ADR $1,000 | ADR $1,300 |
|---|---|---|---|
| Bas : 20 nuits | $1,600 | $2,000 | $2,600 |
| Base : 40 nuits | $3,200 | $4,000 | $5,200 |
| Haut : 60 nuits | $4,800 | $6,000 | $7,800 |

Couts variables par villa : PriceLabs ~$20/mois + listing Guesty ~$30/mois = **~$600/an** ;
onboarding 3-4 h ; reporting mensuel 20 min (a automatiser). **Marge nette base : $2.6k-4.6k/villa/an,
point mort ~8 nuits a $800.** Le highlight (5 %) est du bonus a cout nul.

## 4. Temps par lead, apres automatisation (mesure sur Dreamtime le 11/09)

| Etape | Avant | Maintenant | Outil |
|---|---|---|---|
| Sourcing (Airbnb map, filtre 4BR+, calendrier ouvert, contact) | 10 min | 10 min | manuel (Anthony apporte les URLs) |
| Page perso (photos, chiffres marche, HTML) | 10 min | **1 min** | `villa-site/villa.py <url> --adr N` |
| Message etape 1 + 3 relances | 10 min | **0 min** (genere) | `outreach/<slug>.md` |
| Relecture + envoi + statut funnel | 5 min | 5 min | WhatsApp + `funnel.py set` |
| Clips video de visite (optionnel) | Higgsfield (credits) | 2 min de rendu, $0 | `make_clips.py` (ffmpeg Ken Burns) |
| Call (si reponse) | 20 min | 20 min | WhatsApp |
| Onboarding si signature | 3-4 h | 3-4 h | Guesty / PriceLabs |

**~16 min par lead contacte** (contre 30), **100 leads = ~27 h** dont 17 h de sourcing.

## 5. Funnel cible et checkpoints

100 contacts -> 25 reponses -> 10 calls -> 3-4 co-listings + 2-3 highlights (hypothese de depart).

| Checkpoint | Envoyes | Ce qu'on regarde | Si en dessous |
|---|---|---|---|
| 1 | 30 | taux de reponse >= 10 % | changer l'accroche (chiffre annuel au lieu de basse saison ? canal Instagram ?) |
| 2 | 60 | >= 3 calls | tester "site offert d'abord, on parle apres" en etape 1 |
| 3 | 100 | >= 2 signatures, >= 25 % reponses | pivot : vendre le site seul ($690) comme porte d'entree, ou changer de zone |

`python3 villa-site/funnel.py stats` calcule ces taux ; `funnel.py due` liste les relances du jour.

Sortie a 100 contacts : 3-4 villas x $2.5k-5k = **$8k-20k de fees/an**, recurrentes, + highlights.
Objectif 6 mois (oct -> mars) : 400 contacts, 12-16 villas co-listees, **$40k-80k/an** de fees.
Capacite ops : plafonner a 6-8 onboardings/mois (3-4 h chacun).

## 6. Kill criteria

- < 10 % de reponses a 30 envois puis a 100 : le hook ne marche pas -> changer ou arreter.
- < 2 signatures a 100 envois : l'offre ne convertit pas -> pivot site-seul ou stop.
- Onboarding > 5 h/villa : kit standard (photos, textes, tarifs, iCal) exige avant le call.
- Nuits reellement vendues < 50 % de la cible sur la premiere basse saison : la garantie joue,
  on revoit le taux de capture affiche avant la deuxieme vague.

## 7. Risques

- **Airbnb** : pas de doublon de listing. Co-hosting sur le listing du proprio, ou nos canaux ou il
  n'est pas (Booking, Expedia, VRBO, Marriott). A cadrer dans le contrat.
- **Photos hotlinkees** depuis le CDN Airbnb : si le proprio change ses photos, relancer `villa.py`.
- **Vercel** : les previews de branche sont proteges par login ; une page n'est publique qu'une fois
  la branche sur `main`. Merger avant le premier envoi.
- **Gros PM deja en place** : ne pas cibler ("managed by" sur le listing).
- **Dependance a Anthony** pour sourcing et calls : le script fait le reste.

## 8. Pourquoi ca colle a AC Collection

Chaque "oui" (co-listing) et chaque "non" (highlight) ajoute de l'inventaire au site guest ;
les pages Vercel Dubai / Phuket / Tulum / Mykonos sont le meme playbook, et `market/bali.json`
se rejoue par marche avec les memes appels PriceLabs.

## 9. Les deux decisions (defaut applique, reco)

**Prix du site seul — defaut $690 + $29/mois (applique).** Reco : garder $690 comme ancre dans
l'offre, mais ne pas chercher a le vendre seul : c'est un produit a support et a faible LTV qui
detourne du co-listing. Si on le vend quand meme, l'ancre sera plus credible a **$990 + $39/mois**
(les agences a Bali facturent $1.5k-4k un site villa ; $690 parait "template"). A trancher.

**Taux de capture de l'ecart — defaut 35 % (applique).** Reco : garder 35 % comme cible affichee
(notre portefeuille fait +40 pts vs marche, donc 35 % de l'ecart est deja conservateur), mais
**garantir 50 % de cette cible** (= ~17 % de l'ecart), ce que fait le message. Repasser a 25 %
affiche si la premiere basse saison sort en dessous de la garantie.

Verdict : une machine a cash **si** le funnel tient a 25 % de reponses et 3 % de signatures.
On le saura a 100 messages, soit ~27 h de travail avec le process automatise.
