# Ritmik detay reels (havuz örneği 2026-10-15_01): vuruşa oturan sert kesmeler, kısa derinlikli hareket, sabit daktilo satırı
import sys,os,json,shutil
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from parallax import shot_frames, ease
import reel, sr
from PIL import Image
FPS=30
def main(spec_path,out):
    sp=json.load(open(spec_path)); beat=60/sp.get('bpm',116.5); tmp=out+'_fr'; shutil.rmtree(tmp,ignore_errors=True); os.makedirs(tmp)
    t=0.0; n=0; cache={}
    toplam=sum(c['vurus'] for c in sp['kesmeler'])*beat; sp['_toplam']=toplam
    for c in sp['kesmeler']:
        if c['file'] not in cache: cache[c['file']]=Image.open(sr.buyut(c['file'])).convert('RGB')
        im=cache[c['file']]; d=c['vurus']*beat
        N=int(round((t+d)*FPS))-int(round(t*FPS))
        for f in list(shot_frames(im,tuple(c['win']),max(N,2),c.get('move',{'dolly':0.05})))[:N]:
            f=reel.sabit(f,sp['sabit_yazi'],n/FPS,sp) if sp.get('sabit_yazi') else f
            f.save(f'{tmp}/f{n:05d}.jpg',quality=93); n+=1
        t+=d
    lf=sorted(os.listdir(sp['logo_end'])); last=Image.open(f'{tmp}/f{n-1:05d}.jpg')
    for k,name in enumerate(lf):
        f=Image.open(os.path.join(sp['logo_end'],name)).convert('RGB')
        if k<10: f=Image.blend(last,f,ease((k+1)/10))
        f.save(f'{tmp}/f{n:05d}.jpg',quality=93); n+=1
    print('kare',n,'sn',round(n/FPS,2),'kesme süresi',round(toplam,2))
if __name__=='__main__': main(sys.argv[1],sys.argv[2])
