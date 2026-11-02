# Machine Reels Instagram — prompt de lancement de la session Claude Code

## Comment lancer la session (2 minutes)

Les vidéos sont sur ton Mac (dossier `~/Claude/MEDIA SOCIAL NETWORK`), donc la session tourne **sur le Mac** :

1. Vérifie que le connecteur **Higgsfield** est activé sur claude.ai (Paramètres → Connecteurs). C'est lui qui fait l'analyse des rushes, l'upscale, le recadrage 9:16, le prédicteur de viralité et le doublage.
2. Terminal : `cd ~/Claude/"MEDIA SOCIAL NETWORK" && claude`
3. Colle le prompt ci-dessous. La session commence par ranger les vidéos elle-même (`raw/<villa>/`), pas besoin de trier avant.

---

## Le prompt à coller

```
Tu es un directeur créatif spécialisé dans les Reels Instagram pour les locations de villas haut de gamme, et tu travailles pour AC Collection (collection de villas de luxe à Bali : Canggu, Seminyak, Pererenan, Berawa, Uluwatu ; 9 ans Superhost, 759 avis, 4.84). Réservation en direct : WhatsApp +62 851 9018 1610 et ac-collection.com.

Analyse toutes les vidéos du dossier courant. Les fichiers montrent plusieurs villas différentes ainsi que quelques plans où j'apparais (Anthony, l'hôte).

Commence par identifier et regrouper les vidéos par villa en observant l'architecture, la piscine, le mobilier, la végétation et les décors. Range-les dans ./raw/<villa>/ (et ./raw/anthony/ pour les plans où j'apparais, ./raw/_a-trier/ pour ceux que tu n'arrives pas à attribuer : demande-moi). Montre-moi le tri avant de monter. Ne mélange jamais deux villas dans une même séquence narrative. Chaque villa doit rester clairement identifiable.

OBJECTIF
Créer un Reel vertical 9:16 de 18 à 22 secondes présentant une collection de villas exceptionnelles. Le spectateur doit comprendre qu'il peut choisir parmi plusieurs propriétés et avoir envie de réserver son prochain séjour avec nous. Il ne doit surtout pas croire qu'il s'agit d'une villa unique.

CONCEPT
« Une destination, plusieurs façons de la vivre. »

STRUCTURE
0–2 s : montage très rapide de trois plans spectaculaires provenant de trois villas différentes : piscine, vue, architecture. Hook immédiat.
Texte : « Which one will you choose? »

2–14 s : présenter 4 à 6 villas, 2 à 3 secondes chacune, avec deux plans complémentaires : un plan large spectaculaire, puis un détail émotionnel ou sensoriel. Changer de villa avec un cut franc, un match cut ou une transition motivée par un élément réel : mouvement de caméra, reflet d'eau, ouverture de porte, passage derrière un mur, lumière du soleil.

14–18 s : un plan naturel où j'apparais comme l'hôte, celui qui sélectionne ces expériences. Préserver exactement mon identité, ma tenue et mes mouvements.

18–22 s : terminer avec le meilleur plan de piscine, coucher de soleil ou vue extérieure.
Texte final : « Your next villa is waiting » puis « Book direct on WhatsApp ↓ ».

STYLE VISUEL
Luxury travel editorial, cinematic hospitality campaign, warm tropical light, rich natural colors, elegant contrast, realistic skin tones, refined camera movements, premium but authentic atmosphere.

MONTAGE
10 à 14 plans courts. Début rapide, partie centrale immersive, fin plus lente et aspirationnelle. Uniformiser l'étalonnage pour que les villas appartiennent au même univers de marque. Monter sur une grille rythmique (environ 100-110 BPM) pour que les changements de villa tombent sur les temps forts de la musique, mais N'INCRUSTE PAS de musique dans le fichier : pour la pub, Meta n'accepte que sa propre bibliothèque (Sound Collection), et pour l'organique je choisis un son tendance dans Instagram. Fournis-moi les timecodes des cuts pour caler le son.

FIDÉLITÉ
Préserver l'architecture, les proportions, le mobilier, les équipements et les paysages réels de chaque villa. Préserver exactement mon visage, mon corps et ma tenue. Maintenir une séparation visuelle nette entre les propriétés. Utiliser uniquement les prestations réellement visibles dans les vidéos sources. Rien d'inventé : une pub qui montre ce qui n'existe pas, c'est des plaintes clients et un rejet Meta.

HIGGSFIELD (MCP)
Traite chaque clip SÉPARÉMENT, villa par villa, jamais plusieurs villas dans une seule génération (l'IA fusionnerait piscines, pièces et architectures). Prompt par clip :
"Enhance this existing luxury-villa shot with smooth cinematic camera motion and refined natural lighting. Preserve the exact architecture, furniture, pool, landscape and spatial proportions of this specific property. Warm tropical highlights, rich natural colors, realistic water reflections, elegant 35mm travel-editorial look, smooth stabilized movement, realistic physics, tack-sharp details. Create a premium hospitality-commercial feeling while remaining authentic to the source footage. Vertical 9:16."
Règles : avant chaque lot, donne-moi le coût en crédits et attends mon OK. Après chaque clip amélioré, compare-le au plan source : si un meuble, une forme de piscine, une ouverture ou un paysage a changé, rejette la version Higgsfield et garde la version ffmpeg (étalonnage + stabilisation seulement). Les plans où j'apparais ne passent JAMAIS par une génération Higgsfield (risque sur le visage) : étalonnage ffmpeg uniquement. Utilise aussi Higgsfield pour l'upscale (< 1080p) et le reframe 9:16 des plans horizontaux (sujet centré, jamais de bandes noires), puis le prédicteur de viralité sur les 3 versions finales.

LIVRABLE
Trois versions, même structure, montage différent :
A. Luxe cinématographique
B. Rapide, dynamique et viral
C. Élégant, humain et émotionnel
Fichiers : ./reels/collection/collection-A.mp4, -B.mp4, -C.mp4 en 1080×1920, 9:16, + une miniature .jpg chacun, + ./reels/collection/cuts.md (timecodes des cuts et villa affichée à chaque plan). Un petit "AC Collection" blanc en bas à gauche. Vérifie chaque export (durée, 1080×1920, première et dernière image, texte lisible sur téléphone) et montre-moi les miniatures.

Puis ./reels/collection/scores.md (score de viralité Higgsfield des 3 versions, verdict : laquelle on pousse en pub et pourquoi) et ./reels/collection/ads.md : texte principal (125 caractères visibles max), titre, description, en anglais + version française ; 3 audiences à tester (voyageurs internationaux fréquents intéressés Bali + villas de luxe en Australie / Singapour / Europe de l'Ouest ; lookalike des visiteurs ac-collection.com ; retargeting des vues vidéo ≥ 50 %) ; réglages (objectif Engagement → Messages WhatsApp, placement Reels seul, 15-20 €/jour, 5-7 jours, on garde la version au coût par conversation le plus bas, kill si > 8 € après 5 jours) ; la légende Instagram organique (hook, 3 lignes, hashtags, "lien en bio"). Et ./reels/DASHBOARD.md avec les colonnes que je remplirai (dépense, vues, conversations WhatsApp, réservations).

Garde les scripts réutilisables dans ./tools/ (inventaire, étalonnage, montage, export) : le prochain Reel collection, avec de nouvelles villas, doit être une commande.

ORDRE
1. Inventaire + tri par villa, montre-moi le résultat (combien de plans exploitables par villa, lesquelles entrent dans le Reel).
2. Propose la sélection des 4 à 6 villas et l'ordre, avec le plan large et le détail pour chacune.
3. Version A de bout en bout, montre-la-moi, puis B et C.
```
