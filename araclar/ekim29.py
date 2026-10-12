import math,sys
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np
S='/tmp/claude-0/-home-claude/8c2bb08b-0d28-593e-b9c3-4c3ec033f7cb/scratchpad/'
SS=int(__import__("os").environ.get("SS","2")); W,H=1080*SS,1920*SS
F=lambda name,size: ImageFont.truetype(name,size*SS)
import subprocess
def fpath(q): return subprocess.check_output(['fc-match','-f','%{file}',q]).decode()
SERIF=fpath('Latin Modern Roman:style=Regular'); SERIF_I=fpath('Latin Modern Roman:style=Italic')
THIN=fpath('Inter:style=ExtraLight'); LIGHT=fpath('Inter:style=Light'); MED=fpath('Inter:style=Medium')
MONO=fpath('Latin Modern Mono Light')
WHITE=(255,255,255)
def bg():
    y=np.linspace(0,1,H)[:,None]; x=np.linspace(-1,1,W)[None,:]
    r=np.sqrt(x**2*0.6+(y-0.42)**2*1.4)
    t=np.clip(r,0,1)
    c0=np.array([150,18,30]); c1=np.array([70,6,14])
    img=(c0[None,None,:]*(1-t[...,None])+c1[None,None,:]*t[...,None]).astype(np.uint8)
    return Image.fromarray(img,'RGB').convert('RGBA')
def frame(p=1.0):
    """p: 0..1 drawing progress"""
    def seg(a,b): return max(0,min(1,(p-a)/(b-a)))
    base=bg()
    L=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    # blueprint grid
    g=seg(0,0.15)
    step=60*SS
    for x in range(0,W,step): d.line([(x,0),(x,H)],fill=(255,255,255,int(14*g)),width=1)
    for y in range(0,H,step): d.line([(0,y),(W,y)],fill=(255,255,255,int(14*g)),width=1)
    # flag geometry
    G=1000*SS; cx0=W/2-0.598*G; cy=930*SS
    X=lambda u: cx0+u*G
    oc=(0.5,0.25); ic=(0.5625,0.2); sc=(0.5625-0.2+1/3+0.125,0.125)
    lw=max(1,int(1.4*SS)); ca=150
    def circle(c,r,prog,dash=False,alpha=ca):
        if prog<=0: return
        cxx,rr=X(c),r*G
        n=360; m=int(n*prog)
        pts=[(cxx+rr*math.cos(math.radians(180-i)),cy-rr*math.sin(math.radians(180-i))) for i in range(m+1)]
        for i in range(len(pts)-1):
            if dash and (i//4)%2: continue
            d.line([pts[i],pts[i+1]],fill=(255,255,255,alpha),width=lw)
    # axis
    a=seg(0.08,0.25)
    x1=X(0.1); x2=X(1.05)
    d.line([(x1,cy),(x1+(x2-x1)*a,cy)],fill=(255,255,255,110),width=lw)
    circle(oc[0],oc[1],seg(0.15,0.38))
    circle(ic[0],ic[1],seg(0.25,0.45),dash=True)
    circle(sc[0],sc[1],seg(0.35,0.52),dash=True)
    # center crosses
    cc=seg(0.3,0.4)
    for c in (oc[0],ic[0],sc[0]):
        if cc>0:
            s=14*SS*cc; d.line([(X(c),cy-s),(X(c),cy+s)],fill=(255,255,255,200),width=lw)
    # vertical extension lines + dimensions
    fm=F(LIGHT,17)
    dims=[('D = 2G/5',0.3625,0.7625,-1),('C = G/16',0.5,0.5625,-2),('E = G/3',0.3625,0.3625+1/3,1),('F = G/4',sc[0]-0.125,sc[0]+0.125,2)]
    dd=seg(0.45,0.62)
    if dd>0:
        al=int(215*dd)
        # hoist reference line
        for lab,u1,u2,lvl in dims:
            yy=cy+ (lvl*62*SS + (-205*SS if lvl<0 else 205*SS))
            for u in (u1,u2):
                d.line([(X(u),cy),(X(u),yy+ (10*SS if lvl>0 else -10*SS))],fill=(255,255,255,int(80*dd)),width=1)
            d.line([(X(u1),yy),(X(u2),yy)],fill=(255,255,255,al),width=lw)
            for u in (u1,u2):
                t=8*SS; d.line([(X(u)-t,yy+t),(X(u)+t,yy-t)],fill=(255,255,255,al),width=lw)
            tx=(X(u1)+X(u2))/2; 
            d.text((tx,yy-(16*SS if lvl<0 else -16*SS)),lab,font=fm,fill=(255,255,255,al),anchor='mm')
        # diameter B vertical
        bx=X(0.5)-0.25*G-60*SS
        d.line([(bx,cy-0.25*G),(bx,cy+0.25*G)],fill=(255,255,255,al),width=lw)
        for yv in (cy-0.25*G,cy+0.25*G):
            t=8*SS; d.line([(bx-t,yv+t),(bx+t,yv-t)],fill=(255,255,255,al),width=lw)
            d.line([(bx,yv),(X(0.5),yv)],fill=(255,255,255,int(80*dd)),width=1)
        d.text((bx-14*SS,cy),'B = G/2',font=fm,fill=(255,255,255,al),anchor='rm')
        dx=X(ic[0])+0.2*G+0  # D on inner circle
    base.alpha_composite(L)
    # fill crescent + star
    f=seg(0.62,0.8)
    if f>0:
        M=Image.new('L',(W,H),0); md=ImageDraw.Draw(M)
        R=oc[1]*G; md.ellipse([X(oc[0])-R,cy-R,X(oc[0])+R,cy+R],fill=255)
        R=ic[1]*G; md.ellipse([X(ic[0])-R,cy-R,X(ic[0])+R,cy+R],fill=0)
        r=sc[1]*G; ri=r*0.382; pts=[]
        for i in range(10):
            ang=math.radians(180+i*36); rr=r if i%2==0 else ri
            pts.append((X(sc[0])+rr*math.cos(ang),cy-rr*math.sin(ang)))
        md.polygon(pts,fill=255)
        glow=M.filter(ImageFilter.GaussianBlur(30*SS)).point(lambda v:int(v*0.35*f))
        base.alpha_composite(Image.merge('RGBA',[Image.new('L',(W,H),255)]*3+[glow]))
        base.alpha_composite(Image.merge('RGBA',[Image.new('L',(W,H),255)]*3+[M.point(lambda v:int(v*f))]))
    # typography
    T=Image.new('RGBA',(W,H),(0,0,0,0)); td=ImageDraw.Draw(T)
    t1=seg(0.0,0.12); t2=seg(0.78,0.92); t3=seg(0.86,1.0)
    def spaced(y,text,font,alpha,track):
        ws=[td.textlength(ch,font=font) for ch in text]; tot=sum(ws)+track*SS*(len(text)-1)
        x=W/2-tot/2
        for ch,w in zip(text,ws):
            td.text((x,y),ch,font=font,fill=(255,255,255,alpha),anchor='ls'); x+=w+track*SS
    spaced(250*SS,'29 EKİM 1923',F(LIGHT,30),int(235*t1),14)
    td.line([(W/2-40*SS,290*SS),(W/2+40*SS,290*SS)],fill=(255,255,255,int(160*t1)),width=lw)
    td.text((W/2,395*SS),'Cumhuriyet’in',font=F(SERIF_I,64),fill=(255,255,255,int(255*t1)),anchor='ms')
    td.text((W/2,480*SS),'103. yılı',font=F(SERIF,78),fill=(255,255,255,int(255*t1)),anchor='ms')
    fb=F(LIGHT,29)
    lines=['Ölçüleri kanunla çizilmiş bayrağımız,','sevgisiyle yüreklerimizde.']
    for i,l in enumerate(lines): td.text((W/2,(1420+i*44)*SS),l,font=fb,fill=(255,255,255,int(225*t2)),anchor='ms')
    spaced(1560*SS,'CUMHURİYET BAYRAMIMIZ KUTLU OLSUN',F(MED,23),int(255*t2),6)
    base.alpha_composite(T)
    logo=Image.open(S+'brand/logo_beyaz.png'); logo.thumbnail((250*SS,250*SS),Image.LANCZOS)
    la=logo.split()[3].point(lambda v:int(v*t3)); logo.putalpha(la)
    base.alpha_composite(logo,(int(W/2-logo.width/2),int(1640*SS)))
    return base.convert('RGB').resize((1080,1920),Image.LANCZOS)
if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='still':
        frame(1.0).save(S+'out/29ekim_story.jpg',quality=95)
    else:
        import os; os.makedirs(S+'frames',exist_ok=True)
        N=int(sys.argv[2]); hold=int(sys.argv[3])
        for i in range(N):
            p=i/(N-1); p=1-(1-p)**2
            frame(p).save(S+f'frames/f{i:04d}.png')
        print('ok')
