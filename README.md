# BlackDragonMagic

WeiDU mod for the Enhanced Edition games (BG:EE with SoD, BG2:EE, EET, IWD:EE): the **Black Dragon Disciple** sorcerer kit, its Draconic Transformations, its breath spells and the spells reserved to it.

Branch `restructure`: the mod rebuilt around the kit only, step by step. The former content (spells for every mage, the 18 transformations, the innate breath and its forms, other HLA) is still in the branches `draconic-transformations` and `main`.

Design notes and choices still open: Google Sheets workbook "Black Dragon Magic" (tabs *Sorts de souffle*, *Transformations draconiques*, *Passifs*, *Sorts exclusifs*, *HLA*).

## Installation

One component, **Black Dragon Disciple (sorcerer kit), its Draconic Transformations and its spells**. Games: BG:EE (and SoD), BG2:EE, EET, IWD:EE. The high-level abilities and the creature they call are only installed where the game has HLA tables (BG2:EE, EET, IWD:EE).

**Remastered Spell Icons** (Renegade0): install it **before** this mod. Its spell icons have no stone plate; when it is detected, the mod's ability / memorised icons (B, on a stone plate) are replaced by its spellbook icons (C, no plate) at install time, so they match.

## Content

| Part | Content |
|---|---|
| Kit | Black Dragon Disciple (`NY#BDD`): a plain sorcerer, d6 hit die, one spell slot less per spell level |
| Draconic Transformations | Claw & Bite (1), Dragon Scale (1), Draconic Resilience (2), Swamp Stride (3), Blindsense (6), Dragon Wings (7), Dragon Apotheosis (9): wizard spells `WIZARD_NY_T_<CODE>` learned instead of a spell; level steps at 10 and 15 |
| Black Dragon Breaths | Orb (1), Line (2), Trap (3), Ball (4), Cone (5), Cloud (6), Rain (7), Eruption (8), Bolt (9): `WIZARD_NY_BREATH_<FORM>` |
| Reserved spells | Darkness (level 2, `WIZARD_NY_DARKNESS`) |
| HLA | the sorcerer's extra spells of levels 6, 7 and 8; Call Draconic Ancestor (Nydra'Nath, the Half Black Dragon Spirit); Final Breath (name provisional) |

Only the Black Dragon Disciple is offered the transformations, breaths and reserved spells when choosing spells (character creation, level-up).

## Folder layout

```
BlackDragonMagic/
├── BlackDragonMagic.tp2      the component: includes the tpa/ files in order
├── tpa/
│   ├── kit.tpa               placeholders, copy of the stored files, kit registration
│   ├── transformations.tpa   names, Swamp Stride immunities, ADD_SPELL
│   ├── breath.tpa            breath spells
│   ├── spells.tpa            reserved spells
│   ├── creatures.tpa         Nydra'Nath (animation, script, names)
│   ├── hla.tpa               high-level abilities, LUNYB.2DA
│   └── global.tpa            global script, spell choice filter (Lua)
├── lib/
│   ├── ny#core.tpa           own WeiDU functions (placeholders, spell states, SPLPROT rows, animations)
│   └── a7#add_kit_ex.tpa     ADD_KIT_EX by Argent77 (public domain)
├── lang/english, lang/french one .tra per tpa file (+ setup.tra)
├── spl/ itm/ cre/ eff/ pro/ vvc/ bam/ wav/
│                             the mod's resources, copied as they are
├── 2da/                      CLAB (clny#bdd.2da), HLA table (lunyb.2da)
├── baf/                      scripts compiled at install
├── ini/                      creature animation
├── lua/                      M_NY#BD.LUA (spell choice filter)
└── works/                    sources (icon artworks, BAM generation scripts, archives), not installed
```

## How the resources are made

The mod's spells, items, creatures, projectiles and visual effects are **stored in the mod** and copied at install: they can be edited directly in Near Infinity. They do not copy nor patch the game's own files, so they are the same in every game.

Only what depends on the game and on the mods installed before is written at install:

- names and descriptions (`SAY`, from the `.tra` files): stored files have `-1`;
- the numbers of the spells added to the wizard spell list (`ADD_SPELL`: `SPWIxxx`), the kit id, the global script and the Lua filter;
- the creature animation id (first free one from `0xEC40`);
- **placeholders** in the stored SPL and ITM, replaced by `NY#PLACEHOLDERS` (`lib/ny#core.tpa`):

| In the stored file | Meaning | List (tpa/kit.tpa) |
|---|---|---|
| opcode 328, parameter 2 = `1000 + n` | spell state n | 0 CLB, 1 SCL, 2 RES, 3 SWS, 4 BLS, 5 WNG, 6 APO, 7 LV10, 8 LV15, 9 FIN, 10 FINCD |
| opcodes 318 / 324 / 326, parameter 2 = `2000 + n` | SPLPROT row "has spell state n"; from 20, other rows | same list; 20 = not an enemy of the party (EA < 200) |
| extended header projectile = `3000 + n` | projectile n | 0 `NY#SDRKP`, 1 `NY#BLIL`, 2 `NY#CNYDL`, 3 `INAREANP` (game), 4 `NY#BORB`, 5 `NY#BORBS`, 6 `NY#BTRP`, 7 `NY#BBAL`, 8 `NY#BBALK`, 9 `NY#BCON`, 10 `NY#BCONK`, 11 `NY#BCLD`, 12 `NY#BRAI`, 13 `NY#BERU`, 14 `NY#BBOL`, 15 `NY#HFIN` |

To add a dynamic value, add it to these lists and use its placeholder in Near Infinity.

`works/restructure/` keeps the scripts that built the stored files once: `extract.py` (the files generated by the former code: resrefs renamed, placeholders), `build_breaths.py` (the breath spells and Final Breath).

## Resource names

| Prefix | Family | Examples |
|---|---|---|
| `NY#K` | kit and passives | `NY#KL01` (spell slots), `NY#KM10` / `NY#KM15` (level markers), `NY#KSC10`, `NY#KRE15` (level steps) |
| `NY#T` | transformations | `NY#TCLB` (spell), `NY#TCLBE` (its effects), `NY#TCLBB` / `C` (icons), claws `NY#TCW1`…, Wing Buffet `NY#TWBF` |
| `NY#B` | breath spells | `NY#BLIN` Line, `NY#BORB` Orb, `NY#BTRP` Trap, `NY#BBAL` Ball, `NY#BCON` Cone, `NY#BCLD` Cloud, `NY#BRAI` Rain, `NY#BERU` Eruption, `NY#BBOL` Bolt (same name for spell, projectile and icons B / C); `NY#BLIK` / `NY#BLIG` (the line's two animation layers), `NY#BROAR` (roar), `NY#BCUR1-6` (curses) |
| `NY#S` | reserved spells | `NY#SDRK` (Darkness), `NY#SDRKP` (its projectile) |
| `NY#H` | HLA | `NY#HANC` (Call Draconic Ancestor), `NY#HANCE` (its EFF), `NY#HFIN` (Final Breath) |
| `NY#C` | creatures | `NY#CNYD` (Nydra'Nath), `NY#CNYDW` (its sword), `NY#CNYDB` (its breath), `NY#CNYDS` (its script) |

Spell icons: `B` = ability / memorised icon (stone plate), `C` = spellbook icon.

## Conventions

- **Lowercase file names** everywhere (WeiDU is case-sensitive on Linux/macOS).
- **Resource prefix `NY#`**, max 8 characters per resource name.
- **No inline text**: every string goes in a `.tra` file so it can be translated. English is always loaded first, so a missing translation falls back to English.
- **No dead code in active files**: unfinished parts are listed in `TODO.md`.

## Design choices

- **Draconic Transformations**: everything draconic that is not a breath is a wizard spell of levels 1 to 9 learned instead of a spell. As soon as it is in the spellbook, the global script makes the disciple apply its effects (`NY#T<code>E`) to himself: its spell state and permanent effects (timing 9: through death, not dispellable). No spell slot is lost. It stays in the spellbook; its ability has no location, so it cannot be cast and is not offered again. A second application does nothing (opcode 324); only the script checks the kit (`Kit()`): the KIT stat in SPLPROT.2DA did not work in game, nor a spell state set by the CLAB at level 1 for a character created at a high level.
- **Spell choice filter**: `M_NY#BD.LUA` (loaded by the game, `M_` prefix) removes the kit's spells from the spell choice list (character creation and level-up) unless the character is a Black Dragon Disciple, told by the kit name (compared with the kit's strrefs at run time, whatever the language). Called from `UI.MENU` (`CHARGEN_CHOOSE_SPELLS`, one line added before the list is sorted). If an interface mod has no such line or replaces `UI.MENU` afterwards, nothing is hidden. Technique from OlvynChuru's ClassSpellTool (rows removed from `chargen.choose_spell`).
- **Level steps**: level markers (spell states) set by the global script at levels 10 and 15 apply the steps of the transformations already taken; a transformation taken later applies the steps of the markers already set. Not through the CLAB: a character created at a high level did not get its level 1 CLAB spell before his next level-up.
- **Black Dragon Breaths**: wizard spells reserved to the kit; they ignore magic resistance; impact 1d4 per caster level (capped by the spell level), no save; half the impact again the next round on a failed save vs. Breath (Cloud: a zone that lasts, save vs. Breath for half each round instead; Rain: IWD:EE's Acid Storm as it is, save vs. Spell for half each round, ignoring magic resistance). The Line is the basic breath (no casting time); the other forms have a casting time.
- **Orb's bounces**: the engine's bouncing is tied to Chain Lightning's own projectile (blue lightning, number of jumps fixed). The Orb bursts instead into shards hitting every enemy within 10 ft. of the creature hit (1d4 less), not a number of jumps by level.
- **Independent curses (Bolt, Final Breath)**: each curse is rolled by its own spell (NY#BBOR / NY#HFIR), so the rolls are independent; effects of one spell may share a single roll.
- **Claws**: the transformation only gives Extend Claws; extended by hand, with the stage of the disciple's level (extend them again after a level-up). Main claw in the magical weapon slot (opcode 111), off-hand claw in the shield slot (one more attack per round, Two-Weapon Style 3 points while equipped: no penalty). Retract Claws frees the hands.
- **Hostile flag (SPL flag 0x400)**: only on spells hitting other creatures. The spells a disciple applies to himself must not carry it: applied every script pass, a hostile spell kept the party in combat.
- **Visual effects (opcode 215)**: timing 0 with a short duration; with timing 1 the engine replays the animation each time the creature's effects are re-evaluated.
- **Wing Buffet, Nydra'Nath**: built once from the game's black dragon Wing Buffet (SPIN695), Summon Planetar (SPWI924, PLANEVIL) and the black dragon of Suldanessellar's powers (SPIN688, SPIN689), now stored: they work in games that lack those files (BG:EE, IWD:EE).
- **Icon colours**: acid spells and abilities are acid yellow (hue 62), the kit's natural weapons (claws, bite, wings) black dragon scales.

## Credits

- Nysi: design, artworks (icons, Nydra'Nath's animation conversion).
- Argent77: ADD_KIT_EX (public domain).
- OlvynChuru: the spell list technique of ClassSpellTool.
- Nydra'Nath's animation: the half black dragon of Icewind Dale II; sounds: the half-dragon's of Siege of Dragonspear.
