#!/usr/bin/env python

##################################################################
#Class used to assimilate data input by the user and to create a GMT 
#map of the chosen network/station distribution
###################################################################

from Trace_Fetch import *
import os 
import sys


class Mapcreate:
	def __init__(self,network,station,channel,starttime,endtime,eventbounding,stationbounding,magnitudes,radii):
		'''initialise all the quake variables input from the user form'''

		self.network = network
		self.station = station
		self.channel = channel
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

	def getdata(self):
		'''Get the event information using TraceFetch. May take a long time. Should work out why this is'''

		homedir = os.getcwd()

		data = TraceFetch(network=self.network,station=self.station,starttime=self.starttime,endtime=self.endtime,channel=self.channel,minmagnitude=self.minmag,maxmagnitude=self.maxmag,minradius=self.minrad,maxradius=self.maxrad,minlongitude=self.minstationlon,maxlongitude=self.maxstationlon,minlatitude=self.minstationlat,maxlatitude=self.maxstationlat,mineventlon=self.mineventlon,maxeventlon=self.maxeventlon,mineventlat=self.mineventlat,maxeventlat=self.maxeventlat,homedirectory=homedir)
		allquakes, stationslonlat = data.getquakesformap() #should contain all the information needed to plot a map
		return allquakes, stationslonlat

	def plotmap(self):
		'''Plots the GMT map by calling a shell script'''

		quakes, stations = self.getdata()
		
		if quakes == [None]:
			print 'Warning! No quake data returned from search'

			#write tempery files containing all the station and event longitude and latitude information, ready to be plotted
		stationsfile = open('tmp_plotfile_stations.dat','w')
		for entry in stations:
			stationsfile.write('%s %s\n' %(entry[2],entry[3]))
		stationsfile.close()

		eventsfile = open('tmp_plotfile_events.dat','w')
		uniquelons = []
		uniquelats = []
		for entry in quakes:
			for event in entry:
				lon = event[1]
				lat = event[2]
				if (lon not in uniquelons) and (lat not in uniquelats):
					eventsfile.write('%s %s %s\n' %(lon,lat,event[4]))
					uniquelats.append(lat)
					uniquelons.append(lon)
		eventsfile.close()

		os.system('./Map_Maker.sh') #makes the map 

		print '###############\nCreated map\n###############'

		#clean up
		os.system('rm tmp_plotfile_events.dat')
		os.system('rm tmp_plotfile_stations.dat')
 

def convertstringtolist(inputstring):
	'''deals with lists that have been accidentally converted into strings'''

	comps = inputstring.split(',')
	newlist = []
	for i in range(len(comps)):
		if i == 0:
			element = comps[i][1:]
			if (element != 'None') and (len(element) > 0):
				element = float(element)
			else:
				element = None
			newlist.append(element)
		elif i == len(comps)-1:
			element = comps[i][:-1]
			if (element != 'None') and (len(element) > 0):
				element = float(element)
			else:
				element = None
			newlist.append(element)
		elif i > 0:
			element = comps[i]
			if (element != 'None') and (len(element) > 0):
				element = float(element)
			else:
				element = None
			newlist.append(element)
	return newlist


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

	DATA = Mapcreate(network,station,channel,starttime,endtime,eventbounding,stationbounding,magnitudes,radii)
	DATA.plotmap()


