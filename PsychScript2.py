import numpy, matplotlib
from CoolProp.HumidAirProp import HAProps
from CoolProp.Plots.Plots import InlineLabel 
import numpy as np
import serial
from threading import Thread
import time
from datetime import tzinfo, timedelta, datetime

####################
# Setup for serial #
####################

last_received = ''
mabuffer = ''

# A class building tzinfo objects for fixed-offset time zones.
# Note that FixedOffset(0, "UTC") is a different way to build a
# UTC tzinfo object.
ZERO = timedelta(0)
class FixedOffset(tzinfo):
    """Fixed offset in timedelta (east from UTC)."""

    def __init__(self, offset, name):
        self.__offset = offset
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO
        
def serialLoop(ser,fil):
    global last_received, mabuffer
    try:
        a = ser.readline()
    except serial.SerialException as e:
        print e
        print ser
        if ser.isOpen():
            ser.close()
            print ser            
        try:
            ser.open()
            print ser
        except serial.SerialException as e2:
            print e2
            time.sleep(10)
    if len(a) > 0:
        last_received = a.strip()
        print 'in <',last_received
        if (last_received.find('\x07') > -1):
            # It requests sync
            s="T%.2f"%time.time()
            ser.write(s)
            print 'out>',s
            last_received=last_received[1:]
        print >>fil, last_received
        fil.flush()
        #t = datetime.strptime(last_received,'%Y-%m-%dT%H:%M:%S')
        #t = datetime.utcfromtimestamp(float(last_received))
        tokens = last_received.split(',\t')
        i = 0
        timestr=tokens[i]
        datime = long(timestr)
        i += 1
        status = []
        relhum = []
        temp = []
        try:
            for j in range(5):
                status.append(int(tokens[i])); i += 1
                relhum.append(float(tokens[i])); i += 1
                temp.append(float(tokens[i])); i += 1
        except:
            print tokens, i
            #raise
        return (datime, status, relhum, temp)
    else:
        print "."
        return

######################
# Setup for plotting #
######################
p = 101.325
Tdb = numpy.linspace(-10,40,100)+273.15

#Make the figure and the axes
fig=matplotlib.pyplot.figure(figsize=(10,8))
ax=fig.add_axes((0.1,0.1,0.85,0.85))

fig2=matplotlib.pyplot.figure(figsize=(10,8))
ax2=fig2.add_axes((0.1,0.1,0.85,0.85))
ax2.set_xlim((-1,10))
ax2.set_ylim((0,50))

# Saturation line
w = [HAProps('W','T',T,'P',p,'R',1.0) for T in Tdb]
ax.plot(Tdb-273.15,w,lw=2)

# Humidity lines
RHValues = [0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
for RH in RHValues:
    w = [HAProps('W','T',T,'P',p,'R',RH) for T in Tdb]
    ax.plot(Tdb-273.15,w,'b--',lw=1)

# Enthalpy lines
for H in [-20, -10, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90]:
    #Line goes from saturation to zero humidity ratio for this enthalpy
    T1 = HAProps('T','H',H,'P',p,'R',1.0)-273.15
    T0 = HAProps('T','H',H,'P',p,'R',0.0)-273.15
    w1 = HAProps('W','H',H,'P',p,'R',1.0)
    w0 = HAProps('W','H',H,'P',p,'R',0.0)
    ax.plot(numpy.r_[T1,T0],numpy.r_[w1,w0],'r--',lw=1)

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

t = 0
x = 25
y = 0.005

a,b=[[]]*5,[[]]*5
tt=[-1,0]
xx=[[]]*5
yy=[[]]*5
for j in range(5):
    a[j], = ax.plot(x, y,'o')
    xx[j] = [25.0,25.0]
    yy[j] = [0.005,0.005]
    b[j], = ax2.plot(tt, xx[j],'-')

def funco(framenum,ser,fil):
    global t,a,b,x,y,tt,xx,yy
    print framenum,
    t = time.clock()
    try:
        (datime, status, relhum, temp) = serialLoop(ser,fil)
        #x = 25 + 10 * np.sin(t)
        #y = HAProps('W','T',x+273.15,'P',p,'R',r1)
        #z = HAProps('W','T',x+273.15,'P',p,'R',r2)
        tt.append(t)
        for j in range(5):
            x = temp[j]
            y = HAProps('W','T',x+273.15,'P',p,'R',relhum[j]*0.01)
            xx[j].append(x)
            yy[j].append(y)
            a[j].set_data(x,y)
    except KeyboardInterrupt:
        print('exciting!')
    except TypeError:
        pass

def funca(framenum):
    global a,b,x,y,tt,xx,yy
    t = time.clock()
    for j in range(5):
        # Problem with this is that animation.FuncAnimation
        # only acts on one figure, but we have here a second figure.
        b[j].set_data(tt,xx[j])
    #ax2.relim()
    #ax2.autoscale_view()
    ax2.set_xlim([0,t])
    
print "hello still here"

if __name__ ==  '__main__':
    localtz = FixedOffset(timedelta(seconds=-time.timezone),time.tzname[0])
    utctz = FixedOffset(timedelta(0),'UTC')

    starttime = datetime.now(localtz)
    filname = 'serial4_out_%s.csv'%starttime.strftime('%Y%m%dT%H%M%S')
    with serial.Serial(port='com4',
                       baudrate=9600,
                       timeout=0.1,
                       writeTimeout=0.1) \
            as ser, \
            open(filname,'w') \
            as fil:
                anim = animation.FuncAnimation(fig,funco,
                                               fargs=(ser,fil),interval=400)
                anim2 = animation.FuncAnimation(fig2,funca,
                                               interval=100)
                matplotlib.pyplot.show()
