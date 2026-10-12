import sys; sys.path.insert(0,sys.argv[1])
from sesler import *
m=Mix(5.6)
m.add(pluck(57,0.8,vol=0.08),0.15)
notes=[69,72,76,74,79,81]
for i,n in enumerate(notes): m.add(pluck(n,1.5,vol=0.11),0.78+i*0.2)
m.add(whoosh(1.2,vol=0.05),1.2)
m.add(pad([57,64,69,72,76],4.0,a=0.6,r=2.2,vol=0.14,bright=1800,seed=3),1.9)
m.add(pad([45],4.0,a=0.4,r=2.2,vol=0.10,bright=250,seed=5),1.9)
m.add(bell(88,3,vol=0.13),2.95)
for k,n in enumerate([93,96,100]): m.add(bell(n,2,vol=0.05),3.95+k*0.12)
m.save(sys.argv[2],fade_out=0.8)
