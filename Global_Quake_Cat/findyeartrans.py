#!/usr/bin/env python
#searching the global quake catalog takes a very long time. This speeds things up by finding the approximate locations of particular times and noting them.
import datetime 
cyear = int(str(datetime.datetime.now()).split('-')[0])

years = range(1970,cyear+1)
print years 

infile = open('globalquake_parsed.dat','r')
outfile = open('year_number_list.dat','w')
lines = infile.readlines()
infile.close()

i=0
yearcount = len(years)-1
print yearcount
yearslist = []

for element in lines:
	vals = element.split(',')
	year = float(vals[0].split('-')[0])
	if year != years[yearcount]:
		outfile.write('%g %d\n' %(year+1,i))
		yearslist.append([year+1,i])
		yearcount = yearcount - 1 
	i+=1 

print yearslist