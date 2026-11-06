# Gloria Jean's (Taksim, İstanbul) — ritmik detay reels (havuz 2026-10-15_01): vuruşa oturan kesmeler,
# her kesmede kısa derinlikli hareket, ortada sabit daktilo satırı. Kaynaklar sr.py (Real-ESRGAN x4).
# Kapak: ızgara döngüsünde KOYU çizim (koyu zemin + altın eskiz), 9:16 içinde ortadaki 3:4.
import sys,os,json,subprocess
R='/home/claude/motifo-medya'; sys.path.insert(0,R+'/araclar')
import muzik, izgara as I, sr, ritmik_reel
from PIL import Image
P=R+'/kaynak/PROJELER/GLORİA JEANS/'; O=os.path.dirname(os.path.abspath(__file__))+'/'
BPM=118
K=[('3.jpg',(0.24,0.60,1.7),2,{'dolly':0.06}),        # tepsi, demlik
   ('4.jpg',(0.66,0.26,1.7),1,{'tx':0.03}),           # kahve rafı
   ('1.jpg',(0.30,0.38,1.7),1,{'dolly':0.05}),        # kabartma pano
   ('2.jpg',(0.62,0.42,1.25),2,{'dolly':0.07}),       # siyah kemer
   ('4.jpg',(0.12,0.40,1.7),0.5,{'dolly':0.05}),      # öğütücü
   ('4.jpg',(0.86,0.50,1.7),0.5,{'tx':-0.03}),        # espresso makinesi
   ('1.jpg',(0.90,0.32,1.7),1,{'ty':-0.03}),          # aplik
   ('5.jpg',(0.42,0.52,1.3),2,{'dolly':0.07}),        # kemerli pencereye koridor
   ('3.jpg',(0.48,0.34,1.8),1,{'tx':0.03}),           # dünya haritası duvarı
   ('6.jpg',(0.46,0.42,1.6),1,{'dolly':0.05}),        # ahşap kemerli bar
   ('5.jpg',(0.80,0.38,1.7),0.5,{'dolly':0.05}),      # çıta panel + aplik
   ('2.jpg',(0.14,0.30,1.7),0.5,{'ty':0.03}),         # aplik + bitki
   ('6.jpg',(0.88,0.42,1.7),1,{'tx':-0.03}),          # kabartma panolar
   ('1.jpg',(0.55,0.62,1.6),1,{'dolly':0.05}),        # oturma köşesi
   ('4.jpg',(0.45,0.60,1.8),2,{'dolly':0.06}),        # tezgâh, fincan
   ('2.jpg',(0.62,0.50,1.0),2,{'dolly':0.08})]        # final: kemerden içeri
def main():
    sp={'bpm':BPM,'sabit_yazi':'kahve, ışık, doku.','logo_end':R+'/marka/logo_kapanis_kareleri',
        'kesmeler':[{'file':P+f,'win':list(w),'vurus':v,'move':m} for f,w,v,m in K]}
    json.dump(sp,open(O+'spec.json','w'),indent=1,ensure_ascii=False)
    tmp='/home/claude/gloria_reel'; ritmik_reel.main(O+'spec.json',tmp); fr=tmp+'_fr'
    n=len(os.listdir(fr)); beat=60/BPM; icerik=sum(v for *_,v,_ in K)*beat
    dur=n/30+0.4; cuts=[]; t=0
    for *_,v,_ in K: cuts.append(t); t+=v*beat
    muzik.keman_ritmik(O+'muzik.wav',dur,cuts[1:],end_at=icerik,root=64,scale='minör',bpm=BPM,seed=71)
    muzik.kaydet(R+'/muzik_kayit.json','gloria_jeans_ritmik_reels','keman_ritmik',64,'minör',71)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',f'{fr}/f%05d.jpg','-i',O+'muzik.wav','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',O+'gloria_reels.mp4'],check=True)
    kapak()
    open(O+'aciklama.txt','w').write("Gloria Jean's, Taksim: kabartma panolar, ahşap kemerli bar ve sıcak aplik ışığı.\n\n#kafetasarımı #içmimari #Taksim #mimarlık #MotifoMimarlık")
    print('ok',n,n/30,'icerik',icerik)
def kapak():
    I.load=lambda p: Image.open(sr.buyut(p)).convert('RGB')
    t=I.cizim(P+'2.jpg',9,"Gloria Jean's",'Taksim, İstanbul','Yeme-İçme',fx=0.62,koyu=True)
    t.save(O+'izgara_34.jpg',quality=93)
    c=Image.new('RGB',(1080,1920),(30,28,26)); c.paste(t,(0,240)); c.save(O+'reels_kapak.jpg',quality=93)
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='kapak': kapak()
    else: main()
