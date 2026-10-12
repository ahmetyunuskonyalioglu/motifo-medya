# Logo kapanışı v4: orijinal altın logo (renklere dokunulmaz), yavaşça belirir; dağınık silik amblem filigranları; SESSİZ
import sys,os
from PIL import Image,ImageFilter
import numpy as np, cv2
S='/tmp/claude-0/-home-claude/8c2bb08b-0d28-593e-b9c3-4c3ec033f7cb/scratchpad/'
W,H,FPS=1080,1920,30; DUR=float(os.environ.get('DUR','4.6'))
src=Image.open(S+'brand/orijinal/logo_altin.png').convert('RGBA')
A=np.asarray(src)[...,3]; L=np.asarray(src.convert('L'))
ys,xs=np.where((A>200)&(L>110)); bx0,by0,bx1,by1=xs.min(),ys.min(),xs.max(),ys.max()
m=700
logo=src.crop((max(0,bx0-m),max(0,by0-m),min(src.width,bx1+m),min(src.height,by1+m)))
# kenarlara doğru gölgeyi yumuşakça söndür (renklere dokunmadan sadece alfa)
r_,g_,b_,a_=logo.split(); aa=np.asarray(a_).astype(np.float32)
hh,ww=aa.shape; yy,xx=np.mgrid[0:hh,0:ww]
d=np.minimum.reduce([xx,yy,ww-1-xx,hh-1-yy]).astype(np.float32)
aa*=np.clip(d/450,0,1)**1.5
logo=Image.merge('RGBA',(r_,g_,b_,Image.fromarray(aa.astype(np.uint8))))
sc=820/(bx1-bx0); logo=logo.resize((int(logo.width*sc),int(logo.height*sc)),Image.LANCZOS)
def ease(t): t=min(1,max(0,t)); return t*t*(3-2*t)
def seg(t,a,b): return min(1,max(0,(t-a)/(b-a)))
AM0=Image.open(S+'brand/amblem_siyah.png').split()[3]
def emb_layers(size,angle,depth):
    a=AM0.resize((size,int(size*AM0.height/AM0.width)),Image.LANCZOS).rotate(angle,resample=Image.BICUBIC,expand=True)
    a=np.asarray(a.filter(ImageFilter.GaussianBlur(1.6))).astype(np.float32)/255
    hi=np.roll(np.roll(a,-depth,0),-depth,1); sh=np.roll(np.roll(a,depth,0),depth,1)
    return a,hi,sh
rng=np.random.default_rng(29)
PLACES=[(150,240,300),(930,190,240),(560,95,180),(80,760,260),(1010,700,330),(250,1500,320),(880,1430,280),
        (540,1780,230),(1040,1080,200),(30,1160,210),(690,1640,160),(360,330,150),(760,420,170),(120,1840,190),(980,1880,170)]
WMS=[]
for i,(x,y,sz) in enumerate(PLACES):
    ang=float(rng.uniform(0,360)); a,hi,sh=emb_layers(sz,ang,2 if sz<220 else 3)
    WMS.append((x,y,a,hi,sh,float(rng.uniform(0.0,1.6))))
def background(t):
    base=np.ones((H,W,3),np.float32)
    for (x,y,a,hi,sh,t0) in WMS:
        k=ease(seg(t,t0,t0+2.4))
        if k<=0: continue
        sc_=0.93+0.07*k
        lay=-(np.clip(sh-a,0,1)*0.075*k+a*0.009*k)[...,None]*np.array([0.9,0.86,0.78])[None,None,:]+(np.clip(hi-a,0,1)*0.05*k)[...,None]
        lay=cv2.resize(lay,(max(1,int(lay.shape[1]*sc_)),max(1,int(lay.shape[0]*sc_))),interpolation=cv2.INTER_LINEAR)
        h_,w_=lay.shape[:2]; px=int(x-w_/2); py=int(y-h_/2)
        x0,y0=max(0,px),max(0,py); x1,y1=min(W,px+w_),min(H,py+h_)
        if x1>x0 and y1>y0: base[y0:y1,x0:x1]+=lay[y0-py:y1-py,x0-px:x1-px]
    return Image.fromarray((np.clip(base,0,1)*255).astype(np.uint8)).convert('RGBA')
def frame(t):
    bg=background(t)
    f=ease(seg(t,0.35,2.9))                 # yavaş beliriş
    if f>0:
        z=0.965+0.035*ease(seg(t,0.35,DUR))   # çok yavaş yaklaşma
        lg=logo.resize((int(logo.width*z),int(logo.height*z)),Image.LANCZOS)
        blur=6*(1-ease(seg(t,0.35,2.4)))
        if blur>0.3: lg=lg.filter(ImageFilter.GaussianBlur(blur))
        r,g,b,a=lg.split(); a=a.point(lambda v:int(v*f)); lg=Image.merge('RGBA',(r,g,b,a))
        bg.alpha_composite(lg,(W//2-lg.width//2,H//2-lg.height//2-20))
    return bg.convert('RGB')
if __name__=='__main__':
    out=sys.argv[1]; os.makedirs(out,exist_ok=True)
    N=int(DUR*FPS)
    for i in range(N): frame(i/FPS).save(f'{out}/f{i:04d}.jpg',quality=95)
    print('ok',N)
