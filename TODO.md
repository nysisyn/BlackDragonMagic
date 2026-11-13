# TODO

## To check in game

### Black Dragon Disciple (Draconic Transformations, branch draconic-transformations)
Rebuilt from scratch: **new character needed**. Not tested in game yet; checked only by an install on a mock game (data of the generated files).

Kit:
- [ ] Plain sorcerer: d6, one spell slot less per spell level, no claws, no breath, no AC bonus at level 1.
- [ ] The 18 transformations in the spell list at level-up (levels 1 to 9), names, descriptions and amber icons in English and French.
- [ ] Learning one at level-up: its effects at once (global script), then it leaves the spellbook (opcode 172 on a sorcerer's known spell); no spell slot lost; another sorcerer learning it: nothing happens.
- [ ] Next level-up after a transformation: the engine must not give back the spell choice (it would make the transformations free).
- [ ] Level markers at 10 and 15 (global script): Dragon Scale +1 AC at 10 and 15, Resilience +2 CON at 15, Might +2 STR at 15; a transformation taken after these levels gives the steps at once; a character created at a high level (ToB) gets them right away.
- [ ] Transformations picked at character creation applied as soon as the game starts.

Transformations:
- [ ] Claw & Bite: Extend Claws given; claws in the first weapon slot and the shield slot, 2 attacks, no two-weapon penalty, +4 THAC0, bite 20% per hit (1d6 + 1d4 acid, combat log); Retract / Extend; stage of the level (+2 at 10...); a weapon already in the first slot: what happens to it.
- [ ] Dragon Scale, Draconic Resilience (skull in the helmet slot, critical hits ignored; a helmet already there?), Draconic Might, Apotheosis: values on the record sheet.
- [ ] Breath Weapon: line, 4d4 / 6d4 / 8d4, ignores magic resistance; gone after use, back 10 rounds later (+ about 8 seconds of choice); after a load during the recharge.
- [ ] Meta-breath: menu line / ball / pool, shared charge, recharges 6 / 10 / 8; taken without Breath Weapon: the menu anyway.
- [ ] Breath Mastery: dice doubled, recharges 2 rounds shorter; Acid Mastery: AC -2 for 2 rounds on the breath targets, not cumulative.
- [ ] Draconic Tail: one strike per round, 2d6 + 1 second prone on a failed save vs. Breath.
- [ ] Swamp Stride: poison, Grease, Entangle, Web, Stinking Cloud, Spike Growth.
- [ ] Acidosis: 50% acid resistance, +20% acid damage, 1d2 acid to attackers below 50% health only.
- [ ] Black Dragon Magic / Greater / Mastery: the spells really learned by a sorcerer (opcode 147) and castable with the slots of their level.
- [ ] Blindsense: vision range bonus (opcode 262, +2): visible?
- [ ] Dragon Wings: +4 movement, Wing Buffet at will with a 4-round recharge (BG2EE/EET).
- [ ] Draconic Majesty: CHA, INT, Lore; Charm Reptile 3 per day, no save, magic resistance ignored, dragons and non-reptiles unaffected.
- [ ] Frightful Presence: 10 ft., enemies of lower level only, 24 hours of immunity after the test.
- [ ] Darkness, Corrupt Water (potions destroyed, poison), Summon Reptile (hydra), Swampy Lake.
- [ ] HLA (BG2EE/EET): Breath Doom, Call Ancestor (no Planetar left), Bonemelt (skeletons destroyed), Black Dragon Magic Mastery.

### Acidosis
- [x] Icons, casting, self damage OK.
- [ ] Acid splash on the attacker plays once per retaliation, not again each time the attacker takes damage (opcode 215 timing 0 instead of permanent; same fix for the breath, claws procs and Rot of Ages visuals).
- [ ] Acid burst on the caster when cast; acid splash on the attacker when the retaliation fires; green drop portrait icon for the duration, tooltip "Acidosis"; new spell icons (Nysi's acid drop artwork) in the spellbook and the quick spell bar.
- [ ] At low level 15% of current HP rounds down to 0 (5 HP -> 0): check the self damage at levels 1 and 5.
- [ ] Opcode 12 "Reduce by Percentage" works on **current** HP, not max HP.
- [x] Retaliation fires (damage and splash OK).
- [x] Retaliation reach widened (NY#MELEE, about 12 ft.): a bastard sword wielder triggers it.

### Rot of Ages
- [x] Spell works in game.
- [x] Combat log lines: "Blinded by Rot of Ages", "Diseased by Rot of Ages" (failed save only), "Nauseated by Rot of Ages".
- [ ] Touch range: the caster walks to the target; magic resistance blocks the whole spell.
- [ ] Blind 1 round without save; disease only on a failed save vs. Death: 1 poison damage per round, 1 round per level (max 10), "Diseased" icon.
- [ ] Second casting on a diseased target that fails again: diseases stack and nausea 2 rounds (unconscious, "Nauseated" icon). Check that SPLPROT stat 0x112 (spell state) works with relation 1 (= state set).
- [ ] A target that saved the first time is not nauseated by the second casting.
- [ ] New icons (rotting cloud artwork) in the spellbook and the quick spell bar.

### Ghostly Tail
- [x] Cold damage, no save; casting time 1; duration 1 round per level.
- [ ] Reach widened (NY#MELEE, about 12 ft.); portrait icon during the spell.
- [ ] One strike per round on the nearest enemy in melee reach (spectral splash); nothing when no enemy is that close; allies never hit.
- [ ] Casting again replaces the tail (one strike per round, one portrait icon); no casting glow or text each round.
- [ ] Only one creature hit per strike: an ally next to the targeted enemy is never hit.
- [ ] Enemy AI casting the spell: NearestEnemyOf is only reliable from the party's side.

### Mantidrake Spike
- [ ] One spike per level in a quick slot; thrown as darts (projectile), up to 3 per round, +5 to hit, hits creatures needing +2 weapons.
- [ ] 1d4 piercing; poison 2d4 only on a failed save vs. Death at -2, poison visual on the same roll.
- [ ] New icons (spikes artwork) for the spell and the spikes item; spikes disappear when used up; behaviour after rest / reload as Melf's Minute Meteors.

### Corrosive Spit (only the animated breath's spit now)
- [ ] Acid arrow projectile, range half that of Melf's Acid Arrow; 5d4 acid on impact, magic resistance blocks it.
- [ ] Failed save vs. Spell: blinded for 1 round and 5d4 acid at the next round, combat log line; nothing more on a successful save.

### Summon Black Mantidrake
- [ ] Install on BG:EE and BG2:EE: the .DEBUG prints the animation id; the spell is learnable at level 5.
- [ ] 8 directions (no mirroring), idle, walk, pounce attack, stagger, death; panther sounds (on BG:EE too?).
- [ ] Spikes: one dart flies to each enemy in reach (up to ten, chained forced casts with Continue()), only while no enemy is in melee reach, once every 2 rounds; acid splash on each; melee otherwise; not while disabled.
- [ ] Walks through Entangle and Web; immune to acid.

### Summon Gorgon
- [ ] Install on BG:EE and BG2:EE: the .DEBUG prints the animation id; the spell is learnable at level 5.
- [ ] Dark iron bull, 8 directions, idle breathing, pawing in combat stance, walk, gore attacks, death; sounds (basilisk for now: a bull would fit better).
- [ ] Petrifying breath once per summoning: 30-ft. cone, enemies only, held 2 rounds on a failed save vs. Petrification, stone shards; not while disabled.
- [ ] Stays an ally (no WTASIGHT); 1 round per level.

### Summon Dracockatrix
- [ ] Install on BG:EE and BG2:EE: the .DEBUG prints the animation id; the spell is learnable at level 2.
- [ ] Small black creature (half the thunder lizard), 8 directions, idle breathing, frill display in combat stance, run, attacks, death; basilisk sounds.
- [ ] Bite: 1d4 + 1d4 acid, slowed 2 rounds on a failed save vs. Polymorph; stays an ally (no WTASIGHT).
- [ ] JPEG source: check the edges for cyan fringes (a PNG of the sheet would be cleaner).

### Wyvern Barbed Tail Strike
- [ ] Melee range (range 1), casting time 0; 1d12 piercing and blood splash; magic resistance blocks it.
- [ ] Failed save vs. Poison at -2: immediate damage + 1 every N seconds for 1 turn by level (5th: 4 / 4 s, 7th: 8 / 3 s, 9th: 12 / 2 s, 12th: 16 / 1 s), "Poisoned" icon, combat log line; cured by Neutralize Poison.
- [ ] New icons (barbed tail artwork).

### Black Dragon Breathball
- [ ] Travelling green acid arrow, black dragon breath explosion at the impact, no leftover fire visual (VVC, flame ring).
- [ ] 20 ft. area as Fireball, allies hit; 3d8 at 5th level up to 8d8 at 18th; save vs. Breath halves.
- [ ] Icons readable at 32 px (placeholder: Fireball in acid yellow).

### Stunning Black Dragon Breath
- [ ] Same line, wave, trail, splash and sound as the kit's breath; caster not hit; damage 3d8 to 8d8 by level, save vs. Breath for half.
- [ ] Visuals identical to the kit's breath: no explosion on the creatures hit.
- [ ] Failed save: stunned 2 rounds. Check that a creature taking half damage (save made) is never stunned: if it is, the engine rolls the two saves separately and the stun must move to a subspell sharing the damage roll.

### Black Dragon Pooling Breath
- [ ] Acid puddles on the ground (Grease's recoloured acid green, as the cloud's spread animation), no cloud, no grey grease; lasts 1 turn like Stinking Cloud.
- [ ] Range of the kit's breath (9 m), pool half the size of Stinking Cloud's; 2d6 acid about once per round to everyone in the pool, save vs. Breath for half; allies hit, caster not hit.
- [ ] Caster stunned 2 seconds after breathing, and only once (not again at each pulse of the pool).
- [ ] Icon: Free Action's waves recoloured acid yellow.

### Black Dragon Animate Breath
- [ ] No spit / breath while the creature is asleep, unconscious, stunned, held, panicked or confused (state check before the forced cast).
- [ ] Ooze summoned at the target point, allied, fights on its own; disappears after 1 round per level (14 rounds at least).
- [ ] Attack: 2 per round, 2d8 acid each, no physical damage line; immune to acid.
- [ ] Spits Corrosive Spit once per round while no enemy is in melee reach, without casting animation; melee otherwise; the spit's blindness and second hit work from the creature.
- [ ] Stays on the party's side when caught in the caster's spells (CONTROLLED, as the summoned genies); can be selected and ordered.
- [ ] Animation SLIME_OLIVE shows (green ooze), the spit casts with the slime animation; balance of 65 HP / AC 4 / THAC0 11 against the summoned Djinni and Efreeti.

### Bonemelt
- [ ] Casting opens a menu with the three choices (Legs / Arms / Ribcage, names and icons); the chosen one then asks for a target and hits it (8d8 acid, save vs. Death at -2).
- [ ] The "successful save" subspell (delayed 1 second) is blocked when the save failed.

### Manifest Heritage: Chimera (branch chimera)
- [ ] No spit / breath while the creature is asleep, unconscious, stunned, held, panicked or confused (state check before the forced cast).
- [ ] Install (BG2:EE): the .DEBUG shows the animation id used (0xEC33 or another) and no error.
- [ ] The chimera appears with the IWD2 animation (walk, attacks, death), right size and selection circle; sounds right (battle cry, attacks, breath, damage, death).
- [ ] 110 HP, AC 2, THAC0 7, 3 attacks per round, 2d6+3, hits creatures needing +3 weapons; immune to fear; 75% acid resistance.
- [ ] Acid breath: 3 times per summoning, at most every 3 rounds, at the nearest enemy; line 30 x 10 ft., 6d8 acid, save vs. Breath for half; the chimera not hurt by its own breath.
- [ ] Controlled by the player (allegiance), stays an ally when hit by the party's area spells; disappears after 1 turn + 1 round per level.
- [ ] Icon (placeholder: wyvern head in acid yellow).

### Vitriolic Sphere
- [ ] Impact and delayed damage share the same saving throw; otherwise move the delayed damage to a subspell applied only on a failed save.
- [ ] Green explosion colour: set `ny_vs_color` in `tweaks/vitriolic_sphere/vitriolic_sphere.tpa` (palette index to find in Near Infinity).

### Test: hydra animation (component 900)
- [ ] No spit / breath while the creature is asleep, unconscious, stunned, held, panicked or confused (state check before the forced cast).
- [ ] Install: the .DEBUG prints the animation id; `CLUAConsole:CreateCreature("NY#HYDR")` creates the hydra.
- [ ] Stand, walk, attacks, hit, death, corpse: frames in order, no jitter, feet on the ground, selection circle centred, shadow.
- [ ] Might and Magic VII version: the 8 directions (front, 3/4, profile, back), slate grey everywhere (no green left), death seen from the front whatever the direction.
- [ ] Summon Hydra (wizard level 9): learnable, summons an allied hydra for 1 turn + 1 round per level, controllable, 4 attacks per round, 160 HP, regenerates 1 HP per second (portrait icon); balance against the other level 9 summons; placeholder icon.
- [ ] Hydra's Corrosive Spit: acid blob projectile, only out of melee reach, once per round at most, 5d4 acid then blindness + 5d4 on a failed save; melee otherwise.

## Later
- [ ] Custom icons (BAM) for the claws, breath, aura, wing buffet and spells.
- [ ] Trello *Ideas* list: Swamp Lung, Ghostly Tail, Corrosive Spit, Dracosuchus Jaws, Tail Sweep.
- [ ] Draconic Transformations, own spell list: a G3 library giving the kit its own spell list, so the other sorcerers no longer see the transformations (they already do nothing for them).
- [ ] Draconic Transformations, icons: the amber placeholders replaced by real icons (one shape per transformation).
- [ ] Breath recharge lost if the disciple dies while it recharges (the delayed opcode 146 dies with him): give it back at rest or on resurrection.
- [ ] Acid Mastery: AC reduction only on the breaths; the bite (cast by an item) and the game's acid spells (Melf's Acid Arrow, Vitriolic Sphere...) would need a check of the caster.
- [ ] Corrupt Water: the rain (visual) and grey-blue water instead of the recoloured acid puddles.
- [ ] Call Ancestor: a real Half Black Dragon Spirit (Icewind Dale's MDH1 half-dragon animation) instead of the renamed planetar.
- [ ] Darkness: a darkness visual.
