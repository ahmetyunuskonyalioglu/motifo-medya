# Ofis (kaynak klasörü SHOWROOM) tasarım karuseli — ızgara döngüsü: render (2/4), kapak 'alt_orta'.
# Kaynaklar 1080 px şablonlu ve küçük → cropframe + sr.py (Real-ESRGAN x4). Konum bilinmiyor → yazılmaz.
import sys,os
R='/home/claude/motifo-medya'; sys.path.insert(0,R+'/araclar')
import izgara as I, sr
from PIL import Image
P=R+'/kaynak/PROJELER/SHOWROOM/'; O=os.path.dirname(os.path.abspath(__file__))+'/'
C={}
def L(f):
    if f not in C: C[f]=Image.open(sr.buyut(P+f)).convert('RGB')
    return C[f]
I.load=lambda p: L(os.path.basename(p))
def sayfa(f,et,fx,fy,z,no,top):
    src=L(f); h=src.height/z; w=h*3/4
    x=min(max(0,fx*src.width-w/2),src.width-w); y=min(max(0,fy*src.height-h/2),src.height-h)
    return I.sade_sayfa(src.crop((int(x),int(y),int(x+w),int(y+h))),et,sayfa=no,toplam=top)
KAP=('3.jpg',0.40)
SAY=[('4.jpg','Raf duvarı',0.40,0.5,1.0),('8.jpg','Kemerli niş',0.52,0.5,1.0),('6.jpg','Dolap duvarı',0.62,0.5,1.0),('10.jpg','Ortak alan',0.40,0.5,1.0)]
top=len(SAY)+1
kap=I.sade(P+KAP[0],8,'Ofis','İç mimari','alt_orta',fx=KAP[1])
ims=[(kap,KAP[0])]+[(sayfa(f,e,fx,fy,z,i+2,top),f) for i,(f,e,fx,fy,z) in enumerate(SAY)]
for i,(im,f) in enumerate(ims):
    im.save(O+f'izgara_34/{i+1:02d}.jpg',quality=93)
    I.dort_bes(im,L(f)).save(O+f'{i+1:02d}.jpg',quality=93)
open(O+'aciklama.txt','w').write('Bir ofis: ışıklı kemer nişleri, ahşap raf duvarı ve ortak masa etrafında kurulan çalışma düzeni.\n\n#ofistasarımı #içmimari #çalışmaalanı #mimarlık #MotifoMimarlık')
print('ok',[f for _,f in ims])
