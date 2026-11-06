# Pide Paradise (Uçhisar, Kapadokya) tasarım karuseli — ızgara döngüsü: KREM çizim (kapak eskiz).
# Akış: 1 krem eskiz kapak → 2 aynı karede eskizden render'a yumuşak geçiş → tam ekran renderlar (sade_sayfa).
# Kaynaklar 1080 px şablonlu ve küçük → cropframe + sr.py (Real-ESRGAN x4).
import sys,os
import numpy as np
R='/home/claude/motifo-medya'; sys.path.insert(0,R+'/araclar')
import izgara as I, sr
from PIL import Image
P=R+'/kaynak/PROJELER/PİDECİ/'; O=os.path.dirname(os.path.abspath(__file__))+'/'
C={}
def L(f):
    if f not in C: C[f]=Image.open(sr.buyut(P+f)).convert('RGB')
    return C[f]
I.load=lambda p: L(os.path.basename(p))
def kirp(f,fx,fy=0.5,z=1.0):
    src=L(f); h=src.height/z; w=h*3/4
    x=min(max(0,fx*src.width-w/2),src.width-w); y=min(max(0,fy*src.height-h/2),src.height-h)
    return src.crop((int(x),int(y),int(x+w),int(y+h)))
def gecis(f,fx):
    im=I.cover(kirp(f,fx),I.W,I.H); s=I.sketch(im)
    paper=np.array(I.STONE,np.float32); ink=np.array(I.BRONZE,np.float32)*0.5+np.array(I.INK,np.float32)*0.5
    sk=paper*s[...,None]+ink*(1-s[...,None])
    x=np.linspace(0,1,I.W)[None,:,None]; m=np.clip((x-0.30)/0.32,0,1); m=m*m*(3-2*m)
    out=sk*(1-m)+np.asarray(im,np.float32)*m
    return Image.fromarray(out.astype(np.uint8))
KAP=('7.jpg',0.50)
SAY=[('5.jpg','Giriş',0.55,0.5,1.0),('1.jpg','Merdiven nişi',0.47,0.5,1.0),('6.jpg','Tuğla kemerli teras',0.40,0.5,1.0),('2.jpg','Teras, kuşbakışı',0.50,0.5,1.0),('8.jpg','Sokak cephesi',0.47,0.5,1.0)]
top=len(SAY)+2
kap=I.cizim(P+KAP[0],10,'Pide Paradise','Uçhisar, Kapadokya','Yeme-İçme',fx=KAP[1],koyu=False)
ims=[(kap,KAP[0]),(gecis(KAP[0],KAP[1]),KAP[0])]+[(I.sade_sayfa(kirp(f,fx,fy,z),e,sayfa=i+3,toplam=top),f) for i,(f,e,fx,fy,z) in enumerate(SAY)]
for i,(im,f) in enumerate(ims):
    im.save(O+f'izgara_34/{i+1:02d}.jpg',quality=93)
    I.dort_bes(im,L(f)).save(O+f'{i+1:02d}.jpg',quality=93)
open(O+'aciklama.txt','w').write("Pide Paradise, Uçhisar: taş kemerli giriş, tuğla kemerli teras ve sokağa açılan sıcak bir cephe.\n\n#restorantasarımı #Kapadokya #Uçhisar #mimarlık #MotifoMimarlık")
print('ok',[f for _,f in ims])
