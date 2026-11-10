# 10 Kasım – portreli tasarım. Kullanım: python3 onkasim_portre.py foto.jpg
# Koyu sıcak zemin + üstten yumuşak ışık, ince altın çerçevede sepya portre, altında künye + Şeref Holü çizimi + altın logo.
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from onkasim import *
import numpy as np
from PIL import ImageFilter,ImageOps
def sepya(im):
    g=np.asarray(ImageOps.autocontrast(im.convert('L'),cutoff=1)).astype(np.float32)/255
    lo=np.array([38,30,24],np.float32); hi=np.array([238,226,204],np.float32)
    return Image.fromarray((lo+(hi-lo)*g[...,None]).astype(np.uint8))
def zemin(W2,H2,cy):
    yy,xx=np.mgrid[0:H2,0:W2].astype(np.float32)
    r=np.sqrt(((xx-W2/2)/(W2*0.75))**2+((yy-cy)/(H2*0.55))**2)
    k=np.clip(1-r,0,1)**1.6
    base=np.array([20,17,14],np.float32); warm=np.array([92,66,40],np.float32)
    a=base+(warm-base)*k[...,None]
    a+=np.random.default_rng(3).normal(0,2.2,(H2,W2,1))
    return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
def tasarim(foto,W2,H2,fw,fy,ty,ciz_w,ciz_y,logo_y,logo_w,fs):
    im=zemin(W2,H2,fy+fw*0.6); d=ImageDraw.Draw(im,'RGBA')
    fh=int(fw*1.25); p=I.cover(sepya(foto),fw,fh,0.5,0.3)
    x0=(W2-fw)//2
    sh=Image.new('RGBA',(W2,H2),(0,0,0,0)); ImageDraw.Draw(sh).rectangle([x0+14,fy+24,x0+fw+14,fy+fh+24],fill=(0,0,0,150))
    im=im.convert('RGBA'); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22))); im=im.convert('RGB'); d=ImageDraw.Draw(im,'RGBA')
    m=26; d.rectangle([x0-m,fy-m,x0+fw+m,fy+fh+m],fill=(232,224,208)); d.rectangle([x0-m,fy-m,x0+fw+m,fy+fh+m],outline=GOLD,width=3)
    d.rectangle([x0-m+8,fy-m+8,x0+fw+m-8,fy+fh+m-8],outline=GOLD+(160,),width=1)
    im.paste(p,(x0,fy)); d=ImageDraw.Draw(im,'RGBA')
    y=fy+fh+m+ty
    d.line([(W2//2-300,y-9),(W2//2-170,y-9)],fill=GOLD,width=1); d.line([(W2//2+170,y-9),(W2//2+300,y-9)],fill=GOLD,width=1)
    I.track(d,(W2//2,y),'10 KASIM',ImageFont.truetype(I.INTER_M,30),GOLD,12,'m')
    I.track(d,(W2//2,y+50),'1881 – 1938',ImageFont.truetype(I.INTER_M,22),MUTE,8,'m')
    d.text((W2//2,y+50+fs*1.5),'Saygı ve özlemle.',font=ImageFont.truetype(I.SERIF_I,fs),fill=LINE,anchor='ms')
    if ciz_w:
        full=cephe(9.0).crop((40,440,1040,1500)); c=full.resize((ciz_w,int(full.height*ciz_w/full.width)),Image.LANCZOS)
        a=np.asarray(c).astype(np.float32); bgc=np.array(BG,np.float32); al=np.clip((a-bgc).max(-1)/120,0,1)
        lay=Image.fromarray(a.astype(np.uint8)).convert('RGBA'); lay.putalpha(Image.fromarray((al*255).astype(np.uint8)))
        im=im.convert('RGBA'); im.alpha_composite(lay,((W2-ciz_w)//2,ciz_y)); im=im.convert('RGB')
    lg=Image.open(R+'/marka/logo_altin.png').convert('RGBA'); lg.thumbnail((logo_w,logo_w),Image.LANCZOS)
    im=im.convert('RGBA'); im.alpha_composite(lg,((W2-lg.width)//2,logo_y)); return im.convert('RGB')
if __name__=='__main__':
    f=Image.open(sys.argv[1]).convert('RGB')
    tasarim(f,1080,1920,600,260,90,300,1420,1700,170,76).save(O+'10kasim_portre_story.jpg',quality=94)
    tasarim(f,1080,1350,420,120,70,0,0,1200,105,58).save(O+'10kasim_portre_gonderi_4x5.jpg',quality=94)
    print('ok')
