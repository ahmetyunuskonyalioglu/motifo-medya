# Afra Park (İstanbul Bahçeşehir) tasarım karuseli — ızgara döngüsü: render (2/4), kapak 'dergi'.
# Kaynaklar 3600 px şablonlu → cropframe ile kırpılır, SR gerekmez (CLAUDE.md).
import sys,os
R='/home/claude/motifo-medya'; sys.path.insert(0,R+'/araclar')
import izgara as I
from cropframe import crop_render
P=R+'/kaynak/PROJELER/REPORTAGE AFRA PARK PROJECT/'; O=os.path.dirname(os.path.abspath(__file__))+'/'
C={}
def L(f):
    if f not in C: C[f]=crop_render(P+f)
    return C[f]
I.load=lambda p: L(os.path.basename(p))
from PIL import Image
def sayfa(f,et,fx,no,top,ust=0.0):
    src=L(f); src=src.crop((0,int(src.height*ust),src.width,int(src.height*(0.95 if ust else 1)))); w=int(src.height*3/4); x=int(min(max(0,fx*src.width-w/2),src.width-w))
    return I.sade_sayfa(src.crop((x,0,x+w,src.height)),et,sayfa=no,toplam=top)
KAP=('13.jpg',0.56)
SAY=[('2.jpg','Yatak odası',0.52,0),('7.jpg','Salon',0.47,0.14),('6.jpg','Banyo',0.56,0),('14.jpg','Giriş',0.55,0),('15.jpg','Mutfak',0.45,0)]
top=len(SAY)+1
kap=I.tile('render',P+KAP[0],4,'Afra Park','İstanbul Bahçeşehir','dergi',fx=KAP[1])
ims=[(kap,KAP[0])]+[(sayfa(f,e,fx,i+2,top,u),f) for i,(f,e,fx,u) in enumerate(SAY)]
for i,(im,f) in enumerate(ims):
    im.save(O+f'izgara_34/{i+1:02d}.jpg',quality=93)
    I.dort_bes(im,L(f)).save(O+f'{i+1:02d}.jpg',quality=93)
open(O+'aciklama.txt','w').write('Bahçeşehir’de, sakin tonlarla kurgulanmış bir konut iç mekânı.\n\n#BahçeşehirİçMimar #içmimarlık #interiordesign #konuttasarımı #MotifoMimarlık')
print('ok',[f for _,f in ims])
