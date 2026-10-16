# Metricool ile paylaşılan eski tasarımlı gönderilerin yeni düzene uygun halleri.
# Gabon karuseli (render tipi, 'cerceve' kapak) + Oyster reels için yeni kapak. Tümü SR'li kaynaktan.
import sys,os
R=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..')); sys.path.insert(0,R+'/araclar')
import izgara as I, sr
from PIL import Image
P=R+'/kaynak/PROJELER/'; O=os.path.dirname(os.path.abspath(__file__))+'/'
SRL=lambda p: Image.open(sr.buyut(P+p)).convert('RGB')
I.load=lambda p: SRL(p[len(P):]) if p.startswith(P) else Image.open(p).convert('RGB')
g=O+'gabon_karusel/'; os.makedirs(g,exist_ok=True); os.makedirs(g+'izgara_34',exist_ok=True)
kap=I.tile('render',P+'AFRİKA/13.jpg',1,'Gabon Villası','Gabon','cerceve')
sayfalar=[('8.jpg','Havuz'),('30.jpg','Yatak odası'),('33.jpg','Çalışma odası'),('20.jpg','Banyo')]
ims=[kap]+[I.sade_sayfa(SRL('AFRİKA/'+f),e,sayfa=i+2,toplam=len(sayfalar)+1) for i,(f,e) in enumerate(sayfalar)]
src=['13.jpg']+[f for f,_ in sayfalar]
for i,(im,s) in enumerate(zip(ims,src)):
    im.save(g+f'izgara_34/{i+1:02d}.jpg',quality=93)
    I.dort_bes(im,SRL('AFRİKA/'+s)).save(g+f'{i+1:02d}.jpg',quality=93)
open(g+'aciklama.txt','w').write('Gabon’da doğayla iç içe bir villa.\n\n#mimarlık #içmimarlık #architecture #interiordesign #villa #MotifoMimarlık')
from cropframe import crop_render; I.reel_kapak(crop_render(P+'OYSTER PIRLANTA/Yeni klasör/1 kopya.jpg'),2,'Oyster Pırlanta','Kayseri İldem').save(O+'oyster_reels_kapak.jpg',quality=93)
print('ok')
