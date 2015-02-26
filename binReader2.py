import struct
import glob
import os
import time
import datetime
import numpy
import sys
from CoolProp import HumidAirProp, HumidAirProp

def msoft_to_linux_timestamp(msoft_ts):
    # Fix this. I am manually adjusting for some time zone error.
    # The value is stored by Msoft's System::DateTime::ToBinary.
    # You can run a program to get the value for 1970-01-01 0:0:0.
    linux_ts = (msoft_ts - 621355968000000000L) * 1.0E-07
    linux_ts = linux_ts + 7 * 60 * 60
    dt = datetime.datetime.fromtimestamp(linux_ts)
    return dt
    

def readString(f):
    st1 = struct.Struct('B')
    length, = st1.unpack(f.read(st1.size))
    st2 = struct.Struct('<%ds'%length)
    string, = st2.unpack(f.read(st2.size))
    return string

def readHeader(f):
    # the version string; another string; the number of data fields
    version,string2 = readString(f),readString(f)
    st1=struct.Struct("Bxxx")
    nfields, = st1.unpack(f.read(st1.size))
    # for each field: the channel; the name; the units
    fields = []
    for ifield in range(nfields):
        channel = readString(f)
        name = readString(f)
        unit = readString(f)
        fields += [(channel,name,unit)]
    # the (msoft) timestamp; the time step.
    st3=struct.Struct("Qd")
    msoft_timestamp, deltat = st3.unpack(f.read(st3.size))
    a_datetime = msoft_to_linux_timestamp(msoft_timestamp)
    return version,string2,nfields,fields,msoft_timestamp,a_datetime,deltat

def readRecord(f,nfields):
    st = struct.Struct('%dd'%nfields)
    record = st.unpack(f.read(st.size))
    return record

def ouch():
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

def readFile(f,setdtype=True,window_size=1,deltat_correction_factor=1.0):
    version,string2,nfields,fields,msoft_timestamp,a_datetime,deltat = readHeader(f)
    deltat = deltat * deltat_correction_factor
    records = []
    #for n in range(5):
    time_elapsed = 0
    epoch = datetime.datetime(1970,1,1)
    time_stamp = (a_datetime - epoch).total_seconds()
    while True:
        if window_size > 1:
            try:
                records_in_window = range(window_size) # list
                for i in range(window_size):
                    records_in_window[i] = readRecord(f,nfields) # tuple
                record = tuple(numpy.array(records_in_window).mean(axis=0).tolist())
                records += [(time_elapsed,time_stamp)+record]
                time_elapsed += deltat * window_size
                time_stamp += deltat * window_size
            except:
                break
        else:
            try:
                record = readRecord(f,nfields) # tuple
                records += [(time_elapsed,time_stamp)+record]
                time_elapsed += deltat * window_size
                time_stamp += deltat * window_size
            except:
                break
    nfields += 2
    fields = [('chdt','time_elapsed','s'),('cht','time_stamp','s')] + fields
    dtype = [(fieldname, 'f') for (channel,fieldname,unit) in fields]
    if setdtype:
        data = numpy.array(records,dtype=dtype)
        return version,string2,nfields,fields,msoft_timestamp,a_datetime,deltat,data
    else:
        data = numpy.array(records)
        return version,string2,nfields,fields,msoft_timestamp,a_datetime,deltat,data

def main(fname):
    with open(fname, 'rb') as f:
        version,string2,nfields,fields,msoft_timestamp,a_datetime,deltat,records = readFile(f)
        print fname
        print version
        print string2
        print nfields
        print fields
        print msoft_timestamp
        print a_datetime
        print deltat
        print records
        # Plot them instead!
        nrecords = len(records)
        time_array = a_datetime + numpy.arange(nrecords) * datetime.timedelta(seconds=deltat)
        print time_array
        import matplotlib.pyplot
        for i in range(nfields):
            data = records[:,i]
            # mask out of range
            if (fields[i][1].find('RH') == 0):
                # assume 0-100%
                data[data < 0] = numpy.nan
                data[data > 100] = numpy.nan
            elif (fields[i][1].find('T') == 0):
                # assume 0 deg C to 50 deg C
                data[data < 0] = numpy.nan
                data[data > 50] = numpy.nan
            matplotlib.pyplot.plot(time_array,records[:,i],label=fields[i][1])
        matplotlib.pyplot.ylim([0,50])
        matplotlib.pyplot.legend(loc='best')
        matplotlib.pyplot.show()
    return version,string2,nfields,fields,msoft_timestamp,a_datetime,deltat,records,time_array,data

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        fname = sys.argv[1]
    else:
        fname = '../roof_validation/copy/test1 2014-0526-1516-56.bin'
    version,string2,nfields,fields,msoft_timestamp,a_datetime,deltat,records,time_array,data=main(fname)
else:
    for fname in glob.glob('*.bin'):
        with open(fname,'rb') as f:
            pass

