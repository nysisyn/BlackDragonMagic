"""Builds the IWD-style (monster_icewind, E000) dracockatrix animation MDCK from
the Might and Magic VIII thunder lizard sheet (JPEG, 37 cells of 216.2 px per
row): 5 facings (rows), half the size of the original, recoloured as a black
dragon (scales black, frill dark maroon)."""
import sys,struct,zlib,os
import numpy as np
from PIL import Image
SHEET=sys.argv[1]; OUT=sys.argv[2]
SCALE=0.59; CELL=296; AX,AY=148,215         # half the original size (the JPEG is 0.845 of it); anchor: cell bottom centre
A=np.array(Image.open(SHEET).convert('RGB')).astype(np.int32)
CWF=A.shape[1]/37; CHF=A.shape[0]/5; M=40
def cell(r,c):
    # the cell with a margin on each side (tails overlap the next cells)
    y=round(r*CHF); x=round(c*CWF)
    out=np.zeros((CELL,CELL,3),np.int32); out[...]= (0,255,255)
    src=A[y:y+216, max(0,x-M):x+216+M]
    ox=M-(x-max(0,x-M))
    out[:src.shape[0], ox:ox+src.shape[1]]=src[:, :CELL-ox]
    return out
def fgmask(x): return (x[...,0]**2+(x[...,1]-255)**2+(x[...,2]-255)**2)>90**2   # cyan, JPEG noise included
def blacken(x):
    """black dragon colours: scales black, the orange frill dark maroon"""
    hsv=np.array(Image.fromarray(x.astype(np.uint8)).convert('HSV')).astype(float)
    h,s,v=hsv[...,0],hsv[...,1],hsv[...,2]
    frill=((h<25)|(h>230))&(s>90)
    s=np.where(frill,s*0.7,s*0.25); v=np.where(frill,v*0.45,v*0.42)
    out=np.stack([h,s,np.clip(v,0,255)],-1).astype(np.uint8)
    return np.array(Image.fromarray(out,'HSV').convert('RGB')).astype(np.int32)
from scipy import ndimage
def keep_creature(m):
    """keeps the creature of the cell: the largest blob whose centre is in the
    cell (not the neighbours' tails, the credits or the ripper's portrait)"""
    lab,n=ndimage.label(ndimage.binary_dilation(m,iterations=2))
    best=0; bs=0
    for i in range(1,n+1):
        ys,xs=np.nonzero(m&(lab==i))
        if len(xs)<150: continue
        if not (M<=xs.mean()<M+216): continue
        if len(xs)>bs: bs=len(xs); best=i
    return m&(lab==best)
GROUND=set()                                  # frames lying on the ground (death)
cache={}
def frame(r,c,mirror,breath=0):
    key=(r,c,mirror,breath)
    if key in cache: return cache[key]
    x=cell(r,c); m=keep_creature(fgmask(x)); x=blacken(x)
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
SEQS={'SD':[],'SC':rep([14,15,16,17,18,17,16,15],2),'WK':list(range(26,34)),
      'A1':rep(list(range(19,25))+[0],2),'A2':rep(list(range(2,8))+[0],2),
      'A3':rep(list(range(19,25))+[0],2),'A4':rep(list(range(2,8))+[0],2),
      'CA':rep([14,15,16,17,18,18,17,16,15,14],2),'SP':rep([14,15,16,17,18,18,17,16,15,14],2),
      'GH':[8,8,8,0],'DE':rep(list(range(8,14)),2),'TW':[13,13],'SL':[13],'GU':rep(list(range(13,7,-1)),2)}
BREATH_N=24
def cycle(s,d):
    r,mir=DIRS[d]
    if s=='SD':     # slow breathing (standing frame stretched up to 2%)
        return [(r,0,mir,b) for b in range(BREATH_N) for _ in range(2)]
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
    write_bam(f'{OUT}/mdck{s.lower()}.bam',[cycle(s,d) for d in range(5)])
    write_bam(f'{OUT}/mdck{s.lower()}e.bam',[[],[],[],[],[]]+[cycle(s,d) for d in (5,6,7)])
print('frames',len(cache))
