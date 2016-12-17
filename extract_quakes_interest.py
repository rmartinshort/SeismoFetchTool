#!/usr/bin/env python

################
#Looks at a pre-downloaded list of quakes and outputs a list of those that correspond to search criteria
#Could be optimited further, but this is much faster than using an Obspy get_events search

#NOTE: For the most up-to date events, you will need to re-download the complete catalog using /SeismoFetch_v1/Global_Quake_Cat/MakeGlobalCat.py
#in this file one can specify the minimum quake magnitude to downlaod, and the process will take at least 10 minutes on a good internet connection
################

from obspy.core.util import locations2degrees
from obspy import UTCDateTime
import time 

def geteventslist(times,stationlocation,radii,eventbox,mags,homedir):
	''''Takes a set of lists containing the values of these parameters. Outputs all the quakes that satisfy the paramters by first looking
	at the global quake catalog
	'''

	start = time.time()

	quakefile = open(str(homedir)+'/Global_Quake_Cat/'+'globalquake_parsed.dat','r')
	lines = quakefile.readlines()
	quakefile.close()

	extractquakes = []

	##########################
	#Introducted for speed: first determine the indices of each of the years, so that the quake seatch can be as fast as possible
	##########################
	import datetime 
	cyear = int(str(datetime.datetime.now()).split('-')[0])
	years = range(1970,cyear+1)

	i=0
	yearcount = len(years)-1
	yearslist = {}

	for element in lines:
		vals = element.split(',')
		year = float(vals[0].split('-')[0])
		if year != years[yearcount]:
			yearslist[year]=i
			yearcount = yearcount - 1 
		i+=1 

	##########################

	endtimeyearnum = times[0].year 
	starttimeyearnum = times[1].year
	maxcount = yearslist[endtimeyearnum-1]
	if starttimeyearnum < cyear-1:
		mincount = yearslist[starttimeyearnum+1]
	else:
		mincount = 0

	for line in lines[mincount:maxcount]:
		vals = line.split(',')
		quaketime = UTCDateTime(str(vals[0]))
		quakelat = float(vals[1])
		quakelon = float(vals[2])
		quakemag = float(vals[4])
		quakedepth = float(vals[3])
		#print times[0], times[1], quaketime, quakelat, quakelon, quakemag, quakedepth, stationlocation, radii, eventbox
		if (times[0] < quaketime < times[1]) and (float(mags[0]) < quakemag < float(mags[1])):
			quakedist = locations2degrees(quakelat,quakelon,stationlocation[1],stationlocation[0])
			if (float(radii[0]) < quakedist < float(radii[1])) and (float(eventbox[0]) < quakelon < float(eventbox[1])) and (float(eventbox[2]) < quakelat < float(eventbox[3])):
				extractquakes.append([quaketime,quakelon,quakelat,quakemag,quakedepth])

	return extractquakes

