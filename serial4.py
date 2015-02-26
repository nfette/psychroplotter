import serial
from threading import Thread
import time
from datetime import tzinfo, timedelta, datetime

last_received = ''
mabuffer = ''

def receiving1(ser):
    global last_received
    global mabuffer

    while True:
        # last_received = ser.readline()
        mabuffer += ser.read(ser.inWaiting())
        if '\n' in mabuffer:
            last_received, mabuffer = mabuffer.split('\n')[-2:]

def receiving2(ser):
    global last_received
    global mabuffer

    time.sleep(1)
    print ser
    print ser.isOpen()
    ser.open()
    print ser.isOpen()
    print ser.read(ser.inWaiting())
    ser.write("T%.2f\n"%time.time())
    while True:
        time.sleep(0.5)
        mabuffer = mabuffer + ser.read(ser.inWaiting())
        if '\n' in mabuffer:
            lines = mabuffer.split('\n') # Guaranteed to have at least 2 entries
            last_received = lines[-2]
            #If the Arduino sends lots of empty lines, you'll lose the
            #last filled line, so you could make the above statement conditional
            #like so: if lines[-2]: last_received = lines[-2]
            mabuffer = lines[-1]

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
        while True:
            time.sleep(0.1)
            a = ser.readline()
            if len(a) > 0:
                last_received = a.strip()
                print 'in <',last_received
                # It requests sync
                s="T%.2f"%time.time()
                ser.write(s)
                print 'out>',s
                break
        while True:
            time.sleep(0.1)
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
                timestr=last_received.split(',\t')[0]
                try:
                    #t = datetime.fromtimestamp(float(timestr),utctz)
                    #print '    ',t
                    #t.timetz
                    #print '    ',t.astimezone(localtz)
                    pass
                except:
                    pass
                
        #Thread(target=receiving1, args=(ser,)).start()
        #t=Thread(target=receiving2, args=(ser,))
        #t.start()
        
