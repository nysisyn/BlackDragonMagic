"""Compose a black dragon 'line breath' from ny#tbps.bam explosions."""
import math
import random

import numpy as np
from PIL import Image

from bamlib import Bam

PX_FT_X, PX_FT_Y = 16.0, 12.0   # IE: 16 px per foot horizontally, ~3/4 vertically


# ---------------------------------------------------------------- variants
def load_explosion(path='ny#tbps.bam'):
    """Frames of the explosion as straight RGBA float arrays + centres."""
    b = Bam.load(path)
    out = []
    for fi in b.cycles[0]:
        f = b.frames[fi]
        rgba = b.rgba(fi).astype(np.float32) / 255.0
        out.append((rgba, f.cx, f.cy))
    return out


def glow_to_alpha(rgba):
    """Additive look without blending: brightness becomes opacity, so the
    black halo disappears (what 'blended, glowing' does in game)."""
    rgb, a = rgba[..., :3], rgba[..., 3:]
    m = rgb.max(axis=2, keepdims=True)
    alpha = np.clip(m * 1.15, 0, 1) * a
    col = np.where(m > 1e-4, rgb / np.maximum(m, 1e-4), 0)
    col = np.clip(col * np.clip(m * 1.3, 0, 1), 0, 1)  # keep the bright core bright
    col = np.maximum(col, rgb)
    return np.concatenate([col, alpha], axis=2)


def black_smoke(rgba, core=0.0):
    """Black acid version: the whole shape (halo included) becomes dark,
    sickly green smoke; `core` keeps some of the green glow in the centre."""
    from scipy import ndimage
    rgb, a = rgba[..., :3], rgba[..., 3:]
    lum = rgb.max(axis=2, keepdims=True)
    # the old halo: soft edge (ramp over ~12 px from the outline) instead of
    # the hard ellipse, so the smoke has no disc outline
    inside = ndimage.distance_transform_edt(a[..., 0] > 0)[..., None]
    halo = np.clip(inside / 12.0, 0, 1) ** 1.5
    halo = ndimage.gaussian_filter(halo[..., 0], 1.5)[..., None]
    body = np.clip(lum * 1.6, 0, 1)
    alpha = np.clip(np.maximum(halo * 0.5, body * 0.95) + halo * body * 0.2, 0, 0.96) * (a > 0)
    dark = np.array([0.03, 0.04, 0.02], np.float32)
    tint = np.array([0.07, 0.12, 0.025], np.float32)
    col = dark + tint * lum ** 1.6
    if core > 0:
        g = np.clip((lum - 0.45) / 0.55, 0, 1) * core
        col = col * (1 - g) + rgb * g
    return np.concatenate([col, alpha], axis=2)


def make_variants(frames):
    return {
        'green': [(glow_to_alpha(r), cx, cy) for r, cx, cy in frames],
        'black': [(black_smoke(r), cx, cy) for r, cx, cy in frames],
        'blackcore': [(black_smoke(r, core=0.8), cx, cy) for r, cx, cy in frames],
    }


# ---------------------------------------------------------------- layout
def plan(n=8, length_ft=30, delay=2, seed=7, mix=('black', 'green', 'blackcore')):
    """Explosion list: position along the line (ft), sideways jitter (ft),
    start frame, scale, mirror, variant."""
    rnd = random.Random(seed)
    items = []
    start_ft = 3.0
    step = (length_ft - start_ft) / (n - 1)
    for k in range(n):
        items.append(dict(
            along=start_ft + k * step + rnd.uniform(-0.25, 0.25) * step,
            side=rnd.uniform(-1.2, 1.2),
            start=k * delay + rnd.choice((0, 0, 1)),
            scale=rnd.uniform(0.8, 1.05) * (0.85 + 0.3 * k / (n - 1)),
            flip=rnd.random() < 0.5,
            variant=mix[k % len(mix)] if rnd.random() < 0.8 else rnd.choice(mix),
        ))
        # a second, smaller puff in between, to fill the line
        if k < n - 1:
            items.append(dict(
                along=start_ft + (k + 0.5) * step,
                side=rnd.uniform(-1.8, 1.8),
                start=k * delay + 1 + rnd.choice((0, 1)),
                scale=rnd.uniform(0.55, 0.75),
                flip=rnd.random() < 0.5,
                variant=rnd.choice(('black', 'blackcore')),
            ))
    return items


def direction_vector(d):
    """IE direction 0..15: 0 = south, 4 = west, 8 = north, 12 = east."""
    a = math.radians(d * 22.5)
    return -math.sin(a), math.cos(a)


def scaled(img, s, flip):
    h, w = img.shape[:2]
    pil = [Image.fromarray(img[..., c]) for c in range(4)]
    nw, nh = max(1, round(w * s)), max(1, round(h * s))
    chans = [np.asarray(p.resize((nw, nh), Image.BILINEAR)) for p in pil]
    out = np.stack(chans, axis=2)
    if flip:
        out = out[:, ::-1]
    return out


def render_direction(variants, items, d, nframes=None):
    """List of premultiplied RGBA float frames for direction d, all of the
    same size, with the caster point (cx, cy)."""
    vx, vy = direction_vector(d)
    px, py = -vy, vx   # perpendicular
    seq_len = len(next(iter(variants.values())))
    if nframes is None:
        nframes = max(it['start'] for it in items) + seq_len
    # pre-scale sprites per item
    placed = []
    for it in items:
        x = (vx * it['along'] + px * it['side']) * PX_FT_X
        y = (vy * it['along'] + py * it['side']) * PX_FT_Y
        frames = []
        for img, cx, cy in variants[it['variant']]:
            s = scaled(img, it['scale'], it['flip'])
            ccx = (img.shape[1] - cx) if it['flip'] else cx
            frames.append((s, ccx * it['scale'], cy * it['scale']))
        placed.append((x, y, it['start'], frames))
    # bounding box over all frames
    x0 = y0 = 1e9
    x1 = y1 = -1e9
    for x, y, st, frames in placed:
        for s, cx, cy in frames:
            x0 = min(x0, x - cx); y0 = min(y0, y - cy)
            x1 = max(x1, x - cx + s.shape[1]); y1 = max(y1, y - cy + s.shape[0])
    x0, y0 = math.floor(x0) - 1, math.floor(y0) - 1
    W, H = math.ceil(x1) - x0 + 1, math.ceil(y1) - y0 + 1
    # draw back to front (screen y), the black smoke under the green
    order = sorted(placed, key=lambda p: p[1])
    out = []
    for t in range(nframes):
        canvas = np.zeros((H, W, 4), np.float32)  # premultiplied
        for x, y, st, frames in order:
            i = t - st
            if not (0 <= i < len(frames)):
                continue
            s, cx, cy = frames[i]
            ox, oy = round(x - cx - x0), round(y - cy - y0)
            h, w = s.shape[:2]
            a = s[..., 3:]
            src = np.concatenate([s[..., :3] * a, a], axis=2)
            dst = canvas[oy:oy + h, ox:ox + w]
            dst[:] = src + dst * (1 - a)
        out.append(canvas)
    return out, -x0, -y0


def to_straight(pm):
    a = pm[..., 3:]
    rgb = np.where(a > 1e-4, pm[..., :3] / np.maximum(a, 1e-4), 0)
    return np.concatenate([np.clip(rgb, 0, 1), a], axis=2)


def plan_wide(n=8, length_ft=30, delay=2, seed=11, row_ft=3.2, mix=('black', 'green', 'blackcore')):
    """Twice as wide: two staggered rows of explosions on either side of the
    line, small black puffs along the middle."""
    rnd = random.Random(seed)
    items = []
    start_ft = 3.0
    step = (length_ft - start_ft) / (n - 1)
    v = 0
    for k in range(n):
        for side in (-1, 1):
            along = start_ft + k * step + (0.25 * step if side > 0 else -0.1 * step) + rnd.uniform(-0.15, 0.15) * step
            items.append(dict(
                along=along,
                side=side * (row_ft + rnd.uniform(-1.0, 1.0)),
                start=round(along / step * delay) + rnd.choice((0, 0, 1)),
                scale=rnd.uniform(0.8, 1.05) * (0.85 + 0.3 * k / (n - 1)),
                flip=rnd.random() < 0.5,
                variant=mix[v % len(mix)] if rnd.random() < 0.8 else rnd.choice(mix),
            ))
            v += 1
        if k < n - 1:
            along = start_ft + (k + 0.5) * step
            items.append(dict(
                along=along,
                side=rnd.uniform(-1.0, 1.0),
                start=round(along / step * delay) + rnd.choice((0, 1)),
                scale=rnd.uniform(0.6, 0.8),
                flip=rnd.random() < 0.5,
                variant=rnd.choice(('black', 'blackcore')),
            ))
    return items


# ------------------------------------------------------------------ v2
# Two layers: the black smoke (normal display, palette alpha) and the acid
# explosions in their own colours, shown blended / glowing by the VVC (the
# black halo of ny#tbps disappears, as in the breaths' projectiles).
def make_variants_v2(frames, gain=1.3):
    v = make_variants(frames)
    v['glow'] = [(np.concatenate([np.clip(r[..., :3] * gain, 0, 1), r[..., 3:]], 2), cx, cy)
                 for r, cx, cy in frames]
    return v


def plan_v2(n=10, length_ft=30, delay=3, seed=21, side_ft=2.0):
    """Slower (3 frames between explosions), a little wider (+/- 2 ft,
    overlapping), more acid explosions."""
    rnd = random.Random(seed)
    items = []
    start_ft = 3.0
    step = (length_ft - start_ft) / (n - 1)
    seq = ['glow', 'black', 'blackcore', 'glow', 'black', 'black']
    for k in range(n):
        along = start_ft + k * step + rnd.uniform(-0.25, 0.25) * step
        var = seq[k % len(seq)] if rnd.random() < 0.8 else rnd.choice(('glow', 'black', 'blackcore'))
        items.append(dict(along=along, side=rnd.uniform(-side_ft, side_ft),
                          start=k * delay + rnd.choice((0, 0, 1)),
                          scale=rnd.uniform(0.85, 1.1) * (0.85 + 0.3 * k / (n - 1)),
                          flip=rnd.random() < 0.5, variant=var))
        # a second explosion on the other side, smaller: the line is wider
        other = 'glow' if var != 'glow' else rnd.choice(('black', 'blackcore'))
        items.append(dict(along=along + rnd.uniform(-0.3, 0.3) * step,
                          side=-items[-1]['side'] * rnd.uniform(0.6, 1.0),
                          start=k * delay + 1 + rnd.choice((0, 1)),
                          scale=rnd.uniform(0.6, 0.8) * (0.85 + 0.3 * k / (n - 1)),
                          flip=rnd.random() < 0.5, variant=other))
    return items


def render_layers(variants, items, d, black_scale=1.3):
    """Two lists of frames, same canvas: 'black' (premultiplied RGBA, alpha
    over) and 'glow' (RGB, added), with the caster point."""
    vx, vy = direction_vector(d)
    px, py = -vy, vx
    seq_len = len(next(iter(variants.values())))
    nframes = max(it['start'] for it in items) + seq_len
    placed = []
    for it in items:
        x = (vx * it['along'] + px * it['side']) * PX_FT_X
        y = (vy * it['along'] + py * it['side']) * PX_FT_Y
        frames = []
        # the black smoke a little bigger than the acid it surrounds
        sc = it['scale'] * (1.0 if it['variant'] == 'glow' else black_scale)
        for img, cx, cy in variants[it['variant']]:
            s = scaled(img, sc, it['flip'])
            ccx = (img.shape[1] - cx) if it['flip'] else cx
            frames.append((s, ccx * sc, cy * sc))
        placed.append((x, y, it['start'], frames, it['variant'] == 'glow'))
    x0 = y0 = 1e9
    x1 = y1 = -1e9
    for x, y, st, frames, g in placed:
        for s, cx, cy in frames:
            x0 = min(x0, x - cx); y0 = min(y0, y - cy)
            x1 = max(x1, x - cx + s.shape[1]); y1 = max(y1, y - cy + s.shape[0])
    x0, y0 = math.floor(x0) - 1, math.floor(y0) - 1
    W, H = math.ceil(x1) - x0 + 1, math.ceil(y1) - y0 + 1
    order = sorted(placed, key=lambda p: p[1])
    black, glow = [], []
    for t in range(nframes):
        cb = np.zeros((H, W, 4), np.float32)
        cg = np.zeros((H, W, 3), np.float32)
        for x, y, st, frames, g in order:
            i = t - st
            if not (0 <= i < len(frames)):
                continue
            s, cx, cy = frames[i]
            ox, oy = round(x - cx - x0), round(y - cy - y0)
            h, w = s.shape[:2]
            a = s[..., 3:]
            if g:
                cg[oy:oy + h, ox:ox + w] += s[..., :3] * a
            else:
                src = np.concatenate([s[..., :3] * a, a], axis=2)
                dst = cb[oy:oy + h, ox:ox + w]
                dst[:] = src + dst * (1 - a)
        black.append(cb)
        glow.append(np.clip(cg, 0, 1))
    return black, glow, -x0, -y0
