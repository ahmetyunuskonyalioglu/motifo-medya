# Rocca and Beetle (restoran · bar) — yavaş, derinlikli iç mekân reels (parallax.py, Depth Anything V2).
# Kaynaklar 1080 px şablonlu → cropframe + sr.py (Real-ESRGAN x4). Konum bilinmiyor → yazılmaz.
# Izgara döngüsü: render (1/4) — reels kapağı reel_kapak (çerçeve + künye).
import sys,os,shutil,subprocess
R='/home/claude/motifo-medya'; sys.path.insert(0,R+'/araclar')
import muzik, izgara as I, sr
from parallax import shot_frames, ease
from reel import shade, overlay
from PIL import Image
P=R+'/kaynak/PROJELER/ROCCA AND BEETLE/'; O=os.path.dirname(os.path.abspath(__file__))+'/'
FPS=30; XF=int(0.5*FPS)
SRC=lambda f: Image.open(sr.buyut(P+f)).convert('RGB')
# (kaynak, süre, pencere (cx,cy,zoom), hareket, kicker, başlık)
SH=[('3.jpg',4.2,(0.50,0.50,1.0),{'dolly':0.09},'RESTORAN  ·  BAR','Rocca and Beetle'),
    ('1.jpg',4.0,(0.45,0.50,1.0),{'tx':0.03,'dolly':0.04},'',''),
    ('6.jpg',3.8,(0.55,0.55,1.0),{'dolly':0.08},'',''),
    ('4.jpg',4.0,(0.55,0.50,1.0),{'tx':-0.03,'dolly':0.04},'',''),
    ('5.jpg',4.0,(0.50,0.50,1.0),{'dolly':0.08},'',''),
    ('8.jpg',4.2,(0.62,0.48,1.0),{'ty':-0.02,'dolly':0.06},'','')]
def main():
    tmp='/home/claude/rocca_fr'; shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp)
    n=0; tail=[]; cuts=[]
    for si,(a,dur,win,mv,kic,bas) in enumerate(SH):
        N=int(dur*FPS); A=shot_frames(SRC(a),win,N,mv)
        last=si==len(SH)-1; prev=tail; tail=[]; cuts.append(n/FPS)
        for i in range(N):
            f=overlay(shade(next(A)),kic,bas,i/FPS,dur,'bottom')
            if i<len(prev): f=Image.blend(prev[i],f,ease((i+1)/(len(prev)+1)))
            if not last and i>=N-XF: tail.append(f); continue
            f.save(f'{tmp}/f{n:05d}.jpg',quality=93); n+=1
    end_at=n/FPS; lastf=Image.open(f'{tmp}/f{n-1:05d}.jpg'); LD=R+'/marka/logo_kapanis_kareleri'
    for k,name in enumerate(sorted(os.listdir(LD))[3:]):
        f=Image.open(os.path.join(LD,name)).convert('RGB')
        if k<24: f=Image.blend(lastf,f,ease((k+1)/24))
        f.save(f'{tmp}/f{n:05d}.jpg',quality=93); n+=1
    dur=n/FPS+0.4
    muzik.keman(O+'muzik.wav',dur,cuts[1:],end_at=end_at,root=61,scale='dorian',bpm=68,seed=83)
    muzik.kaydet(R+'/muzik_kayit.json','rocca_beetle_reels','keman',61,'dorian',83)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',f'{tmp}/f%05d.jpg','-i',O+'muzik.wav','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',O+'rocca_reels.mp4'],check=True)
    kapak()
    open(O+'aciklama.txt','w').write('Rocca and Beetle: ışıklı raflarla yükselen bar, kemerli nişler ve sahneye bakan uzun masalar.\n\n#restorantasarımı #bartasarımı #içmimari #mimarlık #MotifoMimarlık')
    print('ok',n,n/FPS,'icerik',end_at)
def kapak():
    k=I.reel_kapak(SRC('7.jpg'),21,'Rocca and Beetle','Restoran · Bar',fx=0.42); k.save(O+'reels_kapak.jpg',quality=93)
    k.crop((0,240,1080,1680)).save(O+'izgara_34.jpg',quality=93)
if __name__=='__main__':
    if 'kapak' in sys.argv: kapak()
    else: main()
