# Cahier des charges – Planches de sprites du Disciple du Dragon Noir

Version 1 – mod BlackDragonMagic (Baldur's Gate II : Enhanced Edition, EET)

---

## 0. Utilisation de ce document

**Pour l'auteur du mod.**
1. Au début d'une conversation ChatGPT, joins ce fichier et les images de
   référence (section 3).
2. Écris : « Lis ce cahier des charges. Ne génère rien pour l'instant, confirme
   simplement que tu l'as compris. »
3. Demande ensuite une planche à la fois, avec son identifiant et sa variante,
   par exemple « Génère la planche CLAW2, variante C ».
4. Contrôle chaque planche avec la section 9 avant de la convertir.

**Pour ChatGPT.**
- Ce document décrit des planches de sprites destinées à un jeu vidéo.
- Pour chaque demande, génère **une seule image** correspondant **exactement** à
  la fiche de la planche demandée (section 7), en respectant toutes les règles
  des sections 2 à 6.
- Si une règle ne peut pas être respectée, dis-le plutôt que de l'ignorer.
- Ne génère pas plusieurs planches dans une seule image.

---

## 1. Contexte et but

- **Où vont les planches.** Elles sont converties automatiquement en animation de
  créature pour un jeu isométrique des années 2000 (moteur Infinity Engine, style
  Baldur's Gate II, sprites 3D pré-rendus).
- **Pourquoi c'est automatique.** Un script découpe la grille, détoure le fond
  cyan et pose chaque image sur le sol.
- **Conséquence.** Toute irrégularité (sprites qui se touchent, fond non uni,
  personnage qui glisse dans sa case) se retrouve dans le jeu.
- **Taille dans le jeu.** Le personnage y mesure **environ 75 pixels de haut**.
  La lisibilité à petite taille prime donc sur le détail.

---

## 2. Le personnage

**Identité.** Le Disciple du Dragon Noir, un demi-elfe qui se transforme peu à
peu en dragon noir.

**Apparence de référence (stade final).**
- **Tête** : cheveux noirs mi-longs, oreilles pointues, petites cornes sombres
  recourbées vers l'arrière.
- **Corps** : silhouette humanoïde élancée.
- **Armure** : pectoraux en bronze nervurés comme une cage thoracique, épaulières
  bronze, peau des bras visible.
- **Tenue** : longue robe noire fendue, bordures et ceinture bronze, bottes
  sombres.
- **Ailes** : grandes ailes de chauve-souris, membranes vert-noir, armature
  noire, griffes au bout.
- **Queue** : longue et épaisse, noire, avec une rangée de pics bronze-os sur le
  dessus.

**Palette imposée.**

| Élément | Couleur |
|---|---|
| Écailles, queue, cornes | noir brillant à reflets vert foncé |
| Membranes des ailes | vert-noir, un peu plus claires que le corps |
| Robe | noire |
| Bordures, armure, pics de la queue | bronze |
| Peau visible (bras, visage) | bronze clair, mat |

Le personnage doit rester **sombre**. La lisibilité vient du liseré de lumière et
du bronze, **jamais** d'un éclaircissement des matières.

---

## 3. Images de référence

À joindre au début de la conversation :
- `v3/idle.png` : le personnage, ses couleurs, l'ordre des directions ;
- `v3/walk.png` : le personnage en mouvement.

Le design, les proportions et les couleurs de ces images font foi. En cas de
contradiction entre le texte et une référence, **la référence l'emporte** pour
l'apparence, et **le texte l'emporte** pour le format (section 4).

---

## 4. Format technique

| Règle | Valeur |
|---|---|
| Image | une seule image carrée, environ 1250 × 1250 px |
| Grille | 8 lignes × 8 colonnes (sauf mention contraire dans la fiche) |
| Cases | toutes de la même taille, grille parfaitement régulière |
| Lignes | une direction de vue par ligne |
| Colonnes | une image de l'animation par colonne, de gauche à droite |
| Fond | cyan pur uni **#00FFFF** partout |
| Interdits sur le fond | dégradé, texture, sol, ombre portée, texte, numéros, bordures, lignes de grille |

**Ordre des lignes, de haut en bas (obligatoire, identique sur toutes les planches).**

| Ligne | Direction | Le personnage… |
|---|---|---|
| 1 | face | regarde vers le spectateur |
| 2 | face-droite | regarde vers le bas-droite de l'écran |
| 3 | profil droit | regarde vers la droite de l'écran |
| 4 | dos-droite | regarde vers le haut-droite de l'écran |
| 5 | dos | tourne le dos au spectateur |
| 6 | dos-gauche | regarde vers le haut-gauche de l'écran |
| 7 | profil gauche | regarde vers la gauche de l'écran |
| 8 | face-gauche | regarde vers le bas-gauche de l'écran |

**Caméra.** La même pour toutes les cases :
- vue de trois quarts plongeante, environ 30 à 40° vers le bas ;
- même distance et même taille de personnage ;
- lumière venant du haut à gauche.

---

## 5. Placement et espacement

1. **Les pieds ne bougent pas.** Dans une ligne, les pieds restent au même
   endroit (même hauteur, même position horizontale) sur toutes les images. Seule
   exception : la mort, où le corps tombe.
2. **Le corps reste centré** dans sa case. Seules les parties animées bougent.
3. **Aucun contact entre sprites.** Chaque sprite reste entièrement dans sa case,
   avec une marge de fond cyan tout autour. Deux sprites ne se touchent jamais,
   ailes et queue comprises.
4. **Ailes ou queue très déployées.** Il vaut mieux dessiner le personnage
   **un peu plus petit sur toute la planche** que déborder sur la case voisine.
   La taille doit rester la même sur toute la planche.

---

## 6. Rendu et lisibilité

- **Netteté** : contours nets et francs ; pas de flou, de flou de mouvement, de
  profondeur de champ, de halo ni de grain.
- **Silhouette** : cornes, bras, ailes et queue bien séparés du corps et
  reconnaissables même en tout petit.
- **Formes** : grandes formes simples plutôt que petits détails. Les petites
  écailles, gravures et motifs d'armure sont simplifiés.
- **Contraste** : un fin liseré de lumière sur le contour pour détacher le corps
  sombre du fond.
- **Mouvements** : amples et exagérés. Chaque pose clé doit se reconnaître à
  75 pixels de haut.
- **Cohérence** : même éclairage, même échelle, mêmes couleurs sur toutes les
  images et toutes les lignes.

---

## 7. Fiches des planches

Règles communes :
- **Boucles** : la dernière image s'enchaîne naturellement avec la première.
- **Attaques** :
  - la première et la dernière image sont la même pose de repos ;
  - l'attaque est dirigée vers la direction que regarde le personnage dans la
    ligne ;
  - les pieds restent plantés, seuls le corps se penche et pivote.

### IDLE – Repos
- **Type** : boucle, 8 images.
- **Description** : debout, immobile, calme.
- **Ce qui bouge** : seuls les épaules et les bras bougent légèrement (respiration
  calme, léger mouvement des bras).
- **Ce qui ne bouge pas** : jambes, pieds, tête, buste, ailes et queue restent
  exactement en place.

### WALK – Marche
- **Type** : boucle, 8 images.
- **Description** : marche sur place.
- **Mouvements** :
  - les jambes et les bras alternent ;
  - les ailes restent repliées dans le dos ;
  - la queue ondule légèrement derrière.

### CAST – Incantation
- **Type** : boucle, 8 images.
- **Description** : le personnage canalise un sort, sur place.
- **Mouvements** :
  - les bras font de grands gestes fluides, comme s'il tissait un sort ;
  - les ailes battent et s'ouvrent lentement.
- **Variantes sans ailes** : seuls les bras bougent.

### WINGS – Libération du sort
- **Type** : une fois, 8 images.
- **Description** :
  - les ailes se déploient d'un coup, grandes ouvertes ;
  - les bras se tendent vers l'avant pour libérer le sort ;
  - puis tout revient au repos.
- **Variantes sans ailes** : ne pas générer.

### CLAW – Griffe droite
- **Type** : attaque, 8 images.
- **Déroulé** :
  1. **armé** : le bras droit est tiré en arrière ;
  2. **frappe** : coup de griffe rapide et large vers l'avant ;
  3. **retour** au repos.

### CLAW2 – Griffe double
- **Type** : attaque, 8 images.
- **Déroulé** :
  1. **armé** : les deux bras montent haut, griffes écartées ;
  2. **frappe** : ils s'abattent ensemble vers l'avant, au même moment ;
  3. **retour** au repos.

### TAIL – Coup de queue
- **Type** : attaque, 8 images.
- **Déroulé** :
  1. **armé** : le corps pivote légèrement ;
  2. **frappe** : la queue balaie bas et vite par le côté et frappe vers l'avant ;
  3. **retour** : le corps revient de face et la queue repasse derrière.
- **Interdits** : la queue reste basse, près du sol. Elle ne passe jamais
  au-dessus de la tête et ne fait jamais le tour du corps.
- **Variantes sans queue** : ne pas générer.

### BUFFET – Coup d'ailes
- **Type** : attaque, 8 images.
- **Déroulé** :
  1. **armé** : les deux ailes se lèvent et s'ouvrent grand derrière le personnage ;
  2. **frappe** : elles battent ensemble vers l'avant en un coup violent, le corps
     penché en avant ;
  3. **retour** : les ailes se replient.
- **Variantes sans ailes** : ne pas générer.

### HIT – Touché
- **Type** : une fois, 8 images.
- **Description** :
  - frappé de face, la tête et le buste partent en arrière ;
  - les ailes tressaillent ;
  - puis il se reprend et revient au repos.

### DEATH – Mort
- **Type** : une fois, 8 images, pas de boucle.
- **Description** :
  - il chancelle, ses genoux plient ;
  - il s'effondre progressivement jusqu'au sol ;
  - la dernière image le montre allongé, immobile.
- **Placement** : seule planche où le corps peut quitter sa position de départ.

---

## 8. Variantes (stades d'évolution)

Le personnage se transforme avec les niveaux. On demande la variante avec la
planche, par exemple « planche WALK, variante A ».

| Variante | Niveaux | Description | Planches à ne pas générer |
|---|---|---|---|
| A | 1 à 8 | ni ailes ni queue, totalement absentes (pas de moignons) | WINGS, TAIL, BUFFET |
| B | 9 à 13 | queue, sans ailes (pas de moignons) | WINGS, BUFFET |
| C | 14 et plus | ailes et queue (apparence des références) | aucune |

Les variantes A et B gardent le même visage, la même armure, la même robe et la
même taille de dessin. La croissance du personnage est gérée dans le jeu, pas
sur la planche.

---

## 9. Critères d'acceptation

Une planche est acceptée si :
- [ ] il y a 8 lignes × 8 colonnes régulières, une seule animation ;
- [ ] le fond est cyan uni partout, sans ombre, sol, texte ni grille ;
- [ ] aucun sprite ne touche son voisin, ailes et queue comprises ;
- [ ] l'ordre des directions est respecté : la ligne 3 regarde à droite, la
      ligne 7 à gauche, la ligne 1 fait face, la ligne 5 montre le dos ;
- [ ] les pieds ne glissent pas d'une image à l'autre (sauf DEATH) ;
- [ ] les couleurs sont celles de la palette : personnage sombre, bronze, ailes
      vert-noir ;
- [ ] le personnage est le même que sur les références (visage, armure, cornes,
      ailes, queue) ;
- [ ] l'animation correspond à la fiche : bonne main, bon membre, bonne
      direction d'attaque ;
- [ ] pour une attaque, la première et la dernière image sont la même pose de
      repos.

---

## 10. Annexe technique (pour l'auteur du mod)

**Fichiers.** Planches enregistrées dans `works/final_form_avatar_source/vN/`
sous les noms ci-dessous.

**Conversion.**
`python3 build_avatar.py vN ../../kits/black_dragon_disciple/avatar/anim`

| Fichier | Planche | Animation du jeu |
|---|---|---|
| `idle.png` | IDLE | SD (debout), SC (prêt au combat) |
| `walk.png` | WALK | WK |
| `cast.png` | CAST | CA |
| `wings.png` | WINGS | SP |
| `claw.png` | CLAW | A1 |
| `claw2.png` | CLAW2 | A2 |
| `tail.png` | TAIL | A3 |
| `buffet.png` | BUFFET | A4 |
| `hit.png` | HIT | GH |
| `death.png` | DEATH | DE, puis TW/SL (au sol) et GU (relevé) |

**Planches absentes d'une variante.** Elles sont remplacées par une autre
attaque à la conversion.
