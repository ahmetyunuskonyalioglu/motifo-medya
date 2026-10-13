# Fotoğrafa birebir oturan BİM röntgen katmanı: hayalet cephe + mavi kenarlar + taşıyıcı + büyüyen tesisat
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
def ease(t): t=min(1,max(0,t)); return t*t*(3-2*t)
def lerp(a,b,u): return (a[0]+(b[0]-a[0])*u, a[1]+(b[1]-a[1])*u)
def base_ghost(photo,S=1.0):
    a=np.asarray(photo.convert('RGB')).astype(np.float32)
    g=a.mean(2,keepdims=True)
    ghost=0.30*g+0.70*np.array([236,242,249],np.float32)
    ghost=ghost*np.ones((1,1,3))
    gray=cv2.GaussianBlur(cv2.cvtColor(a.astype(np.uint8),cv2.COLOR_RGB2GRAY),(0,0),1.1*S)
    e=cv2.Canny(gray,35,100,L2gradient=True).astype(np.float32)/255
    e=cv2.GaussianBlur(e,(0,0),0.55*S); e=np.clip(e*1.4,0,1)[...,None]
    blue=np.array([52,104,176],np.float32)
    m=Image.new('L',photo.size,60); dm=ImageDraw.Draw(m)
    dm.polygon([(x*S,y*S) for x,y in [(0,0),(482,0),(482,560),(0,605)]],fill=255)
    dm.polygon([(x*S,y*S) for x,y in [(482,60),(600,0),(890,150),(872,492),(482,500)]],fill=255)
    dm.polygon([(x*S,y*S) for x,y in [(330,470),(870,455),(870,600),(700,740),(330,740)]],fill=70)   # mobilya
    m=np.asarray(m.filter(ImageFilter.GaussianBlur(6*S))).astype(np.float32)[...,None]/255
    e=e*m; ghost=ghost*m+np.array([242,246,251],np.float32)*(1-m)*0.9+ghost*(1-m)*0.1
    out=ghost*(1-0.75*e)+blue*0.75*e
    return Image.fromarray(out.clip(0,255).astype(np.uint8))
# --- geometri (kaynak foto piksel koordinatları, 1060x741) ---
SLABS=[  # (sol nokta, sağ nokta, kalınlık) — kat döşemeleri ve temel
  ((0,180),(462,204),48),     # sol blok 1. kat döşemesi (balkon bandı)
  ((585,312),(842,345),16),   # sağ blok 1. kat döşemesi
  ((585,104),(842,200),18),   # sağ blok çatı döşemesi
  ((0,598),(462,560),22),     # sol blok zemin/temel
  ((585,497),(865,486),18)]   # sağ blok zemin/temel
COLS=[((8,20),(8,600),26),((468,20),(468,560),20),((560,100),(560,497),34),((852,200),(852,486),16)]
# tesisat: (renk, nokta listesi, kalınlık, t0, t1)
RED=(214,64,52); BLU=(46,108,214); GRN=(52,150,96); YEL=(226,176,40)
PIPES=[
 (GRN,[(478,700),(478,560),(478,0)],9,0.00,0.45),                  # pis su kolonu
 (BLU,[(548,520),(548,497),(548,110)],7,0.05,0.45),                # soğuk su kolonu
 (RED,[(572,520),(572,497),(572,110)],7,0.10,0.50),                # sıcak su kolonu
 (BLU,[(548,330),(842,365)],6,0.42,0.75),                          # sağ kat dalı
 (RED,[(572,340),(842,374)],6,0.48,0.80),
 (BLU,[(462,282),(20,256)],6,0.45,0.82),                           # sol kat dalı (tavan altı)
 (RED,[(462,292),(20,266)],6,0.50,0.88),
 (YEL,[(455,306),(60,284)],10,0.55,0.95),                          # havalandırma kanalı
 (GRN,[(478,610),(1000,640)],8,0.30,0.70),                         # bahçe drenajı (zemin altı)
 (YEL,[(842,382),(600,354)],9,0.60,0.98)]
def _poly_len(pts):
    return sum(np.hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(pts,pts[1:]))
def _partial(pts,u):
    L=_poly_len(pts)*u; out=[pts[0]]
    for a,b in zip(pts,pts[1:]):
        l=np.hypot(b[0]-a[0],b[1]-a[1])
        if L>=l: out.append(b); L-=l
        else: out.append(lerp(a,b,L/max(l,1e-6))); break
    return out
def draw_layer(size,prog,S=1.0,ox=0,oy=0):
    """prog 0..1 tesisat büyüme. S/ox/oy: kaynak→hedef dönüşümü. RGBA döner."""
    W,H=size; im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im,'RGBA')
    P=lambda p:((p[0]-ox)*S,(p[1]-oy)*S)
    for (a,b,th) in SLABS:   # döşeme: koyu kesit + tarama
        a2,b2=P(a),P(b); t=th*S
        d.polygon([a2,b2,(b2[0],b2[1]+t),(a2[0],a2[1]+t)],fill=(70,74,82,95),outline=(30,34,40,200))
    for (a,b,w) in COLS:
        a2,b2=P(a),P(b); w2=w*S
        d.rectangle([a2[0]-w2/2,a2[1],a2[0]+w2/2,b2[1]],fill=(70,74,82,95),outline=(30,34,40,190))
    for (col,pts,th,t0,t1) in PIPES:
        u=ease((prog-t0)/(t1-t0))
        if u<=0: continue
        q=[P(p) for p in _partial(pts,u)]; w=max(2,int(th*S))
        d.line(q,fill=col+(255,),width=w,joint='curve')
        hl=tuple(min(255,c+70) for c in col)
        d.line(q,fill=hl+(200,),width=max(1,w//3),joint='curve')
        if u<1:
            x,y=q[-1]; r=w*0.9; d.ellipse([x-r,y-r,x+r,y+r],fill=(255,255,255,230),outline=col+(255,))
    return im
