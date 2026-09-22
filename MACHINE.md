# La machine à cash AC Partners — vision macro (22/09/2026)

Une seule idée : **posséder la demande, capter l'offre par son calendrier, et transformer chaque villa observée en revenu récurrent.** Tout ce qui a été construit depuis juillet est une pièce de cette machine. Ce document dit où chaque pièce se branche, ce qui manque entre les pièces, et ce que ça rapporte.

## 1. Les trois moteurs de revenu

| Moteur | Unité | Ticket | Aujourd'hui | Cible 6-9 mois |
|---|---|---|---|---|
| **Arbitrage** (client direct → villa d'un autre, marge sur l'écart) | le deal | 768 € de marge moyenne (juil.-sept.) | 3 deals/mois, 2 300 €/mois | 12-15 deals/mois, 10-12 k€ |
| **Distribution** (co-listing AC, 10 % des nuits vendues) | la villa onboardée | 200 à 600 $/villa/mois selon gamme | 25,5 k€ réservés en 2026, 3 villas font 87 % | 40 villas actives, 8-12 k€/mois |
| **Vente** (courtage, KBLI 68200, avec Ben) | la transaction | 7 à 30 k$ par vente | 0 | 3 ventes/an = un doublement |

Soustraction en cours : ~580 €/mois de Guesty sur des annonces parallèles mortes, remplacées par le catalogue iCal.

## 2. Le volant : comment les pièces s'enchaînent

```
 DEMANDE ──────────► MATCH ──────────► CASH 1 : arbitrage
 site + concierge     Dispos (iCal)      marge sur l'écart
 parrainage /prénom   chat « dates »
 Instagram            brochure PDF            │
 Airbnb AC (759 avis) broadcast partenaires   │ la villa a plu, le client revient
 affiliés à paliers   relance devis           ▼
        ▲                                CAPTEUR
        │                        historique d'occupation par villa (iCal relu toutes les 2 h)
        │                                     │ villa < 60 % d'occupation
        │                                     ▼
        │                                DOULEUR
        │                     message mensuel avec SES chiffres (nuits vides, $ perdus)
        │                                     │ « 10 % sur les nuits que je vends, en parallèle »
        │                                     ▼
        │                          ONBOARDING AUTOMATIQUE ──► CASH 2 : distribution récurrente
        │                  guesty.py create · amenities · photos · iCal      10 % des nuits, chaque mois
        │                  PriceLabs · registre · alignement · reel IG
        │                                     │
        └── l'annonce AC ranke sur Airbnb ────┘ (plus de demande, plus d'avis)
                                              │ upsells (radar 45 j), site direct (0 % OTA)
                                              ▼
                                     VENTE (rendement.py, page « for sale » dans la brochure)
                                              │ ──► CASH 3
                                              └── la villa vendue revient au catalogue avec un proprio neuf
```

**Le déclic du 22/09** : l'iCal donné « pour être proposé en privé » est en réalité un **capteur**. Il révèle l'occupation réelle de la villa mieux que son propriétaire ne la connaît, et fabrique tout seul l'argument de vente de la distribution, chaque mois, sans prospection. C'est ce qui relie l'arbitrage (cash immédiat) à la distribution (cash récurrent).

## 3. Où chaque machine existante se branche

| Étage | Machines déjà construites | État |
|---|---|---|
| **Demande** | ac-collection.com + concierge IA (contact avant cartes, conversations enregistrées), parrainage `/prénom` (2 %), machine Instagram, annonces Airbnb AC + relance inquiries J+1/J+5, relevé hebdo des vues Airbnb | en prod |
| **Offre** | villa-prospect (page diagnostic + 3 messages + funnel + sourcing + recherche de contacts), catalogue iCal Dispos (37 villas), inscription libre-service depuis la page diagnostic (22/09), veille double réservation, contrats agences (LataLiana, GORO, TBA, Gravity) | en prod |
| **Match** | recherche Dispos par dates + chat « demande-moi des dates », brochure PDF anonymisée, broadcast WhatsApp du brief aux 9 partenaires, relance devis | broadcast bloqué par la vérification Meta (en examen) |
| **Livraison** | onboarding automatique (SOP 11 étapes, `~/Claude/ac-guesty`), routine pricing + parité, PriceLabs, site direct Stripe, radar upsells | upsells : auto-messages jamais activés |
| **Vente** | rendement.py, alliance Ben | rapport type livré, 0 exclusivité |
| **Mesure** | cockpit (revenus, journal d'arbitrage, to-do serveur), brief matin | l'entonnoir complet n'a pas de KPI hebdo |

## 4. Ce qui manque : les connecteurs

Ce sont des tuyaux entre des pièces qui existent, pas des machines nouvelles.

1. **Capteur d'occupation** — garder l'historique des lectures iCal, calculer par villa l'occupation réalisée par mois, les nuits vides et leur valeur au prix connu. *Une journée, zéro coût.*
2. **Générateur de douleur mensuel** — `make_message.py` version « vos propres chiffres », lancé le 1er du mois pour toute villa du capteur sous 60 %, statut dans le funnel (jamais relancer un refus, cap 8 envois/jour, envoi sur ton OK). *Une journée.*
3. **Lead → Dispos automatique** (tâche p2t4 du plan) — chaque demande du concierge sort les 5 villas libres avec marge + brochure, sans que tu cherches. *Une journée.*
4. **Lien agence** — une page où une agence colle tous ses iCal d'un coup (Gravity, TBA, LataLiana : 60 villas en 3 messages). *Une demi-journée.*
5. **Paliers d'affiliés 3/5/8 %** + kit prescripteur (p3t1, p3t2) — le système de parrainage existe, il manque les paliers et le message prêt à transférer. *Une journée.*
6. **Onboarding léger** — mode « Airbnb co-hôte seul » (0 PMS) pour que la distribution d'une villa middle market coûte une heure, pas une journée et 20 €/mois. *Une journée + une décision sur le PMS.*
7. **KPI hebdo de l'entonnoir** dans le cockpit — demandes qualifiées, devis, deals, iCal reçus, douleurs envoyées, onboardings. *Une demi-journée.*

Blocages externes : vérification Meta (broadcast +62), auto-messages Guesty des upsells (tarifs à confirmer par Anthony).

## 5. Middle market et luxe : deux usages, une machine

- **Luxe (4BR+, > 500 $)** : arbitrage ET distribution. Ticket qui justifie une conversation. Le capteur → douleur → onboarding est fait pour lui.
- **Middle market (150-350 $)** : **pas d'arbitrage à la main** (90-180 $ de marge par deal, ça ne paie pas le temps). Deux usages : (a) **capteur** — il coûte zéro à capter par l'iCal et il densifie la base marché (occupation réelle par zone, argument de vente plus crédible que PriceLabs) ; (b) **distribution seulement si l'onboarding léger existe et qu'un assistant tient la première ligne** (règle : plus de première ligne pour Anthony). 100 villas × 200 $/mois = 20 k$/mois, mais seulement à ce prix-là.

## 6. La demande : le réseau d'affiliés

C'est le pari d'Anthony et il est cohérent avec le modèle (« son actif principal côté Bali est la demande »). Ce qu'il faut pour que ça marche : le lien discret existe, il manque les paliers (3 % proche, 5 % apporteur régulier, 8 % organisateur de retraites, mariages, conseillers voyage), le kit (message à transférer, brochure à leur marque, page de suivi déjà en place) et **un chiffre suivi chaque semaine** : leads apportés par affilié. Cible du plan : 30 prescripteurs + 10 organisateurs avant le 4 décembre.

## 7. Ordre d'exécution proposé

Semaine 1 : capteur (1) + lead → Dispos (3). Semaine 2 : douleur mensuelle (2) + lien agence (4). Semaine 3 : paliers affiliés (5) + KPI (7). Semaine 4 : onboarding léger (6). Chaque connecteur est jugé sur les trois critères d'Anthony : plus de marge, pas de première ligne, remplace un coût.

## 8. Garde-fous

Jamais de devis ferme sans confirmation écrite de l'agence (l'iCal ne donne ni prix ni durée minimum). Jamais de calendrier sans accord (le lien iCal est l'accord). Statut d'intermédiaire et encaissement pour compte de tiers à cadrer avant le volume. Tout ce qui est fait deux fois devient une routine.
