#!/usr/bin/env python

##########################################################
#Installs the seismofetch program. This involves minimal operation - adding some content to the bashrc file and checking if all
# required the packages are installed. Also provides basic checks on the operating system so that the run script can be set up in the 
#correct way
##########################################################


import os
import sys 

seismodir = os.getcwd()

#construct home directory name - for some reason os.chdir('~') doesn't work

seismodirparts = seismodir.split('/')
homedir = '/'+seismodirparts[1]+'/'+seismodirparts[2]

print '####################################\n'
print "Seismofetch thinks your homedir is %s. If this isn't true, or your bash profile file is elsewhere, please change the homedir variable in INSTALL.py" %homedir
print '\n####################################\n'

homedir = homedir

def appendbashprof(infile):
	'''Append essential lines to the bash profile'''

	#Check if the bashfile is not already updated
	bashfile = open(infile,'r')
	lines = bashfile.readlines()
	bashfile.close()


	if '#Appended by SeismoFetch installer\n' in lines:
		print '\nSeismoFetch path already appears to have been added to your bash file\n'

	else:
		bashfile = open(infile,'a')

		bashfile.write('\n\n#Appended by SeismoFetch installer\n')
		bashfile.write('\nalias seismofetch="%s/run_SF2.sh"' %seismodir)
		bashfile.close()

def buildrunscript(systemtype):
   '''Create a script that can be used to run the program on different systems'''
   
   if systemtype == 'OSX':
     print 'Detected OSX'
     outfilename = 'run_SF2.sh'
     outfile = open(outfilename,'w')
     outfile.write('#!/bin/bash\n')
     outfile.write('#Script that runs the seismofetch program\n')
     outfile.write('seismodir="%s"\n' %seismodir)
     outfile.write("echo '\n\nRunning SeismoFetch program. Useful information about the progress of your request will appear in the terminal\n\n'\n")
     outfile.write("cd $seismodir\n")
     outfile.write("arch -i386 /usr/bin/python GUI_layout.py")
     outfile.close()
     os.system('chmod 755 run_SF2.sh')
     
   if systemtype == 'LINUX':
     print 'Detected LINUX'
     outfilename = 'run_SF2.sh'
     outfile = open(outfilename,'w')
     outfile.write('#!/bin/bash\n')
     outfile.write('#Script that runs the seismofetch program\n')
     outfile.write('seismodir="%s"\n' %seismodir)
     outfile.write("echo '\n\nRunning SeismoFetch program. Useful information about the progress of your request will appear in the terminal\n\n'\n")
     outfile.write("cd $seismodir\n")
     outfile.write("python GUI_layout.py")
     outfile.close()
     os.system('chmod 755 run_SF2.sh')
 
#Determine system architecture:

systemtype = None
os.system('uname -a > system_arch.dat')
infile = open('system_arch.dat','r')
line = infile.readlines(1)
infile.close()
if 'Linux' in line[0]:
  systemtype = 'LINUX'
elif 'MacBook' in line[0]:
   systemtype = 'OSX'

os.system('rm system_arch.dat')

#create appropriate run file 

if systemtype is not None:
   buildrunscript(systemtype)
else:
  raise ValueError('Your system type was not recognised: Must be a version of linux or OSX. Its possible that SeismoFetch cannot run on your system')
  sys.exit(1)


#Test for gmt 
os.system('gmt --version > GMTversion.dat')

infile = open('GMTversion.dat','r')
line = infile.readlines(1)
infile.close()

try:
 if len(line[0]) < 2:
   print '####################\nYou do not appear to have GMT-5. SeismoFetch will still run, but you will be unable to make maps\n####################\n'
except:
   print '####################\nYou do not appear to have GMT-5. SeismoFetch will still run, but you will be unable to make maps\n####################\n'
	 

#Test for obspy libraries
try:
	import obspy
	print 'Obspy found'
except:
	print '####################\nObspy libraries not found. Install the latest version of obspy in order to continue\n####################\n'
	sys.exit(1)

#Test for graphics
try:
	from ttk import *
	from Tkinter import *
	print 'ttk and Tkinter found'
except:
	print '####################\nEither ttk or Tkinter could not be found. Its likely that ttk is not installed. Please install this to continue\n####################\n'
	sys.exit(1)


###########################
#Add aliases to bash profile
###########################

print '\nAdding required lines to your bash profile so that Seismofetch can find itself ...\n'

os.chdir(homedir)

if os.path.isfile('.bashrc'):
	print '\nFound a .bashrc file\n'

	appendbashprof('.bashrc')

	#check things are working
	os.chdir(seismodir)

elif os.path.isfile('.bash_profile'):
	print '\nFound a .bash_profile file\n'

	appendbashprof('.bash_profile')
	os.chdir(seismodir)

else: 
	print '\nCould not find a suitable bash profile file - ensure that you are running a bash shell\n'
	os.chdir(seismodir)
	sys.exit(1)

###################################
#Now, see if we have a quake catalog
###################################

if os.path.isfile('%s/Global_Quake_Cat/globalquake_parsed.dat' %seismodir):
	print '\nIt looks like a quake catalog already exists. Remember to update this regularly if you want to get modern quake info\n'
	os.system('ls -ltr %s/Global_Quake_Cat/globalquake_parsed.dat' %seismodir)
else:
	print '\nObtaining quake catalog: All global quakes of M5.0 and above since 01-01-1970 will be found. To change the minimum magnitude, edit /Global_Quake_Cat/MakeGlobalCat.py\n'
	print '####################\nThis could take some time on a slow internet connection\n####################\n'
	os.system('./MakeGlobalCat.py')
	os.chdir(seismodir)

print '####################\nSUCCESS!'
print '\nYou should now be able to run Seismofetch with >seismofetch after having run >source ~/.bashrc'

