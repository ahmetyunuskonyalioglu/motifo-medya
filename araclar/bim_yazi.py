# BİM inşaat animasyonu üzerine aşama yazıları + ilerleme çubuğu + çakışma uyarısı
import sys,os,json,subprocess
from PIL import Image,ImageDraw,ImageFont
W,H,FPS=1080,1920,30
fp=lambda q: subprocess.check_output(['fc-match','-f','%{file}',q]).decode()
MED=fp('Inter:style=Medium'); LIGHT=fp('Inter:style=Light'); SERIF_I=fp('Latin Modern Roman:style=Italic')
INK=(34,31,28); MUTE=(118,110,102); BRONZE=(146,108,74); RED=(214,52,45); GREEN=(46,140,88)
def ease(t): t=min(1,max(0,t)); return t*t*(3-2*t)
def track(d,xy,text,font,fill,sp):
    w=sum(d.textlength(c,font=font) for c in text)+sp*(len(text)-1); x=xy[0]-w/2
    for c in text: d.text((x,xy[1]),c,font=font,fill=fill); x+=d.textlength(c,font=font)+sp
def overlay(img,t,cfg):
    st=cfg['stages']; d=ImageDraw.Draw(img,'RGBA')
    kick=cfg.get('kicker','BİM · İNŞAAT SIRASI')
    track(d,(W/2,150),kick,ImageFont.truetype(MED,24),BRONZE+(235,),7)
    def block(a,no,name,line):
        if a<=0: return
        off=(1-a)*14
        if no: track(d,(W/2,215+off),no,ImageFont.truetype(MED,24),MUTE+(int(255*a),),4)
        d.text((W/2,330+off),name,font=ImageFont.truetype(SERIF_I,78),fill=INK+(int(255*a),),anchor='ms')
        if line: d.text((W/2,392+off),line,font=ImageFont.truetype(LIGHT,30),fill=MUTE+(int(255*a),),anchor='ms')
    # giriş / aşamalar / final
    segs=[(0,st[0]['t0'],'',cfg['intro'],'')]+[(s['t0'],s['t1'],f"{s['no']} / {len(st):02d}",s['name'],s['line']) for s in st]+[(st[-1]['t1'],cfg['end'],'',cfg['final'],'')]
    for a0,a1,no,name,line in segs:
        if a0<=t<=a1:
            a=ease((t-a0)/0.35)*ease((a1-t)/0.25); block(a,no,name,line)
    # ilerleme çubuğu
    if t<cfg['end']:
        n=len(st); x0,x1,y=64,W-64,1790; gap=8; sw=(x1-x0-gap*(n-1))/n
        al=int(255*ease(t/0.6)*ease((cfg['end']-t)/0.5))
        for i,s in enumerate(st):
            xa=x0+i*(sw+gap); p=ease((t-s['t0'])/(s['t1']-s['t0']))
            d.rounded_rectangle([xa,y,xa+sw,y+6],radius=3,fill=(0,0,0,int(al*0.10)))
            if p>0: d.rounded_rectangle([xa,y,xa+max(6,sw*p),y+6],radius=3,fill=BRONZE+(al,))
            d.text((xa+sw/2,y+36),s['no'],font=ImageFont.truetype(MED,18),fill=(MUTE if p<1 else BRONZE)+(int(al*0.9),),anchor='ms')
    # çakışma uyarısı
    c=cfg.get('clash')
    if c and c['t0']-0.1<=t<=c['t2']+0.3:
        f=ImageFont.truetype(MED,27)
        if t<c['t1']: txt,col=c['a'],RED; a=ease((t-c['t0'])/0.25)*ease((c['t1']+0.15-t)/0.2)
        else: txt,col=c['b'],GREEN; a=ease((t-c['t1'])/0.25)*ease((c['t2']+0.3-t)/0.3)
        if a>0:
            tw=d.textlength(txt,font=f); x=W/2-(tw+70)/2; y=470
            d.rounded_rectangle([x,y,x+tw+70,y+60],radius=30,fill=(255,255,255,int(235*a)),outline=col+(int(255*a),),width=2)
            d.ellipse([x+22,y+22,x+38,y+38],fill=col+(int(255*a),))
            d.text((x+50,y+30),txt,font=f,fill=INK+(int(255*a),),anchor='lm')
    return img
if __name__=='__main__':
    cfg=json.load(open(sys.argv[1])); src=sys.argv[2]; dst=sys.argv[3]; os.makedirs(dst,exist_ok=True)
    fs=sorted(os.listdir(src))
    for i,f in enumerate(fs):
        im=Image.open(os.path.join(src,f)).convert('RGB'); overlay(im,i/FPS,cfg).save(os.path.join(dst,f),quality=93)
    print('ok',len(fs))
