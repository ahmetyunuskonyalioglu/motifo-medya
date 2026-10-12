# Editoryal karusel (1080x1350). python karusel.py spec.json outdir
import sys,os,json,subprocess
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cropframe import crop_render
from PIL import Image,ImageDraw,ImageFont,ImageOps
W,H=1080,1350
fp=lambda q: subprocess.check_output(['fc-match','-f','%{file}',q]).decode()
LIGHT=fp('Inter:style=Light'); MED=fp('Inter:style=Medium'); SERIF_I=fp('Latin Modern Roman:style=Italic'); SERIF=fp('Latin Modern Roman:style=Regular')
CREAM=(245,241,234); INK=(34,31,28); BRONZE=(146,108,74); MUTE=(120,112,104)
S='/tmp/claude-0/-home-claude/8c2bb08b-0d28-593e-b9c3-4c3ec033f7cb/scratchpad/'
def track(d,xy,text,font,fill,sp,anchor='l'):
    w=sum(d.textlength(c,font=font) for c in text)+sp*(len(text)-1)
    x,y=xy; x = x-w if anchor=='r' else (x-w/2 if anchor=='m' else x)
    for c in text: d.text((x,y),c,font=font,fill=fill); x+=d.textlength(c,font=font)+sp
def wrap(d,text,font,maxw):
    words=text.split(); lines=[]; cur=''
    for w in words:
        t=(cur+' '+w).strip()
        if d.textlength(t,font=font)<=maxw: cur=t
        else: lines.append(cur); cur=w
    lines.append(cur); return lines
def slide(sp,i,n,s):
    img=Image.new('RGB',(W,H),CREAM); d=ImageDraw.Draw(img)
    fk=ImageFont.truetype(MED,20)
    track(d,(64,62),'MOTİFO',fk,INK,6)
    track(d,(W-64,62),sp['proje'].upper(),fk,MUTE,5,'r')
    src=crop_render(s['file']) if sp.get('crop',True) else Image.open(s['file']).convert('RGB')
    ih=s.get('h',640) if i else 760
    ph=ImageOps.fit(src,(W,ih),Image.LANCZOS,centering=tuple(s.get('center',(0.5,0.5))))
    y_img=130 if i else 330
    img.paste(ph,(0,y_img))
    if i==0:
        d.text((64,190),sp['baslik'],font=ImageFont.truetype(SERIF_I,82),fill=INK,anchor='ls')
        d.text((64,262),sp['alt'],font=ImageFont.truetype(LIGHT,30),fill=MUTE,anchor='ls')
        y=y_img+ih+80
        track(d,(64,y),sp['kunye'],ImageFont.truetype(MED,21),BRONZE,5)
        d.line([(64,y+50),(W-64,y+50)],fill=(214,206,195),width=2)
        d.text((W-64,H-64),'kaydır  →',font=ImageFont.truetype(LIGHT,26),fill=MUTE,anchor='rs')
    else:
        y=y_img+ih+64
        track(d,(64,y),f"{i:02d}",ImageFont.truetype(MED,22),BRONZE,4)
        d.text((64,y+92),s['label'],font=ImageFont.truetype(SERIF_I,62),fill=INK,anchor='ls')
        fb=ImageFont.truetype(LIGHT,30)
        for k,l in enumerate(wrap(d,s['text'],fb,W-128)): d.text((64,y+150+k*44),l,font=fb,fill=(70,64,58),anchor='ls')
        d.text((W-64,H-60),f"{i+1} / {n}",font=ImageFont.truetype(LIGHT,22),fill=MUTE,anchor='rs')
        if i==n-1:
            em=Image.open(S+'brand/amblem_siyah.png'); em.thumbnail((70,70),Image.LANCZOS); img.paste(em,(64,H-64-em.height+8),em)
    return img
if __name__=='__main__':
    sp=json.load(open(sys.argv[1])); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
    n=len(sp['slides'])
    for i,s in enumerate(sp['slides']): slide(sp,i,n,s).save(f'{out}/{i+1:02d}.jpg',quality=94)
    print('ok',n)
