# Hafta 19–23 Ekim story'leri: (1) Florya gündüz→gece derinlikli geçiş videosu, (2) reels duyurusu, (3) karusel duyurusu
import sys,os,shutil,subprocess
R='/home/claude/motifo-medya'; sys.path.insert(0,R+'/araclar')
import izgara as I, muzik
from parallax import shot_frames, ease
from cropframe import crop_render
from PIL import Image,ImageDraw,ImageFont
O=os.path.dirname(os.path.abspath(__file__))+'/'; P=R+'/kaynak/PROJELER/'
SW,SH=1080,1920; CREAM_BG=(244,240,234)
def kunye(fr,a,ust,alt):
    fr=fr.convert('RGBA'); g=Image.new('L',(1,256)); [g.putpixel((0,i),int(150*max(0,(i-170)/86)**1.6)) for i in range(256)]
    sh=Image.new('RGBA',fr.size,(14,12,10,0)); sh.putalpha(g.resize(fr.size).point(lambda v:int(v*a))); fr.alpha_composite(sh)
    d=ImageDraw.Draw(fr,'RGBA')
    d.text((SW//2,SH-250),ust,font=ImageFont.truetype(I.SERIF_I,84),fill=(255,255,255,int(250*a)),anchor='ms')
    I.track(d,(SW//2,SH-200),I.up(alt),ImageFont.truetype(I.INTER_M,24),(255,255,255,int(200*a)),7,'m')
    return fr.convert('RGB')
def gunduz_gece():
    tmp='/home/claude/st_gg'; shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp)
    a=crop_render(P+'FLORYA MAVİKORU/5 GÜNEŞLİ.jpg'); b=crop_render(P+'FLORYA MAVİKORU/5 GECE.jpg')
    N=int(7.5*30); win=(0.27,0.5,1.0); mv={'dolly':0.07,'tx':0.02}
    A=list(shot_frames(a,win,N,mv)); B=list(shot_frames(b,win,N,mv))
    for i in range(N):
        k=ease((i/30-2.4)/2.6)               # 2,4 sn gündüz → 2,6 sn geçiş → gece
        f=Image.blend(A[i],B[i],k)
        f=kunye(f,ease((i/30-0.5)/0.8),'Florya Mavikoru','gündüz  ·  gece')
        f.save(f'{tmp}/f{i:05d}.jpg',quality=93)
    muzik.keman(O+'gunduz_gece.wav',N/30+0.3,[2.4,5.0],end_at=N/30,root=64,scale='majör',bpm=76,seed=11)
    muzik.kaydet(R+'/muzik_kayit.json','story_florya_gunduz_gece','keman',64,'majör',11)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',f'{tmp}/f%05d.jpg','-i',O+'gunduz_gece.wav','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',O+'1_pzt_florya_gunduz_gece.mp4'],check=True)
def duyuru(src,etiket,baslik,satir,out,fx=0.5):
    im=Image.new('RGB',(SW,SH),CREAM_BG); d=ImageDraw.Draw(im)
    I.track(d,(SW//2,195),etiket,ImageFont.truetype(I.INTER_M,26),I.BRONZE,9,'m')
    d.text((SW//2,290),baslik,font=ImageFont.truetype(I.SERIF_I,92),fill=I.INK,anchor='ms')
    ph=I.cover(src,952,1100,fx,0.5); im.paste(ph,(64,330))
    d.text((SW//2,1530),satir,font=ImageFont.truetype(I.INTER_L,34),fill=I.MUTE,anchor='ms')
    lg=Image.open(R+'/marka/logo_siyah.png'); lg.thumbnail((230,230),Image.LANCZOS); im.paste(lg,((SW-lg.width)//2,1640),lg)
    im.save(O+out,quality=93)
if __name__=='__main__':
    gunduz_gece()
    duyuru(crop_render(P+'FLORYA MAVİKORU/7.jpg'),'YENİ REELS','Florya Mavikoru','İçeriden, ayrıntı ayrıntı.','2_car_florya_reels_duyuru.jpg',fx=0.62)
    duyuru(crop_render(P+'REPORTAGE AFRA PARK PROJECT/11.jpg'),'YENİ GÖNDERİ','Bahçeşehir’de bir konut','Salondan mutfağa, altı karede.','3_cum_afra_park_duyuru.jpg',fx=0.68)
    print('ok')
