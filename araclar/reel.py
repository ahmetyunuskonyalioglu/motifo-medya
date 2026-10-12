# Genel reels üretici: python reel.py spec.json out.mp4
import sys,os,json,subprocess,shutil
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from parallax import shot_frames, ease
from cropframe import crop_render
from PIL import Image,ImageDraw,ImageFont
import numpy as np
W,H,FPS=1080,1920,30
fp=lambda q: subprocess.check_output(['fc-match','-f','%{file}',q]).decode()
MED=fp('Inter:style=Medium'); SERIF_I=fp('Latin Modern Roman:style=Italic')
G=np.zeros((H,W),np.float32); G[:700]=np.linspace(0.5,0,700)[:,None]; G[H-700:]=np.linspace(0,0.5,700)[:,None]
def shade(fr):
    a=np.asarray(fr).astype(np.float32)*(1-G[...,None]); return Image.fromarray(a.clip(0,255).astype(np.uint8))
def overlay(fr,kicker,title,t,dur,pos='top'):
    if not (kicker or title): return fr
    d=ImageDraw.Draw(fr,'RGBA')
    a=ease((t-0.3)/0.7)*ease((dur-0.35-t)/0.5)
    if a<=0: return fr
    off=(1-ease((t-0.3)/0.9))*18
    y0=262 if pos=='top' else 1560
    fk=ImageFont.truetype(MED,25); ft=ImageFont.truetype(SERIF_I,68)
    tot=sum(d.textlength(c,font=fk) for c in kicker)+7*(len(kicker)-1); x=W/2-tot/2
    for c in kicker: d.text((x,y0+off),c,font=fk,fill=(255,255,255,int(225*a))); x+=d.textlength(c,font=fk)+7
    d.text((W/2,y0+110+off),title,font=ft,fill=(255,255,255,int(255*a)),anchor='ms')
    return fr
def load(path,crop):
    im=crop_render(path) if crop else Image.open(path).convert('RGB')
    if im.width>3200: im=im.resize((3200,int(im.height*3200/im.width)),Image.LANCZOS)
    return im
def main(spec_path,out):
    sp=json.load(open(spec_path)); tmp=out+'_fr'; shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp)
    n=0; XF=int(sp.get('xfade',0.5)*FPS); prev_tail=[]
    for si,sh in enumerate(sp['shots']):
        im=load(sh['file'],sp.get('crop',True)); N=int(sh['dur']*FPS)
        frames=list(shot_frames(im,tuple(sh['win']),N,sh['move']))
        for i,f in enumerate(frames):
            f=overlay(shade(f),sh.get('kicker',''),sh.get('title',''),i/FPS,sh['dur'],sh.get('pos','top'))
            frames[i]=f
        # crossfade with previous tail
        for i in range(len(prev_tail)):
            frames[i]=Image.blend(prev_tail[i],frames[i],ease((i+1)/(len(prev_tail)+1)))
        keep=frames if si==len(sp['shots'])-1 else frames[:-XF]
        prev_tail=[] if si==len(sp['shots'])-1 else frames[-XF:]
        for f in keep: f.save(f'{tmp}/f{n:05d}.jpg',quality=93); n+=1
    # ending: logo animation frames
    if sp.get('logo_end'):
        lf=sorted(os.listdir(sp['logo_end']))[int(sp.get('logo_skip',0)*FPS):]
        last=Image.open(f'{tmp}/f{n-1:05d}.jpg')
        for k,name in enumerate(lf):
            f=Image.open(os.path.join(sp['logo_end'],name)).convert('RGB')
            if k<12: f=Image.blend(last,f,ease((k+1)/12))
            f.save(f'{tmp}/f{n:05d}.jpg',quality=93); n+=1
    print('frames',n,'sec',n/FPS)
    json.dump({'frames':n},open(out+'.meta.json','w'))
if __name__=='__main__': main(sys.argv[1],sys.argv[2])
