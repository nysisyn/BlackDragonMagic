"""Extract resources from the game's BIF archives (chitin.key)."""
import struct

GAME = '/mnt/user-data/uploads/BG1-2/BIO/BG2 - Test/'
TYPES = {'bam': 0x3e8, 'vvc': 0x3fb, 'pro': 0x3fd, 'spl': 0x3ee}


def _key():
    d = open(GAME + 'chitin.key', 'rb').read()
    nb, nr, bo, ro = struct.unpack_from('<IIII', d, 8)
    bifs = []
    for i in range(nb):
        ln, fo, fl, loc = struct.unpack_from('<IIHH', d, bo + 12 * i)
        bifs.append(d[fo:fo + fl].rstrip(b'\0').decode())
    res = {}
    for i in range(nr):
        name = d[ro + 14 * i:ro + 14 * i + 8].rstrip(b'\0').decode().upper()
        t, loc = struct.unpack_from('<HI', d, ro + 14 * i + 8)
        res[(name, t)] = loc
    return bifs, res


def extract(name, ext):
    bifs, res = _key()
    loc = res[(name.upper(), TYPES[ext])]
    path = GAME + bifs[loc >> 20]
    bd = open(path, 'rb').read()
    assert bd[:8] == b'BIFFV1  ', bd[:8]
    nf, nt, fo = struct.unpack_from('<III', bd, 8)
    for j in range(nf):
        l, off, sz, typ = struct.unpack_from('<IIIH', bd, fo + 16 * j)
        if (l & 0x3fff) == (loc & 0x3fff):
            return bd[off:off + sz]
    raise KeyError(name)


if __name__ == '__main__':
    for n, e in (('SPBDRAE2', 'bam'), ('SPBDIMSP', 'bam'), ('DDBREAT', 'pro')):
        data = extract(n, e)
        open('%s.%s' % (n.lower(), e), 'wb').write(data)
        print(n, e, len(data), data[:8])
