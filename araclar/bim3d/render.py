import asyncio,sys,os,base64,json,time
from playwright.async_api import async_playwright
scene=sys.argv[1]; out=sys.argv[2]; times=sys.argv[3]
async def main():
    os.makedirs(out,exist_ok=True)
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        pg=await b.new_page(viewport={'width':1080,'height':1920})
        await pg.goto('file:///home/claude/bim3d/engine.html')
        n=await pg.evaluate('(s)=>setup(s)',open(scene).read())
        XR=await pg.evaluate('()=>SCENE_XRAY()')
        meta=await pg.evaluate('()=>({stages:SCENE_STAGES()})') if False else None
        if times=='all':
            dur=await pg.evaluate('()=>0')
        ts=[float(x) for x in times.split(',')] if times!='all' else None
        if ts is None:
            D=float(sys.argv[4]); st=int(sys.argv[5]) if len(sys.argv)>5 else 0; ts=[i/30 for i in range(st,int(D*30))]
        t0=time.time()
        for i,t in enumerate(ts):
            xr=XR
            if xr and xr[0]-0.25<=t<=xr[1]+0.25:
                import io
                from PIL import Image
                r=await pg.evaluate('(t)=>frame2(t,t,"real",null)',t); x=await pg.evaluate('(t)=>frame2(t,t,"xray",null)',t)
                R=Image.open(io.BytesIO(base64.b64decode(r.split(',')[1]))); X=Image.open(io.BytesIO(base64.b64decode(x.split(',')[1])))
                k=min(1,max(0,(t-(xr[0]-0.25))/0.5))*min(1,max(0,((xr[1]+0.25)-t)/0.5)); k=k*k*(3-2*k)
                buf=io.BytesIO(); Image.blend(R,X,k).save(buf,'JPEG',quality=94); d='data:,'+base64.b64encode(buf.getvalue()).decode()
            else:
                d=await pg.evaluate('(t)=>frame(t)',t)
            open(f'{out}/f{i+(st if times=="all" else 0):05d}.jpg','wb').write(base64.b64decode(d.split(',')[1]))
            if i%60==0: print(i,round(time.time()-t0,1),flush=True)
        print('elems',n,'frames',len(ts))
        await b.close()
asyncio.run(main())
