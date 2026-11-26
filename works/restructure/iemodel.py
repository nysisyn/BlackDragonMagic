"""Minimal SPL/ITM read/write model (V1 / EE), effects kept as raw 0x30 records."""
import struct
EFF=0x30
class Res:
    def __init__(self,path):
        b=bytearray(open(path,'rb').read()); self.sig=bytes(b[:8]); self.kind=self.sig[:4]
        if self.kind==b'SPL ':
            self.hsize=0x28; self.hfix=0x72 if len(b)>=0x72 else 0x72
            ho,hn,eo,gi,gn=struct.unpack_from('<IHIHH',b,0x64); self.base=bytearray(b[:0x72])
        elif self.kind==b'ITM ':
            self.hsize=0x38
            ho,hn,eo,gi,gn=struct.unpack_from('<IHIHH',b,0x64); self.base=bytearray(b[:0x72])
        else: raise ValueError(path)
        self.glob=[bytearray(b[eo+(gi+i)*EFF:eo+(gi+i+1)*EFF]) for i in range(gn)]
        self.heads=[]
        for h in range(hn):
            hb=bytearray(b[ho+h*self.hsize:ho+(h+1)*self.hsize])
            if self.kind==b'SPL ': en,ei=struct.unpack_from('<HH',hb,0x1e)
            else: en,ei=struct.unpack_from('<HH',hb,0x1e)
            self.heads.append([hb,[bytearray(b[eo+(ei+i)*EFF:eo+(ei+i+1)*EFF]) for i in range(en)]])
    def save(self,path):
        b=bytearray(self.base); ho=0x72; hn=len(self.heads)
        eo=ho+hn*self.hsize
        effs=[]; hb_all=bytearray()
        # global effects first (index 0..gn-1) as weidu does
        effs+=self.glob
        for hb,el in self.heads:
            hb=bytearray(hb); struct.pack_into('<HH',hb,0x1e,len(el),len(effs)); effs+=el; hb_all+=hb
        struct.pack_into('<IHIHH',b,0x64,ho,hn,eo,0,len(self.glob))
        open(path,'wb').write(b+hb_all+b''.join(effs))
    def all_effects(self):
        for e in self.glob: yield e
        for hb,el in self.heads:
            for e in el: yield e
def eop(e): return struct.unpack_from('<H',e,0)[0]
def ep2(e): return struct.unpack_from('<i',e,8)[0]
def eres(e): return e[0x14:0x1c].split(b'\0')[0].decode('latin1')
def set_res(e,r): e[0x14:0x1c]=r.encode('latin1').ljust(8,b'\0')
def mk_eff(op,tg=1,p1=0,p2=0,tm=0,rd=0,du=0,res='',dn=0,ds=0,sv=0,sb=0,sp=0,pr1=100,pr2=0,power=0):
    e=bytearray(EFF)
    struct.pack_into('<HBBiiBBIBB',e,0,op,tg,power,p1,p2,tm,rd,du,pr1,pr2)
    set_res(e,res); struct.pack_into('<IIIiI',e,0x1c,dn,ds,sv,sb,sp); return e

def cre_refs(b):
    out=set()
    for o in (0x34,0x3c,0x248,0x250,0x258,0x260,0x268,0x2cc): out.add(b[o:o+8].split(b'\0')[0].decode('latin1'))
    io,ic=struct.unpack_from('<II',b,0x2bc)
    for i in range(ic): out.add(b[io+i*0x14:io+i*0x14+8].split(b'\0')[0].decode('latin1'))
    ko,kc=struct.unpack_from('<II',b,0x2a0)
    for i in range(kc): out.add(b[ko+i*12:ko+i*12+8].split(b'\0')[0].decode('latin1'))
    mo,mc=struct.unpack_from('<II',b,0x2b0)
    for i in range(mc): out.add(b[mo+i*12:mo+i*12+8].split(b'\0')[0].decode('latin1'))
    eo,ec=struct.unpack_from('<II',b,0x2c4)
    v2=b[0x33]==1
    for i in range(ec):
        if v2: o=eo+i*0x108; out.add(b[o+0x28:o+0x30].split(b'\0')[0].decode('latin1')); out.add(b[o+0x68:o+0x70].split(b'\0')[0].decode('latin1'))
    return {x for x in out if x}
