"""Builds the IWD-style (monster_icewind, E000) gorgon animation MGOR from the
Might and Magic VIII gorgon sheet (JPEG, 34 cells of 235.3 px per row):
5 facings (rows), dark iron variant: the animations exist only in green, so
they are recoloured with a colour table learnt from the green standing frame
(column 22) and the dark one of the same pose (column 32)."""
import sys,struct,zlib,os
import numpy as np
from PIL import Image
SHEET=sys.argv[1]; OUT=sys.argv[2]
SCALE=0.85; CELL=315; AX,AY=158,234         # anchor: cell bottom centre
A=np.array(Image.open(SHEET).convert('RGB')).astype(np.int32)
CWF=A.shape[1]/34; CHF=A.shape[0]/5; M=40; CS=235
def cell(r,c):
    # the cell with a margin on each side (tails overlap the next cells)
    y=round(r*CHF); x=round(c*CWF)
    out=np.zeros((CELL,CELL,3),np.int32); out[...]= (0,255,255)
    src=A[y:y+CS, max(0,x-M):x+CS+M]
    ox=M-(x-max(0,x-M))
    out[:src.shape[0], ox:ox+src.shape[1]]=src[:, :CELL-ox]
    return out
def fgmask(x): return (x[...,0]**2+(x[...,1]-255)**2+(x[...,2]-255)**2)>90**2   # cyan, JPEG noise included
# colour table green -> dark iron, learnt from the same pose (columns 22 / 32)
Q=8
def _lut():
    sums=np.zeros((256//Q,)*3+(3,)); cnt=np.zeros((256//Q,)*3)
    for r in range(5):
        g=cell(r,22); d=cell(r,32); m=fgmask(g)&fgmask(d)
        idx=g[m]//Q
        np.add.at(sums,(idx[:,0],idx[:,1],idx[:,2]),d[m]); np.add.at(cnt,(idx[:,0],idx[:,1],idx[:,2]),1)
    filled=cnt>0
    lut=np.zeros_like(sums); lut[filled]=sums[filled]/cnt[filled][:,None]
    # empty bins: the nearest filled one
    from scipy import ndimage as nd
    _,ind=nd.distance_transform_edt(~filled,return_indices=True)
    return lut[ind[0],ind[1],ind[2]]
LUT=None
def blacken(x):
    global LUT
    if LUT is None: LUT=_lut()
    i=np.clip(x//Q,0,256//Q-1)
    y=LUT[i[...,0],i[...,1],i[...,2]].astype(np.int32)
    # JPEG edges blended with the cyan background: made grey
    cy=(y[...,1]>y[...,0]+30)&(y[...,2]>y[...,0]+30)
    g=(y[...,0]*0.3+y[...,1]*0.45+y[...,2]*0.25).astype(np.int32)
    y[cy]=np.stack([g,g,g+8],-1)[cy]
    return y
from scipy import ndimage
def keep_creature(m):
    """keeps the creature of the cell: the largest blob whose centre is in the
    cell (not the neighbours' tails, the credits or the ripper's portrait)"""
    lab,n=ndimage.label(ndimage.binary_dilation(m,iterations=2))
    best=0; bs=0
    for i in range(1,n+1):
        ys,xs=np.nonzero(m&(lab==i))
        if len(xs)<150: continue
        if not (M<=xs.mean()<M+CS): continue
        if ys.max()<0.7*CS: continue            # credits, ripper's portrait
        if len(xs)>bs: bs=len(xs); best=i
    return m&(lab==best)
GROUND=set()                                  # frames lying on the ground (death)
cache={}
def frame(r,c,mirror,breath=0):
    key=(r,c,mirror,breath)
    if key in cache: return cache[key]
    x=cell(r,c); m=keep_creature(fgmask(x)); m=ndimage.binary_erosion(m); x=blacken(x)   # 1 px of JPEG fringe off
    rgba=np.zeros((CELL,CELL,4),np.uint8); rgba[...,:3]=x; rgba[...,3]=np.where(m,255,0)
    im=Image.fromarray(rgba)
    ys,xs=np.nonzero(m)
    # shadow: flat ellipse under the feet
    sh=Image.new('L',(CELL,CELL),0)
    from PIL import ImageDraw
    w=(xs.max()-xs.min())*0.35
    ImageDraw.Draw(sh).ellipse((AX-w,AY-8,AX+w,AY+6),fill=255)
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
SEQS={'SD':[],'SC':rep([12,13,14,15,16,15,14,13],2),'WK':list(range(23,31)),
      'A1':rep(list(range(0,7)),2),'A2':rep([17,18,19,20,21,22],2),
      'A3':rep(list(range(0,7)),2),'A4':rep([17,18,19,20,21,22],2),
      'CA':rep([17,18,19,19,19,20,21,22],2),'SP':rep([17,18,19,19,19,20,21,22],2),
      'GH':[4,4,4,5,6,22],'DE':rep(list(range(7,12)),2),'TW':[11,11],'SL':[11],'GU':rep(list(range(11,6,-1)),2)}
BREATH_N=24
def cycle(s,d):
    r,mir=DIRS[d]
    if s=='SD':     # slow breathing (standing frame stretched up to 2%)
        return [(r,22,mir,b) for b in range(BREATH_N) for _ in range(2)]
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
    write_bam(f'{OUT}/mgor{s.lower()}.bam',[cycle(s,d) for d in range(5)])
    write_bam(f'{OUT}/mgor{s.lower()}e.bam',[[],[],[],[],[]]+[cycle(s,d) for d in (5,6,7)])
print('frames',len(cache))
