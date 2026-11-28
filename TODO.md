# TODO

## To check in game (branch `restructure`)
Files now stored in the mod: **new character needed**. Installed without error on mock BG2:EE and IWD:EE games (English and French); not played yet.

Kit:
- [ ] Plain sorcerer: d6, one spell slot less per spell level.
- [ ] Spell list at level-up: the 7 transformations (levels 1, 1, 2, 3, 6, 7, 9), Black Dragon Breath: Line (2), Darkness (2); names, descriptions and icons in English and French.
- [ ] Only the kit is offered them: Black Dragon Disciple yes; plain sorcerer, Dragon Disciple and mage at creation no.
- [ ] Learning a transformation: effects at once (global script), no spell slot lost; not offered again; absent from the casting bar.
- [ ] Level markers at 10 and 15: Dragon Scale +1 AC at 10 and 15, Resilience +2 CON at 15; a transformation taken after these levels gives the steps at once.

Transformations:
- [ ] Claw & Bite: Extend / Retract Claws, 2 attacks, +1 to +5, bite 20% per hit (1d6 + 1d4 acid, combat log).
- [ ] Dragon Scale, Draconic Resilience (skull in the helmet slot, critical hits ignored), Apotheosis: values on the record sheet.
- [ ] Swamp Stride: poison, Grease, Entangle, Web, Stinking Cloud, Spike Growth (if the game has it).
- [ ] Blindsense: blindness immunity, invisible creatures seen.
- [ ] Dragon Wings: +4 movement, Wing Buffet at will, back after 4 rounds with its message — now in every game (was BG2:EE / EET only).

Spells:
- [ ] Black Dragon Breath: Line: no casting time, roar, 1-second pause, the two-layer line, allies hit, not the caster; 4d4 (level 4) to 8d4 (level 8); half again the next round on a failed save vs. Breath; magic resistance ignored.
- [ ] Orb: green orb, 2d4 to 5d4; shards on the enemies within 10 ft. of the target (not the target, not allies nor neutrals).
- [ ] Trap: the orb hovers where thrown, explodes when a creature comes close (about 9 ft.), 20 ft.; does it trigger on allies too?
- [ ] Ball: the orb travels slowly, explosion and black puffs at the point.
- [ ] Cone: cone, explosion, black puffs, pause, the disciple not hit.
- [ ] Cloud: the orb, then Cloudkill's green cloud for about 6 rounds, 4d4 per round (half on save).
- [ ] Rain: IWD:EE's Acid Storm as it is (rain, splash, sound), 1d4 each round for 14+ rounds, save vs. Breath for half, roar; only creatures there at the casting are hit.
- [ ] Eruption: explosion around the disciple, allies hit, not him; extra effect still to choose.
- [ ] Bolt: 20d4; failed save: 10d4 the next round, curses 15% each (poison, disease, insects, plants, fear, blindness), never on a successful save.
- [ ] Damage of every header (levels) and the casting times.
- [ ] Darkness: 15 ft., invisible and blinded 3 rounds, allies too.

HLA (BG2:EE, EET, IWD:EE):
- [ ] Extra spells of levels 6, 7, 8.
- [ ] Final Breath: picked once, wide line, enemies only, 30d4 (+15d4, curses 5%); back 6 rounds later with its message; back after a cancelled aim and after death.
- [ ] Call Draconic Ancestor: Nydra'Nath (animation, sounds, blur, greatsword procs plants / insects, rage, Wing Buffet, Ancestral Breath castable once by hand), not hit by the disciple's Line nor Darkness.

IWD:EE:
- [ ] The whole list above once in IWD:EE (kit, global script, spell choice filter, HLA table, Nydra'Nath).

## Next steps (see the Google Sheets workbook)
- Black Dragon Breaths: real icons; Eruption's extra effect; Final Breath's name. Orb: true bounces if a way is found.
- Transformations: 7 kept for 9 places; level 1 has two, levels 4, 5 and 8 are empty; no acid resistance left.
- Reserved spells: Darkness to improve (visuals, balance); Corrupt Water to review; Swampy Lake to make an HLA; Summon Reptile (hydra) to bring back.
- The former spells of the spells component: decide which become reserved to the kit (Solvent of Corrosion: restore from the archive if kept).
- Real icons for Darkness (placeholder: Rot of Ages' icons) and for the transformations.
- Test on EET (no install yet).

## Manifest Heritage (series of summoned spirits)

Fixed: the breaths' / Rain's protection of their caster pointed at NY#<file>
instead of the SPWIxyy name ADD_SPELL gives (tpa/global.tpa).

- [ ] In game: Summon Dracolisk (5), Summon Draco-Hydra (8), Summon Dragon Turtle (9)
      (tpa/heritage.tpa): the creatures appear at the point, fight, use their
      gaze / breath every 3 rounds, vanish at the end; the spell cannot be cast
      again while its creature is there (message).
- [ ] Spirits' names (the user's), and the other levels: Black Pseudo-Dragon
      (familiar, replaces Find Familiar), Kobold, Lizardfolk, Half-Dragon
      (Nydra'Nath, from the HLA), Black Wyvern (Wyvern Call, replaces it), Chimera.
- [ ] Hydra animation (Might and Magic VII) to improve; dracolisk: maybe a
      redrawn one (ChatGPT test, works/dracolisk).
- [ ] Real icons (placeholders: the creature's first frame).

## Acid colour (test)

- [ ] In game: fluorescent green acid instead of yellow (works/restructure/acid_fluo.py):
      Line, Orb, Ball, Cone, Eruption, Trap, Cloud, Rain. The yellow BAMs are kept
      in works/acid_yellow (and the game's SPBDIMSP / SPBDRAE2 / SPCLOUDK); to go
      back: copy them back into bam/ and point the PROs at the game's BAMs again.
      Running build_breaths.py again would also bring the yellow back.
