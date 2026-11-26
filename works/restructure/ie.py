import struct,sys,os
def r8(b,o): return b[o:o+8].split(b'\0')[0].decode('latin1')
def effs(b,off,n):
    out=[]
    for i in range(n):
        o=off+i*0x30
        op,tg,pw,p1,p2,tm,rd,du,pr1,pr2=struct.unpack_from('<HBBiiBBIBB',b,o)
        res=r8(b,o+0x14); dn,ds,sv,sb,sp=struct.unpack_from('<IIIiI',b,o+0x1c)
        out.append(dict(op=op,tg=tg,p1=p1,p2=p2,tm=tm,rd=rd,du=du,pr=(pr1,pr2),res=res,dice=(dn,ds),sv=sv,sb=sb,sp=sp))
    return out
def spl(path):
    b=open(path,'rb').read()
    name,=struct.unpack_from('<i',b,8); fl,typ=struct.unpack_from('<IH',b,0x18); lvl,=struct.unpack_from('<I',b,0x34)
    ho,hn,eo,gi,gn=struct.unpack_from('<IHIHH',b,0x64)
    print(os.path.basename(path),'name',name,'flags',hex(fl),'type',typ,'lvl',lvl,'icon',r8(b,0x3a),'desc',struct.unpack_from('<i',b,0x50)[0])
    for e in effs(b,eo+gi*0x30,gn): print('  G',e)
    for h in range(hn):
        o=ho+h*0x28
        loc=b[o+2]; icon=r8(b,o+4); tgt=b[o+0xc]; rng,lv,ct=struct.unpack_from('<HHH',b,o+0xe); en,ei=struct.unpack_from('<HH',b,o+0x1e); pro,=struct.unpack_from('<H',b,o+0x26)
        print(f' H{h} loc{loc} icon {icon} tgt{tgt} rng{rng} lvl{lv} ct{ct} pro{pro}')
        for e in effs(b,eo+ei*0x30,en): print('   ',e)
if __name__=='__main__':
    for p in sys.argv[1:]: spl(p)
