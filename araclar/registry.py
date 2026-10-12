import sys,json,glob,os
from PIL import Image
import numpy as np
def dhash(p,n=16):
    im=Image.open(p).convert('L').resize((n+1,n),Image.LANCZOS)
    a=np.asarray(im,dtype=np.int16); b=(a[:,1:]>a[:,:-1]).flatten()
    return ''.join('1' if x else '0' for x in b)
def dist(a,b): return sum(x!=y for x,y in zip(a,b))
if __name__=='__main__':
    reg_path=sys.argv[1]; files=sys.argv[2:]
    reg=json.load(open(reg_path)) if os.path.exists(reg_path) else {"used":[]}
    for f in files:
        reg["used"].append({"file":os.path.basename(f),"dhash":dhash(f),"source":"instagram_arsivi_2025-2026"})
    json.dump(reg,open(reg_path,'w'),indent=1,ensure_ascii=False); print(len(reg["used"]))
