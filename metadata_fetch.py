#!/usr/bin/env python

##################################################################
#Base class of the data fetching component of this program. Uses 
#Obspy functions to fetch station and event metadata ready to be passed
#to the fetching class
###################################################################

from obspy.taup.taup import getTravelTimes
from obspy import read
from obspy.iris import Client as iclient
from obspy.sac import SacIO
from obspy.fdsn import Client
from obspy import UTCDateTime
from obspy.core.util import locations2degrees
import os
import glob


class MetaFetch:
	def __init__(self,network=None,station=None,starttime=None,endtime=None,level='channel',channel='BH?',minlongitude=None,maxlongitude=None,minlatitude=None,maxlatitude=None,savedirectory=None):

		#initiase all the necessary variables

		self.network = network
		self.station = station
		self.starttime = starttime
		self.endtime = endtime
		self.minlongitude = minlongitude
		self.minlatitude = minlatitude
		self.maxlongitude = maxlongitude
		self.maxlatitude = maxlatitude
		self.level = level
		self.channel = channel
		self.savedirectory = savedirectory

		error = self.raiseinputerrors()
		if error is not None:
			print 'ERROR on input'

	def fetchinventory(self):
		'''Get an obspy inventory containing all the station information'''

		self.client = Client("IRIS") #eventuually change so that we can get data from elsewhere
		self.Iclient = iclient()

		if self.station != 'None':
			self.inventory = self.client.get_stations(network=self.network,station=self.station,level='channel',channel=self.channel,starttime=self.starttime,endtime=self.endtime,minlongitude=self.minlongitude,minlatitude=self.minlatitude,maxlongitude=self.maxlongitude,maxlatitude=self.maxlatitude)
		else:
			self.inventory = self.client.get_stations(network=self.network,station=None,level='channel',channel=self.channel,starttime=self.starttime,endtime=self.endtime,minlongitude=self.minlongitude,minlatitude=self.minlatitude,maxlongitude=self.maxlongitude,maxlatitude=self.maxlatitude)


	def printinventory(self):
		'''Print out useful metadata about the requested networks and/or channel'''

		print '########################################'
		print 'The following information was requested:'

		for network in self.inventory.networks:
			for station in network.stations:
				print '########################################'
				print station 

	def raiseinputerrors(self):
		'''If incorrect input is entered, raise errors'''

		if self.network == None:
			error = 'A valid network code is needed'
		if self.starttime == None:
			error = 'A valid starttime in UTCDateTime format is needed'
		if self.endtime == None:
			error = 'A valid endtime in UTCDateTime format is needed'
		else:
			error = None


	def extract_stations(self,writefile=True):
		'''Make a dictionary containing station,latitude and longitude for that network. Also output a file containing
	    
	    station lon lat depth 

	    In its rows
		'''

		networks = {}

		for network in self.inventory.networks: #should only be one network

			information = str(network).split('\n')[0]
			networks[information] = {}
			for station in network.stations:
				stationname = str(station).split('\n')[0].split(' ')[1].strip()
				stationlat = station.latitude
				stationlon = station.longitude
				stationelev = station.elevation

				channels = []
				azimuths = []
				dips = []
				for channel in station.channels:
					azimuths.append(channel.azimuth)
					dips.append(channel.dip)
					code = str(channel.code)

					#sometimes the code will appear more than once, in which case the data will be downloaded multiple times. Stop this. 
					
					if code not in channels:
						channels.append(code)

				networks[information][stationname] = [stationlat,stationlon,stationelev,channels,azimuths,dips]

	        #write the information to a file
			if writefile:
				outfilename = information.replace(" ",'_')+'.dat'
				outfilename = outfilename.replace(')','')
				outfilename = outfilename.replace('(','_')
				outfilename = outfilename.replace('-','_')
				outfilename = outfilename.replace('/','_')
				outfile = open(outfilename,'w')
				for station in networks[information]:
					outfile.write('%s %s %s %s\n' %(station,networks[information][station][1],networks[information][station][0],networks[information][station][2]))
				outfile.close()
				#should probably move this file to the save location - contains useful information if one wants to make a plot of the station distribution

		if (self.savedirectory) and (os.getcwd() != self.savedirectory): #moves the metadata file to the location speficied by the user
			os.system('mv %s %s' %(outfilename,self.savedirectory))

		return networks

#testing
if __name__ == '__main__':
	starttime=UTCDateTime("2013-11-01")
	endtime=UTCDateTime("2013-12-25") 
	metadata = MetaFetch(network='TA',starttime=starttime,endtime=endtime)
	metadata.fetchinventory()
	metadata.printinventory()
	networks = metadata.extract_stations()
	print networks




