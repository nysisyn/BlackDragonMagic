"""Approximate preview of the cone breath: green SPBDRAE2 puffs (blended +
glowing, i.e. roughly additive) with a second cone of black puffs (normal
display, palette alpha). The engine's exact timing is approximated."""
import math
import random

import numpy as np
from PIL import Image, ImageDraw

from bamlib import Bam
from compose import black_smoke
from preview import ground

RADIUS = 426          # NY#BDBRT: explosion size (px)
HALF = math.radians(70)   # cone width 140
FPS = 15


def frames_of(bam, cycles=(1, 2), step=2):
    seq = []
    for c in cycles:
        seq += bam.cycles[c][::step]
    out = []
    for fi in seq:
        f = bam.frames[fi]
        out.append((bam.rgba(fi).astype(np.float32) / 255, f.cx, f.cy))
    return out


def puffs(seed, spacing=72, ring_step=30, speed=22, jitter=4, keep=1.0):
    rnd = random.Random(seed)
    out = []
    r = ring_step
    while r <= RADIUS:
        arc = 2 * HALF * r
        n = max(1, int(arc / spacing))
        for i in range(n):
            if rnd.random() > keep:
                continue
            a = -HALF + (i + 0.5) * 2 * HALF / n + rnd.uniform(-0.5, 0.5) * 2 * HALF / n
            rr = r + rnd.uniform(-ring_step / 2, ring_step / 2)
            start = int(rr / speed) + rnd.randint(0, jitter)
            out.append((rr * math.cos(a), rr * math.sin(a) * 0.75, start))
        r += ring_step
    return out


def render(green, black, mode, nframes, size=(500, 680), origin=(36, 340), seed=3):
    W, H = size
    bg = ground(W, H, seed=5)
    pg = puffs(seed)
    pb = puffs(seed + 1, spacing=80, keep=0.6, jitter=6)
    pb = [(x, y, s + 3) for x, y, s in pb]  # the black cone: a tick or so later
    imgs = []
    for t in range(nframes):
        add = np.zeros((H, W, 3), np.float32)
        over = np.zeros((H, W, 4), np.float32)  # premultiplied

        def draw(lst, seq, kind):
            for x, y, st in sorted(lst, key=lambda p: p[1]):
                i = t - st
                if not (0 <= i < len(seq)):
                    continue
                img, cx, cy = seq[i]
                ox, oy = int(origin[0] + x - cx), int(origin[1] + y - cy)
                h, w = img.shape[:2]
                x0, y0 = max(ox, 0), max(oy, 0)
                x1, y1 = min(ox + w, W), min(oy + h, H)
                if x1 <= x0 or y1 <= y0:
                    continue
                sub = img[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
                if kind == 'add':
                    add[y0:y1, x0:x1] += sub[..., :3] * sub[..., 3:]
                else:
                    a = sub[..., 3:]
                    d = over[y0:y1, x0:x1]
                    d[:] = np.concatenate([sub[..., :3] * a, a], 2) + d * (1 - a)

        img = bg.copy()
        if mode in ('green', 'black_under', 'black_over'):
            if mode == 'black_under':
                draw(pb, black, 'over')
                img = over[..., :3] + img * (1 - over[..., 3:])
            draw(pg, green, 'add')
            img = np.clip(img + add * 0.5, 0, 1)
            if mode == 'black_over':
                over[:] = 0
                draw(pb, black, 'over')
                img = over[..., :3] + img * (1 - over[..., 3:])
        im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
        dr = ImageDraw.Draw(im)
        dr.ellipse((origin[0] - 3, origin[1] - 2, origin[0] + 3, origin[1] + 2), outline=(220, 60, 60))
        imgs.append(im)
    return imgs


if __name__ == '__main__':
    rae = Bam.load('spbdrae2.bam')
    green = frames_of(rae)
    black = [(black_smoke(img), cx, cy) for img, cx, cy in green]
    n = 26 + len(green) + 4
    panels = [render(green, black, m, n) for m in ('green', 'black_under', 'black_over')]
    labels = ['actuel (vert seul)', 'noir sous le vert', 'noir par-dessus le vert']
    W, H = panels[0][0].size
    out = []
    for t in range(n):
        im = Image.new('RGB', (3 * W + 40, H + 28), (30, 30, 30))
        dr = ImageDraw.Draw(im)
        for k in range(3):
            im.paste(panels[k][t], (10 + k * (W + 10), 28))
            dr.text((10 + k * (W + 10) + 8, 8), labels[k], fill=(235, 235, 235))
        out.append(im)
    out[0].save('apercu_cone.gif', save_all=True, append_images=out[1:], duration=67, loop=0)
    out[20].save('check_cone.png')
    print(n, out[0].size)
