"""Minimal BAM V1 / BAMC reader and writer (Infinity Engine)."""
import struct
import zlib

import numpy as np


class Frame:
    def __init__(self, w, h, cx, cy, pix, rle=True):
        self.w, self.h, self.cx, self.cy = w, h, cx, cy
        self.pix = pix  # numpy uint8 array (h, w) of palette indices
        self.rle = rle


class Bam:
    def __init__(self):
        self.frames = []
        self.cycles = []  # list of lists of frame indices
        self.palette = np.zeros((256, 4), np.uint8)  # RGBA
        self.rle_index = 0

    # ------------------------------------------------------------ reading
    @classmethod
    def load(cls, path):
        data = open(path, 'rb').read()
        if data[:4] == b'BAMC':
            data = zlib.decompress(data[12:])
        if data[:8] != b'BAM V1  ':
            raise ValueError('not BAM V1: %r' % data[:8])
        b = cls()
        nframes, ncycles, b.rle_index = struct.unpack_from('<HBB', data, 8)
        fe_off, pal_off, flt_off = struct.unpack_from('<III', data, 12)
        for i in range(256):
            bb, g, r, a = data[pal_off + 4 * i: pal_off + 4 * i + 4]
            b.palette[i] = (r, g, bb, a)
        entries = []
        for i in range(nframes):
            w, h, cx, cy, off = struct.unpack_from('<HHhhI', data, fe_off + 12 * i)
            entries.append((w, h, cx, cy, off))
        cyc_off = fe_off + 12 * nframes
        flt_len = 0
        cyc = []
        for i in range(ncycles):
            cnt, idx = struct.unpack_from('<HH', data, cyc_off + 4 * i)
            cyc.append((cnt, idx))
            flt_len = max(flt_len, idx + cnt)
        flt = struct.unpack_from('<%dH' % flt_len, data, flt_off)
        b.cycles = [list(flt[idx:idx + cnt]) for cnt, idx in cyc]
        for w, h, cx, cy, off in entries:
            rle = not (off & 0x80000000)
            off &= 0x7fffffff
            n = w * h
            if not rle:
                pix = np.frombuffer(data, np.uint8, n, off).copy()
            else:
                out = bytearray()
                p = off
                c = b.rle_index
                while len(out) < n:
                    v = data[p]
                    p += 1
                    if v == c:
                        out.extend(bytes([c]) * (data[p] + 1))
                        p += 1
                    else:
                        out.append(v)
                pix = np.frombuffer(bytes(out[:n]), np.uint8).copy()
            b.frames.append(Frame(w, h, cx, cy, pix.reshape(h, w) if n else np.zeros((h, w), np.uint8), rle))
        return b

    def rgba(self, fi):
        """RGBA image of a frame (index 0 = transparent)."""
        f = self.frames[fi]
        pal = self.palette.copy()
        # EE: alpha 0 means opaque
        pal[:, 3] = np.where(pal[:, 3] == 0, 255, pal[:, 3])
        pal[0] = (0, 0, 0, 0)
        return pal[f.pix]

    # ------------------------------------------------------------ writing
    def save(self, path, compress=True):
        nframes = len(self.frames)
        ncycles = len(self.cycles)
        header = 0x18
        fe_off = header
        cyc_off = fe_off + 12 * nframes
        pal_off = cyc_off + 4 * ncycles
        flt = []
        cyc_entries = []
        for c in self.cycles:
            cyc_entries.append((len(c), len(flt)))
            flt.extend(c)
        flt_off = pal_off + 1024
        data_off = flt_off + 2 * len(flt)
        blobs = []
        offs = []
        cur = data_off
        c = self.rle_index
        for f in self.frames:
            raw = f.pix.astype(np.uint8).tobytes()
            enc = bytearray()
            i = 0
            n = len(raw)
            while i < n:
                v = raw[i]
                if v == c:
                    j = i
                    while j < n and raw[j] == c and j - i < 256:
                        j += 1
                    enc.append(c)
                    enc.append(j - i - 1)
                    i = j
                else:
                    enc.append(v)
                    i += 1
            if len(enc) < len(raw):
                offs.append(cur)
                blob = bytes(enc)
            else:
                offs.append(cur | 0x80000000)
                blob = raw
            blobs.append(blob)
            cur += len(blob)
        out = bytearray()
        out += b'BAM V1  '
        out += struct.pack('<HBB', nframes, ncycles, c)
        out += struct.pack('<III', fe_off, pal_off, flt_off)
        for f, o in zip(self.frames, offs):
            out += struct.pack('<HHhhI', f.w, f.h, f.cx, f.cy, o)
        for cnt, idx in cyc_entries:
            out += struct.pack('<HH', cnt, idx)
        for r, g, bb, a in self.palette:
            out += bytes((bb, g, r, a))
        out += struct.pack('<%dH' % len(flt), *flt)
        for blob in blobs:
            out += blob
        if compress:
            out = b'BAMCV1  ' + struct.pack('<I', len(out)) + zlib.compress(bytes(out), 9)
        open(path, 'wb').write(out)
