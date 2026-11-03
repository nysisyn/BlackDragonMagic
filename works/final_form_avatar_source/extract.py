import numpy as np
from PIL import Image
from scipy import ndimage
def load(n):
    A=np.array(Image.open(n).convert('RGB')).astype(np.int32)
    fg=(A[...,0]**2+(A[...,1]-255)**2+(A[...,2]-255)**2)>90**2
    # pixels blended with the cyan background: greyed
    cy=(A[...,1]>A[...,0]+35)&(A[...,2]>A[...,0]+35)&fg
    g=(A[...,0]*0.3+A[...,1]*0.4+A[...,2]*0.3).astype(np.int32)*0.6
    A[cy]=np.stack([g,g,g],-1).astype(np.int32)[cy]
    return A,fg
CWF=CHF=None
def frames(n):
    """{(row,col): (rgb crop, mask crop, (x0,y0))} - 8 rows x 6 columns.
    Per column: the 8 big blobs sorted from top to bottom; two touching
    sprites (fewer than 8 blobs) are split at the thinnest row between them;
    small pieces go to the nearest sprite."""
    global CWF,CHF
    A,fg=load(n); out={}; CHF=A.shape[0]/8
    # columns: the groups of the horizontal projection, cut halfway between
    cols=fg.any(0); runs=np.diff(np.concatenate([[0],cols.astype(int),[0]]))
    st=np.nonzero(runs==1)[0]; en=np.nonzero(runs==-1)[0]
    groups=[(a,b) for a,b in zip(st,en) if b-a>20]
    cuts=[0]+[(groups[i][1]+groups[i+1][0])//2 for i in range(len(groups)-1)]+[A.shape[1]]
    for c in range(len(groups)):
        x0=cuts[c]; strip=fg[:,x0:cuts[c+1]]
        lab,k=ndimage.label(ndimage.binary_dilation(strip,iterations=1)); lab=lab*strip
        blobs=[];small=[]
        for i in range(1,k+1):
            m=lab==i; (blobs if m.sum()>=800 else small).append(m)
        while len(blobs)<8:
            j=max(range(len(blobs)),key=lambda q:np.ptp(np.nonzero(blobs[q])[0]))
            m=blobs.pop(j); yi=np.nonzero(m)[0]; y0,y1=yi.min(),yi.max()
            cnt=m.sum(1); lo=y0+int((y1-y0)*0.3); hi=y0+int((y1-y0)*0.7)
            cut=lo+int(np.argmin(cnt[lo:hi]))
            a=m.copy(); a[cut:]=False; b=m.copy(); b[:cut]=False
            blobs+=[a,b]
        blobs.sort(key=lambda m:np.nonzero(m)[0].mean())
        blobs=blobs[:8] if len(blobs)==8 else sorted(blobs,key=lambda m:-m.sum())[:8]
        blobs.sort(key=lambda m:np.nonzero(m)[0].mean())
        cents=[np.array(np.nonzero(m)).mean(1) for m in blobs]
        for m in small:
            p=np.array(np.nonzero(m)).mean(1)
            j=int(np.argmin([np.linalg.norm(p-q) for q in cents]))
            if np.linalg.norm(p-cents[j])<70: blobs[j]=blobs[j]|m
        for r,m in enumerate(blobs):
            m=ndimage.binary_erosion(m)                  # 1 px of background blend off
            ys2,xs2=np.nonzero(m); Y0,Y1,X0,X1=ys2.min(),ys2.max()+1,xs2.min(),xs2.max()+1
            out[(r,c)]=(A[Y0:Y1,x0+X0:x0+X1],m[Y0:Y1,X0:X1],(X0,Y0))
    return out
