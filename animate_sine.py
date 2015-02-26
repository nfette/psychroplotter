# -*- coding: utf-8 -*-
"""
Spyder Editor

This temporary script file is located here:
C:\Users\nfette\.spyder2\.temp.py
"""

import time
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

x = []
y = []
z = []

fig = plt.figure()
ax = plt.axes(xlim=(0, 50), ylim=(-1, 1))
#ax = plt.axes()

a0, = ax.plot(x, y)
a1, = ax.plot(x, z)

def funco(framenum):
    t = time.clock()
    x.append(t)
    y.append(np.sin(t))
    z.append(np.cos(t))
    a0.set_data(x,y)
    a1.set_data(x,z)
    ax.relim()

anim = animation.FuncAnimation(fig,funco,interval=100)

plt.show()
