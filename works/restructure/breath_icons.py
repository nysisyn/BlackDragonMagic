"""Icons of Cone, Eruption and Cloud, in the style of the other breath icons:
a yellow glyph with a darker rim (C, spellbook) and the same glyph on the
stone plate of the Ball's ability icon (B). Drawn here at 128 px, reduced to
32 px; PNGs kept in works/icons.
Usage: breath_icons.py [mod]
"""
import colorsys, math, os, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
MOD = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..')
P = lambda *a: os.path.join(MOD, *a)
from build_heritage import load_bam, write_icon
S = 128; Y = (236, 232, 52, 255); D = (116, 110, 16, 255); T = (0, 0, 0, 0)


def finish(big, inner=None):
    small = big.resize((32, 32), Image.LANCZOS)
    al = small.split()[3].point(lambda v: 255 if v >= 110 else 0).load()
    out = Image.new('RGBA', (32, 32)); op = out.load()
    ism = inner.resize((32, 32), Image.LANCZOS).split()[3].load() if inner else None
    for y in range(32):
        for x in range(32):
            if al[x, y]:
                edge = any(not (0 <= x + dx < 32 and 0 <= y + dy < 32) or not al[x + dx, y + dy]
                           for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                op[x, y] = D if edge or (ism and ism[x, y] >= 120) else Y
    return out


def cone():
    im = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(im)
    inner = Image.new('RGBA', (S, S)); di = ImageDraw.Draw(inner)
    d.polygon([(8, 64), (112, 6), (124, 64), (112, 122)], fill=Y)
    for a in (-0.32, 0, 0.32):
        di.line([(30, 64), (30 + 86 * math.cos(a), 64 + 86 * math.sin(a))], fill=Y, width=6)
    return finish(im, inner)


def eruption():
    im = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(im)
    for k in range(10):
        a = k * 2 * math.pi / 10
        d.polygon([(64 + 30 * math.cos(a + 0.2), 64 + 30 * math.sin(a + 0.2)),
                   (64 + 62 * math.cos(a), 64 + 62 * math.sin(a)),
                   (64 + 30 * math.cos(a - 0.2), 64 + 30 * math.sin(a - 0.2))], fill=Y)
    d.ellipse((30, 30, 98, 98), fill=Y); d.ellipse((46, 46, 82, 82), fill=T); d.ellipse((56, 56, 72, 72), fill=Y)
    return finish(im)


def cloud():
    im = Image.new('RGBA', (S, S)); d = ImageDraw.Draw(im)
    inner = Image.new('RGBA', (S, S)); di = ImageDraw.Draw(inner)
    puffs = ((34, 60, 26), (64, 42, 32), (96, 60, 26))
    for x, y, r in puffs:
        d.ellipse((x - r, y - r, x + r, y + r), fill=Y)
    d.rectangle((16, 60, 112, 84), fill=Y); d.ellipse((10, 62, 34, 86), fill=Y); d.ellipse((94, 62, 118, 86), fill=Y)
    for x, y, r in puffs[:2]:
        di.arc((x - r + 6, y - r + 6, x + r - 6, y + r - 6), 200, 330, fill=Y, width=6)
    for x, y in ((36, 106), (64, 114), (92, 106)):
        d.polygon([(x, y - 14), (x + 8, y + 2), (x - 8, y + 2)], fill=Y); d.ellipse((x - 8, y - 4, x + 8, y + 12), fill=Y)
    return finish(im, inner)


def plate():
    im = load_bam(P('bam', 'ny#bbalb.bam'))
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a:
                h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                if s > 0.2 and (h < 0.25 or h > 0.8):      # the Ball's glyph -> stone
                    px[x, y] = (34, 34, 30, 255)
    return im


if __name__ == '__main__':
    os.makedirs(P('works', 'icons'), exist_ok=True)
    pl = plate()
    for code, draw in (('bcon', cone), ('beru', eruption), ('bcld', cloud)):
        c = draw(); c.save(P('works', 'icons', f'ny#{code}c.png'))
        b = pl.copy(); g = c.copy(); g.thumbnail((25, 25), Image.NEAREST)
        b.alpha_composite(g, ((b.width - g.width) // 2, (b.height - g.height) // 2))
        b.save(P('works', 'icons', f'ny#{code}b.png'))
        write_icon(P('bam', f'ny#{code}c.bam'), c); write_icon(P('bam', f'ny#{code}b.bam'), b)
    print('ok')
