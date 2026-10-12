# Motifo için telifsiz, kodla üretilmiş sesler
import numpy as np, wave
SR=44100
def t_(d): return np.arange(int(d*SR))/SR
def note(f): return 440*2**((f-69)/12)
def env(n,a,r,sus=1.0):
    e=np.ones(n)*sus; A=int(a*SR); R=int(r*SR)
    if A: e[:A]=np.linspace(0,sus,A)**1.5
    if R: e[-R:]*=np.linspace(1,0,R)**1.2
    return e
def lowpass(x,cut):
    a=np.exp(-2*np.pi*cut/SR); y=np.zeros_like(x); s=0.0
    # vectorized via lfilter-like loop in chunks (scipy may not exist)
    try:
        from scipy.signal import lfilter
        return lfilter([1-a],[1,-a],x)
    except Exception:
        for i in range(len(x)): s=(1-a)*x[i]+a*s; y[i]=s
        return y
def pad(midis,dur,a=1.5,r=2.5,vol=0.12,bright=1800,seed=0):
    rng=np.random.default_rng(seed); t=t_(dur); L=np.zeros_like(t); R=np.zeros_like(t)
    for m in midis:
        f=note(m)
        for det,pan in ((-0.07,0.3),(0.0,0.5),(0.07,0.7)):
            ff=f*2**(det/12); ph=rng.uniform(0,6.28)
            w=sum(np.sin(2*np.pi*ff*k*t+ph*k)/k**1.6 for k in range(1,7))
            lfo=1+0.15*np.sin(2*np.pi*rng.uniform(0.1,0.25)*t+ph)
            L+=w*lfo*(1-pan); R+=w*lfo*pan
    e=env(len(t),a,r)
    L=lowpass(L,bright)*e; R=lowpass(R,bright)*e
    m=max(np.abs(L).max(),np.abs(R).max())+1e-9
    return np.stack([L,R],1)/m*vol
def bell(midi,dur=4,vol=0.18):
    t=t_(dur); f=note(midi)
    parts=[(1,1),(2.0,0.5),(2.76,0.35),(5.4,0.18),(8.93,0.08)]
    x=sum(a*np.sin(2*np.pi*f*r*t)*np.exp(-t*(1.2+r*0.9)) for r,a in parts)
    x=x/np.abs(x).max()*vol
    return np.stack([x*0.9,x],1)
def pluck(midi,dur=1.6,vol=0.12):
    t=t_(dur); f=note(midi)
    x=sum(np.sin(2*np.pi*f*k*t)/k**2*np.exp(-t*(3+k*1.5)) for k in range(1,6))
    x=lowpass(x,3000); x=x/np.abs(x).max()*vol
    return np.stack([x,x*0.85],1)
def pencil(dur,vol=0.05,seed=1):
    rng=np.random.default_rng(seed); n=int(dur*SR)
    noise=rng.standard_normal(n)
    hp=noise-lowpass(noise,1500); bp=lowpass(hp,5500)
    # strokes
    amp=np.zeros(n); i=0
    while i<n:
        L=int(rng.uniform(0.12,0.45)*SR); g=int(rng.uniform(0.03,0.12)*SR)
        seg=np.sin(np.linspace(0,np.pi,min(L,n-i)))**0.6*rng.uniform(0.5,1)
        amp[i:i+len(seg)]=seg; i+=L+g
    x=bp*amp; x=x/np.abs(x).max()*vol
    return np.stack([x*0.8,x],1)
def whoosh(dur=0.6,vol=0.06,seed=2):
    rng=np.random.default_rng(seed); n=int(dur*SR); noise=rng.standard_normal(n)
    x=lowpass(noise,900)*np.sin(np.linspace(0,np.pi,n))**2
    x=x/np.abs(x).max()*vol; return np.stack([x,x],1)
def reverb(x,mix=0.25,seed=3):
    rng=np.random.default_rng(seed); out=x.copy()
    for d,g in ((0.031,0.5),(0.047,0.45),(0.073,0.4),(0.11,0.33),(0.17,0.25),(0.23,0.2),(0.31,0.14),(0.43,0.09)):
        k=int(d*SR); out[k:,0]+=x[:-k,0]*g*mix*rng.uniform(0.8,1.2); out[k:,1]+=x[:-k,1]*g*mix*rng.uniform(0.8,1.2)
    return out
class Mix:
    def __init__(s,dur): s.buf=np.zeros((int(dur*SR),2))
    def add(s,clip,at):
        i=int(at*SR)
        if i>=len(s.buf): return
        j=min(len(s.buf),i+len(clip)); s.buf[i:j]+=clip[:j-i]
    def save(s,path,fade_out=1.2):
        b=reverb(s.buf); n=int(fade_out*SR); b[-n:]*=np.linspace(1,0,n)[:,None]
        b=np.tanh(b*1.2)/np.tanh(1.2); b=b/max(1e-9,np.abs(b).max())*0.89
        w=wave.open(path,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((b*32767).astype('<i2').tobytes()); w.close()
