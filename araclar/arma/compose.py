import sys,os,subprocess,numpy as np,cv2
sys.path.insert(0,'/home/claude/bim3d/arma'); sys.path.insert(0,'/home/claude/motifo-medya/araclar')
from xray import base_ghost,draw_layer,ease
import parallax
from PIL import Image,ImageDraw,ImageFont
W,H,FPS=1080,1920,30; BY0,BH=560,1000
fp=lambda q: subprocess.check_output(['fc-match','-f','%{file}',q]).decode()
MED=fp('Inter:style=Medium'); LIGHT=fp('Inter:style=Light'); SERIF_I=fp('Latin Modern Roman:style=Italic')
INK=(34,31,28); MUTE=(118,110,102); BRONZE=(146,108,74); BLUE=(44,100,170); BG=(246,243,238)
OUT=sys.argv[1]; os.makedirs(OUT,exist_ok=True)
def track(d,xy,text,font,fill,sp,anchor='m'):
    w=sum(d.textlength(c,font=font) for c in text)+sp*(len(text)-1); x=xy[0]-(w/2 if anchor=='m' else (w if anchor=='r' else 0))
    for c in text: d.text((x,xy[1]),c,font=font,fill=fill); x+=d.textlength(c,font=font)+sp
def kf(t,k):
    for (t0,x0),(t1,x1) in zip(k,k[1:]):
        if t0<=t<=t1: return x0+(x1-x0)*ease((t-t0)/(t1-t0))
    return k[-1][1] if t>k[-1][0] else k[0][1]
# ---------- çekim 1: fotoğraf | BİM ----------
photo=Image.open('/home/claude/bim3d/arma_foto.png').convert('RGB')
S=BH/photo.height; big=photo.resize((round(photo.width*S),BH),Image.LANCZOS)
from PIL import ImageFilter
big=big.filter(ImageFilter.UnsharpMask(1.2,60,2))
ghost=base_ghost(big,S)
D=parallax.depth(big); BW=big.width; OX=int(110*S)
gy,gx=np.mgrid[0:BH,0:W].astype(np.float32)
P=np.asarray(big); G=np.asarray(ghost)
T1=9.4
def maps(t,dur,dolly,tx):
    p=ease(t/dur); sc=1+dolly*p*(0.35+0.65*D[:,OX:OX+W]); near=0.25+D[:,OX:OX+W]
    cx,cy=W/2,BH*0.45
    mx=(gx-cx)/sc+cx+OX - tx*(p-0.5)*near; my=(gy-cy)/sc+cy
    return mx,my
SPLIT=[(0,-20),(1.2,-20),(3.4,W*0.5),(5.4,W*0.5),(6.8,W+20),(7.6,W+20),(9.0,W*0.42),(99,W*0.42)]
def shot1(t):
    mx,my=maps(t,T1,0.07,40)
    R=cv2.remap(P,mx,my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
    prog=ease((t-1.6)/5.6)
    X=Image.fromarray(G.copy()).convert('RGBA'); X.alpha_composite(draw_layer((BW,BH),prog,S=S))
    X=cv2.remap(np.asarray(X.convert('RGB')),mx,my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
    sx=int(kf(t,SPLIT)); img=R.copy()
    if sx>0: img[:,:min(W,sx)]=X[:,:min(W,sx)]
    return Image.fromarray(img),sx,prog
# ---------- çekim 2: gerçek Archicad modeli ----------
src2=Image.open('/home/claude/motifo-medya/kaynak/PROJELER/BAHADIR_ARMA/ŞEFFFAF_ZOOM_2.jpg').convert('RGB')
S2=BH*1.08/src2.height; b2=src2.resize((round(src2.width*S2),round(BH*1.08)),Image.LANCZOS)
D2=parallax.depth(b2); P2=np.asarray(b2); OX2=int(b2.width*0.5-W/2); OY2=int(BH*0.04)
T2=4.6
def shot2(t):
    p=ease(t/T2); d=D2[OY2:OY2+BH,OX2:OX2+W]; sc=1+0.08*p*(0.35+0.65*d); near=0.25+d
    cx,cy=W/2,BH/2
    mx=(gx-cx)/sc+cx+OX2+60*(p-0.5)*near; my=(gy-cy)/sc+cy+OY2
    return Image.fromarray(cv2.remap(P2,mx,my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT))
def frame(t):
    img=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(img,'RGBA')
    X0=T1-0.5   # geçiş başlangıcı
    if t<T1:
        b,sx,prog=shot1(t)
        if t>X0: b=Image.blend(b,shot2(t-X0),ease((t-X0)/0.5))
        img.paste(b,(0,BY0)); 
    else:
        b=shot2(t-X0); img.paste(b,(0,BY0)); sx=None
    d=ImageDraw.Draw(img,'RGBA')
    # yazılar
    a1=ease(t/0.6)*ease((X0+0.3-t)/0.4); a2=ease((t-X0-0.2)/0.5)
    for a,kick,l1,l2 in ((a1,'ARMA · BAHÇEŞEHİR','Görünen cephe,','görünmeyen her şey'),(a2,'ARCHICAD BİM MODELİ','Tesisat,','inşaattan önce çözülür')):
        if a<=0: continue
        off=(1-a)*12
        track(d,(W/2,190+off),kick,ImageFont.truetype(MED,24),BRONZE+(int(235*a),),7)
        d.text((W/2,330+off),l1,font=ImageFont.truetype(SERIF_I,74),fill=INK+(int(255*a),),anchor='ms')
        d.text((W/2,414+off),l2,font=ImageFont.truetype(SERIF_I,74),fill=INK+(int(255*a),),anchor='ms')
    if t<T1 and sx is not None:
        fa=1-ease((t-X0)/0.3) if t>X0 else 1
        y0,y1=BY0,BY0+BH
        if 0<sx<W:
            d.line([(sx,y0),(sx,y1)],fill=(255,255,255,int(245*fa)),width=3)
            cy=BY0+BH//2
            d.ellipse([sx-22,cy-22,sx+22,cy+22],fill=(255,255,255,int(245*fa)),outline=(0,0,0,int(50*fa)))
            d.polygon([(sx-12,cy),(sx-5,cy-7),(sx-5,cy+7)],fill=INK+(int(255*fa),)); d.polygon([(sx+12,cy),(sx+5,cy-7),(sx+5,cy+7)],fill=INK+(int(255*fa),))
        fl=ImageFont.truetype(MED,24)
        la=ease((sx-140)/120)*fa*a1; ra=ease((W-160-sx)/120)*fa*a1
        if la>0: track(d,(min(sx,W)-30,BY0+BH+50),'BİM',fl,BLUE+(int(240*la),),6,'r')
        if ra>0: track(d,(max(sx,0)+30,BY0+BH+50),'UYGULAMA',fl,INK+(int(230*ra),),6,'l')
        # tesisat açıklaması
        if 0.02<prog and la>0:
            items=[((52,150,96),'Pis su'),((46,108,214),'Temiz su'),((214,64,52),'Sıcak su'),((226,176,40),'Havalandırma')]
            x=64; f2=ImageFont.truetype(LIGHT,24); y=BY0+BH+110; aa=la*ease((t-2.0)/0.6)
            for c,n in items:
                d.rounded_rectangle([x,y-6,x+26,y+6],radius=3,fill=c+(int(255*aa),)); d.text((x+36,y),n,font=f2,fill=MUTE+(int(255*aa),),anchor='lm'); x+=36+d.textlength(n,font=f2)+34
    return img
if __name__=='__main__':
    ts=[float(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 and sys.argv[2]!='all' else [i/FPS for i in range(int((T1-0.5+T2)*FPS))]
    for i,t in enumerate(ts):
        frame(t).save(f'{OUT}/f{int(round(t*FPS)):05d}.jpg',quality=93)
