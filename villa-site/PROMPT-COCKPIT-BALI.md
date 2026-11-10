# Prompt pour la session Dashboard : section « Bali — villas » dans l'onglet Prospection

Préparé le 10/11/2026 depuis une session cloud. Chiffres lus ce jour-là sur les calendriers Airbnb
(fenêtre décembre 2026 → février 2027, marché PriceLabs relevé le 06/11/2026).

---

```
Ajoute au cockpit une section « Bali — villas » dans l'onglet Prospection, et tiens-la à jour.

OÙ
- Front : artifacts/ac-collection/src/pages/cockpit/cockpit-growth.tsx (CockpitProspection), dépôt ac-collection.
  La section Bali passe AU-DESSUS des nouveaux marchés, qui restent tels quels.
- Données : une nouvelle clé cockpit « bali_prospects », poussée depuis le Mac avec
  PUT /api/cockpit/data/bali_prospects (en-tête x-cockpit-token), comme les autres clés.
  Ainsi, mettre la liste à jour ne demande pas de redéployer.

AFFICHAGE
- Regroupé par zone, dans cet ordre : Uluwatu, Canggu, Pererenan, Berawa, Seminyak.
- Pour chaque villa : nom, chambres, lien de l'annonce Airbnb, occupation villa / secteur sur la fenêtre,
  nuits libres, contact, WhatsApp, statut, et le message 1 à envoyer.
- Boutons : « Open » (wa.me avec le message pré-rempli), « Copy » (message), « ✓ Sent ».
  « ✓ Sent » réutilise l'état « prospect_sent » (clé = id de l'annonce) et le même plafond de 8 envois par jour
  que la file des nouveaux marchés.
- Une villa sans numéro affiche « contact à trouver » et la piste (site, Instagram).
- Si la villa a un slug dans le funnel du site (villa_funnel), afficher son statut réel et le lien de sa page diagnostic.

CORRECTION AU PASSAGE
- MSG1 par défaut (nouveaux marchés) cite encore « 4.84★, 759 reviews over 9 years » : remplacer par
  « Airbnb Superhost (10 years, 800+ reviews) ». Ne pas toucher aux messages déjà personnalisés dans « prosp_msgs ».

MISE À JOUR
- Un script sur le Mac régénère « bali_prospects » chaque matin : find_leads.py sur les zones,
  lecture des calendriers (fetch_listing.fetch_calendar), exclusion des listes AVOID / HOLD / BIG_PM / OURS
  et de tout ce qui est déjà dans le funnel, puis push.
- Uluwatu : diagnostic.py refuse la zone (secteur au-dessus de 55 %). Pour Uluwatu, garder la villa quand SON
  occupation sur la fenêtre est très en dessous du secteur (Uluwatu : déc. 58 %, janv. 63 %, févr. 64 %).
  L'argument n'est pas la basse saison mais « le marché est plein, pas votre calendrier ».
  Toujours écrire « votre calendrier Airbnb » : un calendrier presque vide peut être non synchronisé.

RÈGLES (inchangées)
- Jamais d'envoi automatique : Anthony clique « Open » puis envoie lui-même. 8 par jour maximum.
- Jamais la messagerie Airbnb pour prospecter. Jamais recontacter un refus.
- Gravity (hôte « Gravity » = Gravity Bali, partenaire en attente) : à exclure. Le filtre actuel ne l'attrape pas
  quand l'hôte s'appelle seulement « Gravity » (annonces 39137705 et 1662162419842242632) : à corriger dans
  find_leads.py ET build.ts.
- Message 1 : accroche demande, une question, sans page. La page diagnostic part au message 2, après une réponse.

DONNÉES INITIALES (à pousser telles quelles dans bali_prospects)
```

## Données initiales

Accroche commune (message 1) :
`Hi there, Anthony here. Airbnb Superhost for 10 years (800+ reviews), I run AC Collection, around 30 luxury villas in Canggu, Seminyak and Uluwatu.`

### Uluwatu

| Villa | Ch. | Annonce | Occup. villa / secteur | Nuits libres | Contact | WhatsApp | Statut |
|---|---|---|---|---|---|---|---|
| Casa JOMO, Bingin | 5 | https://www.airbnb.com/rooms/1272808859165361333 | 11 % / 63 % | 66/74 (janvier entier) | site casajomobali.com | +62 877 7654 3211 (à vérifier WhatsApp) | à envoyer |
| Exotik Villas Bali (bureau à Uluwatu) | 5 | https://www.airbnb.com/rooms/1649072131165582352 · Joglo Bingin https://www.airbnb.com/rooms/1467823976593612556 (en pause ?) · Canggu 6 ch. https://www.airbnb.com/rooms/13983899 | Canggu 26 % / 52 % | Canggu 55/74 | exotik-villas-bali.com | +62 812 3765 1008 (à vérifier WhatsApp) | à envoyer |
| Sukacita Hill, falaise, spa | 6 | https://www.airbnb.com/rooms/1288210663512707268 | 9 % / 64 % | 67/74 (février entier) | sukacitahillbali.com, Instagram @sukacitahilluluwatu | à trouver | contact à trouver |
| Casa Di Lusso, Bingin (Loca Villa Group) | 5 | https://www.airbnb.com/rooms/1282352162838926324 | 3 % / 58 % | 72/74 | locavillagroup.com, info@locavillagroup.com | à trouver | vérifier qu'elle est encore louée (une page la dit « SOLD ») |
| Casa Rocoso | 5 | https://www.airbnb.com/rooms/1536772417045566859 | 5 % / 63 % | 70/74 (janvier entier) | inconnu | à trouver | contact à trouver |
| 6 ch. salle de sport, vue océan (hôte Mio) | 6 | https://www.airbnb.com/rooms/1569243074057240780 | 7 % / 63 % | 69/74 | inconnu | à trouver | contact à trouver |
| Tranquil Oasis (hôte Sheena) | 5 | https://www.airbnb.com/rooms/1272728029974116598 | 11 % / 63 % | 66/74 | inconnu | à trouver | contact à trouver |
| 6BR Duo Villas (hôte Mr G, plusieurs villas) | 6 | https://www.airbnb.com/rooms/1619304413229104268 | 18 % / 63 % | 61/74 | inconnu | à trouver | contact à trouver |

Messages Uluwatu :
- Casa JOMO : `{accroche}\n\nI came across Casa JOMO while benchmarking Bingin: Uluwatu villas are running at around 63% occupancy in January, yet your Airbnb calendar is still open for the whole month.\n\nMind if I share what I'm seeing?`
- Exotik : `{accroche}\n\nI came across your villas while benchmarking Uluwatu and Canggu. Your 6-bedroom near the beach in Canggu still shows 55 open nights between December and February, while the area sits at about 52%.\n\nMind if I share the numbers across your portfolio?`
- Sukacita Hill : `{accroche}\n\nI came across Sukacita Hill while benchmarking Uluwatu: the area runs at about 64% occupancy in February, yet your Airbnb calendar is still open for the whole month.\n\nMind if I share what I'm seeing?`
- Casa Di Lusso : `{accroche}\n\nI came across Casa Di Lusso while benchmarking Bingin: Uluwatu villas run at about 58% occupancy in December, yet your Airbnb calendar is still open for the whole of December and February.\n\nMind if I share what I'm seeing across your villas?`
- Casa Rocoso : `{accroche}\n\nI came across Casa Rocoso while benchmarking Uluwatu: the area runs at about 63% occupancy in January, yet your Airbnb calendar is still open for the whole month.\n\nMind if I share what I'm seeing?`
- Autres villas d'Uluwatu : même modèle que Casa Rocoso, avec le mois le plus vide de la villa.

### Canggu, Pererenan, Berawa, Seminyak

| Villa | Zone | Ch. | Annonce | Occup. villa / secteur | Nuits libres | Contact | WhatsApp | Statut |
|---|---|---|---|---|---|---|---|---|
| Villa Luja (GORO) | Canggu | 5 | https://www.airbnb.com/rooms/600173702615262232 | 18 % / 52 % | 61/74 | GORO Villa Management | +62 851 2103 1173 | appel (funnel : villa-luja), page https://www.ac-collection.com/diagnostic/villa-luja?owner |
| Villa Canggu Berawa (Herman, Balivillaco) | Berawa | 5 | https://www.airbnb.com/rooms/1198126622667476950 | 57 % / 52 % | 32/74 | Herman & Komang | +62 812 1148 9565 | a répondu le 16/09 (funnel : villa-berawa-chef) |
| The Continental (5 Star Bali Villa) | Seminyak | 8 | https://www.airbnb.com/rooms/1109807168634359026 | 22 % / 41 % | 58/74 | 5 Star Bali Villa | +62 821 3571 7733 (à vérifier) | à envoyer |
| Villa 6 ch. à 100 m de la plage (sans doute Casa Ola) | Pererenan | 6 | https://www.airbnb.com/rooms/29463987 | 19 % / 52 % | 60/74 | hôte « Ola Bali Management » | +62 818 899 936 (à vérifier) | à envoyer |
| Villa Soul Moon (Martha) | Canggu | 5 | https://www.airbnb.com/rooms/1447879080696061784 | 45 % / 52 % | 41/74 | Martha | +62 895 3470 07195 | envoyé le 13/09, relance à envoyer |
| Villa Sunshine | Umalas | 5 | https://www.airbnb.com/rooms/11226411 | 11 % / 52 % | 66/74 | hôte Nisa | à trouver | contact à trouver |
| Modern Artistic 5BR | Berawa | 5 | https://www.airbnb.com/rooms/1535406640517283940 | 14 % / 52 % | 64/74 | hôte Claudya | à trouver | contact à trouver |
| Buddha Waterfall Villa | Canggu | 5 | https://www.airbnb.com/rooms/1304669022056560763 | 18 % / 52 % | 61/74 | hôte Linda | à trouver | contact à trouver |
| Spacious 5BD | Seminyak | 5 | https://www.airbnb.com/rooms/1008987291245670153 | 19 % / 41 % | 60/74 | hôte Made | à trouver | contact à trouver |
| Grand Villa Puri Padi | Berawa | 5 | https://www.airbnb.com/rooms/1185564387095073509 | 23 % / 52 % | 57/74 | hôte Miss D & Team | à trouver | contact à trouver |
| Villa avec chef | Seminyak | 5 | https://www.airbnb.com/rooms/5055060 | 31 % / 41 % | 51/74 | hôte Natasha | à trouver | contact à trouver |

Messages :
- Villa Luja : `Hi, Anthony here, following up on Villa Luja.\n\nI refreshed the numbers for the coming months: the villa's Airbnb calendar still shows 61 open nights between early December and February, while 5-bedroom villas around it sit at about 52%. Updated private page: https://www.ac-collection.com/diagnostic/villa-luja?owner\n\nWould Thursday or Friday suit you for a 15-minute call?`
- Herman : `Hi Herman, Anthony here. You mentioned you manage several luxury villas like Villa Canggu Berawa.\n\nWhich of them have the most open nights between December and February? I'll run the numbers for those and send them over.`
- The Continental : `{accroche}\n\nI came across The Continental while benchmarking 8-bedroom villas in Seminyak: it still shows 58 open nights between December and February.\n\nMind if I share how that compares to the area?`
- Pererenan 6 ch. : `{accroche}\n\nI came across your 6-bedroom villa by Pererenan Beach while benchmarking the area: it still shows 60 open nights between December and February.\n\nMind if I share how that compares to the area?`
- Martha : `Hi Martha, Anthony here again. Villa Soul Moon's Airbnb calendar is still open for 19 of the first 20 nights of December.\n\nMind if I share what I'm seeing for the area over that period?`

### Écartées
- Gravity (39137705, 1662162419842242632) : partenaire en attente.
- Brand New Villa Jade, The Azure Collection (1642966883626993483) : déjà en discussion avec Anthony.
- Villa Mila, Elld Property (1015878595975323844) : désormais plus remplie que son secteur (62 %).
