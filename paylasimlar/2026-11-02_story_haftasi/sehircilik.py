# 8 Kasım Dünya Şehircilik Günü story'si (2026 konsepti: "kent, bir planla başlar").
# Krem pafta üzerinde altın kalemle bir kent planı kendini çizer: aks çizgileri → sokak ızgarası → yapı adaları
# (taramalı) → eğri park/dere → meydan → ölçek çubuğu + kuzey oku. Sonra tek manşet ve altın logo (renklere dokunulmaz).
import sys,os,math,shutil,subprocess,random
R='/home/claude/motifo-medya'; sys.path.insert(0,R+'/araclar')
import izgara as I, muzik
from parallax import ease
from PIL import Image,ImageDraw,ImageFont
O=os.path.dirname(os.path.abspath(__file__))+'/'
SS=2; W,H=1080,1920; FPS=30
PAPER=(244,240,234); GOLD=(176,138,86); GOLD_D=(140,104,64); INK=I.INK
def seg(t,a,b): return ease((t-a)/(b-a))
rng=random.Random(8)
# plan alanı (story ortası)
PX0,PY0,PX1,PY1=110,420,970,1330
cols=[PX0+i*(PX1-PX0)/6 for i in range(7)]; rows=[PY0+i*(PY1-PY0)/7 for i in range(8)]
def park_curve(n=200):
    pts=[]
    for i in range(n+1):
        u=i/n; x=PX0-20+(PX1-PX0+40)*u
        y=PY0+(PY1-PY0)*(0.62+0.10*math.sin(u*math.pi*1.6+0.4)+0.04*math.sin(u*math.pi*4.3))
        pts.append((x,y))
    return pts
CURVE=park_curve()
def _cy(x):
    u=(x-(PX0-20))/(PX1-PX0+40); u=min(max(u,0),1)
    return PY0+(PY1-PY0)*(0.62+0.10*math.sin(u*math.pi*1.6+0.4)+0.04*math.sin(u*math.pi*4.3))
def in_river(x0,y0,x1,y1):
    # blok, dere/park şeridine ya da çapraz bulvara değiyorsa boş kalır
    for k in range(9):
        for m in range(9):
            x=x0+(x1-x0)*k/8; y=y0+(y1-y0)*m/8
            if abs(y-_cy(x))<62: return True
            # bulvar: (PX0,PY1)->(PX1,PY0)
            yl=PY1+(PY0-PY1)*(x-PX0)/(PX1-PX0)
            if abs(y-yl)<18: return True
    return False
BLOCKS=[]
for i in range(6):
    for j in range(7):
        x0,x1=cols[i]+14,cols[i+1]-14; y0,y1=rows[j]+14,rows[j+1]-14
        if abs((y0+y1)/2-_cy((x0+x1)/2))<40: continue
        if (i,j) in ((2,1),(3,1)): continue   # meydan
        BLOCKS.append((x0,y0,x1,y1,rng.random()))
BLOCKS.sort(key=lambda b:(b[1],b[0]))
def S(v): return v*SS
KESME=Image.new('L',(W*SS,H*SS),0); _k=ImageDraw.Draw(KESME)
_k.polygon([(S(x),S(y-60)) for x,y in CURVE]+[(S(x),S(y+60)) for x,y in CURVE[::-1]],fill=255)
_k.line([(S(PX0-40),S(PY1+40)),(S(PX1+40),S(PY0-40))],fill=255,width=S(40))
def plan(t):
    im=Image.new('RGB',(W*SS,H*SS),PAPER); d=ImageDraw.Draw(im,'RGBA')
    # ince milimetrik ızgara
    g=seg(t,0,0.6)
    for x in range(0,W,30): d.line([(S(x),0),(S(x),S(H))],fill=GOLD+(int(16*g),),width=1)
    for y in range(0,H,30): d.line([(0,S(y)),(S(W),S(y))],fill=GOLD+(int(16*g),),width=1)
    # pafta çerçevesi
    f=seg(t,0.2,1.0)
    if f>0: d.rectangle([S(70),S(380),S(W-70),S(1370)],outline=GOLD+(int(200*f),),width=S(1))
    # sokak aksları (ızgara)
    for k,x in enumerate(cols):
        p=seg(t,0.5+k*0.08,1.3+k*0.08)
        if p>0: d.line([(S(x),S(PY0)),(S(x),S(PY0+(PY1-PY0)*p))],fill=GOLD_D+(230,),width=S(2) if k in (0,6) else S(1))
    for k,y in enumerate(rows):
        p=seg(t,0.6+k*0.08,1.4+k*0.08)
        if p>0: d.line([(S(PX0),S(y)),(S(PX0+(PX1-PX0)*p),S(y))],fill=GOLD_D+(230,),width=S(2) if k in (0,7) else S(1))
    # ana bulvar (çapraz)
    p=seg(t,1.5,2.4)
    if p>0:
        a=(PX0,PY1); b=(PX1,PY0); e=(a[0]+(b[0]-a[0])*p,a[1]+(b[1]-a[1])*p)
        for o in (-9,9): d.line([(S(a[0]),S(a[1]+o)),(S(e[0]),S(e[1]+o))],fill=GOLD_D+(240,),width=S(2))
    # dere / park şeridi
    p=seg(t,2.0,3.2)
    if p>0:
        n=int(len(CURVE)*p)
        for off in (-46,46):
            pts=[(S(x),S(y+off)) for x,y in CURVE[:max(2,n)]]
            d.line(pts,fill=GOLD+(235,),width=S(2))
        # ağaç noktaları
        for k in range(0,n,7):
            x,y=CURVE[k]; r=rng.Random() if False else None
            rr=9+4*math.sin(k)
            yy=y+((k*37)%60-30)
            d.ellipse([S(x-rr),S(yy-rr),S(x+rr),S(yy+rr)],outline=GOLD+(170,),width=S(1))
    # yapı adaları: dolgu + tarama (ayrı katman; dere ve bulvar şeridi maskeyle kesilir)
    BL=Image.new('RGBA',im.size,(0,0,0,0)); d0=d; d=ImageDraw.Draw(BL,'RGBA')
    for k,(x0,y0,x1,y1,r) in enumerate(BLOCKS):
        p=seg(t,2.6+k*0.045,3.1+k*0.045)
        if p<=0: continue
        d.rectangle([S(x0),S(y0),S(x1),S(y1)],fill=GOLD+(int(26*p),),outline=GOLD_D+(int(210*p),),width=S(1))
        if r>0.45:   # tarama
            step=14
            for c in range(int(x0-(y1-y0)),int(x1),step):
                xa,ya,xb,yb=c,y1,c+(y1-y0),y0
                # kırp
                if xa<x0: ya-= (x0-xa); xa=x0
                if xb>x1: yb+= (xb-x1); xb=x1
                if xb>xa: d.line([(S(xa),S(ya)),(S(xb),S(yb))],fill=GOLD+(int(110*p),),width=S(1))
    d=d0; im.paste(BL,(0,0),Image.composite(Image.new('L',im.size,0),BL.getchannel('A'),KESME))
    # meydan: daire
    p=seg(t,4.2,5.0)
    if p>0:
        cx=(cols[2]+cols[4])/2; cy=(rows[1]+rows[2])/2; rr=52
        d.arc([S(cx-rr),S(cy-rr),S(cx+rr),S(cy+rr)],-90,-90+360*p,fill=GOLD_D+(240,),width=S(2))
        d.arc([S(cx-rr*0.45),S(cy-rr*0.45),S(cx+rr*0.45),S(cy+rr*0.45)],-90,-90+360*p,fill=GOLD+(200,),width=S(1))
    # ölçek çubuğu + kuzey oku
    p=seg(t,4.6,5.4)
    if p>0:
        a=int(230*p); y=1410; x0=PX0
        for k in range(4):
            fill=GOLD_D+(a,) if k%2==0 else None
            d.rectangle([S(x0+k*50),S(y),S(x0+(k+1)*50),S(y+10)],fill=fill,outline=GOLD_D+(a,),width=S(1))
        fnt=ImageFont.truetype(I.INTER_M,S(17))
        for k,lab in enumerate(['0','50','100','150','200 m']):
            d.text((S(x0+k*50),S(y+20)),lab,font=fnt,fill=GOLD_D+(a,),anchor='mt')
        nx,ny=PX1-20,1420
        d.polygon([(S(nx),S(ny-34)),(S(nx-12),S(ny+6)),(S(nx),S(ny-4))],fill=GOLD_D+(a,))
        d.polygon([(S(nx),S(ny-34)),(S(nx+12),S(ny+6)),(S(nx),S(ny-4))],outline=GOLD_D+(a,))
        d.text((S(nx),S(ny+16)),'K',font=fnt,fill=GOLD_D+(a,),anchor='mt')
    im=im.resize((W,H),Image.LANCZOS)
    # metin
    d=ImageDraw.Draw(im,'RGBA')
    a=seg(t,5.2,6.2)
    if a>0:
        I.track(d,(W//2,215),'8 KASIM  ·  DÜNYA ŞEHİRCİLİK GÜNÜ',ImageFont.truetype(I.INTER_M,26),I.BRONZE+(int(255*a),),8,'m')
        d.text((W//2,320),'Kent, bir planla başlar.',font=ImageFont.truetype(I.SERIF_I,82),fill=INK+(int(255*a),),anchor='ms')
    a=seg(t,6.4,7.6)
    if a>0:
        lg=Image.open(R+'/marka/logo_altin.png').convert('RGBA'); lg.thumbnail((300,300),Image.LANCZOS)
        al=lg.getchannel('A').point(lambda v:int(v*a)); lg.putalpha(al)
        im=im.convert('RGBA'); im.alpha_composite(lg,((W-lg.width)//2,1560)); im=im.convert('RGB')
    return im
def main():
    tmp='/home/claude/st_sehir'; shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp)
    D=10.0; N=int(D*FPS)
    for i in range(N): plan(i/FPS).save(f'{tmp}/f{i:05d}.jpg',quality=93)
    muzik.keman(O+'sehircilik.wav',D+0.3,[2.0,4.2,6.4],end_at=D,root=62,scale='majör',bpm=76,seed=47)
    muzik.kaydet(R+'/muzik_kayit.json','story_8kasim_sehircilik_2026','keman',62,'majör',47)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',f'{tmp}/f%05d.jpg','-i',O+'sehircilik.wav','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',O+'5_paz_8kasim_sehircilik.mp4'],check=True)
    plan(D).save(O+'5_paz_8kasim_son_kare.jpg',quality=93)
if __name__=='__main__':
    if len(sys.argv)>1: plan(float(sys.argv[1])).save(sys.argv[2],quality=90)
    else: main()
