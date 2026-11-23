import sys

import numpy as np
from PIL import Image, ImageDraw

from compose import load_explosion, make_variants, plan, render_direction, to_straight

BG = (88, 82, 66)


def ground(w, h, seed=1):
    rng = np.random.default_rng(seed)
    base = np.ones((h, w, 3), np.float32) * np.array(BG, np.float32) / 255
    noise = rng.normal(0, 0.025, (h // 6 + 1, w // 6 + 1, 1)).repeat(6, 0).repeat(6, 1)[:h, :w]
    return np.clip(base + noise, 0, 1)


def over_ground(frame_pm, bg):
    a = frame_pm[..., 3:]
    return np.clip(frame_pm[..., :3] + bg * (1 - a), 0, 1)


def gif_for(dirs, name, items, variants, scale=1):
    rendered = [render_direction(variants, items, d) for d in dirs]
    pad = 20
    W = sum(f[0].shape[1] for f, _, _ in rendered) + pad * (len(rendered) + 1)
    H = max(f[0].shape[0] for f, _, _ in rendered) + 2 * pad
    n = max(len(f) for f, _, _ in rendered) + 6
    bg = ground(W, H)
    imgs = []
    for t in range(n):
        canvas = bg.copy()
        x = pad
        marks = []
        for frames, cx, cy in rendered:
            fr = frames[t] if t < len(frames) else np.zeros_like(frames[0])
            h, w = fr.shape[:2]
            canvas[pad:pad + h, x:x + w] = over_ground(fr, canvas[pad:pad + h, x:x + w])
            marks.append((x + cx, pad + cy))
            x += w + pad
        im = Image.fromarray((canvas * 255).astype(np.uint8))
        dr = ImageDraw.Draw(im)
        for mx, my in marks:  # the caster's point
            dr.ellipse((mx - 3, my - 2, mx + 3, my + 2), outline=(220, 60, 60))
        if scale != 1:
            im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
        imgs.append(im)
    imgs[0].save(name, save_all=True, append_images=imgs[1:], duration=67, loop=0, disposal=2)
    return imgs


if __name__ == '__main__':
    variants = make_variants(load_explosion())
    items = plan()
    imgs = gif_for([12], 'apercu_est.gif', items, variants)
    # still sheet to check
    pick = list(range(0, len(imgs), 4))
    sheet = Image.new('RGB', (imgs[0].width, imgs[0].height * len(pick)))
    for k, i in enumerate(pick):
        sheet.paste(imgs[i], (0, k * imgs[0].height))
    sheet.save('apercu_est_sheet.png')
    print(len(imgs), imgs[0].size)
