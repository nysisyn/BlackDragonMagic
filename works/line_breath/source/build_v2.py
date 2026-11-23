"""Line breath v2: two BAMs on the same layout, played together on the caster.
  NY#BDLK  black smoke (normal display, transparency in the palette)
  NY#BDLG  acid explosions in their own colours (VVC blended: the dark
           parts vanish and the yellow glows, as in the breaths' projectiles)
Slower (3 frames between explosions, VVCs at 12 fps), a little wider."""
import struct

import numpy as np
from scipy.cluster.vq import kmeans2
from scipy.spatial import cKDTree

from bamlib import Bam, Frame
from compose import load_explosion, make_variants_v2, plan_v2, render_layers, to_straight

FPS = 12
A_MIN = 0.03      # black layer: below this alpha, transparent
G_MIN = 0.025     # glow layer: darker than this, transparent (adds nothing)


def quantize(samples, with_alpha):
    cent, _ = kmeans2(samples, 255, minit='++', seed=1, iter=25)
    pal = np.zeros((256, 4), np.uint8)
    pal[0] = (0, 255, 0, 0)
    for i, c in enumerate(cent, start=1):
        if with_alpha:
            a = float(np.clip(c[3], 0, 1))
            rgb = np.clip(c[:3] / max(a, 1e-4), 0, 1)
            a8 = int(round(a * 255))
            a8 = 0 if a8 >= 255 else max(a8, 1)   # EE: 0 = opaque
        else:
            rgb = np.clip(c[:3], 0, 1)
            a8 = 0
        r, g, b = (rgb * 255).round().astype(int)
        if (r, g, b) == (0, 255, 0):
            g = 254
        pal[i] = (r, g, b, a8)
    return pal, cKDTree(cent)


def to_frame(img, cx, cy, tree, with_alpha):
    if with_alpha:
        mask = img[..., 3] >= A_MIN
    else:
        mask = img.max(axis=2) >= G_MIN
    if not mask.any():
        return Frame(1, 1, 0, 0, np.zeros((1, 1), np.uint8))
    ys, xs = np.where(mask)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    sub = img[y0:y1, x0:x1]
    m = mask[y0:y1, x0:x1].reshape(-1)
    if with_alpha:
        p = sub.reshape(-1, 4)
        q = np.concatenate([p[:, :3] * p[:, 3:], p[:, 3:]], axis=1)
    else:
        q = sub.reshape(-1, 3)
    _, nn = tree.query(q)
    ind = (nn + 1).astype(np.uint8)
    ind[~m] = 0
    return Frame(x1 - x0, y1 - y0, int(cx - x0), int(cy - y0), ind.reshape(y1 - y0, x1 - x0))


def build():
    variants = make_variants_v2(load_explosion())
    items = plan_v2()
    layers = {'k': [], 'g': []}
    for d in range(9):
        black, glow, cx, cy = render_layers(variants, items, d)
        layers['k'].append([(to_straight(f), cx, cy) for f in black])
        layers['g'].append([(f, cx, cy) for f in glow])
    rng = np.random.default_rng(0)
    out = {}
    for key, with_alpha in (('k', True), ('g', False)):
        samples = []
        for cyc in layers[key]:
            for img, _, _ in cyc:
                if with_alpha:
                    px = img.reshape(-1, 4)
                    px = px[px[:, 3] >= A_MIN]
                    px = np.concatenate([px[:, :3] * px[:, 3:], px[:, 3:]], axis=1)
                else:
                    px = img.reshape(-1, 3)
                    px = px[px.max(axis=1) >= G_MIN]
                if len(px):
                    samples.append(px[rng.choice(len(px), min(len(px), 1500), replace=False)])
        pal, tree = quantize(np.concatenate(samples), with_alpha)
        bam = Bam()
        bam.palette = pal
        for cyc in layers[key]:
            idx = []
            for img, cx, cy in cyc:
                idx.append(len(bam.frames))
                bam.frames.append(to_frame(img, cx, cy, tree, with_alpha))
            bam.cycles.append(idx)
        name = 'NY#BDLK' if key == 'k' else 'NY#BDLG'
        bam.save(name.lower() + '.bam')
        out[name] = bam
    return out


def write_vvc(name, blended):
    v = bytearray(0x1EC)
    v[0:8] = b'VVC V1.0'
    v[0x08:0x10] = name.encode().ljust(8, b'\0')
    # mirror X axis; the acid one blended too (as the game's SPCOMSTT: 0x18)
    struct.pack_into('<H', v, 0x18, 0x10 | (0x08 if blended else 0))
    struct.pack_into('<I', v, 0x20, 0x08)              # draw animation (no loop)
    struct.pack_into('<I', v, 0x2C, 2 if blended else 1)   # Y: the acid a little in front
    struct.pack_into('<I', v, 0x30, 1)                 # use orientation
    struct.pack_into('<I', v, 0x34, FPS)               # slower: 12 fps
    struct.pack_into('<I', v, 0x38, 16)                # 16 orientations (9 cycles mirrored)
    struct.pack_into('<I', v, 0x40, 0x02)              # as the game's oriented VVCs
    struct.pack_into('<I', v, 0x5C, 0xFFFFFFFF)        # duration: the animation's own
    v[0x60:0x68] = name.encode().ljust(8, b'\0')
    open(name.lower() + '.vvc', 'wb').write(bytes(v))


if __name__ == '__main__':
    out = build()
    write_vvc('NY#BDLK', False)
    write_vvc('NY#BDLG', True)
    for n, b in out.items():
        print(n, len(b.frames), [len(c) for c in b.cycles][:2])
