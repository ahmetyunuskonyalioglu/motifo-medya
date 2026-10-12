import sys,glob,os
from PIL import Image,ImageDraw
out=sys.argv[1]; files=sys.argv[2:]
files=sorted(files,key=lambda p:(os.path.dirname(p),int(''.join(c for c in os.path.basename(p) if c.isdigit()) or 0)))
cols=6; tw=300; th=200
rows=(len(files)+cols-1)//cols
sh=Image.new('RGB',(cols*tw,rows*th),'white'); d=ImageDraw.Draw(sh)
for i,p in enumerate(files):
    im=Image.open(p).convert('RGB'); 
    if i==0 or True: pass
    im.thumbnail((tw-4,th-18)); x=(i%cols)*tw; y=(i//cols)*th
    sh.paste(im,(x+2,y+2)); d.text((x+4,y+th-15),os.path.basename(p)+f' {Image.open(p).size}',fill='red')
sh.save(out,quality=80)
