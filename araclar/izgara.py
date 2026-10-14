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
def cizim(src,no,name,loc,tur,fx=0.5,fy=0.5,zoom=1.0):
    bg=Image.new('RGB',(W,H),STONE); d=ImageDraw.Draw(bg,'RGBA')
    bw,bh=W-2*96,820
    im=cover(load(src),bw,bh,fx,fy,zoom); s=sketch(im)
    ink=np.array(BRONZE,np.float32)*0.55+np.array(INK,np.float32)*0.45
    paper=np.array(STONE,np.float32)
    arr=paper*s[...,None]+ink*(1-s[...,None])
    # kenarlara doğru eriyen çizim
    yy,xx=np.mgrid[0:bh,0:bw]; m=np.clip(np.minimum.reduce([xx/80,(bw-xx)/80,yy/60,(bh-yy)/80]),0,1)[...,None]
    arr=paper*(1-m)+arr*m
    bg.paste(Image.fromarray(arr.astype(np.uint8)),(96,150))
    frame_line(d,40,GOLD+(255,),2)
    track(d,(96,90),f'№ {no:02d}   ·   '+up(tur),ImageFont.truetype(INTER_M,28),BRONZE,6)
    d.line([(96,1050),(196,1050)],fill=GOLD,width=2)
    f=ImageFont.truetype(SERIF_I,118)
    while d.textlength(name,font=f)>W-192: f=ImageFont.truetype(SERIF_I,f.size-4)
    d.text((92,1196),name,font=f,fill=INK,anchor='ls')
    track(d,(96,1250),up(loc),ImageFont.truetype(INTER_M,27),MUTE,7)
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
