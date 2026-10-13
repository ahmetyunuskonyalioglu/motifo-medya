# Motifo müzik kütüphanesi — telifsiz, tamamen kodla üretilir.
# Tarzlar: insaat (ritmik, aşamalara senkron), piyano (ambient), lofi (sıcak elektrik piyano + groove),
#          sinematik (drone + yaylı + vuruş). Her üretimde ton/tempo/tohum değişir; kayıt: muzik_kayit.json
import numpy as np, wave, json, os
from scipy.signal import lfilter, butter
SR=44100
def note(m): return 440.0*2**((m-69)/12)
def T(d): return np.arange(int(d*SR))/SR
def lp(x,f,o=2):
    b,a=butter(o,min(0.99,f/(SR/2)),'low'); return lfilter(b,a,x)
def hp(x,f,o=2):
    b,a=butter(o,min(0.99,f/(SR/2)),'high'); return lfilter(b,a,x)
def adsr(n,a,d,s,r):
    e=np.ones(n)*s; A=int(a*SR); D=int(d*SR); R=int(r*SR)
    A=min(A,n); e[:A]=np.linspace(0,1,A)
    if A+D<n: e[A:A+D]=np.linspace(1,s,D)
    if R>0 and R<n: e[-R:]*=np.linspace(1,0,R)
    return e
# --- enstrümanlar ---
def piano(m,d=3.0,v=0.3,rng=None):
    t=T(d); f=note(m); B=0.0004; x=0
    for k in range(1,9):
        fk=f*k*np.sqrt(1+B*k*k); x=x+np.sin(2*np.pi*fk*t+ (rng.uniform(0,6) if rng is not None else 0))*np.exp(-t*(0.8+k*0.55))/k**1.1
    hammer=np.random.default_rng(int(m)).standard_normal(len(t))*np.exp(-t*90)*0.02
    x=(x+hammer)*adsr(len(t),0.003,0.1,1,0.3); x=lp(x,5000)
    return x/np.abs(x).max()*v
def rhodes(m,d=2.5,v=0.25):
    t=T(d); f=note(m); I=1.6*np.exp(-t*3)
    x=np.sin(2*np.pi*f*t+I*np.sin(2*np.pi*f*t))*np.exp(-t*1.1)
    x+=0.25*np.sin(2*np.pi*2*f*t)*np.exp(-t*2.5)
    x=x*adsr(len(t),0.005,0.2,1,0.25)*(1+0.12*np.sin(2*np.pi*4.5*t))
    return x/np.abs(x).max()*v
def strings(ms,d,v=0.15,a=1.2,r=1.5,bright=2400,seed=0):
    rng=np.random.default_rng(seed); t=T(d); x=0
    for m in ms:
        for det in (-0.09,-0.03,0.03,0.09):
            f=note(m)*2**(det/12); ph=rng.uniform(0,1)
            saw=2*((f*t+ph)%1)-1; x=x+saw*(1+0.004*np.sin(2*np.pi*5.2*t+ph*6))
    x=lp(x,bright,2)*adsr(len(t),a,0.5,0.9,r)
    return x/np.abs(x).max()*v
def bass(m,d,v=0.3):
    t=T(d); f=note(m); x=np.sin(2*np.pi*f*t)+0.3*np.sin(4*np.pi*f*t)
    x=lp(x,700)*adsr(len(t),0.005,0.12,0.6,0.08); return x/np.abs(x).max()*v
def pluck(m,d=0.6,v=0.2):
    t=T(d); f=note(m); x=sum(np.sin(2*np.pi*f*k*t)/k**1.5*np.exp(-t*(6+k*2)) for k in range(1,7))
    x=lp(x,3500); return x/np.abs(x).max()*v
def kick(v=0.5):
    t=T(0.45); f=48+90*np.exp(-t*28); ph=2*np.pi*np.cumsum(f)/SR
    x=np.sin(ph)*np.exp(-t*7.5)+np.random.default_rng(1).standard_normal(len(t))*np.exp(-t*160)*0.08
    return x/np.abs(x).max()*v
def hat(v=0.08,open_=False,seed=2):
    t=T(0.3 if open_ else 0.06); x=hp(np.random.default_rng(seed).standard_normal(len(t)),7000)*np.exp(-t*(12 if open_ else 70))
    return x/np.abs(x).max()*v
def clank(v=0.12,f0=1800,seed=3):  # metal / inşaat tıkırtısı
    t=T(0.35); rng=np.random.default_rng(seed); x=0
    for r in (1,2.76,5.4,8.9): x=x+np.sin(2*np.pi*f0*r*t+rng.uniform(0,6))*np.exp(-t*(18+r*6))
    x+=hp(rng.standard_normal(len(t)),3000)*np.exp(-t*90)*0.4
    return x/np.abs(x).max()*v
def boom(v=0.45):
    t=T(2.2); f=38+30*np.exp(-t*6); x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*1.8)
    x+=lp(np.random.default_rng(4).standard_normal(len(t)),300)*np.exp(-t*4)*0.4
    return x/np.abs(x).max()*v
def riser(d=1.5,v=0.12,seed=5):
    t=T(d); x=hp(np.random.default_rng(seed).standard_normal(len(t)),800)
    w=(t/d)**2; x=(lp(x,1500)*(1-w)+lp(x,7500)*w)*w; return x/np.abs(x).max()*v
# --- mikser + yankı ---
class Mix:
    def __init__(s,d): s.b=np.zeros((int(d*SR),2))
    def add(s,x,at,pan=0.0,g=1.0):
        i=int(at*SR)
        if i>=len(s.b) or i<0: return
        if x.ndim==1: x=np.stack([x*(1-max(0,pan)),x*(1+min(0,pan))],1)
        j=min(len(s.b),i+len(x)); s.b[i:j]+=x[:j-i]*g
    def reverb(s,mix=0.22,room=0.84,damp=3800):
        out=np.zeros_like(s.b)
        for ch in range(2):
            x=s.b[:,ch]; y=0
            for dl in ([1557,1617,1491,1422] if ch==0 else [1580,1640,1514,1445]):
                g=room; yy=lfilter([1],np.r_[1,np.zeros(dl-1),-g],x); y=y+lp(yy,damp,1)
            for ap in (225,556,441):
                y=lfilter(np.r_[-0.5,np.zeros(ap-1),1],np.r_[1,np.zeros(ap-1),-0.5],y)
            out[:,ch]=y/4
        s.b=s.b*(1-mix)+out*mix*2.2
    def save(s,path,fade=1.2,rev=0.22):
        s.reverb(rev); n=int(fade*SR); s.b[-n:]*=np.linspace(1,0,n)[:,None]
        b=np.tanh(s.b*1.3)/np.tanh(1.3); b=b/max(1e-9,np.abs(b).max())*0.9
        w=wave.open(path,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((b*32767).astype('<i2').tobytes()); w.close()
# --- ton/akor yardımcıları ---
SCALES={'lidya':[0,2,4,6,7,9,11],'majör':[0,2,4,5,7,9,11],'dorian':[0,2,3,5,7,9,10],'minör':[0,2,3,5,7,8,10]}
def chord(root,scale,deg,n=4):
    sc=SCALES[scale]; out=[]
    for k in range(n):
        i=deg+2*k; out.append(root+sc[i%7]+12*(i//7))
    return out
# --- tarzlar ---
def insaat(out,dur,hits,end_at=None,root=57,scale='dorian',bpm=104,seed=0):
    """hits: aşama başlangıç zamanları (s). end_at: logo kapanışının başladığı an (müzik yumuşar)."""
    rng=np.random.default_rng(seed); m=Mix(dur); beat=60/bpm; end_at=end_at or dur
    prog=[0,5,3,4] if seed%2==0 else [0,3,4,6]
    nb=int(end_at/beat)
    for i in range(nb):
        t=i*beat; bar=i//4; c=chord(root-12,scale,prog[bar%len(prog)],3)
        if i%4==0: m.add(kick(0.42),t)
        if i%4==2 and bar>=1: m.add(kick(0.30),t)
        m.add(hat(0.05 if i%2 else 0.035,seed=i),t+beat/2,pan=0.3)
        if bar>=2 and i%2==1: m.add(clank(0.05,1500+rng.uniform(-200,400),seed=i),t+beat*0.75,pan=-0.4)
        m.add(bass(c[0],beat*0.9,0.26),t)
        if i%2==0: m.add(pluck(c[(i//2)%3]+24,0.5,0.07),t+beat*0.5,pan=0.25)
    for k,h in enumerate(hits):
        m.add(boom(0.32),h); m.add(clank(0.1,2200,seed=40+k),h,pan=0.2)
        if h>1.5: m.add(riser(1.2,0.06,seed=k),h-1.2)
        c=chord(root,scale,prog[k%len(prog)],4)
        m.add(strings(c,min(4.5,dur-h),0.10,a=0.8,r=1.6,seed=k),h)
    # kapanış: ritim durur, akor süzülür
    c=chord(root,scale,0,5); m.add(strings(c,dur-end_at+1.0,0.13,a=0.6,r=dur-end_at,seed=99),end_at-0.4)
    m.add(piano(root+12,3.5,0.18,rng),end_at); m.add(piano(root+19,3.5,0.12,rng),end_at+0.35)
    m.save(out,fade=1.4,rev=0.2)
def piyano(out,dur,cuts,end_at=None,root=60,scale='lidya',seed=0):
    rng=np.random.default_rng(seed); m=Mix(dur); end_at=end_at or dur
    prog=[0,4,5,3]; step=end_at/max(1,len(cuts))
    for k,t0 in enumerate(cuts+[end_at]):
        c=chord(root-12,scale,prog[k%4],4)
        m.add(strings(c,step+2.5,0.07,a=1.5,r=2,bright=1400,seed=k),t0)
        for j,nn in enumerate(c[1:]+[c[0]+12]):
            m.add(piano(nn+12,3.5,0.16*rng.uniform(0.7,1),rng),t0+j*0.42+rng.uniform(0,0.05),pan=rng.uniform(-0.4,0.4))
        m.add(piano(c[0],4,0.2,rng),t0)
    m.save(out,fade=1.6,rev=0.3)
def lofi(out,dur,cuts,end_at=None,root=62,scale='dorian',bpm=82,seed=0):
    rng=np.random.default_rng(seed); m=Mix(dur); beat=60/bpm; end_at=end_at or dur
    prog=[0,3,5,4]
    for i in range(int(end_at/beat)):
        t=i*beat+ (0.03 if i%2 else 0); bar=i//4
        if i%4 in (0,): m.add(kick(0.3),t)
        if i%4==2: m.add(hat(0.09,True,seed=i),t)
        m.add(hat(0.035,seed=i+7),t+beat/2)
        if i%4==0:
            c=chord(root-12,scale,prog[bar%4],4)
            for j,nn in enumerate(c): m.add(rhodes(nn+12,beat*4,0.12),t+j*0.02,pan=(j-1.5)*0.15)
            m.add(bass(c[0]-12,beat*3.5,0.24),t)
    m.add(rhodes(root+12,3,0.15),end_at); m.save(out,fade=1.5,rev=0.25)
def sinematik(out,dur,cuts,end_at=None,root=50,scale='minör',seed=0):
    rng=np.random.default_rng(seed); m=Mix(dur); end_at=end_at or dur
    m.add(strings([root-12,root-5],dur,0.1,a=3,r=3,bright=600,seed=1),0)
    prog=[0,5,3,6]
    for k,t0 in enumerate(cuts):
        c=chord(root,scale,prog[k%4],4); m.add(strings(c,4.5,0.12,a=1.0,r=2,seed=k),t0)
        m.add(boom(0.3),t0)
    m.add(strings(chord(root,scale,0,5),dur-end_at+1,0.14,a=0.8,r=dur-end_at,seed=9),end_at-0.5)
    m.save(out,fade=1.6,rev=0.28)
STYLES={'insaat':insaat,'piyano':piyano,'lofi':lofi,'sinematik':sinematik}
def kaydet(kayit_path,video,stil,root,scale,seed):
    k=json.load(open(kayit_path)) if os.path.exists(kayit_path) else {'parcalar':[]}
    k['parcalar'].append({'video':video,'stil':stil,'ton':root,'mod':scale,'tohum':seed})
    json.dump(k,open(kayit_path,'w'),indent=1,ensure_ascii=False)
def sonraki_stil(kayit_path,uygun):
    """Son 3 videoda kullanılmayan bir tarz seç."""
    k=json.load(open(kayit_path)) if os.path.exists(kayit_path) else {'parcalar':[]}
    son=[p['stil'] for p in k['parcalar'][-3:]]
    for s in uygun:
        if s not in son: return s
    return uygun[0]
