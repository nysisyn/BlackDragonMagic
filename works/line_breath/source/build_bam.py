"""Build NY#BDLN.BAM (9 orientations, mirrored by the VVC) and NY#BDLN.VVC."""
import struct
import sys

import numpy as np
from scipy.cluster.vq import kmeans2
from scipy.spatial import cKDTree

from bamlib import Bam, Frame
from compose import load_explosion, make_variants, plan, plan_wide, render_direction, to_straight

NAME = 'NY#BDLN'
ALPHA_MIN = 0.03


def build(fps=15, wide=False):
    variants = make_variants(load_explosion())
    items = plan_wide() if wide else plan()   # v1 (ny#bdbl1, in use): plan(); wide = two rows (tried, not kept)
    cycles = []  # per IE direction 0..8: list of (straight RGBA, cx, cy)
    for d in range(9):
        frames, cx, cy = render_direction(variants, items, d)
        cycles.append([(to_straight(f), cx, cy) for f in frames])
    nper = len(cycles[0])

    # ---- shared palette: 255 colours (index 0 = transparent)
    rng = np.random.default_rng(0)
    samples = []
    for cyc in cycles:
        for img, _, _ in cyc:
            px = img.reshape(-1, 4)
            px = px[px[:, 3] >= ALPHA_MIN]
            if len(px):
                take = rng.choice(len(px), min(len(px), 1500), replace=False)
                samples.append(px[take])
    s = np.concatenate(samples)
    pm = np.concatenate([s[:, :3] * s[:, 3:], s[:, 3:]], axis=1)  # premultiplied
    cent, _ = kmeans2(pm, 255, minit='++', seed=1, iter=25)
    tree = cKDTree(cent)

    pal = np.zeros((256, 4), np.uint8)
    pal[0] = (0, 255, 0, 0)
    for i, c in enumerate(cent, start=1):
        a = float(np.clip(c[3], 0, 1))
        rgb = np.clip(c[:3] / max(a, 1e-4), 0, 1)
        a8 = int(round(a * 255))
        a8 = 0 if a8 >= 255 else max(a8, 1)  # EE: 0 = opaque
        r, g, b = (rgb * 255).round().astype(int)
        if (r, g, b) == (0, 255, 0):
            g = 254
        pal[i] = (r, g, b, a8)

    bam = Bam()
    bam.palette = pal
    bam.rle_index = 0
    for cyc in cycles:
        idxs = []
        for img, cx, cy in cyc:
            a = img[..., 3]
            mask = a >= ALPHA_MIN
            if not mask.any():
                fr = Frame(1, 1, 0, 0, np.zeros((1, 1), np.uint8))
            else:
                ys, xs = np.where(mask)
                y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
                sub = img[y0:y1, x0:x1]
                p = sub.reshape(-1, 4)
                q = np.concatenate([p[:, :3] * p[:, 3:], p[:, 3:]], axis=1)
                _, nn = tree.query(q)
                ind = (nn + 1).astype(np.uint8)
                ind[p[:, 3] < ALPHA_MIN] = 0
                fr = Frame(x1 - x0, y1 - y0, int(cx - x0), int(cy - y0),
                           ind.reshape(y1 - y0, x1 - x0))
            idxs.append(len(bam.frames))
            bam.frames.append(fr)
        bam.cycles.append(idxs)
    bam.save(NAME.lower() + '.bam')
    return bam, nper


def write_vvc(nframes, fps=15):
    v = bytearray(0x1EC)
    v[0:8] = b'VVC V1.0'
    v[0x08:0x10] = NAME.encode().ljust(8, b'\0')
    struct.pack_into('<H', v, 0x18, 0x10)              # mirror X axis (as SPSTURNI)
    struct.pack_into('<H', v, 0x1A, 0)
    struct.pack_into('<I', v, 0x20, 0x08)              # draw animation (no loop)
    struct.pack_into('<I', v, 0x2C, 1)                 # Y = 1, as most game VVCs
    struct.pack_into('<I', v, 0x30, 1)                 # use orientation
    struct.pack_into('<I', v, 0x34, fps)               # frame rate
    struct.pack_into('<I', v, 0x38, 16)                # 16 orientations (9 cycles mirrored)
    struct.pack_into('<I', v, 0x3C, 0)                 # base orientation
    struct.pack_into('<I', v, 0x40, 0x02)              # as the game's oriented VVCs (SPCOMSTT, SPSTURNI)
    struct.pack_into('<I', v, 0x5C, 0xFFFFFFFF)        # duration: the animation's own length
    v[0x60:0x68] = NAME.encode().ljust(8, b'\0')
    struct.pack_into('<I', v, 0x68, 0)                 # first sequence
    struct.pack_into('<I', v, 0x6C, 0)                 # second sequence
    struct.pack_into('<I', v, 0x90, 0)                 # third sequence
    open(NAME.lower() + '.vvc', 'wb').write(bytes(v))


if __name__ == '__main__':
    bam, n = build()
    write_vvc(n)
    print('frames/cycle', n, 'total frames', len(bam.frames))
