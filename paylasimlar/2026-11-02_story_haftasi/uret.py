# Hafta 2–6 Kasım story'leri: (1) Rocca and Beetle bar derinlikli video, (2) Avanos reels duyurusu, (3) ofis karuseli duyurusu.
# (4) 8 Kasım Dünya Şehircilik Günü → sehircilik.py. Kaynaklar küçük → sr.py ile büyütülmüş.
import sys,os,shutil,subprocess
R='/home/claude/motifo-medya'; sys.path.insert(0,R+'/araclar')
import izgara as I, muzik, sr
from parallax import shot_frames, ease
from PIL import Image,ImageDraw,ImageFont
O=os.path.dirname(os.path.abspath(__file__))+'/'; P=R+'/kaynak/PROJELER/'
SW,SH=1080,1920; CREAM_BG=(244,240,234)
SRC=lambda p: Image.open(sr.buyut(P+p)).convert('RGB')
def kunye(fr,a,ust,alt):
    fr=fr.convert('RGBA'); g=Image.new('L',(1,256)); [g.putpixel((0,i),int(150*max(0,(i-170)/86)**1.6)) for i in range(256)]
    sh=Image.new('RGBA',fr.size,(14,12,10,0)); sh.putalpha(g.resize(fr.size).point(lambda v:int(v*a))); fr.alpha_composite(sh)
    d=ImageDraw.Draw(fr,'RGBA')
    d.text((SW//2,SH-250),ust,font=ImageFont.truetype(I.SERIF_I,84),fill=(255,255,255,int(250*a)),anchor='ms')
    I.track(d,(SW//2,SH-200),I.up(alt),ImageFont.truetype(I.INTER_M,24),(255,255,255,int(200*a)),7,'m')
    return fr.convert('RGB')
def bar_video():
    tmp='/home/claude/st_bar'; shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp)
    N=int(7.0*30); A=shot_frames(SRC('ROCCA AND BEETLE/2.jpg'),(0.5,0.5,1.0),N,{'dolly':0.08,'tx':0.015})
    for i in range(N):
        f=kunye(next(A),ease((i/30-0.5)/0.8),'Rocca and Beetle','restoran  ·  bar')
        f.save(f'{tmp}/f{i:05d}.jpg',quality=93)
    muzik.keman(O+'bar.wav',N/30+0.3,[2.3,4.6],end_at=N/30,root=60,scale='majör',bpm=74,seed=59)
    muzik.kaydet(R+'/muzik_kayit.json','story_rocca_bar','keman',60,'majör',59)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',f'{tmp}/f%05d.jpg','-i',O+'bar.wav','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',O+'1_pzt_rocca_bar.mp4'],check=True)
def duyuru(src,etiket,baslik,satir,out,fx=0.5):
    im=Image.new('RGB',(SW,SH),CREAM_BG); d=ImageDraw.Draw(im)
    I.track(d,(SW//2,195),etiket,ImageFont.truetype(I.INTER_M,26),I.BRONZE,9,'m')
    d.text((SW//2,290),baslik,font=ImageFont.truetype(I.SERIF_I,92),fill=I.INK,anchor='ms')
    ph=I.cover(src,952,1100,fx,0.5); im.paste(ph,(64,330))
    d.text((SW//2,1530),satir,font=ImageFont.truetype(I.INTER_L,34),fill=I.MUTE,anchor='ms')
    lg=Image.open(R+'/marka/logo_siyah.png'); lg.thumbnail((230,230),Image.LANCZOS); im.paste(lg,((SW-lg.width)//2,1640),lg)
    im.save(O+out,quality=93)
if __name__=='__main__':
    bar_video()
    duyuru(SRC('AVANOS HAMAM/20.jpg'),'YENİ REELS','Avanos Hamam','Taş, kemer ve ışık.','2_car_avanos_reels_duyuru.jpg',fx=0.5)
    duyuru(SRC('SHOWROOM/9.jpg'),'YENİ GÖNDERİ','Bir ofis','Kemer nişlerinden ortak masaya, beş karede.','3_cum_ofis_duyuru.jpg',fx=0.72)
    print('ok')
