"""Dracolisk animation (NYDL) from the game's basilisk (MBAS, BG1 'monster_old').

For each of MBASG1, MBASG1E, MBASG2, MBASG2E:
  - palette index 0 stays transparent, index 1 stays the engine's shadow;
  - the body is tinted almost black (luminance x 0.13, a slight green cast);
  - every frame is enlarged x1.5 (Scale2x, then Lanczos down to x1.5),
    centres scaled too;
  - a 1-pixel acid-green outline is drawn around the body (opaque: palette
    BAMs have no partial transparency);
  - one 256-colour palette per BAM (0 transparent, 1 shadow, 2-3 outline,
    the rest the body), cycles and frame order kept as they are.
Writes NYDLG1.BAM ... NYDLG2E.BAM (BAMC) and a preview GIF.
Usage: build_dracolisk.py <folder with mbas*.bam> <output folder>
"""
import os, struct, sys, zlib
from PIL import Image, ImageFilter

SCALE = 1.5
DARK = 0.13
OUTLINE = [(70, 200, 70), (40, 120, 40)]       # outer, inner


def load(path):
    d = open(path, 'rb').read()
    if d[:4] == b'BAMC':
        d = zlib.decompress(d[12:])
    nf, nc, ck = struct.unpack_from('<HBB', d, 8)
    fo, po, lo = struct.unpack_from('<III', d, 12)
    pal = [struct.unpack_from('<BBBB', d, po + i * 4) for i in range(256)]
    frames = []
    for i in range(nf):
        w, h, cx, cy, off = struct.unpack_from('<HHhhI', d, fo + i * 12)
        rle = not (off & 0x80000000); p = off & 0x7fffffff; px = []
        while len(px) < w * h:
            v = d[p]; p += 1
            if rle and v == ck:
                px += [ck] * (d[p] + 1); p += 1
            else:
                px.append(v)
        frames.append((w, h, cx, cy, px[:w * h]))
    cycles = [struct.unpack_from('<HH', d, fo + nf * 12 + i * 4) for i in range(nc)]
    nlut = max((c[0] + c[1] for c in cycles), default=0)
    lut = [struct.unpack_from('<H', d, lo + j * 2)[0] for j in range(nlut)]
    return pal, frames, cycles, lut, ck


def scale2x(im):
    w, h = im.size; s = im.load(); o = Image.new(im.mode, (w * 2, h * 2)); d = o.load()
    for y in range(h):
        for x in range(w):
            P = s[x, y]; A = s[x, y - 1] if y else P; B = s[x + 1, y] if x < w - 1 else P
            C = s[x - 1, y] if x else P; D = s[x, y + 1] if y < h - 1 else P
            d[2*x, 2*y] = C if C == A and C != D and A != B else P
            d[2*x+1, 2*y] = A if A == B and A != C and B != D else P
            d[2*x, 2*y+1] = C if D == C and D != B and C != A else P
            d[2*x+1, 2*y+1] = B if B == D and B != A and D != C else P
    return o


def tint(rgb):
    r, g, b = rgb
    l = 0.3 * r + 0.59 * g + 0.11 * b
    return (int(l * DARK * 0.95), int(l * DARK * 1.1), int(l * DARK * 0.9))


def big_frame(fr, pal, ck):
    """-> (w, h, cx, cy, body RGBA image, shadow mask L, outline masks)"""
    w, h, cx, cy, px = fr
    # pad by 2 so the outline fits
    W, H = w + 4, h + 4
    rgb = Image.new('RGBA', (W, H)); shadow = Image.new('L', (W, H))
    rd, sd = rgb.load(), shadow.load()
    for i, v in enumerate(px):
        x, y = i % w + 2, i // w + 2
        if v == ck:
            continue
        if v == 1:
            sd[x, y] = 255
        else:
            b, g, r, _ = pal[v]
            rd[x, y] = tint((r, g, b)) + (255,)
    nw, nh = max(1, round(W * SCALE)), max(1, round(H * SCALE))
    body = scale2x(rgb).resize((nw, nh), Image.LANCZOS)
    a = body.split()[3].point(lambda v: 255 if v >= 128 else 0)
    body.putalpha(a)
    shad = scale2x(shadow).resize((nw, nh), Image.NEAREST).point(lambda v: 255 if v >= 128 else 0)
    ring1 = Image.eval(a.filter(ImageFilter.MaxFilter(3)), lambda v: v)
    out1 = Image.composite(Image.new('L', a.size, 0), ring1, a)          # 1px ring outside the body
    inner = Image.composite(a, Image.new('L', a.size, 0), Image.eval(a.filter(ImageFilter.MinFilter(3)), lambda v: 255 - v))
    return (nw, nh, round((cx + 2) * SCALE), round((cy + 2) * SCALE), body, shad, out1, inner)


def build(src, dst, name):
    pal, frames, cycles, lut, ck = load(src)
    bigs = [big_frame(f, pal, ck) for f in frames]
    # one palette for all bodies of this BAM
    strip_w = sum(b[0] for b in bigs); strip_h = max(b[1] for b in bigs)
    strip = Image.new('RGB', (strip_w, strip_h), (0, 0, 0)); x = 0
    mask = Image.new('L', (strip_w, strip_h))
    for b in bigs:
        strip.paste(b[4].convert('RGB'), (x, 0)); mask.paste(b[4].split()[3], (x, 0)); x += b[0]
    pix = [p for p, m in zip(strip.getdata(), mask.getdata()) if m]
    sample = Image.new('RGB', (len(pix), 1)); sample.putdata(pix)
    q = sample.quantize(colors=252, method=Image.MEDIANCUT)
    qpal = q.getpalette()[:252 * 3]
    newpal = [(0, 255, 0), (0, 0, 0)] + OUTLINE + [tuple(qpal[i:i + 3]) for i in range(0, len(qpal), 3)]
    newpal += [(0, 0, 0)] * (256 - len(newpal))
    out = []
    for nw, nh, cx, cy, body, shad, out1, inner in bigs:
        qb = body.convert('RGB').quantize(palette=q, dither=Image.NONE)
        qd = qb.load(); ad = body.split()[3].load(); sd = shad.load(); od = out1.load(); idd = inner.load()
        idx = []
        for y in range(nh):
            for x in range(nw):
                if ad[x, y]:
                    idx.append(3 if idd[x, y] else qd[x, y] + 4)
                elif od[x, y]:
                    idx.append(2)
                elif sd[x, y]:
                    idx.append(1)
                else:
                    idx.append(0)
        out.append((nw, nh, cx, cy, idx))
    write_bam(dst, newpal, out, cycles, lut)
    return newpal, out, cycles, lut


def rle(idx):
    o = bytearray(); i = 0
    while i < len(idx):
        if idx[i] == 0:
            n = 0
            while i + n < len(idx) and idx[i + n] == 0 and n < 256:
                n += 1
            o += bytes((0, n - 1)); i += n
        else:
            o.append(idx[i]); i += 1
    return bytes(o)


def write_bam(path, pal, frames, cycles, lut):
    nf, nc = len(frames), len(cycles)
    fo = 0x18; po = fo + nf * 12 + nc * 4; lo = po + 1024; do = lo + len(lut) * 2
    head = bytearray(b'BAM V1  ' + struct.pack('<HBBIII', nf, nc, 0, fo, po, lo))
    fe = bytearray(); data = bytearray()
    for w, h, cx, cy, idx in frames:
        fe += struct.pack('<HHhhI', w, h, cx, cy, do + len(data)); data += rle(idx)
    ce = b''.join(struct.pack('<HH', *c) for c in cycles)
    pe = b''.join(struct.pack('<BBBB', b, g, r, 0) for r, g, b in pal)
    le = b''.join(struct.pack('<H', v) for v in lut)
    raw = bytes(head + fe + ce + pe + le + data)
    open(path, 'wb').write(b'BAMCV1  ' + struct.pack('<I', len(raw)) + zlib.compress(raw, 9))


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    for part in ('G1', 'G1E', 'G2', 'G2E'):
        build(os.path.join(src, f'mbas{part.lower()}.bam'), os.path.join(dst, f'nydl{part.lower()}.bam'), part)
        print('ok', part)
