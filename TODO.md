# TODO

## To check in game

### Black Dragon Disciple
New level-by-level version: **new character needed** (the CLAB gives everything when the level is reached).

Still valid from the previous version (same code):
- [x] Claws replace the fists; back after a load (global script); back after Polymorph Self / Shapechange.
- [x] Level up while unarmed: 2 attacks per round right away (fist reselected once per stage).
- [x] Acid Breath: the wave starts on the disciple, goes straight to the targeted point; creatures crossed are hit; visual and sound OK.
- [x] Bite in the off hand (branch bite): it attacks ("Attack Roll (Off-hand)"), 3 attacks per round, acid damage in the combat log.

To check:
- [x] **No weapon (opcode 319)**: every weapon shown in red and refused for the kit, but still usable by the other characters. If it is the other way round (usable *only* by the kit), the parameter meaning is inverted: tell Claude.
- [x] **Proficiencies**: at creation and at levels 7, 13 and 19, only Single Weapon Style (max 1) and Two-Weapon Style (max 3) can be raised.
- [x] **Spells one level lower**: 2nd-level spell slots at level 5 (not 4), 3rd-level at 7 (not 6)... and one slot less per spell level. At level 4 the disciple may pick a 2nd-level spell he cannot cast yet (spells known are not delayed).
- [x] Claws at levels 1, 4, 8, 12, 16, 20: 1d4, 1d6+1, 1d8+2, 1d10+3, 2d6+4, 2d8+5; old claws gone; still there after a load.
- [x] Bite from level 6 (1d6+1 + 2 acid), replaced at 8, 12, 13 (2d6 + 2d4 acid), 16, 20; the old one gone, even if it was in the backpack.
- [x] Bite: two-weapon penalties lowered by Two-Weapon Style (THAC0 3 / 7 at level 16 with 2 points).
- [x] Bite toggle: Fight without / with the Bite remove and put back the bite of the current stage; the abilities swap.
- [x] Bite: the claws' retry script (fewer than 2 attacks) does not fire for nothing while the bite is equipped.
- [x] Claws icon on the weapon button, and Blindsense (attacks invisible enemies), bite toggle, icons: checked.
- [x] **Claws in both weapon slots** (new character): both weapon buttons show the claws, 2 attacks per round with either slot, still there after a load; new claws at 4/8/12/16/20 replace both copies. The starting weapons go to the backpack (cannot be used by the kit).
- [x] New icons in game: breath, claws, bite (large), wings, Frightful Presence.
- [x] Portrait icons: Frightful Presence while the aura is on (gone when dismissed), bite while it is out, wings while spread. Wings: +2 AC.
- [x] Swamp Stride at level 2: immunity to Entangle, Grease, Web.
- [x] Acid Breath: 15 ft. long and about 5 ft. wide, 4d4; 2/day at 7, 3/day at 11, 4/day at 17 (several GA_ of the same ability in the CLAB); 30 ft. and 10 ft. wide at 19.
- [x] Draconic Tail at level 9: one strike per round on the nearest enemy in melee reach, 1d10 crushing + 1 second unconscious on a failed save vs. Breath; combat log line. One save for both effects?
- [x] Draconic Wings at level 14: equipped in the helmet slot, bonuses applied. Still to check: the wings shown on the character, a helmet already there, after a load.
- [x] Acid Affinity damage bonus (opcode 332, type acid, as the Robe of Red Flames): bite acid 4 → 5 at level 20 (+25%), shown in the combat log as "(1 damage bonus)".
- [x] Blindsense at level 10: immunity to blindness, invisible creatures seen and targetable.
- [x] Frightful Presence at level 18: no longer hits the disciple and his allies (projectile flag 0x40, enemies only).
- [x] Apotheosis at level 20: immunity to sleep and paralysis, acid immunity (5 × 20%).
- [x] Druid THAC0: 18 at level 4, 16 at 7, 14 at 10, 12 at 13 (before Strength and weapon bonuses).
- [x] Frightful Presence: the pulse (opcode 272 -> EFF) really fires and uses the disciple's level.
- [x] Start of Throne of Bhaal (cutscenes): claws and bite kept.

Not done yet:
- [ ] Wing Buffet removed from the kit (code in the branch folder `Branches\bite`, not in this repository's history): maybe a future HLA.

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

### Wyvern Barbed Tail Strike
- [ ] Melee range (range 1), casting time 0; 1d12 piercing and blood splash; magic resistance blocks it.
- [ ] Failed save vs. Poison at -2: immediate damage + 1 every N seconds for 1 turn by level (5th: 4 / 4 s, 7th: 8 / 3 s, 9th: 12 / 2 s, 12th: 16 / 1 s), "Poisoned" icon, combat log line; cured by Neutralize Poison.
- [ ] New icons (barbed tail artwork).

### Black Dragon Breathball
- [ ] Travelling green acid arrow, black dragon breath explosion at the impact, no leftover fire visual (VVC, flame ring).
- [ ] 20 ft. area as Fireball, allies hit; 3d8 at 5th level up to 8d8 at 18th; save vs. Breath halves.
- [ ] Icons readable at 32 px.

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
- [ ] Ooze summoned at the target point, allied, fights on its own; disappears after 1 round per level (14 rounds at least).
- [ ] Attack: 2 per round, 2d8 acid each, no physical damage line; immune to acid.
- [ ] Spits Corrosive Spit once per round while no enemy is in melee reach, without casting animation; melee otherwise; the spit's blindness and second hit work from the creature.
- [ ] Stays on the party's side when caught in the caster's spells (CONTROLLED, as the summoned genies); can be selected and ordered.
- [ ] Animation SLIME_OLIVE shows (green ooze), the spit casts with the slime animation; balance of 65 HP / AC 4 / THAC0 11 against the summoned Djinni and Efreeti.

### Bonemelt
- [ ] The "successful save" subspell (delayed 1 second) is blocked when the save failed.

### Vitriolic Sphere
- [ ] Impact and delayed damage share the same saving throw; otherwise move the delayed damage to a subspell applied only on a failed save.
- [ ] Green explosion colour: set `ny_vs_color` in `tweaks/vitriolic_sphere/vitriolic_sphere.tpa` (palette index to find in Near Infinity).

## Later
- [ ] Unique Black Dragon Disciple HLA (currently the Dragon Disciple ones).
- [ ] Custom icons (BAM) for the claws, breath, aura, wing buffet and spells.
- [ ] Trello *Ideas* list: Swamp Lung, Ghostly Tail, Corrosive Spit, Dracosuchus Jaws, Tail Sweep.
