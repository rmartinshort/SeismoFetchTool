#!/usr/bin/env python
#Fetch moment tensors for a particular request

from obspy import UTCDateTime
from GMT_map import convertstringtolist
import sys
from cat_analysis import * #import catalog analysis python tools
import os
import glob

class MomentTensorFetch:
	def __init__(self,starttime=None,endtime=None,minlon=None,maxlon=None,minlat=None,maxlat=None,savedirectory=None):

		"""Only take the parameters relevent to finding moment tensors as arguments"""

		self.starttime = starttime
		self.endtime = endtime
		self.minlat = minlat
		self.maxlat = maxlat
		self.minlon = minlon
		self.maxlon = maxlon
		self.savedirectory = savedirectory


	def gettensors(self):
		"""Get all the moment tensors that exist within the specified region over the specified time frame , and write to outfile"""

		print 'Requesting event information'
		outfilename = get_hist_mt(self.starttime,self.endtime) #llat=self.minlat,ulat=self.maxlat,llon=self.minlon,ulon=self.maxlon)

        #Note: including lat and lon bounding information causes the cat_analysis function get_hist_mt to fail. This is annoying, but becuase its so quick getting 
        #global mts doesn't really matter. One can sort them or just plot one's bounds in GMT. 


		#move the moment tensor file to the specified location 
		os.system('mv %s %s' %(outfilename,self.savedirectory))
		print '\n####################\nWritten Moment Tensor file to %s\n####################\n' %(self.savedirectory)



if __name__ == "__main__":
	
	#start = UTCDateTime("1990-02-01")
	#end = UTCDateTime("2011-05-01")
	#test = MomentTensorFetch(starttime=start,endtime=end)
	#test.gettensors()


	starttime = convertstringtolist(sys.argv[1])
	endtime = convertstringtolist(sys.argv[2])
	savedir = str(sys.argv[4])

	if str(sys.argv[3]).strip() == 'None':
		bounds = None
	else:
		bounds = convertstringtolist(sys.argv[3])
		minlon = float(bounds[0])
		maxlon = float(bounds[1])
		minlat = float(bounds[2])
		maxlat = float(bounds[3])

	print starttime,endtime

	starttime = UTCDateTime(year=int(starttime[0]),month=int(starttime[1]),day=int(starttime[2]))
	endtime = UTCDateTime(year=int(endtime[0]),month=int(endtime[1]),day=int(endtime[2]))


	if bounds:
		data = MomentTensorFetch(starttime=starttime,endtime=endtime,minlon=minlon,maxlon=maxlon,minlat=minlat,maxlat=maxlat,savedirectory=savedir)
	else:
		data = MomentTensorFetch(starttime=starttime,endtime=endtime,savedirectory=savedir)

	data.gettensors()

