
import numpy, matplotlib
from CoolProp.HumidAirProp import HAProps
from CoolProp.Plots.Plots import InlineLabel 
import numpy as np

p = 101.325
Tdb = numpy.linspace(-10,40,100)+273.15

#Make the figure and the axes
fig=matplotlib.pyplot.figure(figsize=(10,8))
ax=fig.add_axes((0.1,0.1,0.85,0.85))

# Saturation line
w = [HAProps('W','T',T,'P',p,'R',1.0) for T in Tdb]
ax.plot(Tdb-273.15,w,lw=2)

# Humidity lines
RHValues = [0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
for RH in RHValues:
    w = [HAProps('W','T',T,'P',p,'R',RH) for T in Tdb]
    ax.plot(Tdb-273.15,w,'r',lw=1)

# Enthalpy lines
for H in [-20, -10, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90]:
    #Line goes from saturation to zero humidity ratio for this enthalpy
    T1 = HAProps('T','H',H,'P',p,'R',1.0)-273.15
    T0 = HAProps('T','H',H,'P',p,'R',0.0)-273.15
    w1 = HAProps('W','H',H,'P',p,'R',1.0)
    w0 = HAProps('W','H',H,'P',p,'R',0.0)
    ax.plot(numpy.r_[T1,T0],numpy.r_[w1,w0],'r',lw=1)

ax.set_xlim(Tdb[0]-273.15,Tdb[-1]-273.15)
ax.set_ylim(0,0.02)
ax.set_xlabel(r"Dry bulb temperature [$^{\circ}$C]")
ax.set_ylabel(r"Humidity ratio ($m_{water}/m_{dry\ air}$) [-]")

xv = Tdb #[K]
for RH in [0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    yv = [HAProps('W','T',T,'P',p,'R',RH) for T in Tdb]
    #y = HAProps('W','P',p,'H',65.000000,'R',RH)
    y = HAProps('W','P',p,'H',40,'R',RH)
    T_K,w,rot = InlineLabel(xv, yv, y=y, axis = ax)
    string = r'$\phi$='+str(RH*100)+'%'
    bbox_opts = dict(boxstyle='square,pad=0.0',fc='white',ec='None',alpha = 0.5)
    ax.text(T_K-273.15,w,string,rotation = rot,ha ='center',va='center',bbox=bbox_opts)

import matplotlib.animation as animation
import time

x = 25
y = 0.05
z = 0.010
r1 = 0.10
r2 = 0.50

a0, = ax.plot(x, y,'o')
a1, = ax.plot(x, z,'o')

def funco(framenum):
    t = time.clock()
    x = 25 + 10 * np.sin(t)
    y = HAProps('W','T',x+273.15,'P',p,'R',r1)
    z = HAProps('W','T',x+273.15,'P',p,'R',r2)
    a0.set_data(x,y)
    a1.set_data(x,z)

anim = animation.FuncAnimation(fig,funco,interval=100)

matplotlib.pyplot.show()
