# Cold approach — villas luxe Bali, basse saison

Cible : proprietaires ou petits gestionnaires (1 a 5 villas) de villas 4BR+ a Bali, ADR > $500,
sur les zones ou les grandes villas sont structurellement vides (Canggu 4-10BR : 44 % d'occupation
annuelle marche, Seminyak 4-10BR : 53 %, source PriceLabs 09/2026). Pas les gros PM (Elite Havens,
Bali Villa Finder, Nagisa...). Canal : WhatsApp d'abord, DM Instagram ensuite, e-mail en dernier. Anglais.

**Les messages sont generes par `villa-site/make_message.py` a partir du JSON de la villa**
(chiffres du manque a gagner, lien de la page, nom du contact) dans `villa-site/outreach/<slug>.md`.
Rien ne part sans le OK d'Anthony ; cap 8 envois / jour (WhatsApp Business), jamais recontacter
un refus.

## Decision : 3 etapes ou "grand slam offer" a la Hormozi ?

Les deux. La structure reste en 3 etapes (accroche -> page + offre -> fallback), parce qu'un
message froid long est ignore : l'accroche chiffree sert a gagner la permission d'envoyer l'offre.
C'est l'etape 2 qui devient une offre a la Hormozi, et elle empile tout :

1. **Dream outcome** : la basse saison remplie, chiffree pour SA villa (nuits vides x son ADR).
2. **Value stack** : distribution multi-canal + site offert (prix affiche $690 + $29/mois, $0 pour
   les partenaires) + reporting mensuel + pricing dynamique.
3. **Risk reversal** : 10 % uniquement sur les nuits vendues par nous, pas de set-up, pas
   d'exclusivite, pas de duree minimum, et une garantie : si on n'a pas vendu N nuits a la fin de
   la premiere basse saison (N = 50 % de la cible affichee), il garde le site et s'en va.
4. **Preuve** : nos propres villas a 80-100 % contre un marche a 29-47 % (capture PriceLabs).
5. **Scarcite reelle** : une poignee de villas par zone (on ne peut pas remplir 30 villas 7BR a
   Canggu en fevrier), donc "one per street" et une date de fermeture de la liste.

Le fallback (highlight a 5 %) reste : un "non" devient quand meme une ligne de revenu et de
l'inventaire pour le site AC Collection.

## Etape 1 — accroche (WhatsApp)

```
Hi [First name], Anthony here — Airbnb Superhost for 9 years (759 reviews, 4.84★), I run
AC Collection, ~30 luxury villas in Canggu, Seminyak and Uluwatu.

I came across [Villa] while benchmarking [area] and ran it through our PriceLabs market data.
[X]-bedroom villas around you sit at ~[occ]% occupancy in [Feb, Mar and Nov]. At your ~$[ADR]/night
that is about [empty] empty nights and $[loss] not earned per low season.

I put the numbers on a private page for you, with a site for the villa built from your photos
(4-min scroll). Want the link?
```

Variante Instagram (DM, < 300 caracteres) :

```
Hi [First name] — Superhost here, 30 villas in Bali. Ran [Villa] through our low-season data:
about $[loss] left on the table in [Feb, Mar and Nov]. Made you a 4-min page + a site for the
villa, want it?
```

## Etape 2 — la page + l'offre (apres un "oui")

```
Here it is: [base_url]/villa-site/<slug>?owner

Two things on that page:
1. The gap: [empty] empty low-season nights at $[ADR], from PriceLabs data on 350 villas around you.
2. What we do about it: we co-list [Villa] on our channels (Airbnb Superhost profile, Booking.com,
   Expedia, VRBO, Marriott Homes & Villas, plus our AC Collection guest base: repeat guests, groups,
   retreats), one synced calendar, dynamic pricing. You keep the management, the staff and the ops.

The deal, all of it:
• 10% on the nights we sell. Nothing on the nights you sell yourself.
• No set-up fee, no exclusivity, no minimum term. Stop whenever you want.
• The site you just scrolled is yours, on your own domain, the day we go live
  ($690 + $29/month on its own, $0 for partners).
• One-page report on the 1st of every month: channel mix, occupancy, ADR, incremental revenue.
• If we have not sold [N] nights by the end of the first low season, you keep the site and walk
  away. Nothing owed.

For reference, our own villas in Canggu ran 80–100% over the last 30 days against a 29–47% market.
Same playbook.

15 minutes on WhatsApp this week? I have [day] and [day] open.
```

## Etape 3 — si refus : highlight sur le site AC Collection

```
Understood, no problem. One lighter option, zero commitment:
we feature [Villa] as a highlight on the AC Collection guest site and in our guest emails (repeat
guests, groups, retreats looking for large villas). You handle the booking directly. We take 5% on
a booking we send you, nothing otherwise.

If a low-season enquiry lands, you'll be glad it was there. Shall I add it?
```

## Relances (dates calculees dans outreach/<slug>.md, rappel par `python3 villa-site/funnel.py due`)

- J+3 : "Did the page load OK on your side? [lien]. Happy to walk you through the [empty] nights
  in 10 min, or send the calc as a PDF."
- J+7 : preuve, capture PriceLabs d'une de nos villas a 100 % vs marche 45 %, + "same channels,
  same pricing engine, for [Villa]. The site stays yours either way. 10 min this week?"
- J+14 : derniere : "We're closing the Bali low-season partner list this month (a handful of villas,
  one per street). Want the spot for [Villa], or shall I pass? Either way, the site is here: [lien]".

## Regles

- Le chiffre de l'accroche vient de la page (meme calcul), jamais arrondi a la hausse.
- Pas de nom de villa AC Collection ni de tarif de nos villas dans le message (juste le taux d'occupation).
- Statut a jour dans `villa-site/funnel.csv` a chaque contact (`funnel.py set <slug> sent|replied|call|signed|highlight|refused`).
- Hors cible : villa geree par un gros PM (mention "managed by" sur le listing), villa deja
  a > 60 % en basse saison, 1-3BR.
