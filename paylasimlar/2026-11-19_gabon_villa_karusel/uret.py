# Gabon Villası — tasarım karuseli. Izgara döngüsü: render (2/4), kapak 'kenar' (reels kapağı çerçeveli → yan yana farklı).
# Kaynaklar 1080 px şablonlu → cropframe + sr.py (Real-ESRGAN x4). Müştemilat görseli (26) kullanılmadı. Kapak 13, story duyurusu 11.
import sys,os
R='/home/claude/motifo-medya'; sys.path.insert(0,R+'/araclar')
import izgara as I, sr
from PIL import Image
P=R+'/kaynak/PROJELER/AFRİKA/'; O=os.path.dirname(os.path.abspath(__file__))+'/'
C={}
def L(f):
    if f not in C: C[f]=Image.open(sr.buyut(P+f)).convert('RGB')
    return C[f]
I.load=lambda p: L(os.path.basename(p))
def sayfa(f,et,fx,fy,z,no,top):
    src=L(f); h=src.height/z; w=h*3/4
    x=min(max(0,fx*src.width-w/2),src.width-w); y=min(max(0,fy*src.height-h/2),src.height-h)
    return I.sade_sayfa(src.crop((int(x),int(y),int(x+w),int(y+h))),et,sayfa=no,toplam=top)
KAP=('13.jpg',0.42)
SAY=[('8.jpg','Havuz ve bahçe',0.40,0.5,1.0),('10.jpg','Cephe',0.50,0.5,1.0),('30.jpg','Yatak odası',0.50,0.5,1.0),
     ('34.jpg','Çalışma odası',0.45,0.5,1.0),('21.jpg','Banyo',0.40,0.5,1.0)]
top=len(SAY)+1
kap=I.sade(P+KAP[0],22,'Gabon Villası','Gabon','kenar',fx=KAP[1])
ims=[(kap,KAP[0])]+[(sayfa(f,e,fx,fy,z,i+2,top),f) for i,(f,e,fx,fy,z) in enumerate(SAY)]
for i,(im,f) in enumerate(ims):
    im.save(O+f'izgara_34/{i+1:02d}.jpg',quality=93)
    I.dort_bes(im,L(f)).save(O+f'{i+1:02d}.jpg',quality=93)
open(O+'aciklama.txt','w').write('Gabon’da bir villa: ahşap ve beyaz yüzeylerle katmanlanan cephe, havuza açılan bahçe ve sakin iç mekânlar.\n\n#villatasarımı #konutmimarisi #içmimari #mimarlık #MotifoMimarlık')
print('ok',[f for _,f in ims])
