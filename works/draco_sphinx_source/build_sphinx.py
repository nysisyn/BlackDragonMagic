"""Builds the IWD-style (monster_icewind, E000) black draco-sphinx animation
MDSX from three sheets (walk.png, attack.png, death.png): 8 rows = 8 drawn
directions, 6 frames per row."""
import sys,struct,zlib,os
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from extract import frames
SRC=sys.argv[1]; OUT=sys.argv[2] if len(sys.argv)>2 else None
SCALE=1.15
F={n:frames(os.path.join(SRC,n+'.png')) for n in ('walk','attack','death')}
# horizontal anchor of each row: where the body stands in the walk frames
XR={}
for r in range(8):
    xs=[]
    for c in range(6):
        rgb,m,(X0,Y0)=F['walk'][(r,c)]; xs.append(X0+np.nonzero(m)[1].mean())
    XR[r]=float(np.median(xs))
cache={}
def frame(sheet,r,c,breath=0):
    key=(sheet,r,c,breath)
    if key in cache: return cache[key]
    rgb,m,(X0,Y0)=F[sheet][(r,c)]
    h,w=m.shape
    rgba=np.zeros((h,w,4),np.uint8); rgba[...,:3]=rgb; rgba[...,3]=np.where(m,255,0)
    im=Image.fromarray(rgba)
    if breath:
        k=1+0.02*np.sin(2*np.pi*breath/BREATH_N); H=round(h*k)
        st=im.resize((w,H),Image.LANCZOS); im=Image.new('RGBA',(w,H),(0,0,0,0)); im.paste(st,(0,0),st); h=H
    cx=XR[r]-X0; cy=h-2                                   # feet on the ground
    # canvas with room for the shadow
    pad=30; can=Image.new('RGBA',(w+2*pad,h+pad),(0,0,0,0)); can.paste(im,(pad,0),im)
    sh=Image.new('L',can.size,0); sw=max(18,w*0.33)
    ImageDraw.Draw(sh).ellipse((pad+cx-sw,cy-7,pad+cx+sw,cy+6),fill=255)
    S=(round(can.width*SCALE),round(can.height*SCALE))
    im=can.resize(S,Image.LANCZOS); sh=sh.resize(S,Image.NEAREST)
    bb=Image.fromarray(np.maximum(np.array(im)[...,3],np.array(sh))).getbbox()
    im=im.crop(bb); sh=sh.crop(bb)
    cache[key]=(im,sh,round((pad+cx)*SCALE-bb[0]),round(cy*SCALE-bb[1])); return cache[key]
# IE directions 0 S,1 SW,2 W,3 NW,4 N,5 NE,6 E,7 SE -> sheet rows (front, SE, E, NE, back, NW, W, SW)
ROW=[0,7,6,5,4,3,2,1]
BREATH_N=24
def rep(seq,n): return [x for x in seq for _ in range(n)]
SEQS={
 'SD':None,
 'SC':[('attack',c) for c in rep([0,1,2,2,1,0],3)],          # paw raised, menacing
 'WK':[('walk',c) for c in range(6)],
 'A1':[('attack',c) for c in rep(range(6),2)],
 'CA':[('attack',c) for c in rep([0,3,4,4,4,3,0],2)],        # roar
 'GH':[('death',c) for c in [0,1,1,0]],                       # stagger
 'DE':[('death',c) for c in rep(range(6),2)],
 'TW':[('death',5)]*2,'SL':[('death',5)],
 'GU':[('death',c) for c in rep(range(5,-1,-1),2)]}
for a in ('A2','A3','A4'): SEQS[a]=SEQS['A1']
SEQS['SP']=SEQS['CA']
def cycle(s,d):
    r=ROW[d]
    if s=='SD': return [('walk',r,0,b) for b in range(BREATH_N) for _ in range(2)]
    return [(sh,r,c,0) for sh,c in SEQS[s]]
def write_bam(path,cycles):
    uniq=[];idx={}
    for cy in cycles:
        for f in cy:
            if f not in idx: idx[f]=len(uniq); uniq.append(f)
    frs=[frame(*f) for f in uniq]
    W=sum(f[0].width for f in frs); H=max(f[0].height for f in frs)
    sheet=Image.new('RGB',(W,H)); x=0
    for im,_,_,_ in frs: sheet.paste(im.convert('RGB'),(x,0),im); x+=im.width
    q=sheet.quantize(colors=254,method=Image.Quantize.MEDIANCUT); p=q.getpalette()[:254*3]; p+=[0]*(254*3-len(p))
    pal=bytearray(struct.pack('<4B',0,255,0,0)+struct.pack('<4B',0,0,0,0))
    for i in range(254): pal+=struct.pack('<4B',p[i*3+2],p[i*3+1],p[i*3],0)
    data=[]
    for im,sm,cx,cy in frs:
        qa=np.array(im.convert('RGB').quantize(palette=q,dither=Image.Dither.NONE),np.uint8)+2
        al=np.array(im)[...,3]>=128; sh=np.array(sm)>0
        px=np.zeros(qa.shape,np.uint8); px[sh]=1; px[al]=qa[al]
        data.append((im.width,im.height,cx,cy,px.tobytes()))
    nfr=len(frs); ncy=len(cycles); fo=0x18; po=fo+12*nfr+4*ncy; lo=po+1024
    lut=[];cyc=[]
    for cy in cycles: cyc.append((len(cy),len(lut) if cy else 0)); lut+=[idx[f] for f in cy]
    do=lo+2*len(lut)
    out=bytearray(b'BAM V1  '+struct.pack('<HBBIII',nfr,ncy,0,fo,po,lo)); blob=bytearray(); o=do
    for w,h,cx,cy,px in data: out+=struct.pack('<HHhhI',w,h,cx,cy,o|0x80000000); blob+=px; o+=len(px)
    out+=b''.join(struct.pack('<HH',n,s) for n,s in cyc)+pal+b''.join(struct.pack('<H',i) for i in lut)+blob
    open(path,'wb').write(b'BAMCV1  '+struct.pack('<I',len(out))+zlib.compress(bytes(out),9))
if OUT:
    for s in SEQS:
        write_bam(f'{OUT}/mdsx{s.lower()}.bam',[cycle(s,d) for d in range(5)])
        write_bam(f'{OUT}/mdsx{s.lower()}e.bam',[[],[],[],[],[]]+[cycle(s,d) for d in (5,6,7)])
    print('frames',len(cache))
