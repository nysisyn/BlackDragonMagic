"""Manifest Heritage: Summon Dracolisk (5), Summon Draco-Hydra (8), Summon
Dragon Turtle (9). Builds the stored files of the three spells, their
creatures, weapons, abilities and placeholder icons.

  python3 build_heritage.py <WYVERNSU.CRE of BG2:EE> [mod folder]

Strings are -1 (set at install with SAY), the creatures' animation is written
at install (NY#NEW_ANIMATION), their items too (tpa/heritage.tpa). Projectiles
are placeholders (3000+n, lib/ny#core.tpa).
"""
import os, struct, sys, zlib
sys.path.insert(0, os.path.dirname(__file__))
from iemodel import Res, mk_eff, eop, set_res
from PIL import Image, ImageDraw

WYV = sys.argv[1]
MOD = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), '..', '..')
P = lambda *a: os.path.join(MOD, *a)
ROUND = 6
PRO_LINE_WAVE = 3002          # NY#CNYDL, Nydra'Nath's acid wave
PRO_CONE = 3009               # NY#BCON, the breath cone

# name, spell level, creature stats ------------------------------------------
SUMMONS = [
    dict(code='DRL', lvl=5, hp=60, ac=2, thac0=11, apr=2, clvl=8, saves=(10, 12, 11, 12, 13),
         st=(18, 3, 13, 14, 16, 8), dice=(2, 6), bonus=2, ench=2, dtype=1, anim='NYDL'),
    dict(code='HYD', lvl=8, hp=100, ac=2, thac0=8, apr=5, clvl=12, saves=(5, 7, 6, 5, 8),
         st=(19, 4, 13, 14, 19, 10), dice=(1, 10), bonus=2, ench=3, dtype=1, anim='NYHY'),
    dict(code='DTU', lvl=9, hp=130, ac=-2, thac0=6, apr=2, clvl=14, saves=(4, 6, 5, 4, 7),
         st=(21, 10, 13, 10, 21, 12), dice=(4, 6), bonus=4, ench=4, dtype=1, anim='NYDT'),
]


def w8(b, o, s):
    b[o:o + 8] = s.encode('latin1').ljust(8, b'\0')[:8]


# creatures --------------------------------------------------------------
def build_cre(s):
    c = bytearray(open(WYV, 'rb').read())
    assert c[:8] == b'CRE V1.0'
    struct.pack_into('<ii', c, 0x08, -1, -1)            # names: at install
    struct.pack_into('<I', c, 0x14, 0)                  # no experience when killed
    struct.pack_into('<HH', c, 0x24, s['hp'], s['hp'])
    struct.pack_into('<I', c, 0x28, 0)                  # animation: at install
    struct.pack_into('<hh', c, 0x46, s['ac'], s['ac'])
    c[0x52] = s['thac0']; c[0x53] = s['apr']
    for i, v in enumerate(s['saves']):                  # death, wands, polymorph, breath, spells
        c[0x54 + i] = v
    for o in range(0x59, 0x64):                         # resistances
        c[o] = 0
    c[0x5c] = 100                                       # immune to acid
    for o in range(0xa4, 0x234, 4):                     # no voice (strrefs differ per game)
        struct.pack_into('<i', c, o, -1)
    c[0x234] = s['clvl']
    for i, v in enumerate(s['st']):                     # STR INT WIS DEX CON CHA
        c[0x238 + (0 if i == 0 else i + 1)] = v
    c[0x239] = 0                                        # STR bonus
    w8(c, 0x248, f"NY#C{s['code']}S")                   # override script
    w8(c, 0x258, '')                                    # no wyvern race script
    open(P('cre', f"ny#c{s['code'].lower()}.cre"), 'wb').write(c)


# weapons ----------------------------------------------------------------
def build_weapon(s):
    r = Res(P('itm', 'ny#cnydw.itm'))
    b = r.base
    struct.pack_into('<ii', b, 0x08, -1, -1); struct.pack_into('<ii', b, 0x50, -1, -1)
    struct.pack_into('<I', b, 0x60, s['ench'])
    r.glob = [e for e in r.glob if eop(e) in (101, 206)]   # immunities (fear, poison), no Blur
    hb, el = r.heads[0]
    struct.pack_into('<h', hb, 0x14, 0)                 # THAC0 bonus
    hb[0x16] = s['dice'][1]; hb[0x18] = s['dice'][0]
    struct.pack_into('<h', hb, 0x1a, s['bonus'])
    struct.pack_into('<H', hb, 0x1c, s['dtype'])        # piercing
    r.heads[0] = [hb, []]                               # no acid, no curses
    r.save(P('itm', f"ny#c{s['code'].lower()}w.itm"))


# abilities --------------------------------------------------------------
def innate(name_res, icon, target, rng, pro, effects):
    r = Res(P('spl', 'ny#cnydb.spl'))
    struct.pack_into('<ii', r.base, 0x08, -1, -1); struct.pack_into('<i', r.base, 0x50, -1)
    w8(r.base, 0x3a, icon + 'C')
    hb, _ = r.heads[0]
    w8(hb, 4, icon + 'B'); hb[0x0c] = target
    struct.pack_into('<H', hb, 0x0e, rng); struct.pack_into('<H', hb, 0x26, pro)
    r.heads = [[hb, effects]]
    r.save(P('spl', name_res.lower() + '.spl'))


def build_abilities():
    # Dracolisk: stunning gaze, one enemy, save vs. Petrification
    innate('NY#CDRLG', 'NY#MDRL', 1, 20, 1, [
        mk_eff(45, tg=2, tm=0, du=ROUND, sv=0x10),                   # stunned 1 round
        mk_eff(139, tg=2, tm=1, p1=-1, sv=0x10),                     # combat log, at install
    ])
    # Draco-Hydra: acid cone, 6d8, save vs. Breath for half
    innate('NY#CHYDB', 'NY#MHYD', 4, 30, PRO_CONE, [
        mk_eff(206, tg=1, tm=0, du=2, p1=-1, res='NY#CHYDB'),
        mk_eff(12, tg=2, tm=0, p2=0x10000, dn=6, ds=8, sv=2, sp=0x100),
    ])
    # Dragon Turtle: acid steam, a wide wave, 8d8, save vs. Breath for half
    innate('NY#CDTUB', 'NY#MDTU', 4, 40, PRO_LINE_WAVE, [
        mk_eff(206, tg=1, tm=0, du=2, p1=-1, res='NY#CDTUB'),
        mk_eff(215, tg=2, tm=0, du=1, res='NY#CWVH'),
        mk_eff(12, tg=2, tm=0, p2=0x10000, dn=8, ds=8, sv=2, sp=0x100),
    ])


# summoning spells -------------------------------------------------------
def build_spell(s):
    code = s['code']; res = f'NY#M{code}'
    r = Res(P('spl', 'ny#sdrk.spl'))
    b = r.base
    struct.pack_into('<ii', b, 0x08, -1, -1); struct.pack_into('<i', b, 0x50, -1)
    b[0x25] = 2; b[0x27] = 0                            # conjuration
    struct.pack_into('<I', b, 0x34, s['lvl'])
    w8(b, 0x3a, res + 'C')
    tmpl = r.heads[0][0]
    heads = []
    for L in range(2 * s['lvl'] - 1, 31):
        hb = bytearray(tmpl)
        w8(hb, 4, res + 'B'); hb[0x0c] = 4                 # a point
        struct.pack_into('<H', hb, 0x0e, 30)
        struct.pack_into('<H', hb, 0x10, 1 if not heads else L)
        struct.pack_into('<H', hb, 0x12, s['lvl'])          # casting time
        struct.pack_into('<H', hb, 0x26, 1)                 # no projectile
        du = (10 + L) * ROUND                               # 1 turn + 1 round per level
        heads.append([hb, [
            mk_eff(206, tg=1, tm=0, du=du, p1=-1, res=res),   # one at a time; message at install
            mk_eff(67, tg=1, tm=0, du=du, res=f'NY#C{code}'),
        ]])
    r.heads = heads
    r.save(P('spl', res.lower() + '.spl'))


# scripts ----------------------------------------------------------------
GUARD = ('  !StateCheck(Myself,CD_STATE_NOTVALID)\n'
         '  !CheckStatGT(Myself,0,HELD)\n')
MELEE = ('IF\n  See(NearestEnemyOf(Myself))\nTHEN\n  RESPONSE #100\n'
         '    AttackReevaluate(NearestEnemyOf(Myself),15)\nEND\n')


def ability_block(timer, spell, cond):
    return (f'IF\n  See(NearestEnemyOf(Myself))\n{cond}{GUARD}'
            f'  !GlobalTimerNotExpired("{timer}","LOCALS")\nTHEN\n  RESPONSE #100\n'
            f'    SetGlobalTimer("{timer}","LOCALS",18)\n'
            f'    ReallyForceSpellRES("{spell}",NearestEnemyOf(Myself))\nEND\n\n')


HEAD = ('// The forced cast (ReallyForceSpellRES) ignores the creature\'s state, so it\n'
        '// is only tried while the creature can act.\n')


def build_scripts():
    open(P('baf', 'ny#cdrls.baf'), 'w').write(
        HEAD + '// Dracolisk: stunning gaze on the nearest enemy within 20 ft., every 3\n'
        '// rounds at most; otherwise it attacks in melee.\n'
        + ability_block('NY#CDRLT', 'NY#CDRLG', '  Range(NearestEnemyOf(Myself),20)\n') + MELEE)
    open(P('baf', 'ny#chyds.baf'), 'w').write(
        HEAD + '// Draco-Hydra: acid cone at the nearest enemy, every 3 rounds at most;\n'
        '// otherwise it bites.\n'
        + ability_block('NY#CHYDT', 'NY#CHYDB', '  Range(NearestEnemyOf(Myself),25)\n') + MELEE)
    open(P('baf', 'ny#cdtus.baf'), 'w').write(
        HEAD + '// Dragon Turtle: acid steam at the nearest enemy, every 3 rounds at most;\n'
        '// otherwise it bites.\n'
        + ability_block('NY#CDTUT', 'NY#CDTUB', '  Range(NearestEnemyOf(Myself),35)\n') + MELEE)


# icons: works/icons/<spell>.png when drawn, otherwise a placeholder (the
# creature's first standing frame on a dark disc) ----
def load_bam(path):
    d = open(path, 'rb').read()
    if d[:4] == b'BAMC':
        d = zlib.decompress(d[12:])
    nf, nc, ck = struct.unpack_from('<HBB', d, 8); fo, po, lo = struct.unpack_from('<III', d, 12)
    pal = [struct.unpack_from('<BBBB', d, po + i * 4) for i in range(256)]
    w, h, cx, cy, off = struct.unpack_from('<HHhhI', d, fo)
    rle = not (off & 0x80000000); p = off & 0x7fffffff; px = []
    while len(px) < w * h:
        v = d[p]; p += 1
        if rle and v == ck:
            px += [ck] * (d[p] + 1); p += 1
        else:
            px.append(v)
    im = Image.new('RGBA', (w, h))
    im.putdata([(0, 0, 0, 0) if v in (ck, 1) else (pal[v][2], pal[v][1], pal[v][0], 255) for v in px[:w * h]])
    return im


def write_icon(path, im):
    q = im.convert('RGB').quantize(colors=254, dither=Image.NONE)
    qp = q.getpalette()[:254 * 3]
    pal = [(0, 255, 0), (0, 0, 0)] + [tuple(qp[i:i + 3]) for i in range(0, len(qp), 3)]
    pal += [(0, 0, 0)] * (256 - len(pal))
    a = im.split()[3].load(); qd = q.load()
    px = bytes(0 if a[x, y] < 128 else qd[x, y] + 2 for y in range(im.height) for x in range(im.width))
    fo = 0x18; po = fo + 12 + 4; lo = po + 1024; do = lo + 2
    out = (b'BAM V1  ' + struct.pack('<HBBIII', 1, 1, 0, fo, po, lo)
           + struct.pack('<HHhhI', im.width, im.height, 0, 0, do | 0x80000000)
           + struct.pack('<HH', 1, 0)
           + b''.join(struct.pack('<BBBB', bb, g, r, 0) for r, g, bb in pal)
           + struct.pack('<H', 0) + px)
    open(path, 'wb').write(out)


def icon_from_art(path, size=32):
    """a drawn icon (works/icons/<spell>.png): fitted into the square, a 1-pixel
    black outline so it stands out on the spellbook"""
    from PIL import ImageFilter
    art = Image.open(path).convert('RGBA')
    art.putalpha(art.split()[3].point(lambda v: 255 if v >= 128 else 0))
    art = art.crop(art.split()[3].getbbox())
    art.thumbnail((size - 2, size - 2), Image.LANCZOS)
    art.putalpha(art.split()[3].point(lambda v: 255 if v >= 128 else 0))
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    im.alpha_composite(art, ((size - art.width) // 2, (size - art.height) // 2))
    ring = im.split()[3].filter(ImageFilter.MaxFilter(3))
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    out.paste((8, 12, 8, 255), (0, 0), ring)
    out.alpha_composite(im)
    return out


def build_icons(s, frame_bam):
    art = P('works', 'icons', f"ny#m{s['code'].lower()}.png")
    if os.path.exists(art):
        im = icon_from_art(art)
        for kind in ('c', 'b'):
            write_icon(P('bam', f"ny#m{s['code'].lower()}{kind}.bam"), im)
        return
    crea = load_bam(P('bam', frame_bam))
    crea = crea.crop(crea.split()[3].getbbox())
    for kind, size in (('C', 32), ('B', 32)):
        im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(im).ellipse((0, 0, size - 1, size - 1), fill=(28, 40, 26, 255), outline=(70, 200, 70, 255))
        t = crea.copy(); t.thumbnail((size - 6, size - 6), Image.LANCZOS)
        im.alpha_composite(t, ((size - t.width) // 2, (size - t.height) // 2))
        write_icon(P('bam', f"ny#m{s['code'].lower()}{kind.lower()}.bam"), im)


if __name__ == '__main__':
    os.makedirs(P('cre'), exist_ok=True); os.makedirs(P('baf'), exist_ok=True)
    for s in SUMMONS:
        build_cre(s); build_weapon(s); build_spell(s)
    build_abilities(); build_scripts()
    build_icons(SUMMONS[0], 'nydlg1.bam'); build_icons(SUMMONS[1], 'nyhysd.bam'); build_icons(SUMMONS[2], 'nydtsd.bam')
    print('ok')
