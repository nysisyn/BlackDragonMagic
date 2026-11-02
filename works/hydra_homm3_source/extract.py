from PIL import Image
import numpy as np
from scipy import ndimage
im=Image.open('/mnt/user-data/uploads/Creatures/Hydra.png').convert('RGBA')
A=np.array(im); alpha=A[...,3]>0; rgb=A[...,:3].astype(int)
black=alpha&(rgb.sum(-1)<30); col=alpha&~black
boxes=np.load('boxes.npy')
clab,_=ndimage.label(ndimage.binary_dilation(col,iterations=4))
alab,_=ndimage.label(ndimage.binary_dilation(alpha,iterations=1))
aobj=ndimage.find_objects(alab)
def frame(k):
    y0,x0,y1,x1=boxes[k]
    cid=np.bincount(clab[y0:y1,x0:x1][col[y0:y1,x0:x1]]).argmax()
    cm=col&(clab==cid)
    # shadow: black pixels in alpha components touching cm, excluding the long bars
    sh=np.zeros_like(black)
    ids=set(np.unique(alab[ndimage.binary_dilation(cm,iterations=2)]))-{0}
    for i in ids:
        s=aobj[i-1]
        if s[1].stop-s[1].start>170: continue
        sh|=black&(alab==i)
    m=cm|sh
    ys,xs=np.nonzero(m); Y0,Y1,X0,X1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
    return cm[Y0:Y1,X0:X1],sh[Y0:Y1,X0:X1],A[Y0:Y1,X0:X1],(X0,Y0)
def anchor(cm,off):
    # foot line: lowest coloured row; x: centroid of coloured pixels in the 25 lowest rows
    ys,xs=np.nonzero(cm); yb=ys.max()
    sel=ys>=yb-25
    return off[0]+xs[sel].mean(), off[1]+yb
REF=17
def register(k):
    """offset (dx,dy) in sheet coords so that frame k's lower body matches the reference's"""
    rc,_,_,ro=frame(REF); fc,_,_,fo=frame(k)
    H=rc.shape[0]; low=np.zeros_like(rc); low[int(H*0.55):,:]=rc[int(H*0.55):,:]
    best=(-1,0,0)
    fh,fw=fc.shape
    for dy in range(-30,31):
        for dx in range(-40,41):
            # place frame so that its origin is at reference origin + (dx,dy)
            y0=max(0,dy); x0=max(0,dx); y1=min(low.shape[0],dy+fh); x1=min(low.shape[1],dx+fw)
            if y1<=y0 or x1<=x0: continue
            s=(low[y0:y1,x0:x1]&fc[y0-dy:y1-dy,x0-dx:x1-dx]).sum()
            if s>best[0]: best=(s,dx,dy)
    return best
SEQ={'SD':list(range(0,11)),'GH':[11,12],'RD':[13,14,15,16],'UP':list(range(17,24)),'DN':list(range(24,34)),
     'WK':list(range(34,45)),'ST':list(range(54,61)),'DE':list(range(61,67))}
