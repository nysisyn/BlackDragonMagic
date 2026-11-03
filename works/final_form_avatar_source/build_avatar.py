"""Builds the IWD-style (monster_icewind, E000) animation MBDA of the Black
Dragon Disciple's final form (Nysi's own avatar) from the V4 FULL sheets:
idle, walk, cast, wings, claw, claw2, tail, buffet, hit, death; 8 rows = 8
drawn directions, 8 frames per row.
Attacks: A1 claw, A2 double claw, A3 tail, A4 wing buffet.
Usage: build_avatar.py v4_full <out dir>"""
import sys,struct,zlib,os
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from extract import frames,frames_rows
SRC=sys.argv[1]; OUT=sys.argv[2] if len(sys.argv)>2 else None
SCALE=0.50                                      # 0.72 reduced by 30%
SHEETS=[n for n in ('idle','walk','cast','wings','claw','claw2','tail','buffet','hit','death') if os.path.exists(os.path.join(SRC,n+'.png'))]
F={}
for n in SHEETS:
    f=frames(os.path.join(SRC,n+'.png'))
    if len(set(c for r,c in f))!=8: f=frames_rows(os.path.join(SRC,n+'.png'))   # sprites touching side by side
    F[n]=f
# horizontal anchor of each sheet row: where the feet stand (bottom of the sprite)
def feet(m):
    ys,xs=np.nonzero(m); low=ys>=ys.max()-max(4,(ys.max()-ys.min())//10)
    return xs[low].mean()
# Frames of one row are not drawn at exactly the same place: in every sheet
# where the feet stay planted, each frame is registered on a reference frame
# of its row by matching the legs (lowest 40 % of the body), shift searched
# pixel by pixel; walk (legs moving) and death (falling) use their own feet.
REG_REF={'idle':1}
REG_SKIP=('walk','death')
def legs_mask(m,X0,Y0,H):
    ys,xs=np.nonzero(m); top=ys.max()-int((ys.max()-ys.min())*0.4)
    sel=ys>=top; return set(zip((ys[sel]+Y0).tolist(),(xs[sel]+X0).tolist()))
REG={}
def anchor(sheet,r,c):
    """(x,y) of the ground point in cell coordinates"""
    if (sheet,r,c) in REG: return REG[(sheet,r,c)]
    rgb,m,(X0,Y0)=F[sheet][(r,c)]; X0=int(round(X0))
    rc=REG_REF.get(sheet,0)
    if sheet in REG_SKIP or c==rc:
        a=(X0+feet(m),Y0+m.shape[0])
    else:
        ax,ay=anchor(sheet,r,rc)
        _,mr,(RX,RY)=F[sheet][(r,rc)]
        ref=np.zeros((400,400),bool); cur=np.zeros((400,400),bool)
        def put(A,mm,x,y):
            ys,xs=np.nonzero(mm); top=ys.max()-int((ys.max()-ys.min())*0.4); k=ys>=top
            A[ys[k]+y-int(RY)+120,xs[k]+x-int(round(RX))+120]=True
        put(ref,mr,int(round(RX)),int(RY)); put(cur,m,X0,int(Y0))
        best=(-1,0,0)
        for dy in range(-8,9):
            sh_y=np.roll(ref,dy,0)
            for dx in range(-16,17):
                v=(np.roll(sh_y,dx,1)&cur).sum()
                if v>best[0]: best=(v,dx,dy)
        a=(ax+best[1],ay+best[2])
    REG[(sheet,r,c)]=a; return a
XR={}
for n in F:
    for r in range(8):
        XR[(n,r)]=float(np.median([F[n][(r,c)][2][0]+feet(F[n][(r,c)][1]) for c in range(3)]))
cache={}
def frame(sheet,r,c,breath=0,flip=False):
    key=(sheet,r,c,breath,flip)
    if key in cache: return cache[key]
    rgb,m,(X0,Y0)=F[sheet][(r,c)]
    h,w=m.shape
    rgba=np.zeros((h,w,4),np.uint8); rgba[...,:3]=rgb; rgba[...,3]=np.where(m,255,0)
    im=Image.fromarray(rgba)
    if flip: im=im.transpose(Image.FLIP_LEFT_RIGHT)
    if breath:
        k=1+0.02*np.sin(2*np.pi*breath/BREATH_N); H=round(h*k)
        st=im.resize((w,H),Image.LANCZOS); im=Image.new('RGBA',(w,H),(0,0,0,0)); im.paste(st,(0,0),st); h=H
    # AI sheets do not keep a regular grid: each frame is anchored on its own
    # feet, except while falling (death), anchored where the feet stood
    if sheet=='death': cx=XR[(sheet,r)]-X0; cy=h-2
    else:
        ax,ay=anchor(sheet,r,c); cx=ax-int(round(X0)); cy=ay-Y0-2+(h-m.shape[0])
    if flip: cx=w-cx                                   # feet on the ground
    # canvas with room for the shadow
    pad=20; can=Image.new('RGBA',(w+2*pad,h+pad),(0,0,0,0)); can.paste(im,(pad,0),im)
    sh=Image.new('L',can.size,0); sw=max(18,w*0.33)
    ImageDraw.Draw(sh).ellipse((pad+cx-sw,cy-7,pad+cx+sw,cy+6),fill=255)
    S=(round(can.width*SCALE),round(can.height*SCALE))
    im=can.resize(S,Image.LANCZOS); sh=sh.resize(S,Image.NEAREST)
    # readability at small size: light sharpening of the colours only
    a=im.getchannel('A'); im=im.convert('RGB').filter(ImageFilter.UnsharpMask(radius=1.2,percent=70,threshold=2)); im.putalpha(a)
    bb=Image.fromarray(np.maximum(np.array(im)[...,3],np.array(sh))).getbbox()
    im=im.crop(bb); sh=sh.crop(bb)
    cache[key]=(im,sh,round((pad+cx)*SCALE-bb[0]),round(cy*SCALE-bb[1])); return cache[key]
# IE directions 0 S,1 SW,2 W,3 NW,4 N,5 NE,6 E,7 SE -> sheet rows (front, SE, E, NE, back, NW, W, SW)
# V4 sheets: row 1 faces front-left and row 7 front-right (swapped), and row 6
# (left profile) faces right like row 2: the left profile is row 2 mirrored.
ROW=[(0,0),(1,0),(2,1),(5,0),(4,0),(3,0),(2,0),(7,0)]
BREATH_N=24
def rep(seq,n): return [x for x in seq for _ in range(n)]
IDLE=list(range(1,8))+list(range(6,1,-1))                     # back and forth, loops smoothly (frame 0 differs)
SEQS={
 'SD':[('idle',c) for c in rep(IDLE,3)],                      # calm: shoulders and arms only
 'SC':[('idle',c) for c in rep(IDLE,2)],
 'WK':[('walk',c) for c in range(8)],
 'A1':[('claw',c) for c in rep(range(8),2)],
 'A2':[('claw2',c) for c in rep(range(8),2)],
 'A3':[('tail',c) for c in rep(range(8),2)],
 'A4':[('buffet',c) for c in rep(range(8),2)],
 'CA':[('cast',c) for c in rep(range(8),2)],                  # hands raised
 'SP':[('wings',c) for c in rep(range(8),2)],                 # wings spread (powers)
 'GH':[('hit',c) for c in range(8)],                           # hit recoil
 'DE':[('death',c) for c in rep(range(8),2)],
 'TW':[('death',7)]*2,'SL':[('death',7)],
 'GU':[('death',c) for c in rep(range(7,-1,-1),2)]}

# The AI idle frames are not drawn consistently (the silhouette changes by
# 10-20 % from one frame to the next), which reads as wobbling in game.
# SD: the most typical frame of the row (smallest total difference to the
# others) with a slow breathing; SC: the three most alike frames, back and forth.
import itertools
def silhouettes(sheet,r,fl):
    out=[]
    for c in range(8):
        im,_,cx,cy=frame(sheet,r,c,0,fl); A=np.zeros((200,200),bool)
        a=np.array(im)[...,3]>128; A[160-cy:160-cy+a.shape[0],100-cx:100-cx+a.shape[1]]=a; out.append(A)
    return out
def diff(a,b): return 1-(a&b).sum()/(a|b).sum()
def idle_frames(r,fl):
    C=silhouettes('idle',r,fl)
    med=min(range(8),key=lambda i:sum(diff(C[i],C[j]) for j in range(8)))
    tri=min(itertools.combinations(range(8),3),key=lambda t:max(diff(C[a],C[b]) for a,b in itertools.combinations(t,2)))
    return med,tri
def cycle(s,d):
    r,fl=ROW[d]
    if s in ('SD','SC'):
        med,tri=idle_frames(r,fl)
        if s=='SD': return [('idle',r,med,b,fl) for b in range(BREATH_N) for _ in range(2)]
        a,b,c=tri; return [('idle',r,x,0,fl) for x in rep([a,b,c,b],4)]
    return [(sh,r,c,0,fl) for sh,c in SEQS[s]]
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
        write_bam(f'{OUT}/mbda{s.lower()}.bam',[cycle(s,d) for d in range(5)])
        write_bam(f'{OUT}/mbda{s.lower()}e.bam',[[],[],[],[],[]]+[cycle(s,d) for d in (5,6,7)])
    print('frames',len(cache))
