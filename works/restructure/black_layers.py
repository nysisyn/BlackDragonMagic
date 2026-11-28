"""Black layers of the Rain and the Cloud, as the other breaths' black puffs.

  NY#BRAIK  black rain: the Rain's rain (NY#BRAIA) flipped left-right, so its
            drops fall between the yellow ones, only its drops, in black;
            the dark glow around them (made for the brightened drawing) is
            dropped. PRO NY#BRAIK: the Rain's projectile (NY#BRAI), this rain
            as spread, no splash, no sound, not brightened. SPL NY#BRAIK.
  NY#BCLDK  black cloud: the Cloud's cloud (the game's SPCLOUDK) flipped
            left-right, its lighter wisps in black. PRO NY#BCLDK: the Cloud's projectile (NY#BCLD) without the
            orb, the sounds, the brightening. SPL NY#BCLDK.
  NY#BERUK  black puffs of the Eruption: the Ball's and Cone's black puffs
            (NY#BDBS) around the caster. PRO NY#BERUK: the Eruption's
            projectile (NY#BERU), these puffs as spread, no explosion, no
            sound, not brightened. SPL NY#BERUK (on the caster).
All are cast at the same point by the breath (opcode 148, as NY#BCONK for
the Cone, before the breath's protection of its caster). Projectiles:
placeholders 16, 17 and 18 (tpa/kit.tpa).
Usage: black_layers.py <the game's SPCLOUDK.BAM> [mod]
"""
import os, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'dracolisk'))
from iemodel import Res, mk_eff, eop
from build_dracolisk import load, write_bam
CLOUD = sys.argv[1]
MOD = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, '..', '..')
P = lambda *a: os.path.join(MOD, *a)


def blacken(src, dst, thr, dark=(10, 40), mirror=False):
    pal, frames, cycles, lut, ck = load(src)
    lum = [0.3 * p[2] + 0.59 * p[1] + 0.11 * p[0] for p in pal]
    lo, hi = dark
    newpal = [(0, 255, 0)]
    remap = {}
    for i in range(1, 256):
        if i == ck or lum[i] < thr:
            remap[i] = 0
        else:
            v = lo + (hi - lo) * (lum[i] - thr) / max(1, 255 - thr)
            remap[i] = i
    newpal = []
    for i in range(256):
        if i == 0:
            newpal.append((0, 255, 0)); continue
        v = lo + (hi - lo) * max(0, lum[i] - thr) / max(1, 255 - thr)
        newpal.append((round(v * 0.95), round(v * 1.1), round(v * 0.9)))
    out = [(w, h, cx, cy, [0 if (p == ck or remap.get(p, 0) == 0) else p for p in px]) for w, h, cx, cy, px in frames]
    if ck != 0:   # transparent is index 0 in the written BAM
        out = [(w, h, cx, cy, [p for p in px]) for w, h, cx, cy, px in out]
    if mirror:   # flipped left-right: the black falls between the yellow
        out = [(w, h, w - 1 - cx, cy, [p for y in range(h) for p in reversed(px[y * w:(y + 1) * w])])
               for w, h, cx, cy, px in out]
    write_bam(dst, newpal, out, cycles, lut)


def pro_black(src, dst, spread, keep_missile=False):
    b = bytearray(open(src, 'rb').read())
    def w8(o, s): b[o:o + 8] = s.encode('latin1').ljust(8, b'\0')[:8]
    w8(0x10, ''); w8(0x18, '')                         # flight sounds
    if not keep_missile:
        w8(0x104, '')                                  # no missile BAM (the orb)
    w8(0x208, ''); w8(0x238, '')                       # area sounds
    w8(0x21c, '')                                      # no explosion (splash)
    w8(0x228, spread)
    ext = struct.unpack_from('<I', b, 0x240)[0]
    struct.pack_into('<I', b, 0x240, ext & ~0x6000)    # not brightened, as NY#BCONK
    open(dst, 'wb').write(b)


def spl_black(name, rng, ph, target=4):
    r = Res(P('spl', 'ny#bconk.spl'))
    hb, _ = r.heads[0]
    hb[0x0c] = target
    struct.pack_into('<H', hb, 0x0e, rng); struct.pack_into('<H', hb, 0x26, ph)
    r.heads = [[hb, []]]
    r.save(P('spl', name.lower() + '.spl'))


def add_cast(spell, res):
    r = Res(P('spl', spell + '.spl'))
    for hb, el in r.heads:
        if not any(eop(e) == 148 for e in el):
            el.insert(0, mk_eff(148, tg=1, tm=1, p2=1, res=res))
    r.save(P('spl', spell + '.spl'))


if __name__ == '__main__':
    rain = P('works', 'rain_iwd', 'ny#braia.bam')        # IWD's, before rain_yellow.py
    blacken(rain if os.path.exists(rain) else P('bam', 'ny#braia.bam'), P('bam', 'ny#braik.bam'), thr=100, mirror=True)
    blacken(CLOUD, P('bam', 'ny#bcldk.bam'), thr=110, dark=(14, 46), mirror=True)
    pro_black(P('pro', 'ny#brai.pro'), P('pro', 'ny#braik.pro'), 'NY#BRAIK')
    pro_black(P('pro', 'ny#bcld.pro'), P('pro', 'ny#bcldk.pro'), 'NY#BCLDK')
    spl_black('NY#BRAIK', 40, 3016)
    spl_black('NY#BCLDK', 40, 3017)
    add_cast('ny#brai', 'NY#BRAIK')
    add_cast('ny#bcld', 'NY#BCLDK')
    pro_black(P('pro', 'ny#beru.pro'), P('pro', 'ny#beruk.pro'), 'NY#BDBS')
    spl_black('NY#BERUK', 0, 3018, target=5)
    add_cast('ny#beru', 'NY#BERUK')
    print('ok')
