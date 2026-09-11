# Cold approach — villas luxe Bali, basse saison

Cible : proprietaires ou petits gestionnaires (1 a 5 villas) de villas 4BR+ a Bali, ADR > $500,
sur les zones ou les grandes villas sont structurellement vides (Canggu 4-10BR : 44 % d'occupation
annuelle marche, Seminyak 4-10BR : 53 %, source PriceLabs 09/2026). Pas les gros PM (Elite Havens,
Bali Villa Finder, Nagisa...). Canal : WhatsApp d'abord, DM Instagram ensuite, e-mail en dernier. Anglais.

**Les messages sont generes par `villa-site/make_message.py` a partir du JSON de la villa**
(chiffres du manque a gagner, lien de la page, nom du contact) dans `villa-site/outreach/<slug>.md`.
Rien ne part sans le OK d'Anthony ; cap 8 envois / jour (WhatsApp Business), jamais recontacter
un refus.

## Structure : 3 messages courts, l'offre en dernier (decision Anthony, 11/09)

Un message = une idee. Pas de value stack avant que le proprio ait demande la proposition.

1. **Qui je suis** : Superhost 9 ans (759 avis, 4.84), AC Collection, ~30 villas, lien du site ac-collection.com.
   Une seule question : "Mind if I share a couple of numbers on your low season?"
2. **Le manque a gagner** : le chiffre (nuits vides x ADR sur les 3 mois les plus bas) + lien de la page
   privee `?owner`, puis, dans un lien a part, la version guest de la meme page (sans `?owner`) : le
   site qui vend en direct avec film au scroll, pour SA villa a lui, pas une autre. C'est le point :
   on ne montre jamais la villa d'un autre proprio dans le message d'un prospect. Question de sortie :
   "Would you like a collaboration proposal?"
3. **L'offre**, en 5 puces : co-listing multi-canal, 10 % sur les nuits vendues, pas de set-up /
   exclusivite / duree, site offert sur son domaine ($690 + $29/mois affiche), reporting mensuel,
   garantie de nuits (50 % de la cible affichee) sinon il garde le site. Un creneau de 15 min.

Fallback si "non" : highlight AC Collection a 5 %. Relances J+3 / J+7 (capture PriceLabs) / J+14
apres le message 2. Les textes exacts, avec les chiffres de chaque villa, sont dans `outreach/<slug>.md`.

## Message 1 — qui je suis (WhatsApp)

```
Hi [First name], Anthony here. Airbnb Superhost for 9 years (759 reviews, 4.84★), I run AC Collection,
~30 luxury villas in Canggu, Seminyak and Uluwatu: https://ac-collection.com

I came across [Villa] while benchmarking [area]. Mind if I share a couple of numbers on your low season?
```

Instagram : `Hi [First name], Superhost here (759 reviews), 30 villas in Bali: ac-collection.com.
Came across [Villa], can I send you two numbers on your low season?`

## Message 2 — le manque a gagner + le site exemple (apres un "oui", ou 2 jours plus tard)

```
[X]-bedroom villas around [Villa] sit at ~[occ]% occupancy in [Feb, Mar and Nov]. At your ~$[ADR]/night
that is about [empty] empty nights, $[loss] not earned per low season. The detail, on a private page:
[base_url]/villa-site/<slug>?owner

And this is the kind of site we build for our villas to sell direct, scroll it on your phone:
[base_url]/villa-site/<slug>

Would you like a collaboration proposal?
```

## Message 3 — l'offre (apres "yes, send the proposal")

```
Here it is, short:

We co-list [Villa] on our channels (Airbnb Superhost profile, Booking.com, Expedia, VRBO, Marriott
Homes & Villas, plus our AC Collection guests), one synced calendar, dynamic pricing. You keep the
management, the staff and the ops.

• 10% on the nights we sell. Nothing on the nights you sell yourself.
• No set-up fee, no exclusivity, no minimum term.
• A site like the one you scrolled, yours, on your own domain, free ($690 + $29/month on its own).
• A one-page report on the 1st of every month.
• Highlight on the AC Collection guest site and in our guest emails (repeat guests, groups, retreats), included.
• A reel of [Villa] on our Instagram (@acpartners.collection), included.
• A PriceLabs pricing set-up and a listing audit (photos, title, text) in the first week, included.
• If we have not sold [N] nights by the end of the first low season, you keep the site, the highlight
  and the reel, and walk away.

15 minutes on WhatsApp this week? [day] or [day]?
```

## Vivier d'idees pour monter l'offre (Hormozi, "$100M Offers")

Les bonus du message 3 vivent dans `villa-site/config.json` (`offer_bonuses`) : une ligne par bonus,
`{villa}` est remplace. A ajouter quand on peut les livrer :

- **Bonus a cout marginal nul** : reel Instagram (usine ac-instagram), highlight site + newsletter
  guests, audit de listing (skill audit-listings), set-up PriceLabs, brochure PDF client (skill listing-pdf),
  fiche "guest welcome" bilingue, reponse aux avis.
- **Garantie plus forte** : "si on ne vend pas N nuits, on vous paie le site $690" (risque connu, cap $690).
- **Scarcite vraie** : "one villa per street", liste fermee a 10 villas par zone, date limite avant
  la basse saison (15 novembre).
- **Nommer l'offre** : "Low Season Partner" (bronze = highlight 5 %, silver = co-listing 10 %,
  gold = co-listing + site + reel + pricing).
- **Prix ancre** : site $690 + $29, reel $290, audit $190, pricing set-up $290 : "worth $1,460, $0 for partners".
- **Preuve dans le message** : capture PriceLabs occupation de nos villas vs marche, 2 avis Superhost recents.
- **Urgence naturelle** : le calendrier fev/mars se remplit 41 jours avant en moyenne (PriceLabs
  median_booking_window) : "the window for February closes mid-December".

## Si refus — highlight AC Collection

```
Understood, no problem. One lighter option, zero commitment: we feature [Villa] as a highlight on the
AC Collection guest site and in our guest emails (repeat guests, groups, retreats looking for large
villas). You handle the booking directly, we take 5% on a booking we send you, nothing otherwise.
Shall I add it?
```

## Relances (apres le message 2 ; `python3 villa-site/funnel.py due` les liste)

- J+3 : "Did the page load OK on your side? [lien]. Happy to walk you through the [empty] nights in 10 min."
- J+7 : capture PriceLabs d'une de nos villas vs marche + "Same channels, same pricing engine, for [Villa]. 10 min this week?"
- J+14 : "We take a handful of villas per area for the low season. Want the spot for [Villa], or shall I pass? The site stays here either way: [lien site]"

## Regles

- Le chiffre du message 2 vient de la page (meme calcul), jamais arrondi a la hausse.
- Pas de nom de villa AC Collection ni de tarif de nos villas dans les messages (juste le taux d'occupation).
- Statut a jour dans `villa-site/funnel.csv` a chaque contact (`funnel.py set <slug> sent|replied|call|signed|highlight|refused`).
- Hors cible : villa geree par un gros PM ("managed by" sur le listing), villa deja a > 60 % en basse saison, 1-3BR.
