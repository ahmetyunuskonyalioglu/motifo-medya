# Crop the render area out of Motifo's white template (image + logo strip)
from PIL import Image
import numpy as np
def crop_render(path):
    im=Image.open(path).convert('RGB'); a=np.asarray(im.resize((im.width//10,im.height//10))).astype(int)
    nonwhite=(np.abs(a-255).sum(axis=2)>40)
    rows=nonwhite.mean(axis=1)>0.5; cols=nonwhite.mean(axis=0)>0.3
    # largest contiguous run of rows
    best=(0,0);s=None
    for i,v in enumerate(list(rows)+[False]):
        if v and s is None: s=i
        if not v and s is not None:
            if i-s>best[1]-best[0]: best=(s,i)
            s=None
    r0,r1=best
    sub=nonwhite[r0:r1]; c=np.where(sub.mean(axis=0)>0.5)[0]
    box=(c.min()*10+12,r0*10+12,(c.max()+1)*10-12,r1*10-12)
    return im.crop(box)
if __name__=='__main__':
    import sys
    for p in sys.argv[1:]:
        c=crop_render(p); print(p.split('/')[-1],c.size)
