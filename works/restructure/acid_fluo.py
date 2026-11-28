"""Fluorescent green variant of the breaths' yellow acid.

Recolours the palette (hue 30-150 degrees, coloured entries only) towards a
fluorescent green, keeps the shapes, frames and the other colours:
  - the mod's BAMs NY#BLIG (Line), NY#BORBT (orb), NY#BRAIA / NY#BRAIX (Rain);
    the yellow originals are kept in works/acid_yellow;
  - copies of the game's BAMs, as NY# BAMs, the PROs pointing at them:
    SPBDIMSP -> NY#BDIMS, SPBDRAE2 -> NY#BDRAE (explosions of Ball, Cone,
    Eruption, the Orb's shards, Trap), SPCLOUDK -> NY#BCLOK (Cloud).
Usage: acid_fluo.py <folder with spbdimsp.bam spbdrae2.bam spcloudk.bam> [mod]
"""
import colorsys, os, shutil, struct, sys, zlib, glob
SRC = sys.argv[1]
MOD = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), '..', '..')
P = lambda *a: os.path.join(MOD, *a)
HUE = 110 / 360


def recolour(path_in, path_out):
    d = open(path_in, 'rb').read()
    packed = d[:4] == b'BAMC'
    raw = bytearray(zlib.decompress(d[12:]) if packed else d)
    assert raw[:8] == b'BAM V1  ', path_in
    po = struct.unpack_from('<I', raw, 0x10)[0]   # palette
    for i in range(256):
        b, g, r, a = raw[po + i * 4: po + i * 4 + 4]
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if 30 / 360 <= h <= 150 / 360 and s > 0.15:
            r2, g2, b2 = colorsys.hsv_to_rgb(HUE, min(1, s * 1.25 + 0.1), min(1, v * 1.08))
            raw[po + i * 4: po + i * 4 + 3] = bytes((round(b2 * 255), round(g2 * 255), round(r2 * 255)))
    out = (b'BAMCV1  ' + struct.pack('<I', len(raw)) + zlib.compress(bytes(raw), 9)) if packed else bytes(raw)
    open(path_out, 'wb').write(out)


if __name__ == '__main__':
    os.makedirs(P('works', 'acid_yellow'), exist_ok=True)
    for n in ('ny#blig', 'ny#borbt', 'ny#braia', 'ny#braix'):
        keep = P('works', 'acid_yellow', n + '.bam')
        if not os.path.exists(keep):
            shutil.copy(P('bam', n + '.bam'), keep)
        recolour(keep, P('bam', n + '.bam'))
    for game, new in (('spbdimsp', 'ny#bdims'), ('spbdrae2', 'ny#bdrae'), ('spcloudk', 'ny#bclok')):
        recolour(os.path.join(SRC, game + '.bam'), P('bam', new + '.bam'))
    # the PROs
    swap = {b'SPBDIMSP': b'NY#BDIMS', b'SPBDRAE2': b'NY#BDRAE', b'SPCLOUDK': b'NY#BCLOK'}
    for f in glob.glob(P('pro', '*.pro')):
        b = bytearray(open(f, 'rb').read())
        for o in range(0, len(b) - 8, 1):
            for old, new in swap.items():
                if b[o:o + 8] == old:
                    b[o:o + 8] = new
        open(f, 'wb').write(b)
    print('ok')
