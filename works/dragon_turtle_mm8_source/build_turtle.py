"""Builds the IWD-style (monster_icewind, E000) black dragon turtle animation
MDTU from the Might and Magic VIII dragon turtle sheet: 5 facings (rows),
recoloured black (green shell scales desaturated and darkened)."""
import sys,struct,zlib,os
import numpy as np
from PIL import Image
SHEET=sys.argv[1]; OUT=sys.argv[2]
SCALE=0.75; CELL=256; AX,AY=128,178         # anchor (ground): the middle of the body, a flat creature lies on its circle
A=np.array(Image.open(SHEET).convert('RGB')).astype(np.int32)
def cell(r,c): return A[r*CELL:(r+1)*CELL,c*CELL:(c+1)*CELL]
def fgmask(x): return ~(((x[...,1]-x[...,0])>70)&((x[...,2]-x[...,0])>70)&(x[...,1]>150))   # cyan and its blends
def blacken(x):
    """black dragon turtle: green / olive scales desaturated and darkened"""
    hsv=np.array(Image.fromarray(x.astype(np.uint8)).convert('HSV')).astype(float)
    h,s,v=hsv[...,0],hsv[...,1],hsv[...,2]
    green=(h>30)&(h<130)&(s>40)
    s=np.where(green,s*0.25,s*0.6); v=np.where(green,v*0.55,v*0.85)
    out=np.stack([h,s,np.clip(v,0,255)],-1).astype(np.uint8)
    return np.array(Image.fromarray(out,'HSV').convert('RGB')).astype(np.int32)
from scipy import ndimage
def keep_creature(m):
    """drops what is not the creature (credits text, ripper's portrait)"""
    lab,n=ndimage.label(ndimage.binary_dilation(m,iterations=2))
    if n<=1: return m
    sizes=ndimage.sum(m,lab,range(1,n+1)); big=int(np.argmax(sizes))+1
    return m&(lab==big)
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
    w=(xs.max()-xs.min())*0.38
    if c not in GROUND: ImageDraw.Draw(sh).ellipse((AX-w,AY-9,AX+w,AY+9),fill=255)
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
    if c in GROUND:                           # dying / dead: lies on its circle, as the living body
        ay=(ys.mean()+8)*SCALE-bb[1]
    cache[key]=(im,sh,round(ax),round(ay)); return cache[key]
# facings: rows 0 front, 1 front 3/4 (to the right), 2 profile (right), 3 back 3/4, 4 back
# IE order: 0 S, 1 SW, 2 W, 3 NW, 4 N (file XX) / 5 NE, 6 E, 7 SE (file XXE)
DIRS=[(0,False),(1,True),(2,True),(3,True),(4,False),(3,False),(2,False),(1,False)]
def rep(seq,n): return [c for c in seq for _ in range(n)]
IDLE=rep([25,26,27,28,29,28,27,26],3)                   # slow flipper sway
WALK=[9,10,11,12,13,12,11,10]                           # swimming strokes
BITE=rep([0,1,2,2,1,0],2)
SLAM=rep([14,15,16,17,18,0],2)                          # rears up and crashes down
LUNGE=rep([19,20,21,22,23,24,0],2)                      # pulls the head back, lunges (breath)
SEQS={'SD':IDLE,'SC':IDLE,'WK':WALK,'A1':BITE,'A2':SLAM,'A3':BITE,'A4':SLAM,
      'CA':LUNGE,'SP':LUNGE,'GH':rep([20,21,22,21,20],2),'DE':rep([6,7,8],3),'TW':[8,8],'SL':[8],'GU':rep([8,7,6],3)}
GROUND.update({6,7,8})
def cycle(s,d):
    r,mir=DIRS[d]
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
    write_bam(f'{OUT}/mdtu{s.lower()}.bam',[cycle(s,d) for d in range(5)])
    write_bam(f'{OUT}/mdtu{s.lower()}e.bam',[[],[],[],[],[]]+[cycle(s,d) for d in (5,6,7)])
print('frames',len(cache))
