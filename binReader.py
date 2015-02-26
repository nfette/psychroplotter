import struct
import glob
import os
import time
import datetime

with open('timestamps.csv','w') as fout:
    for fname in glob.glob('*.bin'):
    #fname='sample_16field_50Hz 2014-0517-1206-33.bin'
        print fname
        print >>fout, fname, ',',
        print >>fout, os.stat(fname).st_ctime, ',',
        with open(fname,'rb') as f:
            # read a string looks like version number
            fmt1 = 'B'
            st1 = struct.Struct(fmt1)
            i1 = st1.unpack(f.read(st1.size))[0]
            print 'len=',i1
            fmt2 = '<%ds'%i1
            st2 = struct.Struct(fmt2)
            s2 = st2.unpack(f.read(st2.size))[0]
            print 'version=',s2

            # looks like another string
            fmt3 = 'B'
            st3 = struct.Struct(fmt3)
            i3 = st3.unpack(f.read(st3.size))[0]
            print 'len=',i3
            fmt4 = '<%ds'%i3
            st4 = struct.Struct(fmt4)
            s4 = st4.unpack(f.read(st4.size))[0]
            print 'unknown=',s4

            # read the number of data fields
            fmt5 = '4B'
            st5 = struct.Struct(fmt5)
            i5 = st5.unpack(f.read(st5.size))[0]
            print '#channels=',i5
            
            for chan in range(i5):
                fmt6 = 'B'
                st6 = struct.Struct(fmt6)
                i6 = st6.unpack(f.read(st6.size))[0]
                fmt7 = '<%ds'%i6
                st7 = struct.Struct(fmt7)
                s7 = st7.unpack(f.read(st7.size))[0]
                print 'channel=',s7,
                fmt6 = 'B'
                st6 = struct.Struct(fmt6)
                i6 = st6.unpack(f.read(st6.size))[0]
                fmt7 = '<%ds'%i6
                st7 = struct.Struct(fmt7)
                s7 = st7.unpack(f.read(st7.size))[0]
                print ' name=',s7,
                fmt6 = 'B'
                st6 = struct.Struct(fmt6)
                i6 = st6.unpack(f.read(st6.size))[0]
                fmt7 = '<%ds'%i6
                st7 = struct.Struct(fmt7)
                s7 = st7.unpack(f.read(st7.size))[0]
                print ' unit=',s7

            fmt12 = 'Q'
            #fmt12 = '2L'
            st12 = struct.Struct(fmt12)
            d12 = st12.unpack(f.read(st12.size))
            print 'timestamp = ', d12
            print >>fout, d12[0], ',',
            # Fix this. I am manually adjusting for some time zone error.
            # The value is stored by Msoft's System::DateTime::ToBinary.
            # You can run a program to get the value for 1970-01-01 0:0:0.
            ts = (d12[0] - 621355968000000000L) * 1.0E-07
            ts = ts + 7 * 60 * 60
            dt = datetime.datetime.fromtimestamp(ts)
            #print >>fout, ts, ',', dt.isoformat()
            #print >>fout, ts, ',', dt.strftime('%Y-%m-%d %H:%M:%S.%f')
            print >>fout, ts, ',', dt.strftime('%Y-%m-%d %H:%M:%S')
            #print >>fout, d12[0], ',', d12[1]
            
            fmt13 = '<d'
            st13 = struct.Struct(fmt13)
            d13 = st13.unpack(f.read(st13.size))[0]
            print 'deltat = ', d13, 's'

            fmt = '<%dd'%i5
            st = struct.Struct(fmt)
            #while True:
            for row  in range(1):
                data = st.unpack(f.read(st.size))
                print data
            
    
        
        
