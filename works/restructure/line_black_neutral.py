"""The Line's black smoke (NY#BLIK) had a green cast (dark olive palette):
palette made neutral grey/black, same brightness. Usage: line_black_neutral.py [mod]"""
import os, struct, sys, zlib
MOD = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', '..')
p = os.path.join(MOD, 'bam', 'ny#blik.bam')
d = open(p, 'rb').read(); packed = d[:4] == b'BAMC'
raw = bytearray(zlib.decompress(d[12:]) if packed else d)
po = struct.unpack_from('<I', raw, 0x10)[0]
for i in range(1, 256):
    b, g, r = raw[po + i * 4: po + i * 4 + 3]
    l = round(0.3 * r + 0.59 * g + 0.11 * b)
    raw[po + i * 4: po + i * 4 + 3] = bytes((l, l, l))
open(p, 'wb').write((b'BAMCV1  ' + struct.pack('<I', len(raw)) + zlib.compress(bytes(raw), 9)) if packed else bytes(raw))
print('ok')
