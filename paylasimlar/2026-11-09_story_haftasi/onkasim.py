# 10 Kasım 2026 story'si (2026 konsepti: "bir cephe, kendini çizer").
# Koyu pafta üzerinde krem/altın ince kalemle Anıtkabir Şeref Holü'nün sade ön cephesi çizilir:
# yapı ızgarası → zemin ve basamaklar → sütunlar (aşağıdan yukarı) → saçak/atik → orta aks + ölçü çizgisi
# (rakamsız, uydurma ölçü yok). Sonra tek satır ve altın logo (renklere dokunulmaz).
import sys,os,shutil,subprocess
R='/home/claude/motifo-medya'; sys.path.insert(0,R+'/araclar')
import izgara as I, muzik
from parallax import ease
from PIL import Image,ImageDraw,ImageFont
O=os.path.dirname(os.path.abspath(__file__))+'/'
SS=2; W,H=1080,1920; FPS=30
BG=(26,24,22); LINE=(226,212,188); GOLD=(190,152,96); MUTE=(150,138,120)
def seg(t,a,b): return ease((t-a)/(b-a))
def S(v): return int(v*SS)
X0,X1=150,930            # podyum
YB=1120                  # holün oturduğu kot
NC=8; CX0,CX1=205,875    # sütun aksları
CT,CB=770,1080           # sütun üst/alt
def cephe(t):
    im=Image.new('RGB',(W*SS,H*SS),BG); d=ImageDraw.Draw(im,'RGBA')
    g=seg(t,0,1.2)
    for x in range(0,W,40): d.line([(S(x),0),(S(x),S(H))],fill=GOLD+(int(14*g),),width=1)
    for y in range(0,H,40): d.line([(0,S(y)),(S(W),S(y))],fill=GOLD+(int(14*g),),width=1)
    f=seg(t,0.4,1.6)
    if f>0: d.rectangle([S(70),S(470),S(W-70),S(1490)],outline=GOLD+(int(150*f),),width=S(1))
    # zemin çizgisi + podyum
    p=seg(t,1.0,2.4)
    if p>0:
        cx=W/2; hw=(X1-X0)/2*p+40*p
        d.line([(S(cx-hw-60*p),S(YB+40)),(S(cx+hw+60*p),S(YB+40))],fill=LINE+(230,),width=S(1.5))
        d.line([(S(cx-hw),S(YB)),(S(cx+hw),S(YB))],fill=LINE+(230,),width=S(1.5))
        for k in range(1,4): d.line([(S(cx-hw-15*k),S(YB+10*k)),(S(cx+hw+15*k),S(YB+10*k))],fill=LINE+(int(150*p),),width=S(1))
    # yüksek podyum + ortada ana merdiven (sabit genişlik, yan korkuluk duvarları)
    p=seg(t,1.8,2.8)
    if p>0:
        a=int(220*p); PB=YB+40+230
        d.line([(S(X0-55),S(YB+40)),(S(X0-55),S(YB+40+230*p))],fill=LINE+(a,),width=S(1.5))
        d.line([(S(X1+55),S(YB+40)),(S(X1+55),S(YB+40+230*p))],fill=LINE+(a,),width=S(1.5))
        if p>=1: d.line([(S(X0-110),S(PB)),(S(X1+110),S(PB))],fill=LINE+(230,),width=S(1.5))
        for s_ in (-1,1): d.line([(S(W/2+s_*170),S(YB+40)),(S(W/2+s_*170),S(YB+40+230*p))],fill=LINE+(a,),width=S(1.2))
    for k in range(15):
        p=seg(t,2.2+k*0.06,2.7+k*0.06)
        if p<=0: continue
        y=YB+40+(k+1)*15
        d.line([(S(W/2-170*p),S(y)),(S(W/2+170*p),S(y))],fill=LINE+(int(170*p),),width=S(1))
    p=seg(t,2.6,3.4)
    if p>0:
        for y in range(YB+70,YB+270,30): d.line([(S(X0-55),S(y)),(S(X0-55+(W/2-170-X0+55)*p),S(y))],fill=GOLD+(int(35*p),),width=S(1)); d.line([(S(X1+55),S(y)),(S(X1+55-(X1+55-W/2-170)*p),S(y))],fill=GOLD+(int(35*p),),width=S(1))
    # sütunlar — aşağıdan yukarı
    step=(CX1-CX0)/(NC-1); cw=30
    for k in range(NC):
        p=seg(t,3.0+k*0.18,4.4+k*0.18)
        if p<=0: continue
        x=CX0+k*step; top=CB-(CB-CT)*p
        d.line([(S(x-cw/2),S(CB)),(S(x-cw/2),S(top))],fill=LINE+(240,),width=S(1.5))
        d.line([(S(x+cw/2),S(CB)),(S(x+cw/2),S(top))],fill=LINE+(240,),width=S(1.5))
        d.line([(S(x-cw/2-6),S(CB)),(S(x+cw/2+6),S(CB))],fill=LINE+(200,),width=S(1))
        if p>=1:
            d.line([(S(x-cw/2-6),S(CT)),(S(x+cw/2+6),S(CT))],fill=LINE+(220,),width=S(1))
            d.line([(S(x-cw/2-3),S(CT+10)),(S(x+cw/2+3),S(CT+10))],fill=LINE+(150,),width=S(1))
    # holün arka duvarı (sütunlar arası ince gölge çizgileri)
    p=seg(t,4.8,5.8)
    if p>0:
        for y in range(CT+30,CB,26): d.line([(S(CX0+20),S(y)),(S(CX1-20),S(y))],fill=GOLD+(int(40*p),),width=S(1))
    # saçak + atik
    p=seg(t,5.6,7.0)
    if p>0:
        a=int(240*p); L,Rr=X0+10,X1-10
        d.line([(S(L),S(CT)),(S(Rr),S(CT))],fill=LINE+(a,),width=S(1.5))
        d.line([(S(L-8),S(CT-36)),(S(Rr+8),S(CT-36))],fill=LINE+(a,),width=S(1.5))
        d.line([(S(L),S(CT-36)),(S(L),S(CT))],fill=LINE+(a,),width=S(1.5)); d.line([(S(Rr),S(CT-36)),(S(Rr),S(CT))],fill=LINE+(a,),width=S(1.5))
        d.rectangle([S(L+14),S(CT-120),S(Rr-14),S(CT-36)],outline=LINE+(a,),width=S(1.5))
        d.rectangle([S(L+60),S(CT-102),S(Rr-60),S(CT-54)],outline=GOLD+(int(170*p),),width=S(1))
        # yan kütleler
        d.line([(S(L),S(CT)),(S(L),S(YB))],fill=LINE+(a,),width=S(1.5)); d.line([(S(Rr),S(CT)),(S(Rr),S(YB))],fill=LINE+(a,),width=S(1.5))
    # orta aks (kesikli) + ölçü çizgisi (rakamsız)
    p=seg(t,7.0,8.2)
    if p>0:
        a=int(200*p); y=CT-170
        while y<YB+270:
            d.line([(S(W/2),S(y)),(S(W/2),S(min(y+22,YB+270)))],fill=GOLD+(a,),width=S(1)); y+=34
        yd=1440
        d.line([(S(CX0),S(yd)),(S(CX0+(CX1-CX0)*p),S(yd))],fill=GOLD+(a,),width=S(1))
        for k in range(NC):
            x=CX0+k*step
            if x<=CX0+(CX1-CX0)*p+1:
                d.line([(S(x-7),S(yd+7)),(S(x+7),S(yd-7))],fill=GOLD+(a,),width=S(1.5))
                d.line([(S(x),S(yd-14)),(S(x),S(yd+14))],fill=GOLD+(a,),width=S(1))
    im=im.resize((W,H),Image.LANCZOS); d=ImageDraw.Draw(im,'RGBA')
    a=seg(t,8.4,9.6)
    if a>0:
        I.track(d,(W//2,250),'10 KASIM 1938',ImageFont.truetype(I.INTER_M,28),GOLD+(int(255*a),),9,'m')
        d.text((W//2,362),'Saygı ve özlemle.',font=ImageFont.truetype(I.SERIF_I,84),fill=LINE+(int(255*a),),anchor='ms')
    a=seg(t,10.0,11.2)
    if a>0:
        lg=Image.open(R+'/marka/logo_altin.png').convert('RGBA'); lg.thumbnail((260,260),Image.LANCZOS)
        lg.putalpha(lg.getchannel('A').point(lambda v:int(v*a)))
        im=im.convert('RGBA'); im.alpha_composite(lg,((W-lg.width)//2,1580)); im=im.convert('RGB')
    return im
def main():
    tmp='/home/claude/st_10kasim'; shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp)
    D=13.0; N=int(D*FPS)
    for i in range(N): cephe(i/FPS).save(f'{tmp}/f{i:05d}.jpg',quality=93)
    muzik.keman(O+'onkasim.wav',D+0.3,[3.0,5.6,8.4],end_at=D,root=57,scale='minör',bpm=58,seed=61)
    muzik.kaydet(R+'/muzik_kayit.json','story_10kasim_2026','keman',57,'minör',61)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',f'{tmp}/f%05d.jpg','-i',O+'onkasim.wav','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',O+'2_sal_10kasim.mp4'],check=True)
    cephe(D).save(O+'2_sal_10kasim_son_kare.jpg',quality=93)
if __name__=='__main__':
    if len(sys.argv)>1: cephe(float(sys.argv[1])).save(sys.argv[2],quality=90)
    else: main()
