"""The Cloud's cloud in the breaths' yellow acid: the game's Cloudkill cloud
(SPCLOUDK, pale green) recoloured (palette: hue 30-150 degrees -> 58, more
saturated) as NY#BCLOK; the Cloud's projectile NY#BCLD points at it.
Usage: cloud_yellow.py <the game's SPCLOUDK.BAM> [mod]
"""
import colorsys, os, struct, sys, zlib
SRC = sys.argv[1]
MOD = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), '..', '..')
P = lambda *a: os.path.join(MOD, *a)
d = open(SRC, 'rb').read()
packed = d[:4] == b'BAMC'
raw = bytearray(zlib.decompress(d[12:]) if packed else d)
po = struct.unpack_from('<I', raw, 0x10)[0]                # palette
for i in range(256):
    b, g, r, a = raw[po + i * 4: po + i * 4 + 4]
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    if 30 / 360 <= h <= 150 / 360 and s > 0.08:
        r2, g2, b2 = colorsys.hsv_to_rgb(58 / 360, min(1, s * 1.6 + 0.25), v)
        raw[po + i * 4: po + i * 4 + 3] = bytes((round(b2 * 255), round(g2 * 255), round(r2 * 255)))
out = (b'BAMCV1  ' + struct.pack('<I', len(raw)) + zlib.compress(bytes(raw), 9)) if packed else bytes(raw)
open(P('bam', 'ny#bclok.bam'), 'wb').write(out)
pro = bytearray(open(P('pro', 'ny#bcld.pro'), 'rb').read())
assert pro[0x228:0x230].rstrip(b'\0') in (b'SPCLOUDK', b'NY#BCLOK')
pro[0x228:0x230] = b'NY#BCLOK'
open(P('pro', 'ny#bcld.pro'), 'wb').write(pro)
print('ok')
