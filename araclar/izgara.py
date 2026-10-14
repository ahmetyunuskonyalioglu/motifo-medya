# Motifo Instagram ızgara sistemi: "görsel" ve "çizim/künye" kapakları (3:4, 1080x1440)
import sys,os,subprocess,numpy as np,cv2
sys.path.insert(0,os.path.dirname(__file__))
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from cropframe import crop_render
R=os.path.join(os.path.dirname(__file__),'..')
F=lambda n: os.path.join(R,'marka','fonts',n)
fp=lambda q: subprocess.check_output(['fc-match','-f','%{file}',q]).decode()
INTER_M=fp('Inter:style=Medium'); INTER_L=fp('Inter:style=Light')
SERIF_I=F('Cormorant-Italic.ttf'); SERIF_LI=F('Cormorant-LightItalic.ttf'); SERIF=F('Cormorant-Regular.ttf')
W,H=1080,1440
STONE=(239,233,224); INK=(38,34,30); BRONZE=(150,112,76); MUTE=(128,118,106); GOLD=(176,138,86)
def up(t): return t.replace('i','İ').replace('ı','I').upper()
def track(d,xy,text,font,fill,sp,anchor='l'):
    w=sum(d.textlength(c,font=font) for c in text)+sp*(len(text)-1)
    x=xy[0]-(w/2 if anchor=='m' else (w if anchor=='r' else 0))
    for c in text: d.text((x,xy[1]),c,font=font,fill=fill); x+=d.textlength(c,font=font)+sp
    return w
def load(path):
    try: im=crop_render(path)
    except Exception: im=Image.open(path).convert('RGB')
    return im
def cover(im,w,h,fx=0.5,fy=0.5,zoom=1.0):
    s=max(w/im.width,h/im.height)*zoom; nw,nh=int(im.width*s+0.5),int(im.height*s+0.5)
    im=im.resize((nw,nh),Image.LANCZOS); x=int((nw-w)*fx); y=int((nh-h)*fy)
    return im.crop((x,y,x+w,y+h))
def sketch(im,sigma=1.6,k=1.6,tau=0.99,phi=40,eps=-0.015,minarea=40):
    g=cv2.cvtColor(np.asarray(im),cv2.COLOR_RGB2GRAY).astype(np.float32)/255
    g8=cv2.createCLAHE(clipLimit=3.0,tileGridSize=(8,8)).apply((g*255).astype(np.uint8))
    g=cv2.normalize(g8.astype(np.float32),None,0,1,cv2.NORM_MINMAX)
    g=cv2.bilateralFilter(g,9,0.1,7); g=cv2.bilateralFilter(g,9,0.1,7)
    a=cv2.GaussianBlur(g,(0,0),sigma); b=cv2.GaussianBlur(g,(0,0),sigma*k)
    d=a-tau*b
    e=np.where(d>=eps,1.0,1+np.tanh(phi*(d-eps)))
    e=np.clip(e,0,1)
    m=(e<0.6).astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(m,8)
    keep=np.zeros(n,bool); keep[1:]=st[1:,cv2.CC_STAT_AREA]>=minarea
    e=np.where(keep[lab],e,1.0)
    return cv2.GaussianBlur(e.astype(np.float32),(0,0),0.6)   # 1=kağıt, 0=çizgi
def frame_line(d,inset,col,w=2):
    d.rectangle([inset,inset,W-inset,H-inset],outline=col,width=w)
# --- A: görsel kapak ---
def gorsel(src,no,name,loc,fx=0.5,fy=0.5,zoom=1.0):
    im=cover(load(src),W,H,fx,fy,zoom).convert('RGBA')
    g=Image.new('L',(1,256)); [g.putpixel((0,i),int(170*max(0,(i-150)/106)**1.6)) for i in range(256)]
    sh=Image.new('RGBA',(W,H),(14,12,10,0)); sh.putalpha(g.resize((W,H))); im.alpha_composite(sh)
    d=ImageDraw.Draw(im,'RGBA'); frame_line(d,40,(255,255,255,120),2)
    track(d,(96,H-262),f'№ {no:02d}',ImageFont.truetype(INTER_M,30),(255,255,255,235),6)
    d.text((92,H-150),name,font=ImageFont.truetype(SERIF_I,96),fill=(255,255,255,255),anchor='ls')
    track(d,(96,H-128),up(loc),ImageFont.truetype(INTER_M,26),(255,255,255,200),7)
    return im.convert('RGB')
# --- B: çizim / künye kapağı ---
def cizim(src,no,name,loc,tur,fx=0.5,fy=0.5,zoom=1.0,koyu=False):
    STONE_=(30,28,26) if koyu else STONE; INK_=(236,228,214) if koyu else INK; MUTE_=(170,156,136) if koyu else MUTE; BR_=GOLD if koyu else BRONZE
    bg=Image.new('RGB',(W,H),STONE_); d=ImageDraw.Draw(bg,'RGBA')
    bw,bh=W-2*96,820
    im=cover(load(src),bw,bh,fx,fy,zoom); s=sketch(im)
    ink=np.array(GOLD,np.float32) if koyu else np.array(BRONZE,np.float32)*0.55+np.array(INK,np.float32)*0.45
    paper=np.array(STONE_,np.float32)
    arr=paper*s[...,None]+ink*(1-s[...,None])
    # kenarlara doğru eriyen çizim
    yy,xx=np.mgrid[0:bh,0:bw]; m=np.clip(np.minimum.reduce([xx/80,(bw-xx)/80,yy/60,(bh-yy)/80]),0,1)[...,None]
    arr=paper*(1-m)+arr*m
    bg.paste(Image.fromarray(arr.astype(np.uint8)),(96,150))
    frame_line(d,40,GOLD+(255,),2)
    track(d,(96,90),f'№ {no:02d}   ·   '+up(tur),ImageFont.truetype(INTER_M,28),BR_,6)
    d.line([(96,1050),(196,1050)],fill=GOLD,width=2)
    f=ImageFont.truetype(SERIF_I,118)
    while d.textlength(name,font=f)>W-192: f=ImageFont.truetype(SERIF_I,f.size-4)
    d.text((92,1196),name,font=f,fill=INK_,anchor='ls')
    track(d,(96,1250),up(loc),ImageFont.truetype(INTER_M,27),MUTE_,7)
    return bg
# --- sabitlenmiş marka karesi ---
def marka(genislik=700):
    kd=os.path.join(R,'marka','logo_kapanis_kareleri'); fs=sorted(os.listdir(kd))
    fr=Image.open(os.path.join(kd,fs[-1])).convert('RGB')   # 1080x1920: üst ve alt bantta yalnız amblemler var
    bg=Image.new('RGB',(W,H),(255,255,255))
    top=fr.crop((0,0,W,520)); bot=fr.crop((0,fr.height-500,W,fr.height))
    mt=Image.linear_gradient('L').rotate(180).resize((W,520)).point(lambda v:min(255,v*2))
    mb=Image.linear_gradient('L').resize((W,500)).point(lambda v:min(255,v*2))
    bg.paste(top,(0,0),mt); bg.paste(bot,(0,H-500),mb)
    bg=bg.convert('RGBA')
    lg=Image.open(os.path.join(R,'marka','logo_altin.png')).convert('RGBA'); lg=lg.crop(lg.getchannel('A').point(lambda v:255 if v>8 else 0).getbbox())
    lg=lg.resize((genislik,int(lg.height*genislik/lg.width)),Image.LANCZOS)
    bg.alpha_composite(lg,((W-lg.width)//2,(H-lg.height)//2-20))
    return bg.convert('RGB')
# ---------------- Konsept 2: PAFTA (her kapak bir mimari pafta) ----------------
PAPER=(250,249,246); LINE=(30,28,26)
def _logo(w):
    lg=Image.open(os.path.join(R,'marka','logo_altin.png')).convert('RGBA')
    lg=lg.crop(lg.getchannel('A').point(lambda v:255 if v>8 else 0).getbbox())
    return lg.resize((w,int(lg.height*w/lg.width)),Image.LANCZOS)
def pafta(src,no,name,loc,tur,cizim_mi=False,fx=0.5,fy=0.5,zoom=1.0):
    bg=Image.new('RGB',(W,H),PAPER).convert('RGBA'); d=ImageDraw.Draw(bg,'RGBA')
    m=44; d.rectangle([m,m,W-m,H-m],outline=LINE,width=3); d.rectangle([m+14,m+14,W-m-14,H-m-14],outline=LINE,width=1)
    ix0,iy0,ix1,iy1=m+40,m+40,W-m-40,1040
    if cizim_mi:
        im=cover(load(src),ix1-ix0,iy1-iy0,fx,fy,zoom); s=sketch(im)
        arr=np.array(PAPER,np.float32)*s[...,None]+np.array(LINE,np.float32)*(1-s[...,None])
        bg.paste(Image.fromarray(arr.astype(np.uint8)),(ix0,iy0))
    else:
        bg.paste(cover(load(src),ix1-ix0,iy1-iy0,fx,fy,zoom),(ix0,iy0))
    d=ImageDraw.Draw(bg,'RGBA')
    # antet
    y0,y1=1072,H-m-14; xL=m+14; xR=W-m-14
    d.line([(xL,y0),(xR,y0)],fill=LINE,width=2)
    c1=xL+250; c2=xR-250
    d.line([(c1,y0),(c1,y1)],fill=LINE,width=1); d.line([(c2,y0),(c2,y1)],fill=LINE,width=1)
    ym=(y0+y1)//2; d.line([(c2,ym),(xR,ym)],fill=LINE,width=1)
    lg=_logo(190); bg.alpha_composite(lg,(xL+(250-190)//2,y0+(y1-y0-lg.height)//2))
    fs=ImageFont.truetype(INTER_M,20)
    track(d,(c1+30,y0+30),'PROJE',fs,MUTE,5)
    f=ImageFont.truetype(SERIF_I,84)
    while d.textlength(name,font=f)>c2-c1-60: f=ImageFont.truetype(SERIF_I,f.size-4)
    d.text((c1+28,y0+150),name,font=f,fill=LINE,anchor='ls')
    track(d,(c1+30,y0+186),up(loc),ImageFont.truetype(INTER_M,24),MUTE,6)
    track(d,(c2+28,y0+30),'PAFTA',fs,MUTE,5); d.text((c2+28,ym-20),f'A-{no:02d}',font=ImageFont.truetype(INTER_M,46),fill=LINE,anchor='ls')
    track(d,(c2+28,ym+26),'TÜR',fs,MUTE,5); track(d,(c2+28,ym+70),up(tur),ImageFont.truetype(INTER_M,26),LINE,4)
    return bg.convert('RGB')
# ---------------- Konsept 3: PANORAMA SATIRLARI (her satır tek proje) ----------------
def panorama(src,no,name,loc,fx=0.5,fy=0.5,zoom=1.0,koyu=False):
    big=cover(load(src),3*W,H,fx,fy,zoom).convert('RGBA')
    bw=170
    band=Image.new('RGBA',(3*W,bw),(22,20,18,235) if koyu else (250,248,244,240)); big.alpha_composite(band,(0,H-bw))
    d=ImageDraw.Draw(big,'RGBA'); col=(240,232,220) if koyu else INK; mu=(190,176,156) if koyu else MUTE
    yb=H-bw//2
    # her karede ortalanmış bilgi: sol=No, orta=ad, sağ=konum
    track(d,(W//2,yb-14),f'№ {no:02d}',ImageFont.truetype(INTER_M,30),mu,8,'m')
    f=ImageFont.truetype(SERIF_I,86)
    while d.textlength(name,font=f)>W-140: f=ImageFont.truetype(SERIF_I,f.size-4)
    d.text((W+W//2,yb+28),name,font=f,fill=col,anchor='ms')
    track(d,(2*W+W//2,yb-14),up(loc),ImageFont.truetype(INTER_M,30),mu,8,'m')
    d.line([(W+W//2-60,H-bw+22),(W+W//2+60,H-bw+22)],fill=GOLD,width=2)
    return [big.crop((i*W,0,(i+1)*W,H)).convert('RGB') for i in range(3)]
def marka_panorama():
    m=marka(760); left=m.crop((0,0,W,H)); 
    kd=os.path.join(R,'marka','logo_kapanis_kareleri'); fr=Image.open(os.path.join(kd,sorted(os.listdir(kd))[-1])).convert('RGB')
    top=cover(fr.crop((0,0,W,520)),W,H)
    s1=Image.new('RGB',(W,H),(255,255,255)); s1.paste(fr.crop((0,0,W,520)),(0,0)); s1.paste(fr.crop((0,fr.height-520,W,fr.height)),(0,H-520)); 
    s1.paste(fr.crop((0,fr.height-520,W,fr.height)).transpose(Image.FLIP_TOP_BOTTOM),(0,460))
    d=ImageDraw.Draw(s1); 
    s3=s1.transpose(Image.FLIP_LEFT_RIGHT).copy(); d3=ImageDraw.Draw(s3)
    track(d,(W//2,H//2-20),'MİMARLIK',ImageFont.truetype(INTER_M,34),BRONZE,14,'m')
    track(d3,(W//2,H//2-20),'İÇ MİMARLIK · BİM',ImageFont.truetype(INTER_M,34),BRONZE,14,'m')
    return [s1,m,s3]
# ================= Ek konseptler =================
CREAM=(246,243,238)
def _name_fit(d,name,maxw,size,font=None):
    f=ImageFont.truetype(font or SERIF_I,size)
    while d.textlength(name,font=f)>maxw: f=ImageFont.truetype(font or SERIF_I,f.size-4)
    return f
# 4) Paspartu: galeri duvarı — geniş beyaz pasparto, yatay/dikey dönüşümlü
def paspartu(src,no,name,loc,dikey=False,fx=0.5,fy=0.5,zoom=1.0):
    bg=Image.new('RGB',(W,H),CREAM); d=ImageDraw.Draw(bg)
    if dikey: bw,bh=700,960; y0=150
    else: bw,bh=880,660; y0=300
    x0=(W-bw)//2
    sh=Image.new('RGBA',(bw+60,bh+60),(0,0,0,0)); ImageDraw.Draw(sh).rectangle([30,34,bw+30,bh+34],fill=(60,45,30,60))
    sh=sh.filter(ImageFilter.GaussianBlur(14)); bg.paste(sh,(x0-30,y0-30),sh)
    bg.paste(cover(load(src),bw,bh,fx,fy,zoom),(x0,y0))
    yt=y0+bh+110
    d.text((W//2,yt),name,font=_name_fit(d,name,W-200,72),fill=INK,anchor='ms')
    track(d,(W//2,yt+40),f'№ {no:02d}  ·  '+up(loc),ImageFont.truetype(INTER_M,24),MUTE,6,'m')
    return bg
# 5) Kemer: logodaki dairesel/kemer motifinden pencere
def kemer(src,no,name,loc,koyu=False,fx=0.5,fy=0.5,zoom=1.0):
    BG=(30,28,26) if koyu else STONE; TX=(236,228,214) if koyu else INK; MU=(170,156,136) if koyu else MUTE
    bg=Image.new('RGB',(W,H),BG); aw,ah=760,1000; x0=(W-aw)//2; y0=120
    m=Image.new('L',(aw,ah),0); dm=ImageDraw.Draw(m); dm.rectangle([0,aw//2,aw,ah],fill=255); dm.ellipse([0,0,aw,aw],fill=255)
    bg.paste(cover(load(src),aw,ah,fx,fy,zoom),(x0,y0),m)
    d=ImageDraw.Draw(bg); o=26
    d.arc([x0-o,y0-o,x0+aw+o,y0+aw+o],180,360,fill=GOLD,width=2)
    d.line([(x0-o,y0+aw//2),(x0-o,y0+ah+o)],fill=GOLD,width=2); d.line([(x0+aw+o,y0+aw//2),(x0+aw+o,y0+ah+o)],fill=GOLD,width=2)
    d.line([(x0-o,y0+ah+o),(x0+aw+o,y0+ah+o)],fill=GOLD,width=2)
    yt=y0+ah+o+120
    d.text((W//2,yt),name,font=_name_fit(d,name,W-200,76),fill=TX,anchor='ms')
    track(d,(W//2,yt+44),f'№ {no:02d}  ·  '+up(loc),ImageFont.truetype(INTER_M,24),MU,6,'m')
    return bg
# 6) Çizimden gerçeğe: her karede çapraz bölünme, sol üst çizim, sağ alt render
def capraz(src,no,name,loc,fx=0.5,fy=0.5,zoom=1.0):
    im=cover(load(src),W,H,fx,fy,zoom); s=sketch(im)
    paper=np.array(STONE,np.float32); ink=np.array(BRONZE,np.float32)*0.55+np.array(INK,np.float32)*0.45
    sk=Image.fromarray((paper*s[...,None]+ink*(1-s[...,None])).astype(np.uint8))
    yy,xx=np.mgrid[0:H,0:W]; line=(xx/W)+(yy/H)   # 1 = köşegen
    t=np.clip((line-0.98)/0.04,0,1)
    m=Image.fromarray((t*255).astype(np.uint8))
    out=Image.composite(im,sk,m)
    fade=Image.fromarray((np.clip((yy-300)/140,0,1)*255).astype(np.uint8)).point(lambda v:v)
    out=Image.composite(out,Image.new('RGB',(W,H),STONE),Image.fromarray(np.maximum(np.asarray(fade),np.asarray(m)).astype(np.uint8)))
    d=ImageDraw.Draw(out)
    d.line([(W,0),(0,H)],fill=GOLD,width=3)
    track(d,(84,92),f'№ {no:02d}',ImageFont.truetype(INTER_M,28),BRONZE,6)
    d.text((80,250),name,font=_name_fit(d,name,640,92),fill=INK,anchor='ls')
    track(d,(84,290),up(loc),ImageFont.truetype(INTER_M,24),MUTE,6)
    return out
# 7) Malzeme paleti: görsel + sağda renk/malzeme şeridi
def palet(src,no,name,loc,fx=0.5,fy=0.5,zoom=1.0):
    sw=250; im=cover(load(src),W-sw,H,fx,fy,zoom)
    bg=Image.new('RGB',(W,H),CREAM); bg.paste(im,(0,0)); d=ImageDraw.Draw(bg)
    a=np.asarray(im.resize((120,160))).reshape(-1,3).astype(np.float32)
    crit=(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,30,1.0)
    _,lab,cen=cv2.kmeans(a,5,None,crit,4,cv2.KMEANS_PP_CENTERS)
    cnt=np.bincount(lab.ravel(),minlength=5); order=np.argsort(-cnt)[:4]
    cols=sorted([tuple(int(v) for v in cen[i]) for i in order],key=lambda c:sum(c))
    x=W-sw+60; y=150
    track(d,(x,90),f'№ {no:02d}',ImageFont.truetype(INTER_M,26),BRONZE,5)
    for c in cols:
        d.rectangle([x,y,x+130,y+130],fill=c); d.text((x,y+160),'#%02X%02X%02X'%c,font=ImageFont.truetype(INTER_M,20),fill=MUTE); y+=210
    txt=Image.new('RGBA',(H-260,140),(0,0,0,0)); dt=ImageDraw.Draw(txt)
    dt.text((0,80),name,font=_name_fit(dt,name,H-300,84),fill=INK,anchor='ls'); track(dt,(4,104),up(loc),ImageFont.truetype(INTER_M,22),MUTE,6)
    txt=txt.rotate(90,expand=True); bg.paste(txt,(W-sw+8+ (sw-140)//2 if False else W-150,H-txt.height-60),txt)
    return bg
# 8) Siyah-beyaz galeri, her dördüncü kare renkli
def sb_gorsel(src,no,name,loc,renkli=False,fx=0.5,fy=0.5,zoom=1.0):
    im=gorsel(src,no,name,loc,fx,fy,zoom)
    if renkli: return im
    g=np.asarray(im.convert('L')).astype(np.float32)
    g=np.clip((g-128)*1.08+128,0,255)[...,None]
    tone=np.array([1.04,1.0,0.94],np.float32)
    return Image.fromarray(np.clip(g*tone,0,255).astype(np.uint8))
# ================= Sade varyantlar (tam ekran görsel, en az müdahale) =================
def sade(src,no,name,loc,stil='cerceve',fx=0.5,fy=0.5,zoom=1.0):
    if stil=='cerceve': return gorsel(src,no,name,loc,fx,fy,zoom)
    pad=30 if stil=='kenar' else 0
    im=cover(load(src),W-2*pad,H-2*pad,fx,fy,zoom).convert('RGBA')
    if stil in ('alt_orta','kenar'):
        g=Image.new('L',(1,256)); [g.putpixel((0,i),int(150*max(0,(i-170)/86)**1.8)) for i in range(256)]
        sh=Image.new('RGBA',im.size,(12,10,8,0)); sh.putalpha(g.resize(im.size)); im.alpha_composite(sh)
    d=ImageDraw.Draw(im,'RGBA'); w,h=im.size
    if stil=='alt_orta':
        d.text((w//2,h-118),name,font=ImageFont.truetype(SERIF_I,70),fill=(255,255,255,250),anchor='ms')
        track(d,(w//2,h-90),f'№ {no:02d}  ·  '+up(loc),ImageFont.truetype(INTER_M,22),(255,255,255,190),6,'m')
    elif stil=='yok':
        pass
    elif stil=='numara':
        track(d,(70,70),f'№ {no:02d}',ImageFont.truetype(INTER_M,30),(255,255,255,230),6)
    elif stil=='kenar':
        track(d,(60,h-150),f'№ {no:02d}',ImageFont.truetype(INTER_M,26),(255,255,255,220),6)
        d.text((56,h-70),name,font=ImageFont.truetype(SERIF_I,78),fill=(255,255,255,255),anchor='ls')
    if pad:
        bg=Image.new('RGB',(W,H),CREAM); bg.paste(im.convert('RGB'),(pad,pad)); return bg
    return im.convert('RGB')
# ================= Tam ekran ailesi: render / eskiz / BİM — aynı künye düzeni =================
def eskiz_tam(src,no,name,loc,fx=0.5,fy=0.5,zoom=1.0):
    im=cover(load(src),W,H,fx,fy,zoom); s=sketch(im)
    paper=np.array(STONE,np.float32); ink=np.array(BRONZE,np.float32)*0.5+np.array(INK,np.float32)*0.5
    out=Image.fromarray((paper*s[...,None]+ink*(1-s[...,None])).astype(np.uint8)).convert('RGBA')
    g=Image.new('L',(1,256)); [g.putpixel((0,i),int(235*max(0,(i-165)/91)**1.3)) for i in range(256)]
    fade=Image.new('RGBA',(W,H),STONE+(0,)); fade.putalpha(g.resize((W,H))); out.alpha_composite(fade)
    d=ImageDraw.Draw(out,'RGBA'); frame_line(d,40,BRONZE+(150,),2)
    track(d,(96,H-262),f'№ {no:02d}',ImageFont.truetype(INTER_M,30),BRONZE,6)
    d.text((92,H-150),name,font=ImageFont.truetype(SERIF_I,96),fill=INK,anchor='ls')
    track(d,(96,H-128),up(loc),ImageFont.truetype(INTER_M,26),MUTE,7)
    return out.convert('RGB')
def bolunmus(foto,no,name,loc):
    """Arma: sol yarı BİM röntgen, sağ yarı uygulama fotoğrafı (fotoğrafa birebir oturan katman)."""
    import importlib.util
    spec=importlib.util.spec_from_file_location('xray',os.path.join(os.path.dirname(__file__),'arma','xray.py')); xr=importlib.util.module_from_spec(spec); spec.loader.exec_module(xr)
    ph=Image.open(foto).convert('RGB'); S=H/ph.height
    big=ph.resize((round(ph.width*S),H),Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2,60,2))
    gh=xr.base_ghost(big,S).convert('RGBA'); gh.alpha_composite(xr.draw_layer(big.size,1.0,S=S))
    ox=int(250*S); R=big.crop((ox,0,ox+W,H)); X=gh.convert('RGB').crop((ox,0,ox+W,H))
    out=R.copy(); out.paste(X.crop((0,0,W//2,H)),(0,0)); out=out.convert('RGBA')
    g=Image.new('L',(1,256)); [g.putpixel((0,i),int(170*max(0,(i-150)/106)**1.6)) for i in range(256)]
    sh=Image.new('RGBA',(W,H),(14,12,10,0)); sh.putalpha(g.resize((W,H))); out.alpha_composite(sh)
    d=ImageDraw.Draw(out,'RGBA'); d.line([(W//2,0),(W//2,H)],fill=(255,255,255,240),width=4)
    frame_line(d,40,(255,255,255,120),2)
    track(d,(W//2-30,96),'BİM',ImageFont.truetype(INTER_M,28),(44,100,170,255),6,'r'); track(d,(W//2+30,96),'UYGULAMA',ImageFont.truetype(INTER_M,28),(255,255,255,235),6)
    track(d,(96,H-262),f'№ {no:02d}',ImageFont.truetype(INTER_M,30),(255,255,255,235),6)
    d.text((92,H-150),name,font=ImageFont.truetype(SERIF_I,96),fill=(255,255,255,255),anchor='ls')
    track(d,(96,H-128),up(loc),ImageFont.truetype(INTER_M,26),(255,255,255,200),7)
    return out.convert('RGB')
# ================= Tam ekran — stil varyantları (tek fonksiyon) =================
GOLDT=(226,196,140)
def _base(kind,src,fx=0.5,fy=0.5,zoom=1.0):
    im=cover(load(src),W,H,fx,fy,zoom)
    if kind=='eskiz' or kind=='yari':
        s=sketch(im); paper=np.array(STONE,np.float32); ink=np.array(BRONZE,np.float32)*0.5+np.array(INK,np.float32)*0.5
        sk=Image.fromarray((paper*s[...,None]+ink*(1-s[...,None])).astype(np.uint8))
        if kind=='eskiz': return sk,True
        out=im.copy(); out.paste(sk.crop((0,0,W//2,H)),(0,0)); return out,False
    return im,False
def tile(kind,src,no,name,loc,stil='altin',fx=0.5,fy=0.5,zoom=1.0):
    im,acik=_base(kind,src,fx,fy,zoom); im=im.convert('RGBA'); d=ImageDraw.Draw(im,'RGBA')
    if kind=='yari': d.line([(W//2,0),(W//2,H)],fill=GOLD+(255,),width=3)
    txt=INK if acik else (255,255,255); mu=MUTE if acik else (255,255,255)
    if stil=='altin':
        if not acik:
            g=Image.new('L',(1,256)); [g.putpixel((0,i),int(185*max(0,(i-150)/106)**1.6)) for i in range(256)]
            sh=Image.new('RGBA',(W,H),(14,12,10,0)); sh.putalpha(g.resize((W,H))); im.alpha_composite(sh); d=ImageDraw.Draw(im,'RGBA')
        col=BRONZE if acik else GOLDT
        frame_line(d,40,col+(200,),2)
        track(d,(96,H-262),f'№ {no:02d}',ImageFont.truetype(INTER_M,30),col,6)
        d.text((92,H-150),name,font=ImageFont.truetype(SERIF_I,96),fill=(txt if acik else (250,244,232)),anchor='ls')
        track(d,(96,H-128),up(loc),ImageFont.truetype(INTER_M,26),col,7)
    elif stil=='dergi':
        if not acik:
            g=Image.new('L',(1,256)); [g.putpixel((0,i),int(150*max(0,(90-i)/90)**1.5)) for i in range(256)]
            sh=Image.new('RGBA',(W,H),(14,12,10,0)); sh.putalpha(g.resize((W,H))); im.alpha_composite(sh); d=ImageDraw.Draw(im,'RGBA')
        track(d,(80,84),f'№ {no:02d}   —   '+up(loc),ImageFont.truetype(INTER_M,24),mu+(220,),6)
        d.text((76,210),name,font=ImageFont.truetype(SERIF_I,92),fill=txt+(255,),anchor='ls')
    else:  # 'cerceve' (beğenilen hamam karesi)
        if not acik:
            g=Image.new('L',(1,256)); [g.putpixel((0,i),int(170*max(0,(i-150)/106)**1.6)) for i in range(256)]
            sh=Image.new('RGBA',(W,H),(14,12,10,0)); sh.putalpha(g.resize((W,H))); im.alpha_composite(sh); d=ImageDraw.Draw(im,'RGBA')
        frame_line(d,40,(BRONZE if acik else (255,255,255))+(130,),2)
        track(d,(96,H-262),f'№ {no:02d}',ImageFont.truetype(INTER_M,30),(BRONZE if acik else (255,255,255))+(235,),6)
        d.text((92,H-150),name,font=ImageFont.truetype(SERIF_I,96),fill=txt+(255,),anchor='ls')
        track(d,(96,H-128),up(loc),ImageFont.truetype(INTER_M,26),mu+(200,),7)
    return im.convert('RGB')
# ================= Bilgi serisi (BİM / Motifo nasıl çalışır) =================
def bilgi_kapak(src,seri_no,cumle,seri='BİM NOTLARI',fx=0.5,fy=0.5,zoom=1.0):
    im=cover(load(src),W,H,fx,fy,zoom).convert('RGBA')
    sh=Image.new('RGBA',(W,H),(20,18,16,0)); g=Image.new('L',(1,256)); [g.putpixel((0,i),int(200*max(0,(i-90)/166)**1.2)) for i in range(256)]
    sh.putalpha(g.resize((W,H))); im.alpha_composite(sh); d=ImageDraw.Draw(im,'RGBA')
    track(d,(96,96),f'{seri}  ·  {seri_no:02d}',ImageFont.truetype(INTER_M,28),GOLDT,7)
    f=ImageFont.truetype(SERIF_I,104); y=H-120-len(cumle)*112
    for line in cumle: d.text((92,y),line,font=f,fill=(250,244,232),anchor='ls'); y+=112
    d.line([(96,H-110),(196,H-110)],fill=GOLDT,width=2)
    return im.convert('RGB')
def bilgi_sayfa(src,no,toplam,baslik,aciklama,fx=0.5,fy=0.5,zoom=1.0,seri='BİM NOTLARI'):
    bg=Image.new('RGB',(W,H),STONE); d=ImageDraw.Draw(bg)
    track(d,(96,96),f'{seri}',ImageFont.truetype(INTER_M,26),BRONZE,7); track(d,(W-96,96),f'{no:02d} / {toplam:02d}',ImageFont.truetype(INTER_M,26),BRONZE,5,'r')
    d.text((92,250),baslik,font=_name_fit(d,baslik,W-190,92),fill=INK,anchor='ls')
    f=ImageFont.truetype(INTER_L,36); y=320
    for line in aciklama: d.text((96,y),line,font=f,fill=(74,67,59)); y+=54
    top=y+50; bg.paste(cover(load(src),W-192,H-top-96,fx,fy,zoom),(96,top))
    return bg
# ================= BİM eskiz (koyu zemin): yapı altın çizgi, tesisat renkli kalem =================
MEP_KREM={'kirmizi':(186,72,52),'mavi':(52,98,170),'yesil':(58,132,82),'sari':(190,140,40)}
MEP_COL={'kirmizi':(214,104,84),'mavi':(104,150,214),'yesil':(112,176,124),'sari':(226,190,96)}
def bim_eskiz_cizim(im,koyu=True):
    a=np.asarray(im.convert('RGB')); hsv=cv2.cvtColor(a,cv2.COLOR_RGB2HSV).astype(np.float32)
    h,s,v=hsv[...,0]*2,hsv[...,1]/255,hsv[...,2]/255
    col=(s>0.38)&(v>0.22)
    masks={'kirmizi':col&((h<22)|(h>335)),'sari':col&(h>=35)&(h<70)&(s>0.5),'yesil':(s>0.22)&(v>0.3)&(h>=80)&(h<170),'mavi':(s>0.42)&(v>0.25)&(h>=200)&(h<250)}
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    for n in masks:
        m=masks[n].astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,k); 
        nlab,lab,st,_=cv2.connectedComponentsWithStats(m,8); keep=np.zeros(nlab,bool); keep[1:]=(st[1:,cv2.CC_STAT_AREA]>=60)&~((st[1:,cv2.CC_STAT_TOP]<a.shape[0]*0.22)&(n=='mavi'))
        masks[n]=keep[lab]
    mep=np.zeros(a.shape[:2],bool)
    for m in masks.values(): mep|=m
    # yapı eskizi (tesisat bölgesi dışında), gökyüzü gradyanı gürültü yapmasın diye kenar tabanlı
    s1=sketch(im); line=1-s1                          # 1=çizgi
    g=cv2.GaussianBlur(cv2.cvtColor(a,cv2.COLOR_RGB2GRAY),(0,0),1.0)
    ce=cv2.Canny(g,25,80).astype(np.float32)/255; ce=cv2.GaussianBlur(ce,(0,0),0.6)
    sky=(hsv[...,0]*2>190)&(hsv[...,0]*2<240)&(v>0.55)&(s>0.12)
    ce[sky]*=0.15; line[sky]*=0.15
    line=np.clip(np.maximum(line,ce*0.85),0,1)
    line[cv2.dilate(mep.astype(np.uint8),k,iterations=2)>0]*=0.25
    BGc=np.array((26,24,22) if koyu else STONE,np.float32); out=np.ones(a.shape,np.float32)*BGc
    gold=np.array(GOLD if koyu else (92,74,56),np.float32)
    out=out*(1-line[...,None]*0.95)+gold*(line[...,None]*0.95)
    # tesisat: hafif renk yıkaması + kalem kenarı
    for n,m in masks.items():
        c=np.array(MEP_COL[n] if koyu else MEP_KREM[n],np.float32); mf=cv2.GaussianBlur(m.astype(np.float32),(0,0),1.2)
        out=out*(1-mf[...,None]*0.22)+c*(mf[...,None]*0.22)
        e=cv2.Canny((m*255).astype(np.uint8),50,150).astype(np.float32)/255
        e=cv2.GaussianBlur(e,(0,0),0.7); e=np.clip(e*1.8,0,1)
        out=out*(1-e[...,None])+c*e[...,None]
    return Image.fromarray(out.clip(0,255).astype(np.uint8))
def bim_eskiz(src,no,name,loc,tur='BİM',fx=0.5,fy=0.5,zoom=1.0,koyu=True):
    BG_=(26,24,22) if koyu else STONE; AC=GOLD if koyu else BRONZE; TX=(236,228,214) if koyu else INK; MU=(170,156,136) if koyu else MUTE
    bg=Image.new('RGB',(W,H),BG_); d=ImageDraw.Draw(bg,'RGBA')
    bw,bh=W-2*96,860
    im=cover(load(src),bw,bh,fx,fy,zoom); sk=bim_eskiz_cizim(im,koyu)
    arr=np.asarray(sk).astype(np.float32); BGc=np.array(BG_,np.float32)
    yy,xx=np.mgrid[0:bh,0:bw]; m=np.clip(np.minimum.reduce([xx/70,(bw-xx)/70,yy/50,(bh-yy)/90]),0,1)[...,None]
    bg.paste(Image.fromarray((BGc*(1-m)+arr*m).astype(np.uint8)),(96,150))
    frame_line(d,40,(GOLD if koyu else GOLD)+(255,),2)
    track(d,(96,90),f'№ {no:02d}   ·   '+up(tur),ImageFont.truetype(INTER_M,28),AC,6)
    d.line([(96,1060),(196,1060)],fill=GOLD,width=2)
    f=ImageFont.truetype(SERIF_I,118)
    while d.textlength(name,font=f)>W-192: f=ImageFont.truetype(SERIF_I,f.size-4)
    d.text((92,1200),name,font=f,fill=TX,anchor='ls')
    track(d,(96,1252),up(loc),ImageFont.truetype(INTER_M,27),MU,7)
    return bg
# ================= BİM eskiz — DETAY (tam çözünürlük, yakın kadraj, kalın tesisat) =================
MEP_KOYU2={'kirmizi':(232,98,78),'mavi':(96,156,236),'yesil':(120,196,132),'turuncu':(236,160,72),'mor':(200,120,220)}
MEP_KREM2={'kirmizi':(196,54,40),'mavi':(40,92,186),'yesil':(46,136,74),'turuncu':(204,120,30),'mor':(150,60,170)}
def _mep_masks(a):
    hsv=cv2.cvtColor(a,cv2.COLOR_RGB2HSV).astype(np.float32); h,s,v=hsv[...,0]*2,hsv[...,1]/255,hsv[...,2]/255
    M={'kirmizi':(s>0.45)&(v>0.3)&((h<14)|(h>340)),'turuncu':(s>0.40)&(v>0.35)&(h>=14)&(h<48),
       'yesil':(s>0.30)&(v>0.3)&(h>=85)&(h<165),'mavi':(s>0.45)&(v>0.25)&(h>=205)&(h<250),'mor':(s>0.35)&(v>0.35)&(h>=280)&(h<330)}
    H_=a.shape[0]
    for n,m in M.items():
        m=m.astype(np.uint8); nl,lab,st,_=cv2.connectedComponentsWithStats(m,8)
        keep=np.zeros(nl,bool); keep[1:]=st[1:,cv2.CC_STAT_AREA]>=(90 if n=='turuncu' else 12)
        if n=='turuncu':   # toprak/saksı dokusu gibi benekli alanları at: boru uzun ve dolu olur
            bw_=st[1:,cv2.CC_STAT_WIDTH]; bh_=st[1:,cv2.CC_STAT_HEIGHT]; fill=st[1:,cv2.CC_STAT_AREA]/(bw_*bh_+1e-6)
            keep[1:]&=(np.maximum(bw_,bh_)/np.maximum(1,np.minimum(bw_,bh_))>3)|(fill>0.45)
        if n=='mavi': keep[1:]&=~(st[1:,cv2.CC_STAT_TOP]<H_*0.30)   # gökyüzü/bulut
        M[n]=keep[lab]
    return M
def bim_eskiz_detay(src,no,name,loc,tur='BİM',kutu=None,koyu=True,zoom_hedef=None):
    BG_=(24,22,20) if koyu else STONE; AC=GOLD if koyu else BRONZE; TX=(236,228,214) if koyu else INK; MU=(170,156,136) if koyu else MUTE
    LN=np.array(GOLD if koyu else (88,70,54),np.float32); PAL=MEP_KOYU2 if koyu else MEP_KREM2
    full=(src if isinstance(src,Image.Image) else Image.open(src)).convert('RGB')
    if kutu: full=full.crop(kutu)
    bw,bh=W-2*96,880; full=cover(full,int(bw*1.8),int(bh*1.8))   # 1.8x çalış, sonra küçült
    a=np.asarray(full)
    # yapı çizgisi
    g=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY)
    hsv=cv2.cvtColor(a,cv2.COLOR_RGB2HSV).astype(np.float32)
    sky=(hsv[...,0]*2>185)&(hsv[...,0]*2<245)&(hsv[...,2]/255>0.5)&(hsv[...,1]/255>0.10)&(hsv[...,1]/255<0.6)
    gb=cv2.GaussianBlur(g,(0,0),1.1)
    ce=cv2.Canny(gb,22,70).astype(np.float32)/255
    dark=(g<60).astype(np.uint8)                                  # kesit pochesi (döşeme/kolon) → kontur + tarama
    dark=cv2.morphologyEx(dark,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    cont=cv2.morphologyEx(dark,cv2.MORPH_GRADIENT,np.ones((5,5),np.uint8)).astype(np.float32)
    bina=(~sky).astype(np.uint8); bina=cv2.morphologyEx(bina,cv2.MORPH_OPEN,np.ones((9,9),np.uint8))
    sil=cv2.morphologyEx(bina,cv2.MORPH_GRADIENT,np.ones((5,5),np.uint8)).astype(np.float32)
    yy,xx=np.mgrid[0:a.shape[0],0:a.shape[1]]; hatch=(((xx+yy)%14)<2).astype(np.float32)*dark*0.55
    ce=cv2.dilate(ce,np.ones((2,2),np.uint8))
    line=np.clip(np.maximum.reduce([ce*0.85,cont,hatch]),0,1); line[sky]*=0.08
    line=np.maximum(line,sil*0.9)
    M=_mep_masks(a); mep=np.zeros(g.shape,bool)
    for m in M.values(): mep|=m
    line[cv2.dilate(mep.astype(np.uint8),np.ones((5,5),np.uint8))>0]*=0.3
    out=np.ones(a.shape,np.float32)*np.array(BG_,np.float32)
    out=out*(1-line[...,None]*0.9)+LN*line[...,None]*0.9
    for n,m in M.items():
        c=np.array(PAL[n],np.float32)
        mk=cv2.dilate(m.astype(np.uint8),np.ones((3,3),np.uint8))       # ince boruları kalınlaştır
        if koyu:
            glow=cv2.GaussianBlur(mk.astype(np.float32),(0,0),5)*0.45
            out=out*(1-glow[...,None])+c*glow[...,None]
        body=cv2.GaussianBlur(mk.astype(np.float32),(0,0),0.8)
        out=out*(1-body[...,None]*0.92)+c*body[...,None]*0.92
        hl=cv2.erode(mk,np.ones((3,3),np.uint8)).astype(np.float32)*0.35   # boru parlaklık çizgisi
        out=out*(1-hl[...,None])+np.array((255,250,240),np.float32)*hl[...,None]
    sk=Image.fromarray(out.clip(0,255).astype(np.uint8)); ds=ImageDraw.Draw(sk)
    ver=(M['turuncu']|M['kirmizi']|M['mavi']).astype(np.uint8)
    ver=cv2.morphologyEx(ver,cv2.MORPH_CLOSE,np.ones((25,7),np.uint8))
    nl,lab,st,_=cv2.connectedComponentsWithStats(ver,8)
    for i in range(1,nl):
        x,y,w_,h_,ar=st[i]
        if h_>a.shape[0]*0.22 and h_>w_*4:
            p=14; x0,y0,x1,y1=x-p,y-p,x+w_+p,y+h_+p; col=tuple(int(v) for v in (LN if not koyu else np.array(GOLD)))
            for yy_ in range(y0,y1,22): ds.line([(x0,yy_),(x0,min(y1,yy_+12))],fill=col,width=3); ds.line([(x1,yy_),(x1,min(y1,yy_+12))],fill=col,width=3)
            for xx_ in range(x0,x1,22): ds.line([(xx_,y0),(min(x1,xx_+12),y0)],fill=col,width=3); ds.line([(xx_,y1),(min(x1,xx_+12),y1)],fill=col,width=3)
    sk=sk.resize((bw,bh),Image.LANCZOS)
    bg=Image.new('RGB',(W,H),BG_); arr=np.asarray(sk).astype(np.float32)
    yy,xx=np.mgrid[0:bh,0:bw]; mm=np.clip(np.minimum.reduce([xx/60,(bw-xx)/60,yy/40,(bh-yy)/80]),0,1)[...,None]
    bg.paste(Image.fromarray((np.array(BG_,np.float32)*(1-mm)+arr*mm).astype(np.uint8)),(96,140))
    d=ImageDraw.Draw(bg,'RGBA'); frame_line(d,40,GOLD+(255,),2)
    track(d,(96,90),f'№ {no:02d}   ·   '+up(tur),ImageFont.truetype(INTER_M,28),AC,6)
    d.line([(96,1070),(196,1070)],fill=GOLD,width=2)
    f=ImageFont.truetype(SERIF_I,118)
    while d.textlength(name,font=f)>W-192: f=ImageFont.truetype(SERIF_I,f.size-4)
    d.text((92,1206),name,font=f,fill=TX,anchor='ls'); track(d,(96,1258),up(loc),ImageFont.truetype(INTER_M,27),MU,7)
    return bg
# ================= BİM manşet kapağı: eskiz + tek cümle (ızgaradan okunur) =================
BIM_MANSETLER=[['Süperpoze,','üç boyutta.'],['Bütçe,','ilk çizgide belli.'],['Tasarım ve uygulama,','aynı modelde.'],
 ['Çakışma sahada değil,','modelde çözülür.'],['Her boru, yerini','inşaattan önce bilir.'],['Görünmeyeni de','tasarlıyoruz.'],
 ['Tek model.','Tek doğru.'],['Şantiyeye sürpriz değil,','pafta gider.']]
def bim_manset(src,satirlar,altyazi,kutu=None,koyu=True,ust='MOTİFO  ·  BİM'):
    base=bim_eskiz_detay(src,0,'','',' ',kutu=kutu,koyu=koyu)      # görsel alanı + çerçeve
    BG_=(24,22,20) if koyu else STONE; TX=(244,236,222) if koyu else INK; AC=GOLDT if koyu else BRONZE; MU=(170,156,136) if koyu else MUTE
    d=ImageDraw.Draw(base)
    d.rectangle([60,60,W-60,140],fill=BG_); d.rectangle([60,1050,W-60,H-60],fill=BG_)   # eski künyeyi temizle
    frame_line(d,40,GOLD,2)
    track(d,(96,96),ust,ImageFont.truetype(INTER_M,28),AC,8)
    f=ImageFont.truetype(SERIF_I,112)
    for s_ in satirlar:
        while d.textlength(s_,font=f)>W-190: f=ImageFont.truetype(SERIF_I,f.size-4)
    y=1150
    for i,s_ in enumerate(satirlar): d.text((92,y+i*116),s_,font=f,fill=TX,anchor='ls')
    track(d,(96,H-92),up(altyazi),ImageFont.truetype(INTER_M,24),MU,7)
    return base
def sade_sayfa(img,etiket,koyu=False,sayfa=None,toplam=None):
    """İç sayfa: tam ekran görsel + tek küçük etiket."""
    im=cover(img,W,H).convert('RGBA'); d=ImageDraw.Draw(im,'RGBA')
    g=Image.new('L',(1,256)); [g.putpixel((0,i),int(140*max(0,(i-190)/66)**1.5)) for i in range(256)]
    sh=Image.new('RGBA',(W,H),(14,12,10,0)); sh.putalpha(g.resize((W,H))); im.alpha_composite(sh); d=ImageDraw.Draw(im,'RGBA')
    track(d,(80,H-90),up(etiket),ImageFont.truetype(INTER_M,26),(255,255,255,230),7)
    if sayfa: track(d,(W-80,H-90),f'{sayfa:02d} / {toplam:02d}',ImageFont.truetype(INTER_M,26),(255,255,255,200),5,'r')
    return im.convert('RGB')
# ================= BİM açıklamalı sayfa (gerçek görüntü + şematik oklar) =================
def bim_aciklamali(img,notlar,kutular=(),baslik='BİM  ·  ARMA',sayfa=None,toplam=None):
    """img: 1080x1440'a oturtulacak görüntü; notlar: [(etiket,(hx,hy),(lx,ly),renk)] — h=hedef nokta, l=etiket konumu."""
    im=cover(img,W,H).convert('RGBA'); d=ImageDraw.Draw(im,'RGBA')
    for (x0,y0,x1,y1,etiket) in kutular:
        for yy in range(int(y0),int(y1),24): d.line([(x0,yy),(x0,min(y1,yy+12))],fill=INK+(220,),width=3); d.line([(x1,yy),(x1,min(y1,yy+12))],fill=INK+(220,),width=3)
        for xx in range(int(x0),int(x1),24): d.line([(xx,y0),(min(x1,xx+12),y0)],fill=INK+(220,),width=3); d.line([(xx,y1),(min(x1,xx+12),y1)],fill=INK+(220,),width=3)
    f=ImageFont.truetype(INTER_M,25)
    for et,(hx,hy),(lx,ly),col in notlar:
        tw=sum(d.textlength(c,font=f) for c in up(et))+3*len(et); bw_=tw+70; bh_=56
        # etiket kutusunun hedefe bakan kenarı
        ax=lx if hx<lx else lx+bw_; ay=ly+bh_/2
        mx=hx if abs(hy-ay)>40 else (hx+ax)/2
        d.line([(ax,ay),(mx,ay),(hx,hy)],fill=INK+(235,),width=3)
        d.ellipse([hx-11,hy-11,hx+11,hy+11],outline=INK+(255,),width=3,fill=(255,255,255,200))
        d.ellipse([hx-5,hy-5,hx+5,hy+5],fill=col+(255,))
        d.rounded_rectangle([lx,ly,lx+bw_,ly+bh_],radius=28,fill=(248,245,240,240),outline=INK+(60,),width=1)
        d.ellipse([lx+20,ly+20,lx+36,ly+36],fill=col+(255,))
        track(d,(lx+50,ly+14),up(et),f,INK,3)
    # üst bant
    sh=Image.new('RGBA',(W,170),(248,245,240,215)); im.alpha_composite(sh,(0,0)); d=ImageDraw.Draw(im,'RGBA')
    track(d,(80,70),baslik,ImageFont.truetype(INTER_M,26),BRONZE,7)
    if sayfa: track(d,(W-80,70),f'{sayfa:02d} / {toplam:02d}',ImageFont.truetype(INTER_M,26),BRONZE,5,'r')
    return im.convert('RGB')
