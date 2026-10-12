import sys,os,math,subprocess
from PIL import Image,ImageDraw,ImageFilter,ImageChops
import numpy as np
S='/tmp/claude-0/-home-claude/8c2bb08b-0d28-593e-b9c3-4c3ec033f7cb/scratchpad/'
W,H,FPS=1080,1920,30
BG=(17,16,15); GOLD=(201,166,108); CREAM=(246,240,230)
src=Image.open(S+'brand/logo_beyaz.png').split()[3]
sc=760/src.width; src=src.resize((int(src.width*sc),int(src.height*sc)),Image.LANCZOS)
A=np.asarray(src).astype(np.float32)/255
ox=(W-src.width)//2; oy=(H-src.height)//2-40
r=lambda v:int(v*sc)
EMB=(r(8),r(4962)); SW=(r(5088),r(5530)); WM=(r(5606),r(6826)); SUB=(r(7246),r(7728))
def band(r0,r1):
    m=np.zeros_like(A); m[r0:r1]=A[r0:r1]; return m
emb=band(*EMB); swirl=band(*SW); wm=band(*WM); sub=band(*SUB)
# letters by column runs
cols=(wm>0.15).any(0); runs=[];s=None
for i,v in enumerate(list(cols)+[False]):
    if v and s is None:s=i
    if not v and s is not None: runs.append((s,i)); s=None
print('letters',len(runs))
# emblem geometry
ys,xs=np.where(emb>0.2); ecx=(xs.min()+xs.max())/2; ecy=(ys.min()+ys.max())/2; er=(xs.max()-xs.min())/2
yy,xx=np.mgrid[0:A.shape[0],0:A.shape[1]]
ang=(np.degrees(np.arctan2(xx-ecx,-(yy-ecy)))+360)%360   # 0 at top, clockwise
rad=np.hypot(xx-ecx,yy-ecy)
ring=(rad>er*0.93)
def ease(t): t=min(1,max(0,t)); return t*t*(3-2*t)
def eob(t):  # ease out back
    t=min(1,max(0,t)); c=1.7; return 1+(c+1)*(t-1)**3+c*(t-1)**2
def seg(t,a,b): return min(1,max(0,(t-a)/(b-a)))
def frame(t):
    img=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(img)
    # subtle grid
    g=int(10*ease(seg(t,0,0.8)))
    for x in range(0,W,72): d.line([(x,0),(x,H)],fill=(BG[0]+g//2,BG[1]+g//2,BG[2]+g//2))
    for y in range(0,H,72): d.line([(0,y),(W,y)],fill=(BG[0]+g//2,BG[1]+g//2,BG[2]+g//2))
    M=np.zeros_like(A)
    # 1) gold bar grows 0.15-0.6 at wordmark center, then slides left->right revealing letters 0.7-1.9
    wy0,wy1=WM; bx_start=runs[0][0]-14; bx_end=runs[-1][1]+14
    grow=ease(seg(t,0.15,0.55)); sweep=seg(t,0.75,1.95)
    bx=bx_start+(bx_end-bx_start)*ease(sweep)
    if sweep<=0: bx=src.width/2
    # letters revealed when bar passed their left edge; pop with ease-out-back from the bar
    for i,(c0,c1) in enumerate(runs):
        lt=seg(t,0.75+ (c0-bx_start)/(bx_end-bx_start)*1.2, 0.75+(c0-bx_start)/(bx_end-bx_start)*1.2+0.35)
        if lt>0:
            k=eob(lt); m=np.zeros_like(A)
            sub_=wm[:,c0:c1]
            # vertical scale from bar: scale y around baseline center
            h=wy1-wy0; sh=max(1,int(h*min(k,1.08)))
            piece=Image.fromarray((sub_[wy0:wy1]*255).astype(np.uint8)).resize((c1-c0,sh),Image.BICUBIC)
            pa=np.asarray(piece).astype(np.float32)/255
            cy=(wy0+wy1)//2; y0=cy-sh//2
            y0c=max(0,y0); pa=pa[y0c-y0:]; 
            m[y0c:y0c+pa.shape[0],c0:c1]=pa[:A.shape[0]-y0c]
            M=np.maximum(M,m*min(1,lt*3))
    # swirl after letters
    sw=ease(seg(t,2.0,2.5)); 
    if sw>0:
        x0=np.where(swirl.any(0))[0]; m=swirl.copy(); cut=int(x0.min()+(x0.max()-x0.min())*sw); m[:,cut:]=0; M=np.maximum(M,m)
    # emblem: ring draws clockwise 1.2-2.4, inner grows bottom-up 2.0-3.0
    rp=ease(seg(t,1.2,2.4))
    if rp>0: M=np.maximum(M,emb*(ring&(ang<=rp*360)))
    ip=ease(seg(t,2.0,3.1))
    if ip>0:
        ytop=EMB[1]-(EMB[1]-EMB[0])*ip
        M=np.maximum(M,emb*((~ring)&(yy>=ytop)))
    # subtitle tracking-in 2.9-3.7
    sp=ease(seg(t,2.9,3.7))
    if sp>0:
        s_=sub*sp
        cx=src.width/2; spread=1+(1-sp)*0.35
        s_img=Image.fromarray((s_*255).astype(np.uint8))
        nw=int(src.width*spread); s_img=s_img.resize((nw,src.height),Image.BICUBIC)
        crop=s_img.crop(((nw-src.width)//2,0,(nw-src.width)//2+src.width,src.height))
        M=np.maximum(M,np.asarray(crop).astype(np.float32)/255)
    logo=Image.new('RGB',src.size,CREAM)
    # gold sheen sweep 3.9-4.9
    sh=seg(t,3.9,4.9)
    if sh>0:
        band_=np.exp(-((xx+yy*0.5)-(-400+(src.width+src.height)*1.2*sh))**2/(2*90**2))
        col=np.array(CREAM)[None,None,:]*(1-band_[...,None])+np.array(GOLD)[None,None,:]*band_[...,None]
        logo=Image.fromarray(col.astype(np.uint8))
    img.paste(logo,(ox,oy),Image.fromarray((M*255).astype(np.uint8)))
    # bar on top
    if grow>0 and t<2.15:
        fade=1-seg(t,1.95,2.15)
        bh=(wy1-wy0)*grow; cy=oy+(wy0+wy1)/2
        X=ox+bx
        d.rectangle([X-7,cy-bh/2,X+7,cy+bh/2],fill=tuple(int(BG[i]+(GOLD[i]-BG[i])*fade) for i in range(3)))
    return img
if __name__=='__main__':
    out=sys.argv[1]; os.makedirs(out,exist_ok=True)
    N=int(5.6*FPS)
    for i in range(N): frame(i/FPS).save(f'{out}/f{i:04d}.jpg',quality=94)
    print('ok',N)
