#!/usr/bin/env python
#Download traces specified in the GUI

from GMT_map import convertstringtolist
from Trace_Fetch import *
import os 
import sys


class TraceDownload:
	def __init__(self,network,station,channel,starttime,endtime,eventbounding,stationbounding,magnitides,radii,traceduration,response,savingdirectory,homedirectory,samplerate,spectroplot):
		
		'''Get all of the input data into a format accepted by the trace_fetch_v2 program, which actually does the downloading'''

        
		self.network = network
		self.station = station
		self.channel = channel

		if self.channel == 'None':
			self.channel = None

		self.starttime = UTCDateTime(year=int(starttime[0]),month=int(starttime[1]),day=int(starttime[2]),hour=int(starttime[3]),minute=int(starttime[4]),second=int(starttime[5]),microsecond=int(starttime[6]))
		self.endtime = UTCDateTime(year=int(endtime[0]),month=int(endtime[1]),day=int(endtime[2]),hour=int(endtime[3]),minute=int(endtime[4]),second=int(endtime[5]),microsecond=int(endtime[6]))
		self.mineventlon = eventbounding[0]
		self.maxeventlon = eventbounding[1]
		self.mineventlat = eventbounding[2]
		self.maxeventlat = eventbounding[3]
		self.minstationlon = stationbounding[0]
		self.maxstationlon = stationbounding[1]
		self.minstationlat = stationbounding[2]
		self.maxstationlat = stationbounding[3] 
		self.minmag = magnitudes[0]
		self.maxmag = magnitudes[1]
		self.minrad = radii[0]
		self.maxrad = radii[1]
		self.samplerate = samplerate
		self.spectroplot = spectroplot

		if self.samplerate == 'None':
			self.samplerate = None
		else:
			self.samplerate == float(self.samplerate)

		self.traceduration = int(traceduration) #trace duraction must be an integer number of seconds 
		self.responsetype = response
		if (self.responsetype == 'DISP') or (self.responsetype == 'VEL') or (self.responsetype == 'ACC'):
			self.response = True
		else:
			self.response = False

		self.savepath = savingdirectory
		self.homepath = homedirectory


	def writedata(self):
		'''Get the event information using TraceFetch and write it in SAC format'''

		currentdir = os.getcwd()

		os.chdir(self.savepath)
		print '########################\nWriting SAC files in %s\n########################\n' %(self.savepath)
		data = TraceFetch(network=self.network,station=self.station,starttime=self.starttime,endtime=self.endtime,channel=self.channel,minmagnitude=self.minmag,maxmagnitude=self.maxmag,minradius=self.minrad,maxradius=self.maxrad,minlongitude=self.minstationlon,maxlongitude=self.maxstationlon,minlatitude=self.minstationlat,maxlatitude=self.maxstationlat,mineventlon=self.mineventlon,maxeventlon=self.maxeventlon,mineventlat=self.mineventlat,maxeventlat=self.maxeventlat,traceduration=self.traceduration,includearrivals=True,includeresponse=self.response,responsetype=self.responsetype,homedirectory=self.homepath,savedirectory=self.savepath,resample=self.samplerate,spectroplot=self.spectroplot)
		data.getquakes()
		os.chdir(currentdir)

if __name__ == '__main__':
	#This is probably a poor way of running the program, but all of the data should be input as arguments. The script is run
	#like this because it needs 64 bit Anaconda python to work, but is called from the GUI, which is running in 32 bit python

	network = sys.argv[1]
	station= sys.argv[2]
	channel = sys.argv[3]
	starttime = convertstringtolist(sys.argv[4])
	endtime = convertstringtolist(sys.argv[5])
	stationbounding = convertstringtolist(sys.argv[6])
	eventbounding = convertstringtolist(sys.argv[7])
	magnitudes = convertstringtolist(sys.argv[8])
	radii = convertstringtolist(sys.argv[9])
	traceduration = sys.argv[10]
	responsetype = sys.argv[11]
	savepath = sys.argv[12]
	currentdir = sys.argv[13]
	samplerate = sys.argv[14]
	spectroplot = sys.argv[15]
  

    #turn on for debugging 
	#print network,station,channel,starttime,endtime,stationbounding,eventbounding,magnitudes,radii,traceduration,responsetype,savepath,currentdir,samplerate,spectroplot

	DATA = TraceDownload(network,station,channel,starttime,endtime,eventbounding,stationbounding,magnitudes,radii,traceduration,responsetype,savepath,currentdir,samplerate,spectroplot)
	DATA.writedata()