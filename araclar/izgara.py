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
