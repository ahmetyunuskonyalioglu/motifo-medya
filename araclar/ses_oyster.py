import sys; sys.path.insert(0,sys.argv[1])
from sesler import *
import numpy as np
dur=18.7; m=Mix(dur)
cuts=[0,2.4,4.7,7.0,9.3,11.6,13.9,16.1]
chords=[[53,57,60,64],[52,55,59,62],[50,53,57,60,64],[48,52,55,59]]  # Fmaj7 Em7 Dm9 Cmaj7
L=dur/4
for i,c in enumerate(chords):
    m.add(pad(c,L+2.5,a=0.8,r=2.2,vol=0.12,bright=1500,seed=i),i*L)
    m.add(pad([c[0]-12],L+2,a=0.5,r=2,vol=0.10,bright=300,seed=10+i),i*L)
mel=[76,79,74,77,72,76,79,84]
for i,t in enumerate(cuts):
    if t>0: m.add(whoosh(0.5,vol=0.045,seed=i),t-0.3)
    m.add(pluck(mel[i],1.8,vol=0.10),t+0.05)
# soft pulse (shaker) at 96bpm
beat=60/96; rng=np.random.default_rng(7)
for k in range(int((cuts[-1])/beat*2)):
    t=k*beat/2; n=int(0.06*SR); x=rng.standard_normal(n); x=x-lowpass(x,6000)
    x*=np.exp(-np.linspace(0,8,n))*(0.022 if k%2 else 0.012); m.add(np.stack([x*0.7,x],1),t)
m.add(bell(84,4,vol=0.14),16.2); m.add(bell(91,3.5,vol=0.07),16.9)
m.save(sys.argv[2],fade_out=1.0)
