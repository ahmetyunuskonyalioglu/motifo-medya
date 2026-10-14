# Deneme hesabı: seçilen ızgara düzeninin tamamını (sabit Florya üçlüsü + 12 karusel) gönderi paketleri olarak üretir.
import sys,os,json,shutil,glob
sys.path.insert(0,os.path.dirname(__file__))
from izgara import *
R_=os.path.join(os.path.dirname(__file__),'..'); P=os.path.join(R_,'kaynak','PROJELER')+'/'; O=os.path.join(R_,'paylasimlar','deneme_hesap')+'/'
def gecis(src):
    im=cover(load(src),W,H); s=sketch(im)
    paper=np.array(STONE,np.float32); ink=np.array(BRONZE,np.float32)*0.5+np.array(INK,np.float32)*0.5
    sk=paper*s[...,None]+ink*(1-s[...,None]); xx=np.mgrid[0:H,0:W][1]; t=np.clip((xx-W*0.30)/(W*0.40),0,1)[...,None]; t=t*t*(3-2*t)
    return Image.fromarray((sk*(1-t)+np.asarray(im).astype(np.float32)*t).astype(np.uint8))
def ic(srcs,etiketler,bas):
    n=len(srcs)+bas-1
    return [sade_sayfa(load(P+s),e,sayfa=bas+i,toplam=n) for i,(s,e) in enumerate(zip(srcs,etiketler))]
G=lambda proj,ad,yer,kapak,stil,ic_,et,cap:dict(tip='render',proj=proj,ad=ad,yer=yer,kapak=kapak,stil=stil,ic=ic_,et=et,cap=cap)
E=lambda proj,ad,yer,tur,kapak,koyu,ic_,et,cap:dict(tip='eskiz',proj=proj,ad=ad,yer=yer,tur=tur,kapak=kapak,koyu=koyu,ic=ic_,et=et,cap=cap)
# en yeni → en eski (ızgarada soldan sağa, yukarıdan aşağı)
PLAN=[
 G('AFRİKA','Gabon Villası','Gabon','9.jpg','cerceve',['10.jpg','5.jpg','7.jpg'],['Cephe','Bahçe','Havuz'],'Gabon’da doğayla iç içe bir villa.'),
 G('OYSTER PIRLANTA','Oyster Pırlanta','Kayseri İldem','13.jpg','yok',['12.jpg','4.jpg','6.jpg'],['Satış alanı','Bekleme','Vitrin duvarı'],'Oyster Pırlanta, Kayseri İldem.'),
 dict(tip='bim'),
 E('PİDECİ','Pide Paradise','Uçhisar, Kapadokya','Yeme-İçme','8.jpg',False,['7.jpg','1.jpg','6.jpg'],['Giriş','Sokak cephesi','Teras'],'Kapadokya taşının çağdaş yorumu: Pide Paradise, Uçhisar.'),
 G('ROCCA AND BEETLE','Rocca and Beetle','Ataşehir, İstanbul','8.jpg','alt_orta',['2.jpg','4.jpg','6.jpg'],['Bar','Sahne','Bar detayı'],'Rocca and Beetle, Ataşehir.'),
 G('AVANOS HAMAM','Hamam','İç mimari','19.jpg','cerceve',['17.jpg','4.jpg','12.jpg'],['Göbek taşı','Resepsiyon','Koridor'],'Taş, ışık ve buhar.'),
 E('AFRİKA','Gabon Villası','Gabon','Konut','12.jpg',True,['13.jpg','11.jpg','33.jpg'],['Ön cephe','Cephe','Çalışma odası'],'Gabon villası: çizimden gerçeğe.'),
 E('GLORİA JEANS','Gloria Jean\'s','Taksim, İstanbul','Yeme-İçme','2.jpg',False,['4.jpg','6.jpg','5.jpg'],['Bar','Oturma alanı','Salon'],'Gloria Jean’s, Taksim.'),
 G('YCR CONSTRACT, ANTALYA LARA','YCR Pesta Hotel','Antalya Lara','1.jpg','dergi',['2.jpg','3.jpg','4.jpg'],['Cephe','Giriş','Teras'],'YCR Pesta Hotel, Antalya Lara.'),
 G('SHOWROOM','Seçkin Mutfak','Mobilya showroomu','10.jpg','kenar',['2.jpg','4.jpg','11.jpg'],['Mutfak','Sergi','Toplantı'],'Seçkin Mutfak mobilya showroomu.'),
 E('AVANOS HAMAM','Hamam','İç mimari','Ticari','16.jpg',True,['14.jpg','20.jpg','22.jpg'],['Masaj odası','Kubbe altı','Ritüel alanı'],'Hamam: çizgiden mekâna.'),
 E('ADEN REZİDANS','Aden Rezidans','Konut','Cephe','3.jpg',False,['5.jpg','2.jpg','6.jpg'],['Cephe','Giriş','Zemin kat'],'Aden Rezidans.'),
]
ETK='\n\n#mimarlık #içmimarlık #architecture #interiordesign #MotifoMimarlık'
def uret():
    for f in glob.glob(O+'*'): shutil.rmtree(f) if os.path.isdir(f) else os.remove(f)
    sira=[]; N=len(PLAN)
    for k,p in enumerate(reversed(PLAN)):      # paylaşım sırası: en eski önce
        no=k+1; d=O+f'{no:02d}_'
        if p['tip']=='bim':
            d+='bim_superpoze/'; os.makedirs(d)
            for f in ['01_kapak.jpg','02_aciklamali.jpg','03_animasyon.mp4']: shutil.copy(os.path.join(R_,'paylasimlar','taslak_bim_karusel',f),d+f)
            open(d+'aciklama.txt','w').write('Motifo’da süperpoze üç boyutta yapılır.\n\n#BİM #Archicad #mimarlık #içmimarlık #MotifoMimarlık')
        else:
            slug=p['ad'].lower().replace(' ','_').replace("'",'')
            d+=slug+'/'; os.makedirs(d); src=P+p['proj']+'/'+p['kapak']
            if p['tip']=='render':
                kap=tile('render',src,no+12,p['ad'],p['yer'],p['stil']) if p['stil'] in ('cerceve','dergi') else sade(src,no+12,p['ad'],p['yer'],p['stil'])
                kap.save(d+'01_kapak.jpg',quality=93)
                for i,im in enumerate(ic([p['proj']+'/'+x for x in p['ic']],p['et'],2)): im.save(d+f'0{i+2}.jpg',quality=93)
            else:
                cizim(src,no+12,p['ad'],p['yer'],p['tur'],koyu=p['koyu']).save(d+'01_kapak.jpg',quality=93)
                gecis(src).save(d+'02_gecis.jpg',quality=93)
                for i,im in enumerate(ic([p['proj']+'/'+x for x in p['ic']],p['et'],3)): im.save(d+f'0{i+3}.jpg',quality=93)
            open(d+'aciklama.txt','w').write(p['cap']+ETK)
        sira.append(os.path.basename(d[:-1]))
    # sabit Florya üçlüsü: sağ, orta, sol sırayla paylaşılır, sonra aynı sırayla sabitlenir
    pan=panorama(P+'FLORYA MAVİKORU/1 gece.jpg',1,'Florya Mavikoru','İstanbul Florya',koyu=True)
    for i,(ad,im) in enumerate(zip(['sag','orta','sol'],[pan[2],pan[1],pan[0]])):
        d=O+f'{len(sira)+1:02d}_florya_{ad}/'; os.makedirs(d); im.save(d+'01.jpg',quality=94)
        open(d+'aciklama.txt','w').write('Florya Mavikoru, İstanbul Florya.'+ETK); sira.append(os.path.basename(d[:-1]))
    json.dump({'paylasim_sirasi':sira,'not':'Sıra en eskiden en yeniye. Son 3 Florya parçası paylaşıldıktan sonra sağ→orta→sol sırasıyla sabitlenir.'},open(O+'sira.json','w'),ensure_ascii=False,indent=1)
    print(sira)
if __name__=='__main__': uret()
