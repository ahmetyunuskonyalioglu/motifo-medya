# YCR Pesta Hotel (Antalya Lara) tasarım karuseli — ızgara döngüsü: render (2/4), kapak 'kenar'.
# Kaynaklar 3600 px şablonlu → cropframe ile kırpılır, SR gerekmez (CLAUDE.md). 5.jpg geçmişte paylaşıldı → kullanılmaz.
import sys,os
R='/home/claude/motifo-medya'; sys.path.insert(0,R+'/araclar')
import izgara as I
from cropframe import crop_render
P=R+'/kaynak/PROJELER/YCR CONSTRACT, ANTALYA LARA/'; O=os.path.dirname(os.path.abspath(__file__))+'/'
C={}
def L(f):
    if f not in C: C[f]=crop_render(P+f)
    return C[f]
I.load=lambda p: L(os.path.basename(p))
def sayfa(f,et,fx,fy,z,no,top):
    src=L(f); h=src.height/z; w=h*3/4
    x=min(max(0,fx*src.width-w/2),src.width-w); y=min(max(0,fy*src.height-h/2),src.height-h)
    return I.sade_sayfa(src.crop((int(x),int(y),int(x+w),int(y+h))),et,sayfa=no,toplam=top)
KAP=('2.jpg',0.50)
SAY=[('3.jpg','Kavisli çatı',0.30,0.5,1.0),('4.jpg','Yan cephe',0.48,0.5,1.0),('1.jpg','Zemin kat',0.24,0.5,1.0),('2.jpg','Cephe detayı',0.50,0.32,1.4)]
top=len(SAY)+1
kap=I.sade(P+KAP[0],6,'YCR','Antalya Lara','kenar',fx=KAP[1])
ims=[(kap,KAP[0])]+[(sayfa(f,e,fx,fy,z,i+2,top),f) for i,(f,e,fx,fy,z) in enumerate(SAY)]
for i,(im,f) in enumerate(ims):
    im.save(O+f'izgara_34/{i+1:02d}.jpg',quality=93)
    I.dort_bes(im,L(f)).save(O+f'{i+1:02d}.jpg',quality=93)
open(O+'aciklama.txt','w').write('Antalya Lara’da bir yapı: koyu taş cephe, kavisli çatı ve sokağa açılan zemin kat.\n\n#AntalyaMimar #ticariyapı #cephetasarımı #mimarlık #MotifoMimarlık')
print('ok',[f for _,f in ims])
