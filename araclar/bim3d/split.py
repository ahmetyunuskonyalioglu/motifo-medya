# "Aynı bina, iki katman": aynı kamera, iki render (gerçekçi + BİM röntgen), hareketli ayırıcı
import asyncio,sys,os,base64,io,subprocess,math
from playwright.async_api import async_playwright
from PIL import Image,ImageDraw,ImageFont
W,H,FPS=1080,1920,30
scene=sys.argv[1]; out=sys.argv[2]; DUR=float(sys.argv[3])
fp=lambda q: subprocess.check_output(['fc-match','-f','%{file}',q]).decode()
MED=fp('Inter:style=Medium'); LIGHT=fp('Inter:style=Light'); SERIF_I=fp('Latin Modern Roman:style=Italic')
INK=(34,31,28); MUTE=(118,110,102); BRONZE=(146,108,74); BLUE=(44,100,170)
def ease(t): t=min(1,max(0,t)); return t*t*(3-2*t)
CAM="""(t)=>{const u=ease(t/%s); const az=(-30+48*u)*Math.PI/180, el=(17+5*u)*Math.PI/180, R=50-4*u; const tg=[10.5,4.6,5.0];
 return {eye:[tg[0]+R*Math.cos(el)*Math.sin(az),tg[1]+R*Math.sin(el),tg[2]-R*Math.cos(el)*Math.cos(az)],target:tg,fov:56*Math.PI/180};}""" % DUR
def splitx(t):
    # sağdan gelir, ortada durur, sola süpürür (tamamı BİM), ortaya döner
    k=[(0,W+20),(1.0,W+20),(2.6,W*0.5),(5.2,W*0.5),(6.8,W*0.08),(7.8,W*0.08),(9.4,W*0.5),(99,W*0.5)]
    for (t0,x0),(t1,x1) in zip(k,k[1:]):
        if t0<=t<=t1: return x0+(x1-x0)*ease((t-t0)/(t1-t0))
    return W*0.5
def track(d,xy,text,font,fill,sp,anchor='m'):
    w=sum(d.textlength(c,font=font) for c in text)+sp*(len(text)-1); x=xy[0]-(w/2 if anchor=='m' else (w if anchor=='r' else 0))
    for c in text: d.text((x,xy[1]),c,font=font,fill=fill); x+=d.textlength(c,font=font)+sp
async def main():
    os.makedirs(out,exist_ok=True)
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        pg=await b.new_page(viewport={'width':W,'height':H})
        await pg.goto('file:///home/claude/bim3d/engine.html')
        await pg.evaluate('(s)=>setup(s)',open(scene).read())
        N=int(DUR*FPS); ST=int(sys.argv[4]) if len(sys.argv)>4 else 0
        for i in range(ST,N):
            t=i/FPS
            ra=await pg.evaluate('([t,c])=>frame2(30,t,"real",c)',[t,CAM])
            xa=await pg.evaluate('([t,c])=>frame2(30,t,"xray",c)',[t,CAM])
            R=Image.open(io.BytesIO(base64.b64decode(ra.split(',')[1]))).convert('RGB')
            X=Image.open(io.BytesIO(base64.b64decode(xa.split(',')[1]))).convert('RGB')
            sx=int(splitx(t)); img=R.copy()
            if sx<W: img.paste(X.crop((max(0,sx),0,W,H)),(max(0,sx),0))
            d=ImageDraw.Draw(img,'RGBA')
            a=ease((t-0.2)/0.6)*ease((DUR-t)/0.5)
            track(d,(W/2,150),'AYNI BİNA, İKİ KATMAN',ImageFont.truetype(MED,24),BRONZE+(int(235*a),),7)
            d.text((W/2,300),'Görünen tasarım,',font=ImageFont.truetype(SERIF_I,70),fill=INK+(int(255*a),),anchor='ms')
            d.text((W/2,380),'görünmeyen her şey',font=ImageFont.truetype(SERIF_I,70),fill=INK+(int(255*a),),anchor='ms')
            if 0<sx<W:
                d.line([(sx,470),(sx,1700)],fill=(255,255,255,240),width=3)
                d.line([(sx+2,470),(sx+2,1700)],fill=(0,0,0,40),width=1)
                d.ellipse([sx-22,1085-22,sx+22,1085+22],fill=(255,255,255,245),outline=(0,0,0,50))
                d.polygon([(sx-12,1085),(sx-5,1078),(sx-5,1092)],fill=INK); d.polygon([(sx+12,1085),(sx+5,1078),(sx+5,1092)],fill=INK)
            fl=ImageFont.truetype(MED,24)
            on=1.0 if 0<sx<W else 0.0; la=ease((sx-120)/120)*on; ra_=ease((W-120-sx)/120)*on
            if la>0: track(d,(sx-30,1730),'RENDER',fl,INK+(int(230*la*a),),6,'r')
            if ra_>0: track(d,(sx+30,1730),'BİM',fl,BLUE+(int(240*ra_*a),),6,'l')
            img.save(f'{out}/f{i:05d}.jpg',quality=93)
            if i%60==0: print(i,flush=True)
        await b.close()
asyncio.run(main())
