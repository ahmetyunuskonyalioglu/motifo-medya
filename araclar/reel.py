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
MONO=fp('Latin Modern Mono Light:style=Regular')
def sabit(fr,metin,t,sp):
    # tüm video boyunca ortada sabit, küçük daktilo satırı (havuz örneği 2026-10-15_01)
    toplam=sp.get('_toplam',999); a=ease((t-0.4)/0.8)*ease((toplam-t)/0.6)
    if a<=0: return fr
    from PIL import ImageFilter
    f=ImageFont.truetype(MONO,36); d0=ImageDraw.Draw(fr)
    w=sum(d0.textlength(c,font=f) for c in metin)+3*(len(metin)-1); x0=W/2-w/2; y=sp.get('yazi_y',H*0.47)
    sh=Image.new('RGBA',fr.size,(0,0,0,0)); ds=ImageDraw.Draw(sh); x=x0
    for c in metin: ds.text((x,y),c,font=f,fill=(10,8,6,int(170*a))); x+=d0.textlength(c,font=f)+3
    sh=sh.filter(ImageFilter.GaussianBlur(6)); fr=fr.convert('RGBA'); fr.alpha_composite(sh); d=ImageDraw.Draw(fr); x=x0
    for c in metin: d.text((x,y),c,font=f,fill=(248,242,232,int(235*a))); x+=d0.textlength(c,font=f)+3
    return fr.convert('RGB')
def load(path,crop):
    im=crop_render(path) if crop else Image.open(path).convert('RGB')
    if im.width>3200: im=im.resize((3200,int(im.height*3200/im.width)),Image.LANCZOS)
    return im
def main(spec_path,out):
    sp=json.load(open(spec_path)); tmp=out+'_fr'; shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp)
    n=0; XF=int(sp.get('xfade',0.5)*FPS); prev_tail=[]
    sp['_toplam']=sum(sh['dur'] for sh in sp['shots'])-sp.get('xfade',0.5)*(len(sp['shots'])-1)
    if sp.get('golge_yok'): globals()['G'][:]=0
    for si,sh in enumerate(sp['shots']):
        if sp.get('sr'):
            import sr as _sr; im=load(_sr.buyut(sh['file']),False)
        else: im=load(sh['file'],sp.get('crop',True))
        N=int(sh['dur']*FPS)
        frames=list(shot_frames(im,tuple(sh['win']),N,sh['move']))
        for i,f in enumerate(frames):
            f=overlay(shade(f),sh.get('kicker',''),sh.get('title',''),i/FPS,sh['dur'],sh.get('pos','top'))
            frames[i]=f
        # crossfade with previous tail
        for i in range(len(prev_tail)):
            frames[i]=Image.blend(prev_tail[i],frames[i],ease((i+1)/(len(prev_tail)+1)))
        keep=frames if si==len(sp['shots'])-1 else frames[:-XF]
        prev_tail=[] if si==len(sp['shots'])-1 else frames[-XF:]
        for f in keep:
            if sp.get('sabit_yazi'): f=sabit(f,sp['sabit_yazi'],n/FPS,sp)
            f.save(f'{tmp}/f{n:05d}.jpg',quality=93); n+=1
    # ending: logo animation frames
    if sp.get('logo_end'):
        lf=sorted(os.listdir(sp['logo_end']))[int(sp.get('logo_skip',0)*FPS):]
        last=Image.open(f'{tmp}/f{n-1:05d}.jpg')
        for k,name in enumerate(lf):
            f=Image.open(os.path.join(sp['logo_end'],name)).convert('RGB')
            if k<24: f=Image.blend(last,f,ease((k+1)/24))
            f.save(f'{tmp}/f{n:05d}.jpg',quality=93); n+=1
    print('frames',n,'sec',n/FPS)
    json.dump({'frames':n},open(out+'.meta.json','w'))
if __name__=='__main__': main(sys.argv[1],sys.argv[2])
