"""Builds the Black Dragon Breaths (Orb, Trap, Ball, Cone, Cloud, Rain,
Eruption, Bolt), their curses and the HLA Final Breath into the mod's
folders, from:
  - the mod's own Black Dragon Breath: Line (spl/ny#blin.spl), template;
  - the projectiles and BAMs the former code generated (an install of the
    branch draconic-transformations, OLD below);
  - a few game projectiles (GAME below), copied once.
Placeholders as in lib/ny#core.tpa (projectile 3000 + n, spell state 1000 +
n, SPLPROT row 2000 + n); n as in tpa/kit.tpa.
Run once; the results are then edited in Near Infinity.
"""
import os, shutil, struct, sys, zlib
sys.path.insert(0, os.path.dirname(__file__))
from iemodel import *

MOD = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/blackdragonmagic'
OLD = sys.argv[2] if len(sys.argv) > 2 else '/home/claude/bg2old/override'
GAME = sys.argv[3] if len(sys.argv) > 3 else '/tmp/ex'

PRO = {'NY#BORB': 4, 'NY#BORBS': 5, 'NY#BTRP': 6, 'NY#BBAL': 7, 'NY#BBALK': 8, 'NY#BCON': 9, 'NY#BCONK': 10,
       'NY#BCLD': 11, 'NY#BRAI': 12, 'NY#BERU': 13, 'NY#BBOL': 14, 'NY#HFIN': 15}
ST_FIN, ST_FINCD = 9, 10          # spell states: Final Breath taken / recharging
ROW_NOT_ENEMY = 20                # SPLPROT row: EA < 200 (not an enemy of the party)
ACID = 0x10000
ROUND = 6

def ph(name): return 3000 + PRO[name]

# ---------------------------------------------------------------- projectiles
def w8(b, o, s): b[o:o+8] = s.encode().ljust(8, b'\0')[:8]
def pro_from(src, dst, **kw):
    b = bytearray(open(src, 'rb').read())
    for k, v in kw.items():
        o, kind = {'speed': (0x0a, 'H'), 'flags': (0x0c, 'I'), 'snd1': (0x10, 's'), 'snd2': (0x18, 's'),
                   'bam': (0x104, 's'), 'shadow': (0x10c, 's'),
                   'aflags': (0x200, 'I'), 'size': (0x204, 'S'), 'asnd': (0x208, 's'), 'freq': (0x210, 'H'),
                   'rep': (0x216, 'B'), 'exeff': (0x217, 'B'), 'col': (0x218, 'B'),
                   'expl': (0x21c, 's'), 'cone': (0x224, 'H'), 'spread': (0x228, 's'), 'ring': (0x230, 's'),
                   'asnd2': (0x238, 's'), 'ext': (0x240, 'I')}[k]
        if kind == 's': w8(b, o, v)
        elif kind == 'S': struct.pack_into('<HH', b, o, *(v if isinstance(v, tuple) else (v, v)))
        elif kind == 'B': b[o] = v
        else: struct.pack_into('<' + kind, b, o, v)
    open(f'{MOD}/pro/{dst.lower()}.pro', 'wb').write(b)

FT = 12.8   # pixels per foot (FIREBALL.PRO: 256 = 20 ft.)
# Orb: a green orb thrown at one creature (the breath ball's orb NY#PBRT)
pro_from(f'{GAME}/arrowflg.pro', 'NY#BORB', bam='NY#BORBT', speed=40, snd1='TRA_06', snd2='EFF_M21')
# Orb, the shards: 10-ft. burst on the creature hit, the breaths' explosion, smaller
pro_from(f'{OLD}/ny#tbpx.pro', 'NY#BORBS', size=int(10 * FT), bam='', snd1='', snd2='')
# Trap: Skull Trap's trap (trigger ~9 ft., area 20 ft.), the orb instead of
# the skull, exploding as the breaths' explosion (fields 0x208-0x24f of the
# breath ball's projectile)
pro_from(f'{GAME}/trapskul.pro', 'NY#BTRP', bam='NY#BORBT', shadow='', size=(150, int(20 * FT)))
b = bytearray(open(f'{MOD}/pro/ny#btrp.pro', 'rb').read()); x = open(f'{OLD}/ny#tbpx.pro', 'rb').read()
b[0x208:0x250] = x[0x208:0x250]
open(f'{MOD}/pro/ny#btrp.pro', 'wb').write(b)
# Ball: the breath ball (orb, then the black dragon breath explosion), the orb
# travels slowly (Vitriolic Sphere); its black puffs: a second projectile
pro_from(f'{OLD}/ny#tbbp.pro', 'NY#BBAL', speed=15, bam='NY#BORBT')
pro_from(f'{OLD}/ny#tbkb.pro', 'NY#BBALK', speed=15)
# Cone: the Dragon Disciple's cone with the explosion; its black puffs
pro_from(f'{OLD}/ny#bdbrt.pro', 'NY#BCON')
pro_from(f'{OLD}/ny#tbkc.pro', 'NY#BCONK')
# Cloud: Cloudkill's green cloud for 6 pulses, about one per round; the orb
# travels to the point
pro_from(f'{GAME}/cloudkil.pro', 'NY#BCLD', bam='NY#BORBT', rep=6, freq=90)
# Rain: IWD:EE's Acid Storm, copied as it is by rain_from_iwd.py
# Eruption: the breaths' explosion, 20 ft. around the caster
pro_from(f'{OLD}/ny#tbpx.pro', 'NY#BERU', size=int(20 * FT), bam='', snd1='', snd2='', speed=40)
# Bolt: Melf's Acid Arrow's projectile
pro_from(f'{GAME}/arrowflg.pro', 'NY#BBOL')
# Final Breath: the Line's invisible line, twice as wide
b = bytearray(open(f'{MOD}/pro/ny#blil.pro', 'rb').read())
struct.pack_into('<H', b, 0x2a, 2 * struct.unpack_from('<H', b, 0x2a)[0])    # proximity radius (width)
open(f'{MOD}/pro/ny#hfin.pro', 'wb').write(b)

# ---------------------------------------------------------------- BAMs
def bam_palette_recolour(src, dst, fn):
    d = open(src, 'rb').read()
    if d[:4] == b'BAMC':
        d = zlib.decompress(d[12:])
    d = bytearray(d)
    po = struct.unpack_from('<I', d, 0x10)[0]
    for i in range(1, 256):
        bb, g, r, a = d[po + i * 4:po + i * 4 + 4]
        r, g, bb = fn(r, g, bb)
        d[po + i * 4:po + i * 4 + 3] = bytes((bb, g, r))
    raw = bytes(d)
    open(dst, 'wb').write(b'BAMCV1  ' + struct.pack('<I', len(raw)) + zlib.compress(raw, 9))
def acid(r, g, b):            # grey -> acid green, by luminance
    L = (r + g + b) / 3
    return int(min(255, L * 0.75)), int(min(255, L * 1.05)), int(min(255, L * 0.2))
shutil.copy(f'{OLD}/ny#pbrt.bam', f'{MOD}/bam/ny#borbt.bam')
shutil.copy(f'{OLD}/ny#bdbs.bam', f'{MOD}/bam/ny#bdbs.bam')
# icons: placeholders, the former breath icons
for new, old in {'NY#BORB': 'ny#bdbb', 'NY#BTRP': 'ny#pbr', 'NY#BBAL': 'ny#bdbl', 'NY#BCON': 'ny#tbrw',
                 'NY#BCLD': 'ny#tmbr', 'NY#BERU': 'ny#tbms', 'NY#BBOL': 'ny#sbb',
                 'NY#HFIN': 'ny#bdbl'}.items():
    for s in 'bc':
        shutil.copy(f'{OLD}/{old}{s}.bam', f'{MOD}/bam/{new.lower()}{s}.bam')

# ---------------------------------------------------------------- spells
TEMPLATE = Res(f'{MOD}/spl/ny#blin.spl')
H0 = bytearray(TEMPLATE.heads[0][0])
def eff(op, **kw): return mk_eff(op, **kw)
def roar(): return eff(174, tg=1, tm=1, res='NY#BROAR')
def pause(): return eff(165, tg=1, du=1)
def self_immune(res, du=2): return eff(206, tg=1, p1=-1, du=du, res=res)
def impact(dice): return eff(12, tg=2, p2=ACID, dn=dice, ds=4)
def later(dice): return eff(12, tg=2, p2=ACID, tm=4, du=ROUND, dn=max(1, dice // 2), ds=4, sv=2)

def spl(path, *, typ=1, level=1, icon, heads, school=6, flags=0x400, sectype=10):
    r = Res(f'{MOD}/spl/ny#blin.spl')
    struct.pack_into('<H', r.base, 0x1c, typ)
    struct.pack_into('<I', r.base, 0x34, level)
    struct.pack_into('<I', r.base, 0x18, flags)
    r.base[0x25] = school; r.base[0x27] = sectype
    w8(r.base, 0x3a, icon + 'C')
    r.glob = []; r.heads = []
    for (lvl, tgt, rng, ct, pro, effs) in heads:
        hb = bytearray(H0)
        hb[2] = 2 if typ == 1 else 4
        w8(hb, 4, icon + 'B')
        hb[0x0c] = tgt; struct.pack_into('<HHH', hb, 0x0e, rng, lvl, ct)
        struct.pack_into('<H', hb, 0x26, pro)
        r.heads.append([hb, [bytearray(e) for e in effs]])
    r.save(f'{MOD}/spl/{path.lower()}.spl')

def leveled(lo, cap, step=1, mindice=1):
    """(header level, dice): one header per level from 1 to cap"""
    return [(l, max(mindice, min(l, cap))) for l in range(1, cap + 1, step)]

# Orb, level 1: 2d4, +1d4 at levels 3, 5, 7 (5d4); the shards hit the enemies
# within 10 ft. of the creature hit (not itself), 1d4 less
orb_dice = {1: 2, 3: 3, 5: 4, 7: 5}
for lvl, n in orb_dice.items():
    spl(f'NY#BORS{n}', typ=4, icon='NY#BORB', heads=[(1, 4, 30, 0, ph('NY#BORBS'), [
        eff(324, tg=2, du=1, p2=2000 + ROW_NOT_ENEMY, res=f'NY#BORS{n}'), impact(n - 1), later(n - 1)])])
spl('NY#BORB', level=1, icon='NY#BORB', heads=[(lvl, 1, 30, 1, ph('NY#BORB'), [
    roar(), impact(n), later(n),
    eff(206, tg=2, p1=-1, du=1, res=f'NY#BORS{n}'),         # the creature hit: not hit by its own shards
    eff(148, tg=2, tm=1, p2=1, res=f'NY#BORS{n}')]) for lvl, n in orb_dice.items()])

# Trap, level 3: 1d4 per level, 10d4
spl('NY#BTRP', level=3, icon='NY#BTRP', heads=[(l, 4, 30, 3, ph('NY#BTRP'), [impact(n), later(n)]) for l, n in leveled(1, 10)])
# Ball, level 4: 1d4 per level, 12d4; the black puffs thrown with it
spl('NY#BBALK', typ=4, icon='NY#BBAL', heads=[(1, 4, 40, 0, ph('NY#BBALK'), [])])
spl('NY#BBAL', level=4, icon='NY#BBAL', heads=[(l, 4, 40, 4, ph('NY#BBAL'), [
    roar(), eff(148, tg=1, tm=1, p2=1, res='NY#BBALK'), impact(n), later(n)]) for l, n in leveled(1, 12)])
# Cone, level 5: 1d4 per level, 15d4; the disciple holds still, is not hit
spl('NY#BCONK', typ=4, icon='NY#BCON', heads=[(1, 4, 30, 0, ph('NY#BCONK'), [])])
spl('NY#BCON', level=5, icon='NY#BCON', heads=[(l, 4, 30, 5, ph('NY#BCON'), [
    pause(), roar(), eff(148, tg=1, tm=1, p2=1, res='NY#BCONK'), self_immune('NY#BCON'), impact(n), later(n)])
    for l, n in leveled(1, 15)])
# Cloud, level 6: 4d4 per round for 6 rounds, save vs. Breath for half
spl('NY#BCLD', level=6, icon='NY#BCLD', heads=[(1, 4, 40, 6, ph('NY#BCLD'), [
    eff(12, tg=2, p2=ACID, dn=4, ds=4, sv=2, sp=0x100)])])
# Rain, level 7: IWD:EE's Acid Storm, see rain_from_iwd.py (run after this script)
# Eruption, level 8: 1d4 per level, 20d4, around the disciple, allies hit, not himself
spl('NY#BERU', level=8, icon='NY#BERU', heads=[(l, 5, 0, 8, ph('NY#BERU'), [
    pause(), roar(), self_immune('NY#BERU'), impact(n), later(n)]) for l, n in leveled(1, 20)])

# Curses (Bolt 15%, Final Breath 5%), each one rolled by its own spell
def curse_spl(i, effs):
    spl(f'NY#BCUR{i}', typ=4, icon='NY#BBOL', heads=[(1, 1, 30, 0, 1, effs)], flags=0x400)
dur2, dur4 = 2 * ROUND, 4 * ROUND
ins = Res(f'{MOD}/spl/ny#cnydi.spl').heads[0][1]
ent = Res(f'{MOD}/spl/ny#cnydp.spl').heads[0][1]
def redur(effs, du):
    out = []
    for e in effs:
        e = bytearray(e)
        if struct.unpack_from('<I', e, 0x0e)[0]: struct.pack_into('<I', e, 0x0e, du)
        struct.pack_into('<IiI', e, 0x24, 0, 0, 0)        # no save: the creature already failed one
        out.append(e)
    return out
curse_spl(1, [eff(25, tg=2, p1=1, p2=0, du=dur4), eff(142, tg=2, p2=6, du=dur4)])                            # poison
curse_spl(2, [eff(44, tg=2, p1=-2, du=dur4), eff(15, tg=2, p1=-2, du=dur4), eff(142, tg=2, p2=7, du=dur4)])  # disease
curse_spl(3, redur(ins, dur2))                                                                                 # insects
curse_spl(4, redur(ent, dur2))                                                                                 # swamp plants
curse_spl(5, [eff(24, tg=2, du=dur2), eff(142, tg=2, p2=36, du=dur2)])                                         # fear
curse_spl(6, [eff(74, tg=2, du=dur2), eff(142, tg=2, p2=8, du=dur2)])                                          # blindness
def rolls(prefix, pct):
    for i in range(1, 7):
        spl(f'{prefix}{i}', typ=4, icon='NY#BBOL', heads=[(1, 1, 30, 0, 1, [
            eff(146, tg=2, tm=1, p2=1, res=f'NY#BCUR{i}', pr1=pct - 1, pr2=0)])])
rolls('NY#BBOR', 15)
rolls('NY#HFIR', 5)
# Bolt, level 9: 20d4; failed save vs. Breath: 10d4 the next round and the curses
spl('NY#BBOLX', typ=4, icon='NY#BBOL', heads=[(1, 1, 30, 0, 1, [later(20)] + [
    eff(146, tg=2, tm=1, p2=1, res=f'NY#BBOR{i}') for i in range(1, 7)])])
for e in Res(f'{MOD}/spl/ny#bbolx.spl').heads[0][1]: pass
r = Res(f'{MOD}/spl/ny#bbolx.spl')
struct.pack_into('<I', r.heads[0][1][0], 0x24, 0)       # the delayed damage: no own save (the bolt's save decides)
r.save(f'{MOD}/spl/ny#bbolx.spl')
spl('NY#BBOL', level=9, icon='NY#BBOL', heads=[(1, 1, 40, 9, ph('NY#BBOL'), [
    roar(), impact(20), eff(146, tg=2, tm=1, p2=1, res='NY#BBOLX', sv=2)])])

# Final Breath (HLA, innate, unlimited, recharge 6 rounds): the Line, twice
# as wide, 30d4, enemies only; failed save: 15d4 the next round, curses 5%
spl('NY#HFINX', typ=4, icon='NY#HFIN', heads=[(1, 1, 30, 0, 1, [later(30)] + [
    eff(146, tg=2, tm=1, p2=1, res=f'NY#HFIR{i}') for i in range(1, 7)])])
r = Res(f'{MOD}/spl/ny#hfinx.spl'); struct.pack_into('<I', r.heads[0][1][0], 0x24, 0); r.save(f'{MOD}/spl/ny#hfinx.spl')
spl('NY#HFIN', typ=4, icon='NY#HFIN', school=6, heads=[(1, 4, 30, 1, ph('NY#HFIN'), [
    eff(172, tg=1, tm=1, res='NY#HFIN'),                                         # used: removed...
    eff(328, tg=1, du=6 * ROUND, p2=1000 + ST_FINCD, sp=1),                        # ... recharging 6 rounds
    eff(139, tg=1, tm=4, du=6 * ROUND, p1=-1),                                     # "Final Breath ready"
    pause(), roar(),
    eff(215, tg=1, du=5, res='NY#BLIK'), eff(215, tg=1, du=5, res='NY#BLIG'),
    self_immune('NY#HFIN'),
    eff(324, tg=2, du=1, p2=2000 + ROW_NOT_ENEMY, res='NY#HFIN'),                 # enemies only
    impact(30), eff(146, tg=2, tm=1, p2=1, res='NY#HFINX', sv=2)])])
# taken (AP_ in LUNYB.2DA): state + the ability; given back by the global script
spl('NY#HFINA', typ=4, icon='NY#HFIN', flags=0, heads=[(1, 5, 1, 0, 1, [
    eff(328, tg=1, tm=9, p2=1000 + ST_FIN, sp=1), eff(171, tg=1, tm=1, res='NY#HFIN')])])
spl('NY#HFING', typ=4, icon='NY#HFIN', flags=0, heads=[(1, 5, 1, 0, 1, [eff(171, tg=1, tm=1, res='NY#HFIN')])])
print('built')
