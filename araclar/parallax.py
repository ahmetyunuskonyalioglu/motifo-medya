# 2.5D kamera: Depth Anything V2 ile derinlik + paralaks
import numpy as np, cv2, onnxruntime as ort
from PIL import Image
_sess=None
MODEL='/home/claude/models/da2s.onnx'
def depth(img):
    global _sess
    if _sess is None: _sess=ort.InferenceSession(MODEL,providers=['CPUExecutionProvider'])
    a=np.asarray(img.convert('RGB').resize((518,518),Image.BICUBIC)).astype(np.float32)/255
    a=(a-[0.485,0.456,0.406])/[0.229,0.224,0.225]
    d=_sess.run(None,{_sess.get_inputs()[0].name:a.transpose(2,0,1)[None].astype(np.float32)})[0][0]
    d=(d-np.percentile(d,2))/(np.percentile(d,98)-np.percentile(d,2)+1e-6)
    d=np.clip(d,0,1).astype(np.float32)
    d=cv2.resize(d,img.size,interpolation=cv2.INTER_CUBIC)
    d=cv2.GaussianBlur(d,(0,0),img.size[0]/300)   # yumuşat, yırtılma azalsın
    return d
def ease(t): t=min(1,max(0,t)); return t*t*(3-2*t)
def shot_frames(img,win,N,move,out=(1080,1920)):
    """img: PIL kaynak; win: (cx,cy) kaynakta dikey pencere merkezi (0-1) + zoom;
       move: dict(tx,ty,dolly,rot) — tümü kare boyunca 0->1 eased."""
    W,H=out; ov=1.14
    cx,cy,z=win
    ih=img.height/z; iw=ih*W/H
    x0=min(max(0,cx*img.width-iw/2),img.width-iw); y0=min(max(0,cy*img.height-ih/2),img.height-ih)
    big=(int(W*ov),int(H*ov))
    # pencereyi overscan ile al
    pad_w=iw*(ov-1)/2; pad_h=ih*(ov-1)/2
    bx0=max(0,x0-pad_w); by0=max(0,y0-pad_h); bx1=min(img.width,x0+iw+pad_w); by1=min(img.height,y0+ih+pad_h)
    src=img.crop((int(bx0),int(by0),int(bx1),int(by1))).resize(big,Image.LANCZOS)
    D=depth(src)
    S=np.asarray(src.convert('RGB'))
    gy,gx=np.mgrid[0:big[1],0:big[0]].astype(np.float32)
    cxp,cyp=big[0]/2,big[1]/2
    for i in range(N):
        p=ease(i/(N-1))-0.5   # -0.5..0.5 merkezli hareket
        tx=move.get('tx',0)*p*W; ty=move.get('ty',0)*p*H; dz=move.get('dolly',0)*(p+0.5)
        near=0.25+D           # uzak düzlem de biraz kayar
        sc=1+dz*(0.35+0.65*D)
        mx=(gx-cxp)/sc+cxp - tx*near
        my=(gy-cyp)/sc+cyp - ty*near
        f=cv2.remap(S,mx,my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
        ox=(big[0]-W)//2; oy=(big[1]-H)//2
        yield Image.fromarray(f[oy:oy+H,ox:ox+W])
