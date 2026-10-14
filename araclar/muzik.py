# Motifo müzik kütüphanesi — telifsiz, tamamen kodla üretilir.
# Tarzlar: insaat (ritmik, aşamalara senkron), piyano (ambient), lofi (sıcak elektrik piyano + groove),
#          sinematik (drone + yaylı + vuruş), keman (sıcak majör keman melodisi + yaylılar — Ahmet'in tercihi). Her üretimde ton/tempo/tohum değişir; kayıt: muzik_kayit.json
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

# --- keman (yay sürtmeli, legato, vibrato) ---
from scipy.signal import iirpeak
def _body(x):
    y=x*0.35
    for f,q,g in ((290,4,0.9),(480,5,0.7),(1050,3,0.5),(2600,2.5,0.6),(3400,3,0.35)):
        b,a=iirpeak(f/(SR/2),q); y=y+lfilter(b,a,x)*g
    return y
def violin_line(notes,d,v=0.2,seed=0,vib=0.22,bright=5200):
    """notes: [(midi,baş,süre)] — tek yay çizgisi, notalar arası kısa glissando."""
    rng=np.random.default_rng(seed); n=int(d*SR); t=np.arange(n)/SR
    m=np.full(n,np.nan); amp=np.zeros(n); onset=np.zeros(n)
    for (mm,s,du) in notes:
        a=int(s*SR); b=min(n,int((s+du)*SR)); 
        if a>=n: continue
        m[a:b]=mm; L=b-a; tt=np.arange(L)/SR
        env=np.minimum(1,tt/min(0.18,du*0.35))*(0.82+0.18*np.sin(np.pi*np.minimum(1,tt/du)))  # yay şişmesi
        rel=int(min(0.12,du*0.25)*SR); env[-rel:]*=np.linspace(1,0.55,rel)
        amp[a:b]=np.maximum(amp[a:b],env); onset[a:b]=tt
    # boşlukları önceki notayla doldur (frekans), sessiz kal (genlik)
    last=np.nan
    for i in range(n):
        if np.isnan(m[i]): m[i]=last if not np.isnan(last) else 69
        last=m[i]
    # glissando: midi çizgisini 70 ms yumuşat
    k=int(0.07*SR); m=np.convolve(np.pad(m,(k,k),mode='edge'),np.ones(k)/k,'same')[k:-k]
    vibd=np.clip((onset-0.22)/0.35,0,1)*vib
    m=m+vibd*np.sin(2*np.pi*5.4*t+rng.uniform(0,6))+0.02*np.sin(2*np.pi*0.7*t)
    f=440*2**((m-69)/12); ph=2*np.pi*np.cumsum(f)/SR; x=0
    for h in range(1,16):
        x=x+np.sin(h*ph+rng.uniform(0,6))/h**1.05*(1 if h<8 else 0.6)
    x=x*np.where(f*16>SR/2,0.7,1)
    bow=hp(rng.standard_normal(n),2500)*0.03
    x=_body(x+bow); x=lp(x,bright,2)
    a=lp(amp,18,1); x=x*a
    return x/np.abs(x).max()*v
def _melodi(rng,root,scale,prog,beats_per_chord,beat,start=0.0,octv=0):
    sc=SCALES[scale]; out=[]; t=start; prev=None
    pat=[[2,1,1],[1,1,2],[1.5,0.5,2],[1,0.5,0.5,2],[3,1],[1,1,1,1],[2,0.5,0.5,1]]
    for ci,deg in enumerate(prog):
        ch=[deg,deg+2,deg+4]
        rh=pat[rng.integers(len(pat))] if ci<len(prog)-1 else [4]
        for j,r in enumerate(rh):
            if prev is None: d_=ch[rng.integers(3)]%7+(7 if deg%7<3 else 0)
            elif j==0 or ci==len(prog)-1:   # akor tonu, öncekine en yakın
                c2=[c+7*k for c in ch for k in (-1,0,1)]; c2=[c for c in c2 if c!=prev] ; d_=min(c2,key=lambda c:abs(c-prev)+rng.uniform(0,1.5))
            else: d_=prev+[-1,1,1,2,-2,-1][rng.integers(6)]
            d_=d_-2 if d_>9 else (d_+2 if d_<0 else d_); prev=d_
            mm=root+octv+12*(d_//7)+sc[d_%7]
            out.append((mm,t,r*beat*0.97)); t+=r*beat
    return out
def keman(out,dur,cuts,end_at=None,root=62,scale='majör',bpm=80,seed=0):
    """Sıcak, umutlu yaylı parça: keman melodisi + yaylı pad + pizzicato + yumuşak piyano."""
    rng=np.random.default_rng(seed); m=Mix(dur); beat=60/bpm; end_at=end_at or dur
    progs=[[0,4,5,3],[0,5,3,4],[5,3,0,4],[0,3,5,4]]; prog=progs[seed%4]
    bar=beat*4; nb=int(np.ceil(end_at/bar)); P=[prog[i%4] for i in range(nb)]
    for i,deg in enumerate(P):
        t0=i*bar; c=chord(root-12,scale,deg,4)
        m.add(strings(c,bar+1.6,0.075,a=0.9,r=1.4,bright=1700,seed=i),t0,g=1.0)
        m.add(bass(c[0]-12,bar*0.95,0.13),t0)
        for j in range(4):   # pizzicato
            nn=c[[0,2,1,3][j]]+12
            m.add(pluck(nn,0.5,0.06),t0+j*beat+0.01,pan=(j-1.5)*0.25)
        if i%2==1: m.add(piano(c[-1]+24,3,0.07,rng),t0+beat*2,pan=0.3)
    mel=_melodi(rng,root,scale,P[1:],4,beat,start=bar)   # ilk ölçü giriş
    m.add(violin_line(mel,dur,0.2,seed=seed),0,pan=-0.1)
    # ikinci keman: üçlü altta, daha sessiz, son yarıda
    sc=SCALES[scale]; inS=lambda q:((q-root)%12) in sc
    half=[((a-3) if inS(a-3) else (a-4),s_,d_) for (a,s_,d_) in mel if s_>end_at*0.45]
    if half: m.add(violin_line(half,dur,0.08,seed=seed+1,vib=0.18,bright=3800),0,pan=0.25)
    # kapanış: tonik akor uzun yaylı + keman tonikte
    m.add(strings(chord(root-12,scale,0,5),dur-end_at+1.5,0.1,a=1.0,r=dur-end_at,bright=1600,seed=99),end_at-0.4)
    m.add(violin_line([(root+12,0.0,dur-end_at+0.3)],dur-end_at+1.2,0.12,seed=seed+5),end_at-0.2)
    m.save(out,fade=1.8,rev=0.32)

STYLES={'insaat':insaat,'piyano':piyano,'lofi':lofi,'sinematik':sinematik,'keman':keman}
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
# --- keman_ritmik: referans (havuz 2026-10-15_01) gibi ~118 BPM, yumuşak 4/4 vuruş + bas groove + keman ---
def keman_ritmik(out,dur,cuts=None,end_at=None,root=62,scale='minör',bpm=118,seed=0):
    rng=np.random.default_rng(seed); m=Mix(dur); beat=60/bpm; end_at=end_at or dur
    progs=[[0,5,3,4],[0,3,5,4],[5,3,0,4],[0,4,5,3]]; prog=progs[seed%4]; bar=beat*4
    nb=int(np.ceil(end_at/bar)); P=[prog[(i//1)%4] for i in range(nb)]
    for i in range(int(end_at/beat)):
        t=i*beat; b=i//4
        m.add(kick(0.34 if b>0 else 0.0),t)                          # ilk ölçü vuruşsuz giriş
        m.add(hat(0.05,False,seed=i),t+beat/2)
        if i%4 in (1,3) and b>0: m.add(hat(0.035,True,seed=i+3),t)
        c=chord(root-12,scale,P[min(b,nb-1)],4)
        if i%4==0:
            m.add(strings(c,bar+0.8,0.05,a=0.4,r=0.8,bright=1500,seed=b),t)
        # senkoplu bas
        for off,nn in ((0,c[0]-12),(0.75,c[0]-12),(1.5,c[0])):
            if i%2==0: m.add(bass(nn,beat*0.42,0.22),t+off*beat)
        # pizzicato arpej (8'lik)
        for k in range(2):
            m.add(pluck(c[(i*2+k)%4]+12,0.35,0.05),t+k*beat/2,pan=(k-0.5)*0.4)
    P2=[p for p in P[2:] for _ in (0,1)]
    mel=_melodi(rng,root,scale,P2,4,beat/2,start=bar*2)          # 2. ölçüden sonra keman, 8'lik ritim
    m.add(violin_line(mel,dur,0.17,seed=seed,vib=0.16),0,pan=-0.1)
    m.add(strings(chord(root-12,scale,0,5),dur-end_at+1.2,0.08,a=0.6,r=dur-end_at,bright=1500,seed=77),end_at-0.3)
    m.add(violin_line([(root+12,0.0,dur-end_at+0.2)],dur-end_at+1.0,0.1,seed=seed+5),end_at-0.2)
    m.save(out,fade=1.6,rev=0.22)
STYLES['keman_ritmik']=keman_ritmik
