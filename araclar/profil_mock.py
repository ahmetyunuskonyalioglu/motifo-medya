# Instagram profil önizlemesi (ziyaretçi görünümü) — ızgara sistemini gerçek ekranda göstermek için
import sys,os,json
sys.path.insert(0,os.path.dirname(__file__))
from izgara import *
from PIL import Image,ImageDraw,ImageFont,ImageOps
UI=fp('Inter:style=Regular'); UIB=fp('Inter:style=SemiBold'); UIBB=fp('Inter:style=Bold')
SW=1170; GAP=3; TW=(SW-2*GAP)//3; TH=TW*4//3
def tiles(plan,P):
    out=[]
    for t in plan:
        if t['tip']=='panorama':
            ims=panorama(P+t['src'],t['no'],t['ad'],t['yer'],t.get('fx',0.5),t.get('fy',0.5),t.get('zoom',1.0),t.get('koyu',False))
            for k,im in enumerate(ims): out.append((im,dict(t,ikon=t.get('ikonlar',[None]*3)[k],pin=t.get('pin',False))))
            continue
        if t['tip']=='marka_panorama':
            for im in marka_panorama(): out.append((im,{'pin':True}))
            continue
        if t['tip']=='pafta':
            out.append((pafta(P+t['src'],t['no'],t['ad'],t['yer'],t['tur'],t.get('cizim',False),t.get('fx',0.5),t.get('fy',0.5),t.get('zoom',1.0)),t)); continue
        k=dict(fx=t.get('fx',0.5),fy=t.get('fy',0.5),zoom=t.get('zoom',1.0))
        if t['tip']=='sade': out.append((sade(P+t['src'],t['no'],t['ad'],t['yer'],t.get('stil','cerceve'),**k),t)); continue
        if t['tip']=='paspartu': out.append((paspartu(P+t['src'],t['no'],t['ad'],t['yer'],t.get('dikey',False),**k),t)); continue
        if t['tip']=='kemer': out.append((kemer(P+t['src'],t['no'],t['ad'],t['yer'],t.get('koyu',False),**k),t)); continue
        if t['tip']=='capraz': out.append((capraz(P+t['src'],t['no'],t['ad'],t['yer'],**k),t)); continue
        if t['tip']=='palet': out.append((palet(P+t['src'],t['no'],t['ad'],t['yer'],**k),t)); continue
        if t['tip']=='sb': out.append((sb_gorsel(P+t['src'],t['no'],t['ad'],t['yer'],t.get('renkli',False),**k),t)); continue
        if t['tip']=='marka': im=marka()
        elif t['tip']=='gorsel': im=gorsel(P+t['src'],t['no'],t['ad'],t['yer'],t.get('fx',0.5),t.get('fy',0.5),t.get('zoom',1.0))
        else: im=cizim(P+t['src'],t['no'],t['ad'],t['yer'],t['tur'],t.get('fx',0.5),t.get('fy',0.5),t.get('zoom',1.0),t.get('koyu',False))
        out.append((im,t))
    return out
def icon_pin(d,x,y):
    d.polygon([(x,y),(x+26,y),(x+20,y+18),(x+26,y+30),(x,y+30),(x+6,y+18)],fill=(255,255,255))
    d.line([(x+13,y+30),(x+13,y+46)],fill=(255,255,255),width=4)
def icon_carousel(d,x,y):
    d.rounded_rectangle([x+8,y,x+40,y+32],radius=5,outline=(255,255,255),width=4)
    d.rounded_rectangle([x,y+8,x+32,y+40],radius=5,fill=(255,255,255))
def icon_reel(d,x,y):
    d.rounded_rectangle([x,y,x+40,y+40],radius=9,outline=(255,255,255),width=4)
    d.line([(x,y+12),(x+40,y+12)],fill=(255,255,255),width=4)
    d.polygon([(x+15,y+19),(x+15,y+35),(x+29,y+27)],fill=(255,255,255))
def grid(img,y0,tl):
    d=ImageDraw.Draw(img)
    for k,(im,t) in enumerate(tl):
        r,c=divmod(k,3); x=c*(TW+GAP); y=y0+r*(TH+GAP)
        img.paste(im.resize((TW,TH),Image.LANCZOS),(x,y))
        ix,iy=x+TW-58,y+16
        if t.get('pin'): icon_pin(d,ix+8,iy)
        elif t.get('ikon')=='reel': icon_reel(d,ix,iy)
        elif t.get('ikon')=='karusel': icon_carousel(d,ix,iy)
    return y0+((len(tl)+2)//3)*(TH+GAP)
def header(img,meta):
    d=ImageDraw.Draw(img); K=(0,0,0); G=(115,115,115)
    f=lambda p,s: ImageFont.truetype(p,s)
    d.text((80,62),'22:12',font=f(UIB,46),fill=K)
    # sağ durum ikonları
    for i,h in enumerate([12,20,28,36]): d.rounded_rectangle([878+i*16,96-h,888+i*16,96],radius=2,fill=K)
    d.pieslice([952,48,1012,108],225,315,fill=K); d.pieslice([967,63,997,93],225,315,fill=(255,255,255)); d.pieslice([975,71,989,85],225,315,fill=K)
    d.rounded_rectangle([1028,62,1100,96],radius=9,outline=K,width=3); d.rounded_rectangle([1034,68,1086,90],radius=5,fill=K); d.rectangle([1102,73,1107,85],fill=K)
    # gezinme
    d.line([(58,190),(38,170),(58,150)],fill=K,width=6,joint='curve')
    d.text((100,170),meta['kullanici'],font=f(UIBB,50),fill=K,anchor='lm')
    for i in range(3): d.ellipse([1078+i*24,164,1090+i*24,176],fill=K)
    # zil
    d.chord([952,140,996,196],180,360,outline=K,width=5); d.line([(952,168),(952,186)],fill=K,width=5); d.line([(996,168),(996,186)],fill=K,width=5)
    d.line([(942,188),(1006,188)],fill=K,width=5); d.ellipse([967,194,981,208],fill=K)
    # avatar
    av=Image.new('RGB',(260,260),(255,255,255)); lg=Image.open(os.path.join(R,'marka','logo_altin.png')).convert('RGBA')
    lg=lg.crop(lg.getchannel('A').point(lambda v:255 if v>8 else 0).getbbox()); lg.thumbnail((200,200),Image.LANCZOS)
    av.paste(lg,((260-lg.width)//2,(260-lg.height)//2+6),lg)
    m=Image.new('L',(260,260),0); ImageDraw.Draw(m).ellipse([0,0,259,259],fill=255)
    d.ellipse([40,260,312,532],outline=(219,219,219),width=3); img.paste(av,(46,266),m)
    d.text((370,300),meta['ad'],font=f(UIB,44),fill=K)
    xs=[370,600,850]
    for x,(n,l) in zip(xs,meta['sayilar']):
        d.text((x,370),n,font=f(UIBB,46),fill=K); d.text((x,428),l,font=f(UI,38),fill=K)
    y=580
    d.text((44,y),meta['kategori'],font=f(UI,38),fill=G); y+=56
    for line in meta['bio']: d.text((44,y),line,font=f(UI,40),fill=K); y+=56
    y+=26
    d.rounded_rectangle([40,y,520,y+86],radius=18,fill=(0,149,246)); d.text((280,y+43),'Takip et',font=f(UIB,40),fill=(255,255,255),anchor='mm')
    d.rounded_rectangle([536,y,1016,y+86],radius=18,fill=(239,239,239)); d.text((776,y+43),'Mesaj gönder',font=f(UIB,40),fill=K,anchor='mm')
    d.rounded_rectangle([1032,y,1130,y+86],radius=18,fill=(239,239,239))
    d.ellipse([1066,y+18,1090,y+42],outline=K,width=4); d.arc([1056,y+44,1100,y+80],180,360,fill=K,width=4)
    y+=130
    # öne çıkanlar
    for i,(lab,im) in enumerate(meta['hl']):
        cx=40+i*214+86
        d.ellipse([cx-90,y,cx+90,y+180],outline=(219,219,219),width=3)
        c=ImageOps.fit(im,(164,164),Image.LANCZOS); m=Image.new('L',(164,164),0); ImageDraw.Draw(m).ellipse([0,0,163,163],fill=255)
        img.paste(c,(cx-82,y+8),m)
        d.text((cx,y+222),lab,font=f(UI,34),fill=K,anchor='mm')
    y+=290
    # sekmeler
    d.line([(0,y+96),(SW,y+96)],fill=(219,219,219),width=2)
    for i in range(3):
        cx=SW//6+i*SW//3; cy=y+46
        if i==0:
            for a in range(3):
                for b in range(3): d.rectangle([cx-26+a*19,cy-26+b*19,cx-12+a*19,cy-12+b*19],fill=K)
            d.line([(0,y+94),(SW//3,y+94)],fill=K,width=4)
        elif i==1:
            d.rounded_rectangle([cx-26,cy-26,cx+26,cy+26],radius=10,outline=G,width=4); d.line([(cx-26,cy-12),(cx+26,cy-12)],fill=G,width=4)
            d.polygon([(cx-7,cy-2),(cx-7,cy+16),(cx+9,cy+7)],fill=G)
        else:
            d.rounded_rectangle([cx-26,cy-26,cx+26,cy+26],radius=10,outline=G,width=4); d.ellipse([cx-9,cy-14,cx+9,cy+4],outline=G,width=4); d.arc([cx-18,cy+4,cx+18,cy+34],200,340,fill=G,width=4)
    return y+100
if __name__=='__main__':
    spec=json.load(open(sys.argv[1])); out=sys.argv[2]; P=os.path.join(R,'kaynak','PROJELER')+'/'
    tl=tiles(spec['izgara'],P)
    hl=[(h['ad'],cizim(P+h['src'],0,'','',' ',h.get('fx',.5),h.get('fy',.5)).crop((96,150,984,970))) for h in spec['one_cikan']]
    meta=dict(spec['profil'],hl=hl)
    H_=3000+((len(tl)+2)//3)*(TH+GAP)
    img=Image.new('RGB',(SW,H_),(255,255,255))
    y=header(img,meta); y=grid(img,y,tl)
    img=img.crop((0,0,SW,y)); img.save(out+'_tam.jpg',quality=92)
    img.crop((0,0,SW,2532)).save(out+'_ekran.jpg',quality=92)
    print(img.size)
