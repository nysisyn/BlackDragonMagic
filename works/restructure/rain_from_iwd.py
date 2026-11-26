"""Black Dragon Breath: Rain = IWD:EE's Acid Storm (SPWI724), copied as it is
into the mod, under the mod's names:
  - IDPRO211.PRO -> pro/ny#brai.pro (the rain ASTORMA -> NY#BRAIA, the
    splash ASTORMX -> NY#BRAIX, the sound ARE_M04 -> NY#BRAIS);
  - SPWI724.SPL  -> spl/ny#brai.spl: same headers and damage (1d4 x3,
    1d6 x3, then 1d8 every 6 s, one more per level from 15; save vs. Spell
    for half each), with these changes only:
      * its self-protection (op 324 'SPWI724') points to NY#BRAI;
      * the damage ignores magic resistance (resist/dispel 0), as every
        breath;
      * the projectile is the placeholder 3012 (NY#BRAI);
      * icons NY#BRAIB / C (Acid Storm's), strings set at install (-1).
  - SPWI724B/C.BAM -> bam/ny#braib.bam / ny#braic.bam.
Usage: rain_from_iwd.py <folder with the IWD:EE files> [mod]
"""
import os, shutil, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
from iemodel import *
SRC = sys.argv[1]
MOD = sys.argv[2] if len(sys.argv) > 2 else '/home/claude/blackdragonmagic'
PH_PRO = 3012
def w8(b, o, s): b[o:o+8] = s.encode().ljust(8, b'\0')[:8]

p = bytearray(open(f'{SRC}/idpro211.pro', 'rb').read())
w8(p, 0x208, 'NY#BRAIS'); w8(p, 0x238, 'NY#BRAIS')
w8(p, 0x21c, 'NY#BRAIX'); w8(p, 0x228, 'NY#BRAIA')
open(f'{MOD}/pro/ny#brai.pro', 'wb').write(p)
for a, b in {'astorma.bam': 'bam/ny#braia.bam', 'astormx.bam': 'bam/ny#braix.bam', 'are_m04.wav': 'wav/ny#brais.wav',
             'spwi724b.bam': 'bam/ny#braib.bam', 'spwi724c.bam': 'bam/ny#braic.bam'}.items():
    shutil.copy(f'{SRC}/{a}', f'{MOD}/{b}')

s = Res(f'{SRC}/spwi724.spl')
struct.pack_into('<ii', s.base, 0x08, -1, -1); struct.pack_into('<i', s.base, 0x50, -1)
w8(s.base, 0x3a, 'NY#BRAIC')
for hb, el in s.heads:
    w8(hb, 4, 'NY#BRAIB'); struct.pack_into('<H', hb, 0x26, PH_PRO)
    for e in el:
        if eop(e) == 324: set_res(e, 'NY#BRAI')
        e[0x0d] = 0
s.save(f'{MOD}/spl/ny#brai.spl')
