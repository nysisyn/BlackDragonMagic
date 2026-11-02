"""Builds the IWD-style (monster_icewind, E000) hydra animation MHYD from the
Might and Magic VII hydra sheet (Hydra_MM7.png): 5 facings (rows), slate grey
variant obtained by the exact palette swap read from the standing frames."""
import sys,struct,zlib,os
import numpy as np
from PIL import Image
SHEET=sys.argv[1]; OUT=sys.argv[2]
SCALE=0.8; CELL=256; AX,AY=128,255          # anchor of every cell: bottom centre
A=np.array(Image.open(SHEET).convert('RGB')).astype(np.int32)
def cell(r,c): return A[r*CELL:(r+1)*CELL,c*CELL:(c+1)*CELL]
def fgmask(x): return ~((x[...,0]<60)&(x[...,1]>200)&(x[...,2]>200))
# slate palette swap: green (column 0) -> slate (column 1), same pose
SWAP={}
for r in range(5):
    g,s=cell(r,0),cell(r,1); m=fgmask(g)
    for a,b in zip(map(tuple,g[m]),map(tuple,s[m])): SWAP.setdefault(a,b)
def slate(x,m):
    y=x.copy()
    for i,j in zip(*np.nonzero(m)): y[i,j]=SWAP.get(tuple(x[i,j]),tuple(x[i,j]))
    return y
cache={}
def frame(r,c,mirror,breath=0):
    key=(r,c,mirror,breath)
    if key in cache: return cache[key]
    x=cell(r,c); m=fgmask(x)
    if c>=3: x=slate(x,m)
    else: x=cell(r,1)
    rgba=np.zeros((CELL,CELL,4),np.uint8); rgba[...,:3]=x; rgba[...,3]=np.where(m,255,0)
    im=Image.fromarray(rgba)
    ys,xs=np.nonzero(m)
    # shadow: flat ellipse under the feet
    sh=Image.new('L',(CELL,CELL),0)
    from PIL import ImageDraw
    w=(xs.max()-xs.min())*0.42; ImageDraw.Draw(sh).ellipse((AX-w,AY-14,AX+w,AY+6),fill=255)
    if breath:
        # idle breathing: body slightly stretched upwards from the feet
        k=1+0.02*np.sin(2*np.pi*breath/BREATH_N)
        H=round(CELL*k); st=im.resize((CELL,H),Image.LANCZOS)
        if H>CELL: st=st.crop((0,H-CELL,CELL,H)); H=CELL
        im=Image.new('RGBA',(CELL,CELL),(0,0,0,0)); im.paste(st,(0,CELL-H),st)
    if mirror: im=im.transpose(Image.FLIP_LEFT_RIGHT); sh=sh.transpose(Image.FLIP_LEFT_RIGHT)
    S=round(CELL*SCALE); im=im.resize((S,S),Image.LANCZOS); sh=sh.resize((S,S),Image.NEAREST)
    # crop to content
    bb=Image.fromarray(np.maximum(np.array(im)[...,3],np.array(sh))).getbbox()
    im=im.crop(bb); sh=sh.crop(bb)
    ax=(AX if not mirror else CELL-1-AX)*SCALE-bb[0]; ay=AY*SCALE-bb[1]
    cache[key]=(im,sh,round(ax),round(ay)); return cache[key]
# facings: rows 0 front, 1 front 3/4 (to the right), 2 profile (right), 3 back 3/4, 4 back
# IE order: 0 S, 1 SW, 2 W, 3 NW, 4 N (file XX) / 5 NE, 6 E, 7 SE (file XXE)
DIRS=[(0,False),(1,True),(2,True),(3,True),(4,False),(3,False),(2,False),(1,False)]
def rep(seq,n): return [c for c in seq for _ in range(n)]
BREATH_N=24
STAND=None                                  # built per direction in cycle()
READY=rep([1,3,4,3],3)
ATTACK=rep(list(range(3,12))+[1],2)
HIT=rep(list(range(12,18)),1)+[1]
WALK=list(range(18,26))
DEATH=list(range(3,8))                     # row 5, front only
SEQS={'SD':[],'SC':READY,'WK':WALK,'A1':ATTACK,'A2':ATTACK,'A3':ATTACK,'A4':ATTACK,
      'CA':ATTACK,'SP':ATTACK,'GH':HIT,'DE':DEATH,'TW':[7,7],'SL':[7],'GU':DEATH[::-1]}
DEATHLIKE={'DE','TW','SL','GU'}
def cycle(s,d):
    r,mir=DIRS[d]
    if s=='SD':
        # slow breathing (each step shown twice), and seen from the front the
        # sheet's own fidget (row 5, columns 9-12) once per cycle
        out=[(r,1,mir,b) for b in range(BREATH_N) for _ in range(2)]
        if r==0: out+=[(5,c,False,0) for c in rep([9,10,11,12,11,10,9],3)]
        return out
    if s in DEATHLIKE: return [(5,c,mir and d in (1,2,3)) for c in SEQS[s]]
    return [(r,c,mir) for c in SEQS[s]]
def write_bam(path,cycles):
    uniq=[];idx={}
    for c in cycles:
        for f in c:
            if f not in idx: idx[f]=len(uniq); uniq.append(f)
    frames=[frame(*f) for f in uniq]
    W=sum(f[0].width for f in frames); H=max(f[0].height for f in frames)
    sheet=Image.new('RGB',(W,H)); x=0
    for im,_,_,_ in frames: sheet.paste(im.convert('RGB'),(x,0),im); x+=im.width
    q=sheet.quantize(colors=254,method=Image.Quantize.MEDIANCUT); p=q.getpalette()[:254*3]; p+=[0]*(254*3-len(p))
    pal=bytearray(struct.pack('<4B',0,255,0,0)+struct.pack('<4B',0,0,0,0))
    for i in range(254): pal+=struct.pack('<4B',p[i*3+2],p[i*3+1],p[i*3],0)
    data=[]
    for im,sm,cx,cy in frames:
        qa=np.array(im.convert('RGB').quantize(palette=q,dither=Image.Dither.NONE),np.uint8)+2
        al=np.array(im)[...,3]>=128; sh=np.array(sm)>0
        px=np.zeros(qa.shape,np.uint8); px[sh]=1; px[al]=qa[al]
        data.append((im.width,im.height,cx,cy,px.tobytes()))
    nfr=len(frames); ncy=len(cycles); fo=0x18; po=fo+12*nfr+4*ncy; lo=po+1024
    lut=[];cyc=[]
    for c in cycles: cyc.append((len(c),len(lut) if c else 0)); lut+=[idx[f] for f in c]
    do=lo+2*len(lut)
    out=bytearray(b'BAM V1  '+struct.pack('<HBBIII',nfr,ncy,0,fo,po,lo)); blob=bytearray(); o=do
    for w,h,cx,cy,px in data: out+=struct.pack('<HHhhI',w,h,cx,cy,o|0x80000000); blob+=px; o+=len(px)
    out+=b''.join(struct.pack('<HH',n,s) for n,s in cyc)+pal+b''.join(struct.pack('<H',i) for i in lut)+blob
    open(path,'wb').write(b'BAMCV1  '+struct.pack('<I',len(out))+zlib.compress(bytes(out),9))
for s in SEQS:
    write_bam(f'{OUT}/mhyd{s.lower()}.bam',[cycle(s,d) for d in range(5)])
    write_bam(f'{OUT}/mhyd{s.lower()}e.bam',[[],[],[],[],[]]+[cycle(s,d) for d in (5,6,7)])
print('frames',len(cache))
