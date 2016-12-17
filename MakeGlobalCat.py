#!/usr/bin/env python

#This speeds up the process of fetching seismic data: make a global catalog of events to access. This takes a very long time to run,
#but creates a file of up-to-date earthquake information that can be accessed by the trace fetch program

from obspy.fdsn import Client
from obspy import UTCDateTime
import datetime 

today = datetime.date.today()

client = Client('IRIS')
t1 = UTCDateTime(1970,1,1)
t2 = UTCDateTime(today.year,today.month,today.day)
client.get_events(starttime=t1,endtime=t2,filename='global_quake_cat.dat',minmagnitude=5.0) #all global events in the catalog



#write the parsed version of this file,ready to manipulate.
outfile = open('globalquake_parsed.dat','w')
infile = open('global_quake_cat.dat','r')
lines = infile.readlines()
infile.close()
depths =[]
lats =[]
lons = []
times = []
mags = []
for i, j in enumerate(lines):
	if j.strip() == '<depth>':
		depth = float(lines[i+1].strip().split('>')[1].split('<')[0])/1000.0
		depths.append(depth)
	if j.strip() == '<latitude>':
		lat = float(lines[i+1].strip().split('>')[1].split('<')[0])
		lats.append(lat)
	if j.strip() == '<longitude>':
		lon = float(lines[i+1].strip().split('>')[1].split('<')[0])
		lons.append(lon)
	if j.strip() == '<time>':
		time = lines[i+1].strip().split('>')[1].split('<')[0]
		times.append(time)
	if j.strip() == '<mag>':
		mag = lines[i+1].strip().split('>')[1].split('<')[0]
		mags.append(mag)



for element in zip(times,lats,lons,depths,mags):
	outfile.write('%s,%s,%s,%s,%s\n' %(element[0],element[1],element[2],element[3],element[4]))

outfile.close()

print 'UPDATED CATALOG!'