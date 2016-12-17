#!/usr/bin/env python

##########################################
#Class for fetching station traces. Uses prebuilt OBSPY classes to 
#obtain seismograms for an entire network or station choice, within specified 
#coordinartes or within a given set of radii. Also supports removal of
#instrument response to displacement,velocity or acceleration.
##########################################

from metadata_fetch import *
from extract_quakes_interest import * #import function that looks at global quake file and extracts events
import os
#from obspy.taup import TauPyModel

class TraceFetch(MetaFetch):

	def __init__(self,network=None,station=None,starttime=None,endtime=None,level='channel',channel=None,minlongitude=None,maxlongitude=None,minlatitude=None,maxlatitude=None,mineventlon=None,maxeventlon=None,mineventlat=None,maxeventlat=None,minmagnitude=None,maxmagnitude=None,minradius=None,maxradius=None,traceduration=None,includearrivals=True,includeresponse=False,responsetype=False,homedirectory=None,savedirectory=None,resample=None,spectroplot=None):
		MetaFetch.__init__(self,network,station,starttime,endtime,level,channel,minlongitude,maxlongitude,minlatitude,maxlatitude,savedirectory)

		#These variables will have True or False values depending on input
		self.includearrivals = includearrivals
		self.includeresponse = includeresponse
		self.responsetype = responsetype
		self.homedirectory = homedirectory
		self.resample = resample
		self.spectroplot = spectroplot

		#minmagnitude should be high for long collection times to avoid massive delays in data collection 
		self.minmagnitude = minmagnitude
		self.maxmagnitude = maxmagnitude

		if self.minmagnitude == None:
			self.minmagnitude = 0.0 #Note that the global quake catalog only contains event of M3.0 and above
		if self.maxmagnitude == None:
			self.maxmagnitude = 11.0

		#minimum and maximum radii should be in degrees
		self.maxradius = maxradius
		self.minradius = minradius

		if self.minradius == None:
			self.minradius = 0.0
		if self.maxradius == None:
			self.maxradius = 360.0 

		self.mineventlon = mineventlon
		self.maxeventlon = maxeventlon

		if self.mineventlon == None:
			self.mineventlon = -180.0
		if self.maxeventlon == None:
			self.maxeventlon = 180.0 

		self.mineventlat = mineventlat
		self.maxeventlat = maxeventlat

		if self.mineventlat == None:
			self.mineventlat = -90.0
		if self.maxeventlat == None:
			self.maxeventlat = 90.0 

		self.traceduration = traceduration #should return an error if this is less then 0

		self.dm = 1 #marker for the number of networks

	def getazimuths(self,stationlat,stationlon,quakelat,quakelon):
		'''Get the azimuth and backazimuth of the event/station pair'''

		dist = locations2degrees(quakelat,quakelon,stationlat,stationlon) #find distance from the quake to the station

		arcs = self.Iclient.distaz(stalat=stationlat,stalon=stationlon,evtlat=quakelat,evtlon=quakelon)
		azimuth = arcs['backazimuth']
		backazimuth = arcs['azimuth']

		return dist, azimuth, backazimuth

	def gettraveltimes(self,dist,quakedepth,quaketime,model='iasp91'):
		'''Get the P, S, SKS and SKKS arrival time estimates (if they exist). Add more arrivals if desired'''

		#timemodel = TauPyModel(model=model)

		#arrivals = timemodel.get_travel_times(distance_in_degree=dist,source_depth_in_km=quakedepth,phase_list=['P','S','SKS','SKKS'])
		#print arrivals

		traveltimes = getTravelTimes(dist,quakedepth, model=model)

		for element in traveltimes:
			phaseinfo = element['phase_name']
			if phaseinfo[:3] == 'SKS':
				SKStime = element['time']
			if phaseinfo == 'P':
				Ptime = element['time']
			if phaseinfo == 'S':
				Stime = element['time']
			if phaseinfo[:-2] == 'SKKS':
				SKKStime = element['time']

		starttrace = quaketime

        #if these various arrivals exist, find their associated times in the seismogram
		try:
			SKSarrival = quaketime + SKStime
		except:
			SKSarrival = UTCDateTime(0.0)

		try:
			Parrival = quaketime + Ptime
		except:
			Parrival = UTCDateTime(0.0)

		try:
			Sarrival = quaketime + Stime
		except:
			Sarrival = UTCDateTime(0.0)

		try:
			SKKSarrival = quaketime + SKKStime
		except:
			SKKSarrival = UTCDateTime(0.0)


		endtrace = starttrace + self.traceduration

		Relative_Sarrival = Sarrival - starttrace
		Relative_Parrival = Parrival - starttrace
		Relative_SKSarrival = SKSarrival - starttrace
		Relative_SKKSarrival = SKKSarrival - starttrace

		return Relative_Parrival,Relative_Sarrival,Relative_SKKSarrival,Relative_SKSarrival,starttrace,endtrace

	def constructSACfilename(self,quaketimestr,stationname,networkname,channel):
		'''Constucts a SAC file name in RDSEED format ("yyyy.ddd.hh.mm.ss.ffff.NN.SSSSS.LL.CCC.Q.SAC") from input metadata'''

		starttime = UTCDateTime(quaketimestr)

		year=int(starttime.year)
		day=int(starttime.julday)
		hour=int(starttime.hour)
		minute=int(starttime.minute)
		second=int(starttime.second)
		microsecond=int(starttime.microsecond)

		network = networkname.strip()
		station = stationname.strip()
		comp = channel.strip()

		filename = '%04d.%03d.%02d.%02d.%02d.%04d.%s.%s..%s.M.SAC' %(year,day,hour,minute,second,microsecond,network,station,comp)

		return filename

	def getcomptraces(self,quaketimestr,starttrace,endtrace,networkname,stationname,stlat,stlon,channels,azimuths,dips,stationdepth,eventlat,eventlon,az,baz,mag,dist,eventdepth,P,S,SKS,SKKS,response=False,responsetype=False):
		'''Download the traces and append vital information to the SAC header'''

		if len(channels) != 3:
			print 'ALERT: Three component data not requested. Seismofetch will try to find %s' %channels 

		j=0

		#print channels

		for channel in channels:
			azimuth = float(azimuths[j])
			dip = float(abs(dips[j]))

			j += 1

			#Put in to ensure that the naming convention is correct for onshore data.
			#in the case of offshore data, the components will be labelled ?H1/?H2, so this will be skipped anyway 

			channelname = channel.strip()

			if dip == 0.0:
				dip = 90.0
			elif dip == 90.0:
				dip = 0.0

			#For onshore data, this convention appears to be typical
			if channelname == 'BHZ':
				dip = 0.0
				azimuth = 0.0
			elif channelname == 'BHE':
				dip = 90.0
				azimuth = 90.0
			elif channelname == 'BHN':
				dip = 90.0
				azimuth = 0.0

			#set the sacfile name. Currently it will only output in RDSEED format, but in future we should make various options 
			filename = self.constructSACfilename(quaketimestr,stationname,networkname,channel)

			#get the data. This process could be speeded up by using obspy's 'get waveforms bulk', but this would require major changes to the code
			data = self.client.get_waveforms(networkname,stationname,"??",channel,starttrace,endtrace,attach_response=response)
			
			print data 

			#for some reason, some channels may have two locations - perhaps if there is more than one instrument on site (i.e. multiple locations) 
			#Alert the user to this, and for simplicity choose the data with the highest sampling rate. If this is not appropriate, the below should be
			#edited 	

			########################################################
			datalength = len(data)

			if datalength > 1:

				maxsamplingrate = 0
				tracechoice = 0
				k = 0 
				for trace in data:
					tracesamplingrate = trace.stats.sampling_rate

					if tracesamplingrate > maxsamplingrate:
						maxsamplingrate = tracesamplingrate
						tracechoice = k

					k += 1
				print '\nALERT: The site %s has %g instruments with channel %s. Choosing instrument with sampling rate %g [highest available]\n' %(stationname,datalength,channel,maxsamplingrate)
				data = data[tracechoice]
			########################################################

			#add resampling option 
			if self.resample:
				data.resample(float(self.resample))

			#plot spectrograms of each component
			if self.spectroplot == 'Yes':
				data.spectrogram(fmt='eps',outfile=filename+'_spectrogram.eps',title=filename,show=False)

			#plot the data too - probably don't need this, but its a useful obspy feature
			#data.plot()

			#remove the instrument response, if requested
			if response and responsetype:
				data = data.remove_response(responsetype)

			#write SAC file 
			data.write(filename,format='SAC')
			
			print filename
			
			with open(filename,'rb+') as tr: 

			   comp = SacIO(tr) 

			   #set the SAC headers that have not been filled in. At some point may
			   #also want to enter a value for station to event distance in km

			   comp.SetHvalue('EVLA',float(eventlat))
			   comp.SetHvalue('EVLO',float(eventlon))
			   comp.SetHvalue('EVDP',float(eventdepth))
			   comp.SetHvalue('AZ',float(az))
			   comp.SetHvalue('BAZ',float(baz))
			   comp.SetHvalue('MAG',float(mag))
			   comp.SetHvalue('CMPAZ',azimuth)
			   comp.SetHvalue('CMPINC',dip)
			   comp.SetHvalue('STLA',float(stlat))
			   comp.SetHvalue('STLO',float(stlon))
			   comp.SetHvalue('STEL',float(stationdepth))
			   comp.SetHvalue('GCARC',float(dist))
			   comp.SetHvalue('T1',P)
			   comp.SetHvalue('T2',S)
			   comp.SetHvalue('T3',SKS)
			   comp.SetHvalue('T4',SKKS)

			   comp.WriteSacHeader(tr)

			print 'Written SAC file %s' %filename

	def getquakesformap(self):
		'''Returns a long list containing all the earthquakes whose data is to be downloaded. This function is for use with the GMT mapper only'''

		self.fetchinventory() #make the station inventory
		networks = self.extract_stations() #make the networks dictionary

		allquakes = []
		stationslonlat = []
		i=0

		for network in networks: #should only be one network
			if i <= self.dm:
				networkname = str(network).split(' ')[1].strip()
				for station in networks[network]:
					stationame = str(station.strip())
					lon = float(networks[network][station][1])
					lat = float(networks[network][station][0])
					depth = float(networks[network][station][2])
					channels = networks[network][station][3]
					azimuths = networks[network][station][4]
					dips = networks[network][station][5]

					#print self.minmagnitude,self.minradius,self.maxradius
					#print self.starttime,self.endtime,lon,lat

                    #this runs really slowly in some cases
					#quakecat = self.client.get_events(starttime=self.starttime, endtime=self.endtime, minmagnitude=self.minmagnitude, maxmagnitude=self.maxmagnitude,longitude=lon, latitude=lat, minradius=self.minradius, maxradius=self.maxradius)

					quakecat = geteventslist([self.starttime,self.endtime],[lon,lat],[self.minradius,self.maxradius],[self.mineventlon,self.maxeventlon,self.mineventlat,self.maxeventlat],[self.minmagnitude,self.maxmagnitude],self.homedirectory)
					#quakecat = self.client.get_events(starttime=self.starttime, endtime=self.endtime, minmagnitude=6.0, longitude=lon, latitude=lat, minradius=85.0, maxradius=130.0)

					allquakes.append(quakecat) #quakecat is a list of [time,lon,lat,mag,depth]
					stationslonlat.append([networkname,station,lon,lat,depth,channels,azimuths,dips])
					print '############\nGot quake catalog for %s in network %s between times %s and %s\n############' %(station,networkname,str(self.starttime),str(self.endtime))
			i+=1

		return allquakes,stationslonlat

	def getquakes(self):
		'''Returns a long list containing all the earthquakes whose data is to be downloaded'''

		self.fetchinventory() #make the station inventory
		networks = self.extract_stations() #make the networks dictionary

		allquakes = []
		stationslonlat = []
		i=0

		for network in networks: #should only be one network
			if i <= self.dm:
				networkname = str(network).split(' ')[1].strip()
				for station in networks[network]:
					stationname = str(station.strip())
					stationlon = float(networks[network][station][1])
					stationlat = float(networks[network][station][0])
					stationdepth = float(networks[network][station][2])
					stationchannels = networks[network][station][3]
					stationazimuths = networks[network][station][4]
					stationdips = networks[network][station][5]

					#print self.minmagnitude,self.minradius,self.maxradius
					#print self.starttime,self.endtime,lon,lat

                    #this runs really slowly in some cases
					#quakecat = self.client.get_events(starttime=self.starttime, endtime=self.endtime, minmagnitude=self.minmagnitude, maxmagnitude=self.maxmagnitude,longitude=lon, latitude=lat, minradius=self.minradius, maxradius=self.maxradius)

                    #This version is faster - uses a prebuilt catalog to obtain quakes. Rememeber to periodically update the catalog.
					catalog = geteventslist([self.starttime,self.endtime],[stationlon,stationlat],[self.minradius,self.maxradius],[self.mineventlon,self.maxeventlon,self.mineventlat,self.maxeventlat],[self.minmagnitude,self.maxmagnitude],self.homedirectory)
					#quakecat = self.client.get_events(starttime=self.starttime, endtime=self.endtime, minmagnitude=6.0, longitude=lon, latitude=lat, minradius=85.0, maxradius=130.0))
					print '###########################\nGot quake catalog for %s in network %s between times %s and %s\n###########################' %(station,networkname,str(self.starttime),str(self.endtime))

					for event in catalog:
						quaketime = event[0]
						quakelat = float(event[2])
						quakelon = float(event[1])
						quakedepth = float(event[4])
						quakemag = float(event[3])

						dist, azimuth, backazimuth = self.getazimuths(stationlat,stationlon,quakelat,quakelon)
						
						Relative_Parrival,Relative_Sarrival,Relative_SKKSarrival,Relative_SKSarrival,starttrace,endtrace = self.gettraveltimes(dist,quakedepth,quaketime)

						quaketimestr = str(starttrace)

						response = self.includeresponse
						responsetype = self.responsetype

						#In this version, we're getting the events file by file, rather than sendoing a bulk request to IRIS. The main advantage of this is that
						#it allows the user to see whats going on, rather than waiting a very long time for the obspy bulk request to return.

						try:
							self.getcomptraces(quaketimestr,starttrace,endtrace,networkname,stationname,stationlat,stationlon,stationchannels,stationazimuths,stationdips,stationdepth,quakelat,quakelon,azimuth,backazimuth,quakemag,dist,quakedepth,Relative_Parrival,Relative_Sarrival,Relative_SKSarrival,Relative_SKKSarrival,response=response,responsetype=responsetype)
							i+=1
						except:
							print '\nALERT:\nCould not find channel data for event at %s. Moving on to next event\n' %quaketimestr


		print '###################\n\nDone downloading SACfiles!\n\n###################'
		print 'Total number of events: %g' %i


if __name__ == '__main__':
	#testing. Note inclusion of the instrument response
	cwd = os.getcwd()
	starttime=UTCDateTime("2010-04-01")
	endtime=UTCDateTime("2014-08-25") 
	Traces = TraceFetch(network='TA',station='I02D',starttime=starttime,endtime=endtime,channel='BH?',minmagnitude=7.0,traceduration=3600.0,minradius=85.0,maxradius=130.0,includeresponse=True,responsetype='DISP',homedirectory=cwd)
	Traces.getquakes()	