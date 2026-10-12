# Altın logo, beyaz zemin, lüks parıltı + kabaran silik amblem filigranı
import sys,os,math
from PIL import Image,ImageFilter,ImageChops
import numpy as np
S='/tmp/claude-0/-home-claude/8c2bb08b-0d28-593e-b9c3-4c3ec033f7cb/scratchpad/'
W,H,FPS=1080,1920,30; DUR=6.6
g=Image.open(S+'brand/orijinal/logo_altin.png').convert('RGBA')
sc=800/1636; g=g.resize((int(g.width*sc),int(g.height*sc)),Image.LANCZOS)
G=np.asarray(g).astype(np.float32)/255
alpha=G[...,3]; lum=G[...,:3].mean(2)
metal=(alpha>0.75)&(lum>0.45)
ys,xs=np.where(metal); bx0,by0,bx1,by1=xs.min(),ys.min(),xs.max(),ys.max()
ALPHA_M=np.clip((alpha-0.55)/0.4,0,1)*np.clip((lum-0.22)/0.18,0,1)
_a=Image.fromarray((ALPHA_M*255).astype(np.uint8))
SHADOW=np.asarray(_a.filter(ImageFilter.GaussianBlur(9))).astype(np.float32)/255
SHADOW=np.roll(np.roll(SHADOW,10,0),7,1)*0.22
ox=int(W/2-(bx0+bx1)/2); oy=int(H/2-(by0+by1)/2)-30
rows=metal.any(1); runs=[];s=None
for i,v in enumerate(list(rows)+[False]):
    if v and s is None:s=i
    if not v and s is not None:
        if i-s>3: runs.append((s,i))
        s=None
print('row runs',runs)
# beklenen: amblem, kıvrım, MOTİFO, alt yazı(lar)
big=sorted(runs,key=lambda r:r[1]-r[0],reverse=True)
EMB=big[0]; WM=big[1]
rest=[r for r in runs if r not in (EMB,WM)]
SW=[r for r in rest if r[0]<WM[0] and r[0]>EMB[1]]
SUB=[r for r in rest if r[0]>WM[1]]
SUBR=(min(r[0] for r in SUB),max(r[1] for r in SUB)) if SUB else (WM[1]+5,WM[1]+5)
SWR=(min(r[0] for r in SW),max(r[1] for r in SW)) if SW else (EMB[1],WM[0])
cols=metal[WM[0]:WM[1]].any(0); letters=[];s=None
for i,v in enumerate(list(cols)+[False]):
    if v and s is None:s=i
    if not v and s is not None:
        if i-s>4: letters.append((s,i))
        s=None
print('letters',len(letters),'EMB',EMB,'WM',WM,'SW',SWR,'SUB',SUBR)
ey,ex=np.where(metal[EMB[0]:EMB[1]]); ecx=(ex.min()+ex.max())/2; ecy=EMB[0]+(EMB[1]-EMB[0])/2; er=(ex.max()-ex.min())/2
yy,xx=np.mgrid[0:g.height,0:g.width].astype(np.float32)
ang=(np.degrees(np.arctan2(xx-ecx,-(yy-ecy)))+360)%360; rad=np.hypot(xx-ecx,yy-ecy)
def ease(t): t=min(1,max(0,t)); return t*t*(3-2*t)
def seg(t,a,b): return min(1,max(0,(t-a)/(b-a)))
# bölge maskeleri (gölge dahil, satır bantlarıyla)
pad=18
def band(r0,r1): m=np.zeros(alpha.shape,np.float32); m[max(0,r0-pad):r1+pad]=1; return m
mEMB=band(*EMB); mWM=band(*WM); mSW=band(*SWR); mSUB=band(*SUBR)
mEMB[EMB[1]+pad:]=0
ring=(rad>er*0.90)
# filigran: büyük kabartma amblem
am=Image.open(S+'brand/amblem_siyah.png').split()[3]
am=am.resize((1240,int(1240*am.height/am.width)),Image.LANCZOS)
def emboss_layer(depth):
    a=np.asarray(am).astype(np.float32)/255
    a=np.asarray(Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.5))).astype(np.float32)/255
    d=max(1,int(depth))
    hi=np.roll(np.roll(a,-d,0),-d,1); sh=np.roll(np.roll(a,d,0),d,1)
    return a,hi,sh
EA,EH,ES=emboss_layer(4)
def watermark(t):
    k=ease(seg(t,0.0,DUR-0.6))          # zamanla kabarır
    scale=1.06-0.06*k
    base=np.ones((H,W,3),np.float32)
    # çok hafif sıcak degrade
    yv=np.linspace(0,1,H)[:,None,None]; base-= (0.018*yv+0.004)*np.array([0.2,0.5,1.0])[None,None,:]
    sh_=np.clip(ES-EA,0,1)*0.075*k; hi_=np.clip(EH-EA,0,1)*0.05*k; fill=EA*0.010*k
    lay=np.zeros((ES.shape[0],ES.shape[1],3),np.float32)
    lay[...]=-(sh_+fill)[...,None]*np.array([0.9,0.85,0.75])[None,None,:]
    lay+=hi_[...,None]
    li=Image.fromarray(((lay+0.5)*255).clip(0,255).astype(np.uint8))
    nw=int(li.width*scale); li=li.resize((nw,int(li.height*scale)),Image.BICUBIC)
    L=np.asarray(li).astype(np.float32)/255-0.5
    px=W//2-nw//2; py=H//2-li.height//2-60
    x0,y0=max(0,px),max(0,py); x1,y1=min(W,px+nw),min(H,py+li.height)
    base[y0:y1,x0:x1]+=L[y0-py:y1-py,x0-px:x1-px]
    return np.clip(base,0,1)
def logo_mask(t):
    M=np.zeros(alpha.shape,np.float32)
    span=(letters[-1][1]-letters[0][0])
    for (c0,c1) in letters:
        st=0.75+(c0-letters[0][0])/span*1.2
        lt=seg(t,st,st+0.45)
        if lt>0:
            m=np.zeros_like(M); m[:,max(0,c0-pad):c1+pad]=1
            # soldan sağa yumuşak silme
            edge=c0-pad+(c1-c0+2*pad)*ease(lt*1.3)
            soft=np.clip((edge-xx)/14,0,1)
            M=np.maximum(M,m*mWM*soft)
    sw=ease(seg(t,2.0,2.6))
    if sw>0: M=np.maximum(M,mSW*np.clip((bx0+(bx1-bx0)*sw-xx)/30+0,0,1)*(xx>bx0-5))
    rp=ease(seg(t,1.2,2.5))
    if rp>0: M=np.maximum(M,mEMB*ring*(1.0 if rp>=0.999 else np.clip((rp*362-ang)/6,0,1)))
    ip=ease(seg(t,2.0,3.2))
    if ip>0:
        ytop=EMB[1]+pad-(EMB[1]-EMB[0]+2*pad)*ip
        M=np.maximum(M,mEMB*(~ring)*np.clip((yy-ytop)/20,0,1))
    sp=ease(seg(t,2.9,3.8))
    if sp>0: M=np.maximum(M,mSUB*sp)
    return M
def sparkle(img,cx,cy,r,a):
    if a<=0: return
    yv,xv=np.ogrid[-r:r+1,-r:r+1]
    d=np.hypot(xv,yv)+1e-3
    star=(np.exp(-np.abs(xv)/2.6)*np.exp(-np.abs(yv)/(r*0.45))+np.exp(-np.abs(yv)/2.6)*np.exp(-np.abs(xv)/(r*0.45)))
    star+=np.exp(-(d/6.0)**2)+0.35*np.exp(-(d/(r*0.35))**2)
    star=np.clip(star*a,0,1)
    y0,x0=int(cy-r),int(cx-r)
    sub=img[y0:y0+2*r+1,x0:x0+2*r+1]
    halo=np.clip(0.55*np.exp(-(d/(r*0.55))**2)*a,0,1)
    gold=np.array([0.93,0.74,0.40]); white=np.array([1.0,0.99,0.95])
    sub=sub*(1-halo[...,None]*0.5)+gold*halo[...,None]*0.5
    core=np.clip(star,0,1)
    sub=sub*(1-core[...,None])+ (white*0.6+gold*0.4)*core[...,None]
    img[y0:y0+2*r+1,x0:x0+2*r+1]=sub
GLINTS=None
GLOW=np.zeros(alpha.shape,np.float32)
def frame(t):
    bg=watermark(t)
    M=logo_mask(t)
    z=1.0+0.025*ease(seg(t,0,DUR))
    rgb=G[...,:3].copy()
    # daha zengin altın tonu
    l=rgb.mean(2,keepdims=True); rgb=np.clip(l*np.array([1.06,0.90,0.66])*0.92+rgb*0.22,0,1)
    GLOW[...]=0
    a=np.maximum(ALPHA_M*M, 0)
    shd=SHADOW*M
    # metal parıltı: diyagonal hüzme logonun üzerinden geçer
    sh=seg(t,3.9,5.1)
    if 0<sh<1:
        pos=-300+(g.width+g.height*0.6+600)*ease(sh)
        bandv=np.exp(-((xx+yy*0.6)-pos)**2/(2*70**2))
        core=np.exp(-((xx+yy*0.6)-pos)**2/(2*18**2))
        mm=ALPHA_M
        k=(bandv*0.75+core*0.6)*mm
        rgb=rgb+(np.array([1,0.98,0.92])-rgb)*np.clip(k,0,1)[...,None]
        GLOW[...]=bandv*mm
    # ikinci yumuşak nefes parlaması
    br=0.06*math.sin(math.pi*seg(t,5.0,6.4))
    rgb=np.clip(rgb*(1+br*metal[...,None]),0,1)
    # gölge + metal birleşik katman
    a_tot=a+shd*(1-a)
    col=(rgb*a[...,None]+np.array([0.35,0.30,0.24])*(shd*(1-a))[...,None])/np.maximum(a_tot,1e-4)[...,None]
    lg=Image.fromarray((np.dstack([np.clip(col,0,1),np.clip(a_tot,0,1)])*255).astype(np.uint8),'RGBA')
    if z!=1.0:
        nw=int(lg.width*z); lg=lg.resize((nw,int(lg.height*z)),Image.BICUBIC)
    canvas=Image.fromarray((bg*255).astype(np.uint8)).convert('RGBA')
    px=int(W/2-((bx0+bx1)/2)*z); py=int(H/2-((by0+by1)/2)*z)-30
    canvas.alpha_composite(lg,(px,py))
    out=np.asarray(canvas.convert('RGB')).astype(np.float32)/255
    if GLOW.max()>0:
        gl=Image.fromarray((GLOW*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))
        if z!=1.0: gl=gl.resize((int(gl.width*z),int(gl.height*z)))
        ga=np.zeros((H,W),np.float32); gg=np.asarray(gl).astype(np.float32)/255
        x0,y0=max(0,px),max(0,py); x1,y1=min(W,px+gl.width),min(H,py+gl.height)
        ga[y0:y1,x0:x1]=gg[y0-py:y1-py,x0-px:x1-px]
        out=out+(np.array([1,0.93,0.75])-out)*(ga*0.35)[...,None]
    # altın çubuk
    grow=ease(seg(t,0.15,0.55)); sw=seg(t,0.75,1.95)
    if grow>0 and t<2.2:
        fade=1-seg(t,1.95,2.2)
        bxp=letters[0][0]-14+(letters[-1][1]-letters[0][0]+28)*ease(sw) if sw>0 else (bx0+bx1)/2
        X=int(px+bxp*z); h=(WM[1]-WM[0])*grow*z; cy=py+(WM[0]+WM[1])/2*z
        gold=np.array([0.80,0.66,0.42])
        y0,y1=int(cy-h/2),int(cy+h/2)
        out[y0:y1,X-5:X+5]=out[y0:y1,X-5:X+5]*(1-fade)+gold*fade
    # pırıltılar
    for (gx,gy,t0,r) in GLINTS:
        a_=math.sin(math.pi*seg(t,t0,t0+0.7))
        sparkle(out,int(px+gx*z),int(py+gy*z),r,a_)
    return Image.fromarray((np.clip(out,0,1)*255).astype(np.uint8))
# pırıltı noktaları: halkanın üst-sağı, İ kıvrımı, O harfi, halka sol-alt
GLINTS=[(ecx+er*0.71,ecy-er*0.71,4.35,48),(letters[3][0]+ (letters[3][1]-letters[3][0])/2, SWR[0]+8,4.75,40),
        (letters[-1][1]-6,WM[0]+12,5.05,42),(ecx-er*0.8,ecy+er*0.55,5.35,36)]
if __name__=='__main__':
    out=sys.argv[1]; os.makedirs(out,exist_ok=True)
    N=int(DUR*FPS)
    for i in range(N): frame(i/FPS).save(f'{out}/f{i:04d}.jpg',quality=95)
    print('ok',N)
