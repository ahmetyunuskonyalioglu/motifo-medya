import sys; sys.path.insert(0,sys.argv[1])
from sesler import *
m=Mix(8.5)
m.add(pencil(1.9,vol=0.06),0.15)
m.add(pad([50,57,62],8.0,a=1.2,r=3,vol=0.10,bright=900),0.3)       # D kök
m.add(pad([62,66,69,76],6.6,a=0.5,r=3.5,vol=0.16,bright=2200,seed=4),1.9)  # Dadd9 açılış
m.add(whoosh(0.7,vol=0.05),1.7)
m.add(bell(81,4.5,vol=0.16),2.45)   # hilal belirirken
m.add(bell(86,4.5,vol=0.10),3.45)   # logo
m.save(sys.argv[2])
