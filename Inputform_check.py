#!/usr/bin/env python

##################################################################
#Functions that check for errors in the user input form and return
#command line messages if incorrect information is entered
###################################################################

def checkforerrors(params):
	'''Params must be a list output by GUI_layout.getallformparams. This is by no means a complete error check; its basically just checking
    to see if the user has entered the minimunm requred information and hasn't spoiled the form. More error checks are placed in the fetching
    scripts
	'''

	network_name,station_name,channel_name,start_time,end_time,trace_length,response_type,client_name,station_box,event_box,min_mag,max_mag,min_rad,max_rad,resamplerate,spectroplot = params
	

	#test if the user has entered the minimum requred information 
	if not network_name:
		raise ValueError('Need to specify a network name. Check the IRIS metadata site (for example) for a complete list')

	if not channel_name:
		print 'WARNING: You did not enter a channel name: The request might still work, but many channels will be dumped'
		channel_name = '?'

	if not start_time:
		raise ValueError('Need to specify a start time for the trace search')

	if not end_time:
		raise ValueError('Need to specify an end time for the trace seatch')

	if not trace_length:
		raise ValueError('Need to specify a trace length in seconds')

	if not min_mag:
		raise Warning('No minimum magnitude selected! Earthquake search is likely to take VERY long time')

	if not station_name:
		station_name = None

	if resamplerate.strip() != 'None': #if the user has specified the resample rate, check that its in the correct format
		try:
			resamplerate = float(resamplerate)
		except:
			raise ValueError('Something wrong with the user-specified resample rate')

	if max_mag: #there must be a min mag specified
		try:
			min_mag = float(min_mag)
			max_mag = float(max_mag)
		except:
			raise ValueError('Magnitude input must be a number')
		if min_mag > max_mag or max_mag > 11.0:
			raise ValueError('Magnitudes entered incorrectly!')
	else:
		max_mag = None

	if max_rad:
		try:
			max_rad = float(max_rad)
		except:
			raise ValueError('Radius must be a number')
		if min_rad:
			try:
				min_rad = float(min_rad)
			except:
				raise ValueError('Radius must be a number')
			if (max_rad > 360.0): #these need to be floats. Fix it!
				raise ValueError('Radii entered incorrectly!')
		else: 
			min_rad = None
	else:
		max_rad = None


	#if yes, begin associated testing. This check is not sufficient - for some reason some requests return 
	#more than three components, and this needs to be fixed

	if channel_name != '?':
		if len(channel_name) != 3:
			raise ValueError('Input channel not a recognised type')

	starttime = testtime(start_time,'start time')
	endtime = testtime(end_time,'end_time')

	if station_box:
		stationbounds = testboundingbox(station_box,'station boundary box')
	else:
		stationbounds = [None,None,None,None]
	if event_box:
		eventbounds = testboundingbox(event_box,'event boundary box')
	else:
		eventbounds = [None,None,None,None]

	print '\n##################\nUser input form style appears correct!\n##################\n'

	return network_name,station_name,channel_name,starttime,endtime,stationbounds,eventbounds,[min_mag,max_mag],[min_rad,max_rad],response_type,client_name,trace_length,resamplerate,spectroplot



def testtime(inputtimestring,name):
	'''Tests if an inputtimestring is in the correct format. If not, returns errors'''

	comps = inputtimestring.split('-')
	if len(comps) != 7:
		raise ValueError('%s not entered in correct format' %name)

	try:
		year = float(comps[0])
		month = float(comps[1])
		day = float(comps[2])
		hour = float(comps[3])
		minute = float(comps[4])
		second = float(comps[5])
		microsecond = float(comps[6])

	except:
		raise ValueError('%s not entered in the correct format. Not all components could be converted into numbers')

	return [year,month,day,hour,minute,second,microsecond]


def testboundingbox(boundingboxstring,name):

	comps = boundingboxstring.split('/')
	if len(comps) != 4:
		raise ValueError('%s not entered in correct format' %name)

	lonmin=float(comps[0])
	lonmax=float(comps[1])
	latmin=float(comps[2])
	latmax=float(comps[3])

	if (lonmin >= lonmax) or (lonmin < -180) or (lonmax > 180):
		raise ValueError('Error in user supplied longitude for %s. Supply longitude from -180 to 180.' %name)
	if (latmin >= latmax) or (latmin < -90) or (latmax > 90):
		raise ValueError('Error in user supplied latitude for %s. Supply latitude from -90 to 90.' %name)

	return [lonmin,lonmax,latmin,latmax]





