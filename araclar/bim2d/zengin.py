# Arma BİM görüntüsünü yeniden oluştur: siyah kesit → renkli betonarme, şap içi yerden ısıtma,
# şaft + kolonlar + vanalar, radyatör, kollektör; mevcut boruları kalınlaştır/parlat.
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
RED=(206,62,46); BLUE=(44,104,196); ORNG=(226,150,52); GREEN=(64,150,92)
def tube(d,pts,col,w):
    d.line(pts,fill=col,width=w,joint='curve')
    hl=tuple(min(255,int(c*0.45+255*0.55)) for c in col)
    d.line([(x,y-w*0.22) for x,y in pts],fill=hl,width=max(1,w//4),joint='curve')
    dk=tuple(int(c*0.6) for c in col)
    d.line([(x,y+w*0.3) for x,y in pts],fill=dk,width=max(1,w//5),joint='curve')
def valve(d,x,y,col,s=12,yatay=False):
    if yatay: d.polygon([(x-s,y-s),(x+s,y+s),(x+s,y-s),(x-s,y+s)],fill=col,outline=(30,28,26))
    else: d.polygon([(x-s,y-s),(x+s,y-s),(x-s,y+s),(x+s,y+s)],fill=col,outline=(30,28,26))
    d.line([(x,y),(x+(0 if yatay else s+8),y-(s+8 if yatay else 0))],fill=(30,28,26),width=3)
def concrete(shape,seed=3):
    rng=np.random.default_rng(seed); h,w=shape
    base=np.ones((h,w,3),np.float32)*np.array([184,178,168],np.float32)
    n=cv2.GaussianBlur(rng.standard_normal((h,w)).astype(np.float32),(0,0),2.5)*9
    base+=n[...,None]
    agg=(rng.random((h,w))>0.993).astype(np.uint8); agg=cv2.dilate(agg,np.ones((3,3),np.uint8))
    base[agg>0]=base[agg>0]*0.72
    yy,xx=np.mgrid[0:h,0:w]; hatch=((xx+yy)%18<2)
    base[hatch]=base[hatch]*0.82
    return base
def slab_edges(mask):
    """Geniş yatay koyu bileşenler için üst kenar doğrusu (y=a*x+b) ve x aralığı."""
    mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,np.ones((1,90),np.uint8))
    nl,lab,st,_=cv2.connectedComponentsWithStats(mask,8); out=[]
    for i in range(1,nl):
        x,y,w,h,ar=st[i]
        if w<800: continue
        xs=np.arange(x+10,x+w-10,8); ys=[]
        for cx in xs:
            col=np.where(lab[y:y+h,cx]==i)[0]
            ys.append(y+col.min() if len(col) else np.nan)
        ys=np.array(ys,float); ok=~np.isnan(ys)
        if ok.sum()<10: continue
        a,b=np.polyfit(xs[ok],ys[ok],1)
        # alt kenar
        yb=[]
        for cx in xs:
            col=np.where(lab[y:y+h,cx]==i)[0]; yb.append(y+col.max() if len(col) else np.nan)
        yb=np.array(yb,float); a2,b2=np.polyfit(xs[~np.isnan(yb)],yb[~np.isnan(yb)],1)
        th=np.nanmedian(yb-ys)
        if th>70 or th<12: continue           # döşeme kalınlığı aralığı
        out.append(dict(x0=x,x1=x+w,a=a,b=b,th=th))
    return sorted(out,key=lambda s:s['b'])
def zenginlestir(img,shaft_x=None,radyator=None,seed=3,sap=True):
    a=np.asarray(img.convert('RGB')).astype(np.float32); H,W=a.shape[:2]
    g=cv2.cvtColor(a.astype(np.uint8),cv2.COLOR_RGB2GRAY)
    dark=(g<55).astype(np.uint8); dark=cv2.morphologyEx(dark,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    # 1) betonarme kesit
    conc=concrete((H,W),seed); m=cv2.GaussianBlur(dark.astype(np.float32),(0,0),0.7)[...,None]
    out=a*(1-m)+conc*m
    edge=cv2.morphologyEx(dark,cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8)).astype(np.float32)[...,None]
    out=out*(1-edge*0.9)+np.array([46,42,38],np.float32)*edge*0.9
    # 2) mevcut renkli boruları doygunlaştır
    hsv=cv2.cvtColor(out.clip(0,255).astype(np.uint8),cv2.COLOR_RGB2HSV).astype(np.float32)
    col=(hsv[...,1]>90)&(hsv[...,2]>70); hsv[...,1][col]=np.minimum(255,hsv[...,1][col]*1.35)
    out=cv2.cvtColor(hsv.clip(0,255).astype(np.uint8),cv2.COLOR_HSV2RGB)
    im=Image.fromarray(out).convert('RGBA'); d=ImageDraw.Draw(im,'RGBA')
    slabs=slab_edges(dark)
    # 3) şap + yerden ısıtma + donatı
    for s in (slabs if sap else []):
        x0,x1=s['x0']+6,s['x1']-6; yt=lambda x:s['a']*x+s['b']
        sc=22
        d.polygon([(x0,yt(x0)-sc),(x1,yt(x1)-sc),(x1,yt(x1)),(x0,yt(x0))],fill=(236,226,206,235),outline=(120,108,92,255))
        k=0
        for x in np.arange(x0+18,x1-12,30):
            c=RED if k%2==0 else BLUE; y=yt(x)-sc/2
            d.ellipse([x-7,y-7,x+7,y+7],fill=c+(255,),outline=(40,36,32,255)); d.ellipse([x-3,y-5,x+1,y-1],fill=(255,255,255,170)); k+=1
        for x in np.arange(x0+20,x1-10,66):          # donatı (alt ve üst) — yalnız beton içinde
            for off in (9,s['th']-9):
                y=yt(x)+off
                if 0<=int(y)<H and dark[int(y),int(x)]: d.ellipse([x-3.5,y-3.5,x+3.5,y+3.5],fill=(120,40,32,255))
    if not sap:
        for s in slabs:
            yt=lambda x:s['a']*x+s['b']
            for x in np.arange(s['x0']+26,s['x1']-10,66):
                for off in (9,s['th']-9):
                    y=yt(x)+off
                    if 0<=int(y)<H and dark[int(y),int(x)]: d.ellipse([x-3.5,y-3.5,x+3.5,y+3.5],fill=(120,40,32,255))
    # 4) şaft: kolonlar + vanalar + katlarda branşman
    if shaft_x and slabs:
        sx0,sx1=shaft_x; ytop=slabs[0]['a']*sx0+slabs[0]['b']-150; ybot=slabs[-1]['a']*sx0+slabs[-1]['b']+slabs[-1]['th']
        for yy in np.arange(ytop,ybot,26):
            d.line([(sx0,yy),(sx0,yy+14)],fill=(60,54,48,255),width=3); d.line([(sx1,yy),(sx1,yy+14)],fill=(60,54,48,255),width=3)
        d.line([(sx0,ytop),(sx1,ytop)],fill=(60,54,48,255),width=3)
        cols=[(sx0+18,ORNG,20),(sx0+48,RED,12),(sx0+72,BLUE,12)]
        for x,c,w in cols: tube(d,[(x,ytop+10),(x,ybot-4)],c,w)
        for s in slabs[1:]:
            yf=s['a']*sx0+s['b']
            for (x,c,w),dy in zip(cols[1:],(30,52)):
                y=yf-dy; valve(d,x,y-26,c,9)
                xe=min(s['x1']-30,sx1+380); tube(d,[(x,y),(x,y-2),(xe,s['a']*xe+s['b']-dy)],c,9)
            # kollektör
            xm=sx1+40; ym=s['a']*xm+s['b']-22-74
            d.rounded_rectangle([xm,ym,xm+120,ym+60],radius=6,fill=(214,208,198,255),outline=(60,54,48,255),width=3)
            for j in range(5): d.line([(xm+16+j*22,ym+60),(xm+16+j*22,s['a']*(xm+16+j*22)+s['b']-11)],fill=(RED if j%2==0 else BLUE)+(255,),width=5)
            for j in range(5): d.ellipse([xm+11+j*22,ym+8,xm+21+j*22,ym+18],fill=(60,54,48,255))
    # 5) radyatörler
    for (rx,rw,rh,si) in (radyator or []):
        if si>=len(slabs): continue
        s=slabs[si]; ry=int(s['a']*rx+s['b']-22-rh-44)
        d.rounded_rectangle([rx,ry,rx+rw,ry+rh],radius=5,fill=(246,244,240,255),outline=(90,84,78,255),width=3)
        for x in range(rx+10,rx+rw-6,12): d.line([(x,ry+6),(x,ry+rh-6)],fill=(170,164,156,255),width=2)
        tube(d,[(rx+10,ry+rh),(rx+10,ry+rh+44)],RED,8); tube(d,[(rx+rw-10,ry+rh),(rx+rw-10,ry+rh+44)],BLUE,8)
        valve(d,rx+10,ry+rh+18,RED,7); valve(d,rx+rw-10,ry+rh+18,BLUE,7)
    return im.convert('RGB'),slabs
