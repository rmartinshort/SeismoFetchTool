#!/usr/bin/env python

##################################################################
#Class that sets up all visual components of the SeismoFetch
#GUI. The user fills in the form and when one of the three 
#colored buttons are pressed the data gets handed to another class
#this could be impoved by reorganising and thinking more about user 
#friendly graphics, but the basics are here

#On a Mac this should be run in 32 bit python, but some of the colors won't display correctly. 
#On linux it works in regular 64 bit python with colored buttons. This has not been fully tested. 
###################################################################

from ttk import *
from Tkinter import *
import tkFileDialog
from quitter import Quitter
from Inputform_check import checkforerrors
import os

class entrygui(Frame):
	"""Class that defines the GUI setup. Contains all aspects of the user interface and calls other components
	of the program to check input for errors, make a map and download traces"""
	
	def __init__(self,parent):
		Frame.__init__(self,parent)
		self.grid(sticky=N+S+E+W)

		#configure all rows and columns so that they can be resized. This doesn't quite work as intended

		top=self.winfo_toplevel()
		for i in range(30):
			top.rowconfigure(i,weight=1)
			self.rowconfigure(i,weight=1)
		for i in range(5):
			top.columnconfigure(i,weight=1)
			self.columnconfigure(i,weight=1)

		parent.title('SeismoFetch user window')

		welcome = Label(self,text='This is SeismoFetch V2.0\n\nSee File -> Help for instructions',bg='SlateBlue3',font="Helvetica 20 bold")
		welcome.grid(row=0,sticky=W+E+S+N,columnspan=5,ipady=10)

		#Let the program know that its child windows are closed currently
		self.helpwindowopen = False
		self.MTwindowopen = False
		self.ADVwindowopen = False

		#other variables associated with the advanced options window
		self.resamplevalue = None
		self.spectrograms = 'No'

		#makes the resizing widget (from ttk)
		Sizegrip(self).grid(column=999,row=999,sticky=S+E)

        #save all entry box entries in a list so that they can be easily reset
		self.allentries = []

		#variable that displays the directory to which data is being saved 
		self.savelocation = StringVar()
		self.savelocation.set('Saving to: %s' %(os.getcwd()))

		#set up all the GUI components
		################################
		self.makestationform()
		self.maketimeform()
		self.makeinstrumentresponsemenu()
		self.stationposform()
		self.eventposform()
		self.makegmtmapbutton()
		self.maketracegetbutton()
		self.makeresetfieldsbutton()
		self.makeminmaxradiuslabel()
		self.maketracelengthlabel()
		self.makemagnitudeform()
		self.makesavedirectorybutton()
		self.makeclientmenu()
		self.makehelpmenubar(parent)

		self.currentdir = os.getcwd()
		self.defaultsavedirectory = self.currentdir

		#Quitter(self).grid(row=18,column=4,ipady=10,ipadx=10,sticky=E)

		self.showsavelocation()
		################################

	def makestationform(self):
		'''Make Station, Network and Channels entry labels'''

		Label(self,text='Network (e.g. "TA" or "7D". This is required)').grid(row=1,column=0,sticky=W,pady=5)
		Label(self,text='Station (e.g. "I02D". Leave blank to get all stations)').grid(row=2,column=0,sticky=W,pady=5)
		Label(self,text='Channel (e.g. "HH?". Use ? or * as a wildcard. This is required)').grid(row=3,column=0,sticky=W,pady=5)

		e1 = Entry(self)
		e2 = Entry(self)
		e3 = Entry(self)

		e1.grid(row=1,column=1,sticky=W+E+S+N,pady=5)
		e2.grid(row=2,column=1,sticky=W+E+S+N,pady=5)
		e3.grid(row=3,column=1,sticky=W+E+S+N,pady=5)
		
		self.stationentries = [('Network',e1),('Station',e2),('Channel',e3)] #pack the entries
		self.allentries.append(e1)
		self.allentries.append(e2)
		self.allentries.append(e3)

	def maketimeform(self):
		'''Start and end time entry labels'''

		Label(self,text='Event search parameters',bg='SteelBlue2',font="Helvetica 14 bold").grid(row=5,column=0,columnspan=2,ipady=10,sticky=W+E+S+N)

		starttimelabel = Label(self,text='Enter a start and end time for the trace search',bg='SteelBlue1')
		starttimelabel.grid(row=6,sticky=W+E+S+N,columnspan=2,ipady=8)

		Label(self,text='Start time in form YYYY-MM-DD-HH-mm-SS-ffff').grid(row=7,column=0,sticky=E+W+S+N,pady=5)
		Label(self,text='End time in form YYYY-MM-DD-HH-mm-SS-ffff').grid(row=8,column=0,sticky=E+W+S+N,pady=5)

		e4 = Entry(self)
		e5 = Entry(self)

		e4.config(width=20)
		e5.config(width=20)

		e4.grid(row=7,column=1,sticky=E+W+S+N,ipady=5)
		e5.grid(row=8,column=1,sticky=E+W+S+N,ipady=5)

		self.timeentries = [('starttime',e4),('endtime',e5)]
		self.allentries.append(e4)
		self.allentries.append(e5)

	def makeinstrumentresponsemenu(self):
		'''Instrument response drop down menu'''

		Label(self,text='Instrument response removal type').grid(row=2,column=3,pady=10,padx=20,sticky=W)
		optionList=('No removal','Pole zero to displacement','Pole zero to velocity','Pole zero to acceleration')

		self.responsevariable = StringVar()

		self.responsevariable.set(optionList[0])

		mb = OptionMenu(self,self.responsevariable,*optionList)
		mb.config(width=20)

		#use variable.get() to get the set value of this variable

		mb.grid(row=2,column=4,pady=10)

	def makeclientmenu(self):
		'''Client choice drop down menu'''

		Label(self,text='Client server name').grid(row=3,column=3,ipady=10,padx=20,sticky=W)
		optionList=('IRIS','NCEDC','RESIF','USGS')

		self.clientvariable = StringVar()

		self.clientvariable.set(optionList[0])

		mb = OptionMenu(self,self.clientvariable,*optionList)
		mb.config(width=20)

		#use variable.get() to get the set value of this variable

		mb.grid(row=3,column=4,ipady=10)

	def stationposform(self):
		'''Entry bar for a boundary box for the stations'''

		Label(self,text='Station search parameters',bg='SteelBlue2',font="Helvetica 14 bold").grid(row=5,column=3,columnspan=2,ipady=10,sticky=E+W+S+N)

		Label(self,text='Enter coordinates of region of interest (stations)',bg='SteelBlue1').grid(row=6,column=3,columnspan=2,sticky=W+E+S+N,ipady=8)

		Label(self,text='Bounding box [lonmin/lonmax/latmin/latmax]:').grid(row=7,column=3,ipady=5,padx=20,sticky=W)

		e6 = Entry(self)

		e6.grid(row=7,column=4,sticky=E+W+S+N,ipady=5) 

		self.allentries.append(e6)

		self.stationbounding = [('stationbounding',e6)]

	def makemagnitudeform(self):
		'''Entry bars for maximum and minimum magnitudes'''

		Label(self,text='Enter minimum and maximum quake magnitudes',bg='SteelBlue1',pady=5).grid(row=17,column=0,columnspan=2,sticky=E+W)

		Label(self,text='Minimum magnitude').grid(row=18,column=0,sticky=E+W,ipady=5)

		e7 = Entry(self)
		e7.grid(row=18,column=1,ipady=5,stick=E+W+S+N)

		Label(self,text='Maximum magnitide').grid(row=19,column=0,sticky=E+W,ipady=5)
		e8 = Entry(self)
		e8.grid(row=19,column=1,ipady=5,sticky=E+W+S+N)

		self.minmaxmag =  [('minmag',e7),('maxmag',e8)]

		self.allentries.append(e7)
		self.allentries.append(e8)

	def eventposform(self):
		'''Entry bar for the boundaries of an event position form'''

		Label(self,text='Enter coordinates of region of interest (events)',bg='SteelBlue1').grid(row=12,column=0,columnspan=2,sticky=W+E+S+N,ipady=8)

		Label(self,text='Bounding box [lonmin/lonmax/latmin/latmax]:').grid(row=13,column=0,pady=5,sticky=E+W)
		e9 = Entry(self)

		e9.grid(row=13,column=1,ipady=5,sticky=E+W+S+N) 

		self.eventbounding = [('eventbounding',e9)]

		self.allentries.append(e9)

	def makeminmaxradiuslabel(self):
		'''Entry bars for maximum and minimum radius for the quake search'''

		Label(self,text='Enter minimum and maximum radii (in degrees, from stations)',bg='SteelBlue1').grid(row=14,column=0,columnspan=2,sticky=E+W+S+N,ipady=8)

		Label(self,text='Minimum radius',pady=5).grid(row=15,column=0,sticky=E+W+S+N)

		e10 = Entry(self)
		e10.grid(row=15,column=1,ipady=5,sticky=E+W+S+N)

		Label(self,text='Maximum radius',pady=5).grid(row=16,column=0,sticky=E+W+S+N)
		e11 = Entry(self)
		e11.grid(row=16,column=1,ipady=5,sticky=E+W+S+N)

		self.minmaxrad = [('minrad',e10),('maxrad',e11)]

		self.allentries.append(e10)
		self.allentries.append(e11)

	def makesavedirectorybutton(self):
		'''Button that allows users to choose a directory inwhich to save the SAC files'''

		Button(self,text='Change save location', command=self.askdirectory,width=20,bg='SteelBlue2').grid(row=13,column=3,ipady=10,ipadx=10,sticky=E)

	def makegmtmapbutton(self):
		'''Button to make the GMT map. links to the mapper command'''

		Button(self,text='Generate map!',command=self.makemapcommand,width=20,bg='SteelBlue1').grid(row=15,column=3,ipady=10,ipadx=10,sticky=E)
	
	def maketracegetbutton(self):
		'''Button to fetch the traces. links to the trace fetch command'''

		Button(self,text='Get events!',command=self.getevents,width=20,background='SteelBlue1').grid(row=17,column=3,ipady=10,ipadx=10,sticky=E)

	def makeresetfieldsbutton(self):
		'''Reset all the fields to null'''

		Button(self,text='Reset form',command=self.reset,width=20,bg='SteelBlue2').grid(row=14,column=3,ipady=10,ipadx=10,sticky=E)

	def makegettmtsbutton(self):
		'''Get moment tensors for the quake(s) of interest'''

		Button(self,text='Get moment tensors',command=self.getmts,width=20,bg='SteelBlue1').grid(row=14,column=4,ipady=10,ipadx=10,sticky=W)

	def maketracelengthlabel(self):
		'''Entry bar for the trace duration'''

		Label(self,text='Trace duration (s):').grid(row=1,column=3,pady=10,padx=30,sticky=W)

		e12=Entry(self)

		e12.grid(row=1,column=4,ipady=5,sticky=E+W)

		self.traceduration = [('traceduration',e12)]

		self.allentries.append(e12)

	def makehelpmenubar(self,parent): 
		'''Create the 'file->help' drop down menu'''

		menubar = Menu(self)

		filemenu = Menu(menubar,tearoff=0,font="Helvetica 16 bold") #insert a drop-down menu

		filemenu.add_command(label='Help',command=self.addhelptext)
		filemenu.add_command(label='Get Moment Tensors',command=self.mmtscreen)
		filemenu.add_command(label='Advanced options',command=self.advoptscreen)
		filemenu.add_command(label='Quit',command=self.quit)
		menubar.add_cascade(label='Options',menu=filemenu) #add the drop down menu to the menu bar 
		parent.config(menu=menubar)

	def advoptscreen(self):
		'''Creates a window that allows the user to choose some other options that affect the trace fetch process. These options are autometically set 
		unless the user chooses to access this window and edit them'''

		if self.ADVwindowopen == True:
			print 'Error: The advanced options window is already open'
			return 
		else:
			self.ADVwindowopen == True

		advwindow = Toplevel(self)
		advwindow.wm_title('More SeismoFetch options')

		Label(advwindow,text='Use these tools to futher customise your download [may add considerable time to large downloads]',bg='Slateblue2',font='Helvetica 14 bold').grid(row=0,column=0,columnspan=2,ipady=20,ipadx=5,sticky=E+W+S+N)


        #Add entry option for data resampling 
		Label(advwindow,text='Resample data to a given frequency: [enter in Hz]').grid(row=1,column=0,sticky=W,ipady=5,padx=20)

		resamplevalue = StringVar()

		adv1 = Entry(advwindow,textvariable=resamplevalue)
		adv1.config(width=20)

		adv1.grid(row=1,column=1,sticky=W,ipady=5)

		if self.resamplevalue:
			resamplevalue.set(self.resamplevalue)

		self.resample = [('resample',adv1)]

		#Add option list for spectrograms
		Label(advwindow,text='Plot spectrograms? [written in eps format]').grid(row=2,column=0,ipady=5,padx=20,sticky=W)
		specoptionList=['No','Yes']

		self.spectrogramvariable = StringVar()

		if self.spectrograms == 'Yes':
			self.spectrogramvariable.set(specoptionList[1])
		else:
			self.spectrogramvariable.set(specoptionList[0])

		advmb1 = OptionMenu(advwindow,self.spectrogramvariable,*specoptionList)
		advmb1.config(width=20)

		advmb1.grid(row=2,column=1,ipady=10,sticky=W)

		Label(advwindow,text='Note typical sample rates of data types: LH?: 1Hz; BH?: 40Hz; HH?: 100Hz').grid(row=3,column=0,columnspan=2,ipady=10,sticky=E+N+S+W)

		Button(advwindow,text='Set options',command=self.advwindowsetoptions).grid(row=4,column=0,ipady=10,padx=20,pady=10,sticky=W)

		#Add the quit button
		Button(advwindow, text='Done',width=50,bg='SteelBlue1',command=lambda: self.closechild(advwindow,self.ADVwindowopen)).grid(row=5,column=0,columnspan=2,sticky=E+N+W+S,ipady=5)


	def advwindowsetoptions(self):
		'''Advanced options window setup'''

		userresampvalue = self.resample[0][1].get()
		self.resamplevalue = str(userresampvalue)
		if not userresampvalue:
			print '\nYou did not enter a resample value: using defualt sampling rate\n'
			self.resamplevalue = 'None'

		self.spectrograms = self.spectrogramvariable.get()
		if self.spectrograms == 'Yes':
			print '\nOutputting spectrograms for each component in eps format\n'


	def mmtscreen(self):
		'''Creates a new window that allows a user to download moment tensors for quakes within a timeframe and region of interest'''

		if self.MTwindowopen == True:
			print 'Error: The "Moment Tensor" window is already open'
			return 
		else:
			self.MTwindowopen = True

		#Create pop-up window
		mmtwindow = Toplevel(self)
		mmtwindow.wm_title('Get Moment Tensors')

		topmmt=mmtwindow.winfo_toplevel()
		for i in range(30):
			topmmt.rowconfigure(i,weight=1)
			mmtwindow.rowconfigure(i,weight=1)
		for i in range(5):
			topmmt.columnconfigure(i,weight=1)
			mmtwindow.columnconfigure(i,weight=1)

		#makes the resizing widget (from ttk)
		Sizegrip(mmtwindow).grid(column=999,row=999,sticky=S+E)

		Label(mmtwindow,text='Use these tools to download moment tensors for a set of earthquakes of interest',bg='Slateblue2',font='Helvetica 16 bold').grid(row=0,column=0,columnspan=2,ipady=20,sticky=W+E+S+N)
		
		#create all the labels 

		Label(mmtwindow,text='Moment tensors will be written to %s in psmeca format' %self.defaultsavedirectory).grid(row=1,column=0,columnspan=2,ipady=5,sticky=W+E+S+N)

		starttimelabel = Label(mmtwindow,text='Enter a start and end time for the MT search',bg='SteelBlue1')
		starttimelabel.grid(row=3,sticky=W+E+S+N,columnspan=2,ipady=8)

		Label(mmtwindow,text='Start time in form YYYY-MM-DD-HH-mm-SS-ffff').grid(row=5,column=0,sticky=E+W+S+N,ipady=5)
		Label(mmtwindow,text='End time in form YYYY-MM-DD-HH-mm-SS-ffff').grid(row=6,column=0,sticky=E+W+S+N,ipady=5)

		mmte1 = Entry(mmtwindow)
		mmte2 = Entry(mmtwindow)

		mmte1.config(width=20)
		mmte2.config(width=20)

		mmte1.grid(row=5,column=1,sticky=E+W+S+N,ipady=5)
		mmte2.grid(row=6,column=1,sticky=E+W+S+N,ipady=5)

		Label(mmtwindow,text='Bounding box [lonmin/lonmax/latmin/latmax]').grid(row=7,column=0,sticky=E+W+S+N,ipady=5)

		mmte3 = Entry(mmtwindow)
		mmte3.config(width=20)
		mmte3.grid(row=7,column=1,sticky=E+W+S+N,ipady=5)

		self.mtentries = [('mtstarttime',mmte1),('mteendtime',mmte2),('mtebounds',mmte3)]

		#create the quit button 
		Button(mmtwindow, text='Download Moment Tensors',width=80,bg='SteelBlue1',command=self.getmts,pady=10).grid(row=9,column=0,columnspan=2,sticky=E+N+W+S,ipady=5)

		Button(mmtwindow, text='Done',width=50,bg='SteelBlue1',command=lambda: self.closechild(mmtwindow,self.MTwindowopen)).grid(row=10,column=0,columnspan=2,sticky=E+N+W+S,ipady=5)


	def addhelptext(self):
		'''Create a new window containing information about the project. This is called from the Menu items in the __init__ function'''

		if self.helpwindowopen == True:
			print 'Error: The "About" window is already open'
			return 
		else:
			self.helpwindowopen = True

		#Create a new pop-up window by assigning the top level to the exsiting arena
		aboutwindow = Toplevel(self)
		aboutwindow.wm_title('SeismoFetch help')

		#Add an escape button
		Button(aboutwindow, text='Done',width=50,bg='SteelBlue1',command=lambda: self.closechild(aboutwindow,self.helpwindowopen)).pack(side=BOTTOM,expand=YES)

		#Make a Y axis scrollbar 
		scroll = Scrollbar(aboutwindow)

		#Set up the text style and other information 
		T2 = Text(aboutwindow,height=30, width=140,yscrollcommand=scroll.set)

		#create the text section of the window
		T2.pack(side=RIGHT)
		T2.tag_configure('title',font=('Helvetica', 16, 'bold'))
		T2.tag_configure('heading',font=('Helvetica',14, 'bold'))   
		T2.tag_configure('standard',font=('Helvetia',12))

		T2.insert(END,'\nSeismoFetch V2.0: Download seismograms for any network/station combination\n\nRead this help to get started', 'title')
		T2.insert(END,'\n\nUses:','heading')
		T2.insert(END,'\n\nFill in the form with sufficient information for the program to find the data you want. The following fields are required as minimum:','standard') 

		T2.insert(END,'\n\nNetwork (enter the network code of interest)\n\nChannel(s) (typically BH?, HH? or LH? for broadband earthquake data. Use * or ? as a wildcard to get three component data, or enter a specific channel e.g. "BHZ")\
		\n\nStart time for trace search in format year-month-day-hour-minute-second-microsecond.\n\nEnd time for trace search in format year-month-day-hour-minute-second-microsecond.\n\nTrace duration in seconds (i.e. the time lengths of the SAC files)\n\nMinimum and maximum quake magnitudes to search for. \
		\n\nThe remaining options are not required. If you want to data for a specific station, enter the station code. Otherwise the program will search the entire network.\nYou can constrain the station search by entering coordinates of a bounding box in lat/lon space\
		in the specified format under "Station search parameters".\nAlternatively, you can constrain the region in which events are searched by entering box coordinates or minumum and/or maximum radii (in degrees).\
		\nThere is also the option to remove instrument reponse to displacment, velocity or acceleration.\nTo test if your parameters are correct, press "Generate Map" to get a map of your station/event choices.\
		\n\nAs a general rule, leave all fields irrelevent to your search blank. Errors will occur if a field is partially filled in. \
		\n\n\nUse the "Get events!" button to start the trace download. You can select the download location by using the "Change save location" button \
		and navigating to the desired directory.\
		\n\nWARNING: Requesting large numbers of quakes (i.e. large magnitude range, large network, large area) could take a VERY long time.\
		\n\nTo speed up the process of obtaining quake catalog, the program reads from a pre-downloaded list of quakes, found in the SeismoFetch \
		\nhome directory in the folder "Global_Quake_Cat". Update this regularly if you want modern events.','standard') 

		T2.insert(END,'\n\nData format:','heading')
		T2.insert(END,'\n\nData is output in SAC format with the RDSEED name convention (yyyy.ddd.hh.mm.ss.ffff.NN.SSSSSS.LL.CCC.Q.SAC)\
		\nThe program puts the following (extra) information into the SAC headers:\
		\n\nStation latitide, longitude and elevation\n\nComponent azimuth (90 for ?HE, 0 for ?HN, 0 for ?HZ and 0 for all unoriented data)\n\nComponent dip (90 for all but ?HZ, which = 0)\
		\n\nEvent latitude, longitude, depth and magnitude\n\nAzimuth, Backazimuth and station-event distance in degrees\n\nEstimated arrival times for P (T1), S (T2), SKS (T3) and SKKS (T4) if present\
		\n\nYou can also use this program to download moment tensors for a set of earthwquakes in psmeca format, ready for plotting in GMT\
		.To do this, click on the "File -> Get Moment Tensors" and use the window tools to make your selection.','standard')
		
		T2.insert(END,'\n\nPowered by Python and GMT. Requires Obspy, pyttk and GMT 5.','heading')
		T2.insert(END,'\nSend questions to rmartin-short@berkeley.edu, or just write suggestions here: (edit GUI_layout.py, line 331)', 'standard')


		T2.configure(state=DISABLED)

		scroll.config(command=T2.yview)

		scroll.pack(side=LEFT,fill=Y)

	def closechild(self,child,windowname):
		'''Close a child window'''
		child.destroy()
		self.helpwindowopen = False
		self.MTwindowopen = False

	def getallformparameters(self):
		'''Gets all the latest form parameters'''

        #############################################
        #Load all the parameters entered by the user
        #############################################
        
		trace_length = self.traceduration[0][1].get()
		network_name = self.stationentries[0][1].get()
		station_name = self.stationentries[1][1].get()
		channel_name = self.stationentries[2][1].get()
		start_time = self.timeentries[0][1].get()
		end_time = self.timeentries[1][1].get()
		response_type = self.responsevariable.get()
		client_name = self.clientvariable.get()
		station_box = self.stationbounding[0][1].get()
		min_mag = self.minmaxmag[0][1].get()
		max_mag = self.minmaxmag[1][1].get()
		event_box = self.eventbounding[0][1].get()
		min_rad = self.minmaxrad[0][1].get()
		max_rad = self.minmaxrad[1][1].get()

		#Advanced options
		resamplerate = self.resamplevalue

		if not resamplerate:
			resamplerate = 'None'

		spectroplot = self.spectrograms

		params = [network_name,station_name,channel_name,start_time,end_time,trace_length,response_type,client_name,station_box,event_box,min_mag,max_mag,min_rad,max_rad,resamplerate,spectroplot]
		return params 

	def makemapcommand(self):
		'''Get information about the requested events and stations and make a GMT map showing their positions'''

		print '\n\n#################\n\nMaking map [Please wait. This may take some time]\n\n#################\n\n'

		params = self.getallformparameters()
		network_name,station_name,channel_name,starttime,endtime,stationbounds,eventbounds,magnitudes,radii,response_type,client_name,trace_length,resamplerate,spectroplot = checkforerrors(params)
		#print network_name,station_name,channel_name,starttime,endtime,stationbounds,eventbounds,magnitudes,radii,response_type,client_name,trace_length

		#becuase python needs to run in 32 bit mode on MAC and obspy only works with 64 bit python, an external script needs to be called here 
		os.system('./GMT_map.py %s %s %s %s %s %s %s %s %s' %(network_name,station_name,channel_name,str(starttime).replace(" ",""),str(endtime).replace(" ",""),str(stationbounds).replace(" ",""),str(eventbounds).replace(" ",""),str(magnitudes).replace(" ",""),str(radii).replace(" ","")))

	def getevents(self):
		'''Download the requested traces'''

		if self.defaultsavedirectory == self.currentdir:
			print '###########\nWARNING:\n###########\nA directory to save the SAC files was not selected. Proceeding to write in the program home directory \n###########'

		print '\n\n#################\n\nDownloading traces [Please wait. This may take some time]\n\n#################\n\n'

		params = self.getallformparameters()
		network_name,station_name,channel_name,starttime,endtime,stationbounds,eventbounds,magnitudes,radii,response_type,client_name,trace_length,resamplerate,spectroplot = checkforerrors(params)

        #designate the response type
		if response_type == 'No removal':
			response_type = None
		elif response_type == 'Pole zero to displacement':
			response_type = 'DISP'
		elif response_type == 'Pole zero to velocity':
			response_type = 'VEL'
		elif response_type == 'Pole zero to acceleration':
			response_type = 'ACC'
		else:
			raise ValueError('Instrument response type not recorded correctly')

		#print network_name,station_name,channel_name,starttime,endtime,stationbounds,eventbounds,magnitudes,radii,response_type,client_name,trace_length

		#run the script that downloads the traces and saves as SAC files

		os.system('./Download_traces.py %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s' %(network_name,station_name,channel_name,str(starttime).replace(" ",""),str(endtime).replace(" ",""),str(stationbounds).replace(" ",""),str(eventbounds).replace(" ",""),str(magnitudes).replace(" ",""),str(radii).replace(" ",""), trace_length, response_type, str(self.defaultsavedirectory),str(self.currentdir),str(resamplerate),str(spectroplot)))

	def getmts(self):
		'''Download moment tensors and write file'''

		if self.defaultsavedirectory == self.currentdir:
			print '###########\nWARNING:\n###########\nA directory to save the SAC files was not selected. Proceeding to write in the program home directory \n###########'

		mtestarttime = self.mtentries[0][1].get()
		mteendtime = self.mtentries[1][1].get()
		mtebounds = self.mtentries[2][1].get()

		print mtestarttime,mteendtime,str(mtebounds)

		from Inputform_check import testtime, testboundingbox

		MTstart = testtime(str(mtestarttime),'start_time')
		MTend = testtime(str(mteendtime),'end_time')

		if mtebounds:
			MTbounding = testboundingbox(str(mtebounds),'bounding_box')
		else:
			MTbounding = None

		savepath = self.defaultsavedirectory
		homepath = self.currentdir

		#print str(MTstart).replace(" ",""), str(MTend).replace(" ",""), str(MTbounding).replace(" ",""), str(savepath)

		os.system('./moment_tensor_fetch.py %s %s %s %s' %(str(MTstart).replace(" ",""),str(MTend).replace(" ",""),str(MTbounding).replace(" ",""),str(savepath)))


	def reset(self):
		''''Reset all the entry boxes on the form'''

		print '\n\n#################\n\nForm reset\n\n#################\n\n'

		for entry in self.allentries:
			entry.delete(0,END)

	def askdirectory(self):
		'''Returns a selected directory name. Used when saving the SAC files'''

		self.defaultsavedirectory = tkFileDialog.askdirectory()

		if not self.defaultsavedirectory:
			self.defaultsavedirectory = os.getcwd()

		self.savelocation.set('Saving to %s' %self.defaultsavedirectory)

	def showsavelocation(self):
		'''Displays the location inwhich the current batch of SAC files are being saved'''

		savelabel = Label(self,textvariable=self.savelocation,font=('Helvetica', 10,'bold')).grid(row=12,column=3,sticky=E+W+S+N,pady=10)


if __name__ == '__main__':
	'''The GUI loop'''
	tk = Tk()
	entrygui(tk)
	tk.mainloop()