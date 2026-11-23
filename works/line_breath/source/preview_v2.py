import numpy as np
from PIL import Image, ImageDraw
from compose import load_explosion, make_variants_v2, plan_v2, render_layers, plan, make_variants, render_direction
from preview import ground, over_ground


def frames_v2(d, items, variants, glow_on_top=True):
    black, glow, cx, cy = render_layers(variants, items, d)
    return black, glow, cx, cy


def gif(dirs, name, scale=1, extra=6):
    v = make_variants_v2(load_explosion())
    items = plan_v2()
    rend = [render_layers(v, items, d) for d in dirs]
    pad = 20
    W = sum(r[0][0].shape[1] for r in rend) + pad * (len(rend) + 1)
    H = max(r[0][0].shape[0] for r in rend) + 2 * pad
    n = max(len(r[0]) for r in rend) + extra
    bg = ground(W, H)
    imgs = []
    for t in range(n):
        canvas = bg.copy()
        x = pad
        marks = []
        for black, glow, cx, cy in rend:
            h, w = black[0].shape[:2]
            sub = canvas[pad:pad + h, x:x + w]
            if t < len(black):
                sub[:] = over_ground(black[t], sub)
                sub[:] = np.clip(sub + glow[t] * 0.85, 0, 1)   # blended + glowing ~ added
            marks.append((x + cx, pad + cy))
            x += w + pad
        im = Image.fromarray((canvas * 255).astype(np.uint8))
        dr = ImageDraw.Draw(im)
        for mx, my in marks:
            dr.ellipse((mx - 3, my - 2, mx + 3, my + 2), outline=(220, 60, 60))
        if scale != 1:
            im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
        imgs.append(im)
    # VVC at 12 fps: 83 ms a frame
    imgs[0].save(name, save_all=True, append_images=imgs[1:], duration=83, loop=0)
    return imgs


if __name__ == '__main__':
    a = gif([12], 'apercu_ligne_v2_est.gif', scale=2)
    a[20].save('check_v2.png')
    b = gif([14, 0], 'apercu_ligne_v2_sud_est_sud.gif')
    print(len(a), a[0].size)
