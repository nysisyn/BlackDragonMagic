# Prompt ChatGPT – planches de sprites du Disciple du Dragon Noir

Ce fichier sert à générer, avec ChatGPT, les planches de sprites de l'avatar du
Disciple du Dragon Noir. Ces planches sont ensuite converties en animation de
créature Infinity Engine par `build_avatar.py`.

## Mode d'emploi

1. **Une planche par demande.** On demande une seule animation à la fois, c'est
   plus fiable.
2. **Toujours joindre une image de référence.** Une ou deux planches déjà
   validées, par exemple `v3/idle.png` et `v3/walk.png`. C'est ce qui garde le
   même personnage et le même ordre des directions d'une planche à l'autre.
3. **Construire le prompt.** On colle le **prompt de base** ci-dessous, puis on
   remplace les trois champs entre crochets :
   - `[VARIANT]` : une ligne de la section *Variantes* ;
   - `[ANIMATION]` : un bloc de la section *Animations* ;
   - `[FRAMES]` : le nombre d'images, 8 par défaut.
4. **Contrôler la planche** avant de la convertir (voir *Vérifications*).
5. **L'enregistrer** sous le nom indiqué dans *Correspondance avec le jeu*, dans
   le dossier de la version (par exemple `v4/`). On lance ensuite
   `python3 build_avatar.py v4 ../../kits/black_dragon_disciple/avatar/anim`.

## Prompt de base

```
Sprite sheet for a classic isometric CRPG (Baldur's Gate II style, pre-rendered 3D sprites).

Character: the same black dragon disciple as the attached reference sheets: a winged
half-elf with dark leathery wings, a long spiked tail, small horns, a black robe with
bronze trims and bronze ribbed chest armour. Keep the exact same design, colours and
proportions in every frame.
Variant: [VARIANT]

Animation: [ANIMATION]
[FRAMES] frames.

Layout: a grid of 8 rows x [FRAMES] columns. Each row is one viewing direction, in this
exact order from top to bottom: 1 front (facing the viewer), 2 front-right, 3 right
profile, 4 back-right, 5 back, 6 back-left, 7 left profile, 8 front-left. Each column is
one frame of the animation, left to right. All cells are the same size and form a
regular grid.

Camera: the same high three-quarter view from above (about 30-40 degrees down) for every
direction, same distance, same lighting from the upper left.

Colours: keep the original dark colours: glossy black scales with a dark green sheen,
dark green-black wing membranes, black robe with bronze trims. Readability must come
from a thin light rim light and the contrast of the bronze trims, NOT from lightening
the materials.

Readability at small size (very important): these sprites will be shrunk to about
75 pixels tall in the game, so design them to read clearly at that size.
- Clear, strong silhouette: horns, arms, wings and tail clearly separated from the body
  and easy to tell apart.
- Big, simple shapes instead of fine detail: simplify small scales, engravings, folds
  and tiny armour patterns. Avoid noisy textures.
- Strong contrast and a thin light rim light along the outline so the dark body stands
  out from the background.
- Wing membranes slightly lighter than the body so the wings never merge with the torso.
- Wide, exaggerated, easy-to-read motions: each key pose must be recognisable even as a
  tiny silhouette.

Rendering: crisp and sharp, clean hard edges, no blur, no motion blur, no depth of
field, no glow, no film grain, no soft focus.

Background: perfectly flat solid cyan (#00FFFF) everywhere, no gradient, no texture, no
ground, no cast shadow, no text, no labels, no borders, no grid lines.

Spacing: each sprite fully inside its cell with clear empty space around it. Sprites
must never touch or overlap, wings and tail included: when the wings or tail spread
wide, make the whole character a bit smaller rather than crossing into the next cell.

Placement: the feet stay on the same spot (same baseline, same horizontal position) in
every frame of a row, and the body stays centred in its cell; only the animated parts
move. The only exception is the death animation, where the body falls to the ground.

Attacks: every attack is aimed toward the direction the character faces in that row.
The feet stay planted; only the body leans and turns. The first and last frames are the
same rest pose so the attack starts and ends cleanly.

Idle: the character stands still; only the shoulders and arms move slightly (a calm
breathing or shifting of the arms). The legs, feet, head, body, tail and wings stay
exactly in place in every frame.

Casting: the character channels a spell, standing in place: the arms move in wide,
fluid gestures, and the wings beat and spread slowly while he channels (for the variants
without wings: only the arms move). The movement loops smoothly: the last frame leads
back into the first one.
```

## Variantes

Les trois stades du kit. La taille du personnage grandit dans le jeu, pas sur la
planche.

| Niveaux | Ligne `[VARIANT]` |
|---|---|
| 1 à 8 | `no wings and no tail at all (remove them completely, no stumps).` |
| 9 à 13 | `tail but no wings at all (remove the wings completely, no stumps).` |
| 14 et plus | `wings and tail.` |

Sur les variantes sans ailes, on ne génère pas les planches qui n'ont pas de sens
(coup d'ailes, ailes déployées). Sans queue, on ne génère pas le coup de queue.
`build_avatar.py` remplacera ces animations par une autre attaque.

## Animations

Chaque bloc se colle à la place de `[ANIMATION]`.

### Repos (idle)
```
idle, a calm standing loop: only the shoulders and arms move slightly; the last frame
leads back into the first one.
```

### Marche (walk)
```
walk cycle, walking in place: legs and arms alternating, wings folded on the back, tail
swaying slightly behind; seamless loop.
```

### Incantation (cast)
```
casting loop: the arms move in wide, fluid gestures as if weaving a spell while the
wings slowly beat and spread; seamless loop.
```

### Ailes déployées (wings)
```
spell release: the wings spread wide in one powerful burst and the arms thrust forward
to release the spell, then everything returns to the rest pose. Keep the spread wings
inside the cell.
```

### Griffe droite (claw)
```
claw attack with the RIGHT hand: wind-up with the arm drawn back, a fast and wide slash
toward the front, then recovery to the rest pose.
```

### Griffe double (claw2)
```
double claw rake: both arms rise high with the claws spread, then slash down together
toward the front at the same time, then return to the rest pose.
```

### Coup de queue (tail)
```
tail lash: the body turns away slightly to wind up, the tail swings low and fast around
the side and strikes toward the front (the direction the character faces in that row),
then the body turns back and the tail returns behind. The tail stays low near the
ground; it never loops above the head or around the body.
```

### Coup d'ailes (buffet)
```
wing buffet: both wings rise and open wide behind the character, then beat forward
together in one violent stroke toward the front, the body leaning forward, then the
wings fold back to the rest pose. Keep the wings inside the cell.
```

### Touché (hit)
```
hit recoil: the character is struck from the front: the head and torso jerk backwards,
the wings flinch, then he recovers to the rest pose.
```

### Mort (death)
```
death: he staggers, his knees bend and he collapses step by step until he lies still on
the ground; the last frame is lying on the ground, motionless. No loop.
```

## Correspondance avec le jeu

Une créature Infinity Engine a un emplacement par type d'animation, et quatre
emplacements d'attaque (A1 à A4).

| Fichier | Planche | Animation du jeu |
|---|---|---|
| `idle.png` | Repos | SD (debout), SC (en combat) |
| `walk.png` | Marche | WK |
| `cast.png` | Incantation | CA (pendant l'incantation) |
| `wings.png` | Ailes déployées | SP (lancement du sort) |
| `claw.png` | Griffe droite | A1 |
| `claw2.png` | Griffe double | A2 |
| `tail.png` | Coup de queue | A3 |
| `buffet.png` | Coup d'ailes | A4 |
| `hit.png` | Touché | GH |
| `death.png` | Mort | DE, puis TW/SL (au sol) et GU (relevé) |

## Vérifications avant conversion

- **Ordre des directions** : la ligne 3 regarde vers la droite de l'écran et la
  ligne 7 vers la gauche ; la ligne 1 fait face, la ligne 5 montre le dos.
- **Fond** : cyan uni partout, sans ombre portée ni sol.
- **Espacement** : aucun sprite ne touche son voisin. Ailes et queue dépassent
  parfois ; `build_avatar.py` sait couper entre deux sprites qui se touchent de
  côté, mais le bout d'aile est alors rogné.
- **Couleurs** : noir, vert foncé et bronze, comme la référence. Si ChatGPT
  éclaircit le corps, il faut régénérer ou faire recolorer à la conversion.
- **Première et dernière image** : la même pose de repos sur les attaques.
