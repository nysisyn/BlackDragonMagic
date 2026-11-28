"""Test: the Cloud with the other breaths' animation. Its projectile NY#BCLD
(6 pulses, one per round) shows the breaths' explosion (SPBDIMSP centre,
SPBDRAE2 spread, brightened: extended area flags 0x7214 as NY#BBAL), and its
black layer NY#BCLDK the breaths' black puffs (NY#BDBS, as NY#BBALK). The
yellow cloud NY#BCLOK and the black cloud NY#BCLDK BAMs stay in the mod,
unused (cloud_yellow.py, black_layers.py bring them back).
Usage: cloud_as_breaths.py [mod]
"""
import os, struct, sys
MOD = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', '..')
P = lambda *a: os.path.join(MOD, *a)
w8 = lambda b, o, s: b.__setitem__(slice(o, o + 8), s.encode().ljust(8, b'\0'))
p = bytearray(open(P('pro', 'ny#bcld.pro'), 'rb').read())
w8(p, 0x21c, 'SPBDIMSP'); w8(p, 0x228, 'SPBDRAE2')
struct.pack_into('<I', p, 0x240, 0x7214)
p[0x218] = 67                                      # explosion colour, as NY#BBAL
open(P('pro', 'ny#bcld.pro'), 'wb').write(p)
k = bytearray(open(P('pro', 'ny#bcldk.pro'), 'rb').read())
w8(k, 0x228, 'NY#BDBS')
struct.pack_into('<I', k, 0x240, 0x1214)
k[0x218] = 67
open(P('pro', 'ny#bcldk.pro'), 'wb').write(k)
print('ok')
