# Reels müziği: shots bölümü + logo kapanışı. python ses_reel.py tools_dir out.wav total shots_end n_shots seed
import sys; sys.path.insert(0,sys.argv[1])
from sesler import *
import numpy as np
out=sys.argv[2]; total=float(sys.argv[3]); send=float(sys.argv[4]); ns=int(sys.argv[5]); seed=int(sys.argv[6]) if len(sys.argv)>6 else 0
rng=np.random.default_rng(seed)
progs=[[[53,57,60,64],[52,55,59,62],[50,53,57,60,64],[48,52,55,59]],
       [[57,60,64,67],[53,57,60,64],[55,59,62,65],[52,55,59,64]],
       [[50,54,57,61],[47,50,54,57],[43,47,50,54],[45,49,52,57]]]
prog=progs[seed%len(progs)]
m=Mix(total)
step=send/ns
cuts=[i*step for i in range(ns)]
for i,t in enumerate(cuts):
    c=prog[i%len(prog)]
    m.add(pad(c,step+2.6,a=1.2,r=2.4,vol=0.12,bright=1300,seed=i+seed),t)
    m.add(pad([c[0]-12],step+2.2,a=0.8,r=2.0,vol=0.09,bright=260,seed=20+i),t)
    if t>0: m.add(whoosh(0.9,vol=0.035,seed=i),t-0.45)
    top=[76,79,74,77,72,76,79,84][i%8]
    m.add(pluck(top,2.2,vol=0.085),t+0.1); m.add(pluck(top-5,2.0,vol=0.05),t+0.1+step/2)
# logo kapanışı
L=send-0.1
m.add(pluck(57,0.8,vol=0.08),L+0.15)
for i,n in enumerate([69,72,76,74,79,81]): m.add(pluck(n,1.5,vol=0.10),L+0.78+i*0.2)
m.add(pad([57,64,69,72,76],max(1.5,total-(L+1.9)),a=0.6,r=1.8,vol=0.13,bright=1800,seed=3),L+1.9)
m.add(bell(88,3,vol=0.12),L+2.95)
for k,n in enumerate([93,96,100]): m.add(bell(n,2,vol=0.045),L+3.95+k*0.12)
m.save(out,fade_out=0.9)
