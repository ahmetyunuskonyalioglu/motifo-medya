# Aden Rezidans — gündüzden geceye derinlikli reels (yeni format: aynı kadrajda gece/gündüz geçişi).
# Kaynaklar 3600 px şablonlu → cropframe ile kırpılır, SR gerekmez (CLAUDE.md). Konum bilinmiyor → yazılmaz.
import sys,os,shutil,subprocess
R='/home/claude/motifo-medya'; sys.path.insert(0,R+'/araclar')
import muzik, izgara as I
from parallax import shot_frames, ease
from cropframe import crop_render
from reel import shade, overlay
from PIL import Image
P=R+'/kaynak/PROJELER/ADEN REZİDANS 2/'; O=os.path.dirname(os.path.abspath(__file__))+'/'
FPS=30; XF=int(0.5*FPS)
# (gündüz, gece|None, süre, pencere, hareket, geçiş başlangıç/uzunluk sn, kicker, başlık)
SH=[('9.jpg',None,3.8,(0.30,0.5,1.0),{'dolly':0.09,'tx':0.02},None,'KONUT  ·  CEPHE','Aden Rezidans'),
    ('14.jpg',None,4.0,(0.50,0.5,1.0),{'ty':-0.03,'dolly':0.04},None,'',''),
    ('15.jpg','16.jpg',6.6,(0.50,0.45,1.0),{'dolly':0.07},(2.0,2.6),'',''),
    ('13.jpg',None,4.0,(0.50,0.55,1.0),{'ty':0.03,'dolly':0.04},None,'',''),
    ('12.jpg',None,4.2,(0.50,0.5,1.0),{'dolly':0.08},None,'','')]
def main():
    tmp='/home/claude/aden_fr'; shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp)
    n=0; tail=[]; cuts=[]
    for si,(a,b,dur,win,mv,gec,kic,bas) in enumerate(SH):
        N=int(dur*FPS); A=shot_frames(crop_render(P+a),win,N,mv)
        B=shot_frames(crop_render(P+b),win,N,mv) if b else None
        last=si==len(SH)-1; prev=tail; tail=[]; cuts.append(n/FPS)
        for i in range(N):
            f=next(A)
            if B is not None: f=Image.blend(f,next(B),ease((i/FPS-gec[0])/gec[1]))
            f=overlay(shade(f),kic,bas,i/FPS,dur,'bottom')
            if i<len(prev): f=Image.blend(prev[i],f,ease((i+1)/(len(prev)+1)))
            if not last and i>=N-XF: tail.append(f); continue
            f.save(f'{tmp}/f{n:05d}.jpg',quality=93); n+=1
    end_at=n/FPS; lastf=Image.open(f'{tmp}/f{n-1:05d}.jpg'); LD=R+'/marka/logo_kapanis_kareleri'
    for k,name in enumerate(sorted(os.listdir(LD))[3:]):
        f=Image.open(os.path.join(LD,name)).convert('RGB')
        if k<24: f=Image.blend(lastf,f,ease((k+1)/24))
        f.save(f'{tmp}/f{n:05d}.jpg',quality=93); n+=1
    dur=n/FPS+0.4
    muzik.keman(O+'muzik.wav',dur,cuts[1:],end_at=end_at,root=67,scale='majör',bpm=72,seed=23)
    muzik.kaydet(R+'/muzik_kayit.json','aden_reels_gunduz_gece','keman',67,'majör',23)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',f'{tmp}/f%05d.jpg','-i',O+'muzik.wav','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',O+'aden_reels.mp4'],check=True)
    I.reel_kapak(crop_render(P+'15.jpg'),5,'Aden Rezidans','Konut · Cephe',fx=0.5).save(O+'reels_kapak.jpg',quality=93)
    open(O+'aciklama.txt','w').write('Aynı cephe, gündüzden geceye: taş, kemer ve ışık.\n\n#cephetasarımı #konutprojesi #mimarlık #architecture #MotifoMimarlık')
    print('ok',n,n/FPS,'icerik',end_at)
main()
