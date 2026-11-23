"""NY#BDBS.BAM: black version of SPBDRAE2 (the cone's spread puffs), same
cycles and frames, transparency in the palette (no blending needed)."""
import numpy as np
from scipy.cluster.vq import kmeans2
from scipy.spatial import cKDTree

from bamlib import Bam, Frame
from compose import black_smoke

ALPHA_MIN = 0.03


def palette_and_map(images):
    rng = np.random.default_rng(0)
    samples = []
    for img in images:
        px = img.reshape(-1, 4)
        px = px[px[:, 3] >= ALPHA_MIN]
        if len(px):
            samples.append(px[rng.choice(len(px), min(len(px), 4000), replace=False)])
    s = np.concatenate(samples)
    pm = np.concatenate([s[:, :3] * s[:, 3:], s[:, 3:]], axis=1)
    cent, _ = kmeans2(pm, 255, minit='++', seed=1, iter=25)
    pal = np.zeros((256, 4), np.uint8)
    pal[0] = (0, 255, 0, 0)
    for i, c in enumerate(cent, start=1):
        a = float(np.clip(c[3], 0, 1))
        rgb = np.clip(c[:3] / max(a, 1e-4), 0, 1)
        a8 = int(round(a * 255))
        a8 = 0 if a8 >= 255 else max(a8, 1)   # EE: 0 = opaque
        r, g, b = (rgb * 255).round().astype(int)
        if (r, g, b) == (0, 255, 0):
            g = 254
        pal[i] = (r, g, b, a8)
    return pal, cKDTree(cent)


def convert(src, dst):
    b = Bam.load(src)
    imgs = [black_smoke(b.rgba(i).astype(np.float32) / 255) for i in range(len(b.frames))]
    pal, tree = palette_and_map(imgs)
    out = Bam()
    out.palette = pal
    out.cycles = [list(c) for c in b.cycles]
    for f, img in zip(b.frames, imgs):
        p = img.reshape(-1, 4)
        q = np.concatenate([p[:, :3] * p[:, 3:], p[:, 3:]], axis=1)
        _, nn = tree.query(q)
        ind = (nn + 1).astype(np.uint8)
        ind[p[:, 3] < ALPHA_MIN] = 0
        out.frames.append(Frame(f.w, f.h, f.cx, f.cy, ind.reshape(f.h, f.w)))
    out.save(dst)
    return out


if __name__ == '__main__':
    o = convert('spbdrae2.bam', 'ny#bdbs.bam')
    print(len(o.frames), [len(c) for c in o.cycles])
