# Florya Mavikoru iç mekân — ritmik detay reels. Kaynaklar 2000-3600 px: CLAUDE.md gereği SR'siz (sadece şablon kırpma), zoom ≤1,3.
import sys,os,hashlib
sys.path.insert(0,'/home/claude/motifo-medya/araclar')
import sr
from cropframe import crop_render
def buyut(path,cache_dir='/home/claude/sr_cache'):
    os.makedirs(cache_dir,exist_ok=True); out=f"{cache_dir}/n_{hashlib.md5(path.encode()).hexdigest()[:12]}.jpg"
    if not os.path.exists(out): crop_render(path).save(out,quality=96)
    return out
sr.buyut=buyut
import ritmik_reel
ritmik_reel.main(sys.argv[1],sys.argv[2])
