"""Builds the IWD-style (monster_icewind, E000) animation MHYD from the HoMM3 Chaos Hydra sheet."""
import sys,struct,json,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from extract import *
from PIL import Image
OUT=sys.argv[1]; SCALE=1.25
reg={int(k):v for k,v in json.load(open('reg.json')).items()}
rc,_,_,_=frame(REF); BASE=107; AXR=43
def placed(k):
    cm,sh,a,off=frame(k); dx,_=reg[k]
    ys,_=np.nonzero(cm); dy=BASE-ys.max()            # feet on the ground line
    t=np.zeros_like(a); t[cm]=a[cm]; t[...,3]=np.where(cm,255,0)
    s=np.zeros(cm.shape,np.uint8); s[sh&~cm]=255
    cx,cy=AXR-dx,BASE-dy
    im=Image.fromarray(t); sm=Image.fromarray(s)
    W,H=round(im.width*SCALE),round(im.height*SCALE)
    im=im.resize((W,H),Image.LANCZOS); sm=sm.resize((W,H),Image.NEAREST)
    return im,sm,round(cx*SCALE),round(cy*SCALE)
SD=list(range(0,11)); UP=list(range(17,24)); DN=list(range(24,34)); WK=list(range(34,45))
ST=list(range(54,61)); DE=list(range(61,67))
SEQS={'SD':SD,'SC':SD,'WK':WK,'A1':ST+ST[-2:0:-1],'A4':DN,'CA':UP+UP[-2:0:-1],'SP':UP+UP[-2:0:-1],
      'GH':[11,12,11],'DE':DE,'TW':[66,66],'SL':[66],'GU':DE[::-1]}
cache={}
def get(k,mirror):
    if (k,mirror) not in cache:
        im,sm,cx,cy=placed(k)
        if mirror:
            im=im.transpose(Image.FLIP_LEFT_RIGHT); sm=sm.transpose(Image.FLIP_LEFT_RIGHT); cx=im.width-1-cx
        cache[(k,mirror)]=(im,sm,cx,cy)
    return cache[(k,mirror)]
def write_bam(path,cycles):
    """cycles: list of lists of (k,mirror) (empty list = empty cycle)"""
    uniq=[]; idx={}
    for c in cycles:
        for f in c:
            if f not in idx: idx[f]=len(uniq); uniq.append(f)
    frames=[get(*f) for f in uniq]
    # shared palette: 0 transparent green, 1 shadow black, 2.. colours
    W=sum(f[0].width for f in frames); H=max(f[0].height for f in frames)
    sheet=Image.new('RGB',(W,H)); x=0
    for im,_,_,_ in frames: sheet.paste(im.convert('RGB'),(x,0),im); x+=im.width
    q=sheet.quantize(colors=254,method=Image.Quantize.MEDIANCUT); p=q.getpalette()[:254*3]; p+=[0]*(254*3-len(p))
    pal=bytearray(struct.pack('<4B',0,255,0,0)+struct.pack('<4B',0,0,0,0))
    for i in range(254): pal+=struct.pack('<4B',p[i*3+2],p[i*3+1],p[i*3],0)
    data=[]
    for im,sm,cx,cy in frames:
        qi=im.convert('RGB').quantize(palette=q,dither=Image.Dither.NONE)
        qa=np.array(qi,np.uint8)+2; al=np.array(im)[...,3]>=128; sh=np.array(sm)>0
        px=np.zeros(qa.shape,np.uint8); px[sh]=1; px[al]=qa[al]
        data.append((im.width,im.height,cx,cy,px.tobytes()))
    nfr=len(frames); ncy=len(cycles)
    fo=0x18; co=fo+12*nfr; po=co+4*ncy; lo=po+1024
    lut=[]; cyc=[]
    for c in cycles: cyc.append((len(c),len(lut) if c else 0)); lut+= [idx[f] for f in c]
    do=lo+2*len(lut)
    hdr=bytearray(b'BAM V1  '+struct.pack('<HBBIII',nfr,ncy,0,fo,po,lo))
    fb=bytearray(); blob=bytearray(); o=do
    for w,h,cx,cy,px in data:
        fb+=struct.pack('<HHhhI',w,h,cx,cy,o|0x80000000); blob+=px; o+=len(px)
    cb=b''.join(struct.pack('<HH',n,s) for n,s in cyc)
    out=hdr+fb+cb+pal+b''.join(struct.pack('<H',i) for i in lut)+blob
    open(path,'wb').write(out)
# directions: 0 S,1 SW,2 W,3 NW,4 N | E file: 5 NE,6 E,7 SE. The art faces east.
for s,ks in SEQS.items():
    orig=[(k,False) for k in ks]; mir=[(k,True) for k in ks]
    write_bam(f'{OUT}/mhyd{s.lower()}.bam',[orig,mir,mir,mir,mir])
    write_bam(f'{OUT}/mhyd{s.lower()}e.bam',[[],[],[],[],[],orig,orig,orig])
print('ok',len(cache))
