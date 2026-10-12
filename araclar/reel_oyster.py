import sys,os,math,subprocess
sys.path.insert(0,os.path.dirname(__file__))
from cropframe import crop_render
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np
S='/tmp/claude-0/-home-claude/8c2bb08b-0d28-593e-b9c3-4c3ec033f7cb/scratchpad/'
D='/mnt/user-data/uploads/MOTİFO/PROJELER/OYSTER PIRLANTA/Yeni klasör/'
W,H,FPS=1080,1920,30
fp=lambda q: subprocess.check_output(['fc-match','-f','%{file}',q]).decode()
LIGHT=fp('Inter:style=Light'); MED=fp('Inter:style=Medium'); SERIF_I=fp('Latin Modern Roman:style=Italic'); SERIF=fp('Latin Modern Roman:style=Regular')
# shots: (file, duration s, cam: (x0,y0,z0)->(x1,y1,z1) normalized center + zoom, kicker, title)
shots=[
 ('2 kopya 7.jpg',2.4,(0.30,0.55,1.00),(0.62,0.55,1.18),'KAYSERİ · İLDEM','Bir pırlanta mağazası'),
 ('1 kopya.jpg',2.3,(0.20,0.50,1.05),(0.55,0.48,1.05),'01 · MARKA','Oyster: istiridye'),
 ('2 kopya 2.jpg',2.3,(0.35,0.50,1.00),(0.40,0.45,1.35),'02 · DUVAR','İnci dokusu'),
 ('2 kopya 4.jpg',2.3,(0.70,0.50,1.05),(0.35,0.50,1.05),'03 · KEMERLER','Kabuğun kavisi'),
 ('2 kopya.jpg',2.3,(0.55,0.42,1.25),(0.45,0.55,1.00),'04 · TAVAN','Bakır bir heykel'),
 ('2 kopya 5.jpg',2.3,(0.25,0.50,1.05),(0.60,0.50,1.10),'05 · RENK','Bakır ve sedef'),
 ('2 kopya 8.jpg',2.2,(0.50,0.50,1.30),(0.50,0.52,1.00),'',''),
]
END=2.6; XF=0.25
def ease(t): return t*t*(3-2*t)
imgs={}
def get(f):
    if f not in imgs:
        im=crop_render(D+f); im=im.resize((im.width*2//3,im.height*2//3),Image.LANCZOS); imgs[f]=im
    return imgs[f]
def cam(im,cx,cy,z):
    ih=im.height; ch=ih/z; cw=ch*W/H
    x=cx*im.width-cw/2; y=cy*ih-ch/2
    x=min(max(0,x),im.width-cw); y=min(max(0,y),ih-ch)
    return im.transform((W,H),Image.EXTENT,(x,y,x+cw,y+ch),Image.BICUBIC)
def grad(fr):
    a=np.zeros((H,W),np.float32); a[:620]=np.linspace(0.55,0,620)[:,None]; a[H-520:]=np.linspace(0,0.5,520)[:,None]
    return a
G=grad(None)
def shade(fr):
    arr=np.asarray(fr).astype(np.float32); arr*= (1-G[...,None]*0.9); return Image.fromarray(arr.clip(0,255).astype(np.uint8))
def text(fr,kicker,title,t,dur,big=False):
    d=ImageDraw.Draw(fr,'RGBA')
    a=min(1,max(0,(t-0.15)/0.35))*min(1,max(0,(dur-t)/0.25))
    if a<=0: return
    off=(1-ease(min(1,(t-0.15)/0.45)))*24
    fk=ImageFont.truetype(MED,26); ft=ImageFont.truetype(SERIF_I,74 if big else 66)
    # tracking kicker
    x=W/2; total=sum(d.textlength(c,font=fk) for c in kicker)+6*(len(kicker)-1); cx=x-total/2
    for c in kicker: d.text((cx,250+off),c,font=fk,fill=(255,255,255,int(230*a))); cx+=d.textlength(c,font=fk)+6
    d.text((W/2,360+off),title,font=ft,fill=(255,255,255,int(255*a)),anchor='ms')
def endcard(t):
    bg=Image.new('RGB',(W,H),(246,242,236)); d=ImageDraw.Draw(bg,'RGBA')
    a=min(1,t/0.5)
    logo=Image.open(S+'brand/logo_siyah.png'); logo.thumbnail((560,560),Image.LANCZOS)
    la=logo.split()[3].point(lambda v:int(v*a)); logo.putalpha(la)
    bg.paste(logo,(int(W/2-logo.width/2),int(620-(1-a)*20)),logo)
    b=min(1,max(0,(t-0.5)/0.5))
    d.text((W/2,1320),'Mağaza · Konut · Villa · Ticari',font=ImageFont.truetype(LIGHT,32),fill=(40,35,30,int(255*b)),anchor='ms')
    d.text((W/2,1400),'Projeniz için DM',font=ImageFont.truetype(MED,34),fill=(150,95,60,int(255*b)),anchor='ms')
    return bg
def main(outdir):
    os.makedirs(outdir,exist_ok=True); n=0
    frames_per=[int(s[1]*FPS) for s in shots]
    for si,(f,dur,c0,c1,k,ti) in enumerate(shots):
        im=get(f); N=frames_per[si]
        nxt=shots[si+1] if si+1<len(shots) else None
        for i in range(N):
            t=i/FPS; p=ease(i/(N-1))
            cx,cy,z=[a+(b-a)*p for a,b in zip(c0,c1)]
            fr=shade(cam(im,cx,cy,z))
            text(fr,k,ti,t,dur,big=(si==0))
            # crossfade into next at end
            xf=int(XF*FPS)
            if i>=N-xf:
                q=(i-(N-xf))/xf
                if nxt:
                    im2=get(nxt[0]); fr2=shade(cam(im2,*nxt[2])); fr=Image.blend(fr,fr2,ease(q))
                else:
                    fr=Image.blend(fr,endcard(0),ease(q))
            fr.save(f'{outdir}/f{n:04d}.jpg',quality=93); n+=1
    for i in range(int(END*FPS)):
        endcard(i/FPS).save(f'{outdir}/f{n:04d}.jpg',quality=93); n+=1
    print('frames',n,'dur',n/FPS)
    # cut times for audio
    ts=[0];acc=0
    for s in shots: acc+=s[1]; ts.append(acc)
    print('cuts',ts)
if __name__=='__main__': main(sys.argv[1])
