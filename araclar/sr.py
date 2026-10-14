# Real-ESRGAN (realesr-general-x4v3, SRVGGNetCompact) — torch'suz, numpy ile x4 süper çözünürlük
# Ağırlık: https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth → /home/claude/models/
import zipfile,pickle,numpy as np,os
from numpy.lib.stride_tricks import sliding_window_view
MODEL='/home/claude/models/realesr-general-x4v3.pth'
_W=None
def _load():
    z=zipfile.ZipFile(MODEL); names=z.namelist(); root=names[0].split('/')[0]
    class Storage:
        def __init__(s,key,dtype): s.key=key; s.dtype=dtype
    DT={'FloatStorage':np.float32,'HalfStorage':np.float16}
    def rebuild(storage,offset,size,stride,*a):
        buf=np.frombuffer(z.read(f'{root}/data/{storage.key}'),dtype=storage.dtype)
        if not size: return np.array(buf[offset:offset+1],dtype=np.float32)
        arr=np.lib.stride_tricks.as_strided(buf[offset:],shape=size,strides=[s*buf.itemsize for s in stride])
        return np.array(arr,dtype=np.float32)
    class U(pickle.Unpickler):
        def find_class(s,mod,name):
            if name=='_rebuild_tensor_v2': return rebuild
            if name in DT: return name
            if mod=='collections' and name=='OrderedDict':
                import collections; return collections.OrderedDict
            return super().find_class(mod,name)
        def persistent_load(s,pid):
            _,typ,key,loc,n=pid; return Storage(key,DT[typ])
    sd=U(z.open(f'{root}/data.pkl')).load()
    sd=sd.get('params_ema',sd.get('params',sd))
    L=[]; i=0
    while f'body.{i}.weight' in sd:
        w=sd[f'body.{i}.weight']
        L.append(('conv',w,sd[f'body.{i}.bias']) if w.ndim==4 else ('prelu',w,None)); i+=1
    return L
def _conv(x,w,b):
    xp=np.pad(x,((1,1),(1,1),(0,0)),mode='edge')
    v=sliding_window_view(xp,(3,3),axis=(0,1))       # H,W,C,3,3
    H,W_,C=x.shape
    wm=w.transpose(1,2,3,0).reshape(C*9,-1)
    return (np.ascontiguousarray(v).reshape(H*W_,C*9)@wm+b).reshape(H,W_,-1).astype(np.float32)
def _net(x):
    global _W
    if _W is None: _W=_load()
    h=x
    for t,w,b in _W:
        h=_conv(h,w,b) if t=='conv' else np.where(h>=0,h,h*w)
    H,W_,_=h.shape
    h=h.reshape(H,W_,3,4,4).transpose(0,3,1,4,2).reshape(H*4,W_*4,3)   # pixel_shuffle
    return h+np.repeat(np.repeat(x,4,0),4,1)
def x4(img,tile=96,pad=10):
    from PIL import Image
    a=np.asarray(img.convert('RGB')).astype(np.float32)/255; H,W_,_=a.shape
    out=np.zeros((H*4,W_*4,3),np.float32)
    for y in range(0,H,tile):
        for x in range(0,W_,tile):
            y0,x0=max(0,y-pad),max(0,x-pad); y1,x1=min(H,y+tile+pad),min(W_,x+tile+pad)
            r=_net(a[y0:y1,x0:x1]); oy,ox=(y-y0)*4,(x-x0)*4; th,tw=min(tile,H-y)*4,min(tile,W_-x)*4
            out[y*4:y*4+th,x*4:x*4+tw]=r[oy:oy+th,ox:ox+tw]
    return Image.fromarray((np.clip(out,0,1)*255+0.5).astype(np.uint8))
def buyut(path,cache_dir='/home/claude/sr_cache'):
    """Kaynak görseli (şablon kırpılmış) x4 büyütüp önbellekler; yolu döner."""
    import sys,hashlib; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from cropframe import crop_render
    os.makedirs(cache_dir,exist_ok=True); k=hashlib.md5(path.encode()).hexdigest()[:12]; out=f'{cache_dir}/{k}.jpg'
    if not os.path.exists(out): x4(crop_render(path)).save(out,quality=95)
    return out
