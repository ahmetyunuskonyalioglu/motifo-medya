# 10 Kasım 2026 – sabit tasarım (story 9:16 + gönderi 4:5). Söz + küçük Şeref Holü cephe çizimi + altın logo.
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from onkasim import *
def tasarim(W2,H2,ust,soz_y,ciz_w,ciz_y,logo_y,logo_w,fs):
    full=cephe(9.0)                                   # çizim tamam, yazı/logo yok
    ciz=full.crop((40,440,1040,1500)); ciz=ciz.resize((ciz_w,int(ciz.height*ciz_w/ciz.width)),Image.LANCZOS)
    im=Image.new('RGB',(W2,H2),BG); d=ImageDraw.Draw(im,'RGBA')
    for x in range(0,W2,40): d.line([(x,0),(x,H2)],fill=GOLD+(10,))
    for y in range(0,H2,40): d.line([(0,y),(W2,y)],fill=GOLD+(10,))
    I.track(d,(W2//2,ust),'10 KASIM 1938  ·  09.05',ImageFont.truetype(I.INTER_M,26),GOLD,9,'m')
    f=ImageFont.truetype(I.SERIF_I,fs); y=soz_y
    for s in ['“Benim naçiz vücudum','elbet bir gün toprak olacaktır,','fakat Türkiye Cumhuriyeti','ilelebet payidar kalacaktır.”']:
        d.text((W2//2,y),s,font=f,fill=LINE,anchor='ms'); y+=int(fs*1.22)
    d.line([(W2//2-40,y+10),(W2//2+40,y+10)],fill=GOLD,width=1)
    I.track(d,(W2//2,y+70),'MUSTAFA KEMAL ATATÜRK',ImageFont.truetype(I.INTER_M,24),MUTE,8,'m')
    im.paste(ciz,((W2-ciz.width)//2,ciz_y))
    lg=Image.open(R+'/marka/logo_altin.png').convert('RGBA'); lg.thumbnail((logo_w,logo_w),Image.LANCZOS)
    im=im.convert('RGBA'); im.alpha_composite(lg,((W2-lg.width)//2,logo_y)); return im.convert('RGB')
tasarim(1080,1920,300,470,640,1000,1640,220,62).save(O+'10kasim_story.jpg',quality=94)
tasarim(1080,1350,130,265,420,700,1205,115,50).save(O+'10kasim_gonderi_4x5.jpg',quality=94)
print('ok')
