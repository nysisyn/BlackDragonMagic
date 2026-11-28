"""The Rain in the breaths' yellow: IWD:EE's acid rain and splash (NY#BRAIA,
NY#BRAIX) are a dark yellow, which looks olive green when drawn brightened;
made as bright as the breaths' explosion (hue 58). Its icons (Acid Storm's,
red) recoloured in the same yellow. The originals are kept in works/rain_iwd.
Usage: rain_yellow.py [mod]
"""
import colorsys, os, shutil, struct, sys, zlib
MOD = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', '..')
P = lambda *a: os.path.join(MOD, *a)


def recolour(src, dst, match, new):
    d = open(src, 'rb').read()
    packed = d[:4] == b'BAMC'
    raw = bytearray(zlib.decompress(d[12:]) if packed else d)
    po = struct.unpack_from('<I', raw, 0x10)[0]            # palette
    for i in range(256):
        b, g, r, a = raw[po + i * 4: po + i * 4 + 4]
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if match(h * 360, s, v):
            r2, g2, b2 = colorsys.hsv_to_rgb(*new(s, v))
            raw[po + i * 4: po + i * 4 + 3] = bytes((round(b2 * 255), round(g2 * 255), round(r2 * 255)))
    out = (b'BAMCV1  ' + struct.pack('<I', len(raw)) + zlib.compress(bytes(raw), 9)) if packed else bytes(raw)
    open(dst, 'wb').write(out)


if __name__ == '__main__':
    os.makedirs(P('works', 'rain_iwd'), exist_ok=True)
    for n in ('ny#braia', 'ny#braix', 'ny#braib', 'ny#braic'):
        keep = P('works', 'rain_iwd', n + '.bam')
        if not os.path.exists(keep):
            shutil.copy(P('bam', n + '.bam'), keep)
    acid = lambda h, s, v: 30 <= h <= 150 and s > 0.08
    bright = lambda s, v: (58 / 360, min(0.75, s * 1.05), min(1, v * 1.7))
    for n in ('ny#braia', 'ny#braix'):
        recolour(P('works', 'rain_iwd', n + '.bam'), P('bam', n + '.bam'), acid, bright)
    red = lambda h, s, v: (h <= 40 or h >= 330) and s > 0.3
    yellow = lambda s, v: (58 / 360, min(0.9, s * 1.15), min(1, v * 1.15))
    for n in ('ny#braib', 'ny#braic'):
        recolour(P('works', 'rain_iwd', n + '.bam'), P('bam', n + '.bam'), red, yellow)
    print('ok')
