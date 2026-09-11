# AC Partners — plan "villa site + gap + distribution" (Bali basse saison)

Date : 11 sept. 2026. Chiffres PriceLabs du jour, hypotheses marquees comme telles.

## 1. Le constat marche (donnees PriceLabs, portefeuille AC Collection)

| Villa (AC Collection) | Occ. 30 prochains jours | Marche 30 j | Base /nuit |
|---|---|---|---|
| The Dreamtime House, 7BR Canggu | 80% | 29% | IDR 21.5M (~$1,300) |
| BREIG River Villa, 5BR Pererenan | 100% | 47% | IDR 15M |
| BREIG Lot 8B, 4BR Canggu | 100% | 47% | IDR 12.5M |
| OXO Black Villa, 4BR Berawa | 97% | 48% | IDR 13M |
| Villa Ultimate, 8BR Canggu | 83% | 39% | IDR 11M |
| Aquamarine Lot 4, 3BR Canggu | 100% | 46% | IDR 8M |

Comp set Seminyak 4-10BR : 350 listings, basse saison fev/mars/dec, pics d'occupation a 33-49%.
Comp set Canggu 6-8BR : 29% d'occupation sur les 30 prochains jours.

Lecture business : le marche luxe Bali est structurellement sous-rempli hors haute saison,
et le portefeuille AC Collection fait 2x le marche sur les memes zones. C'est l'argument de vente,
et il est verifiable (captures PriceLabs).

## 2. L'offre (3 niveaux, du plus rentable au plus facile a signer)

1. Co-listing (coeur) : 10% sur les nuits vendues, site offert, pas d'exclusivite.
   Revenu recurrent, aligne sur la performance.
2. Site seul : $690 one-off + $29/mois (hebergement, mises a jour), pour ceux qui refusent
   le co-listing. Garde la relation, upsell co-listing a la prochaine basse saison.
3. Highlight AC Collection : 0 upfront, 5% sur les reservations envoyees. Le "non" devient
   quand meme une ligne de revenu et alimente le site AC Collection en inventaire.

## 3. Economie par villa signee (hypotheses)

- ADR moyen cible : $800-1,300.
- Nuits incrementales vendues par AC : 40-60/an (basse saison + trous de calendrier).
  Notre propre portefeuille fait +40 pts vs marche ; on prend 35% de l'ecart, prudent.
- Revenu incremental proprietaire : $32k-78k/an. Fee AC 10% : $3.2k-7.8k/villa/an.
- Couts variables : seat PMS + PriceLabs ~$25-40/listing/mois ($300-500/an), messagerie
  guests (equipe existante, marginal), 3-4 h de set-up canaux.
- Marge nette par villa : ~$2.5k-7k/an. Point mort : ~12 nuits vendues.

## 4. Temps par lead (process a l'unite, sans automatisation supplementaire)

| Etape | Temps | Outil |
|---|---|---|
| Sourcing : Airbnb/Insta, filtre 4BR+, calendrier ouvert fev-mars, contact trouve | 10 min | Airbnb map + site villa/Insta |
| Page perso : JSON (nom, ADR, zone) + 5 URLs photos via flux PDF listing | 10 min | generate_villa.py |
| Message etape 1 + 3 relances | 10 min | WhatsApp / Insta / Gmail |
| Call (seulement si reponse) | 20 min | WhatsApp |
| Onboarding si signature (canaux, calendrier, pricing) | 3-4 h | Guesty / PriceLabs |

Cout par lead contacte : ~30 min. Cout par call : +20 min.

## 5. Funnel (hypotheses a valider sur les 100 premiers)

100 contacts -> 25 reponses (page perso + chiffre precis = hook fort) -> 10 calls
-> 3-4 co-listings + 2-3 highlights.

Temps : 100 x 30 min = 50 h sourcing/pages/messages + 10 calls x 20 min = ~53 h.
Sortie : 3-4 villas x $3.2k-7.8k = $10k-31k ARR + highlights.
Soit $200-600 de revenu recurrent par heure investie, en cumul (les villas restent).

Mieux : les 50 h de sourcing/pages sont automatisables a 70% (script photos + JSON auto,
sequences WhatsApp). Avec ca, ~20 h par 100 leads.

Objectif 6 mois (oct -> mars, la fenetre basse saison) : 500 contacts, 15-20 villas
co-listees, $60k-150k ARR de fees. Capacite ops : plafonner a 8-10 onboarding/mois.

## 6. Kill criteria / pivots

- < 10% de reponses apres 100 messages : changer le hook (chiffre trop abstrait ?) ou le canal.
- < 2 signatures / 100 : passer le site en accroche gratuite ("site offert, on parle apres").
- Onboarding > 5 h/villa : standardiser un kit (photos, textes, tarifs) avant le call.

## 7. Risques

- Airbnb : pas de doublon de listing. Co-hosting sur le listing du proprio, ou nos canaux
  ou il n'est pas (Booking, Expedia, VRBO, Marriott). A cadrer contrat.
- Gros PM deja en place : ne pas cibler. Filtrer "geree par" sur le listing.
- Effet saisonnier : la promesse est basse saison ; mesurer et reporter chaque mois
  (la page "One page. Every month." du plan).
- Dependance a 1 personne (Anthony) pour les calls : script + fiche d'appel (deja dans Drive).

## 8. Pourquoi ca colle a AC Collection

- Le site guest AC Collection devient une marketplace de villas luxe ouverte sur le monde :
  chaque "non" (highlight) et chaque "oui" (co-listing) ajoute de l'inventaire.
- Les pages Vercel existantes (Dubai, Phuket, Tulum, Mykonos) sont le meme template :
  le playbook Bali se rejoue marche par marche, meme data PriceLabs, meme site.
- Le Superhost 9 ans + 759 avis est un actif qu'aucun concurrent local ne peut copier vite.

Verdict : pas une folie. Une machine a cash si, et seulement si, le funnel tient a 25% de
reponses et 3% de signatures. On le saura apres 100 messages, soit ~2 semaines de travail.
