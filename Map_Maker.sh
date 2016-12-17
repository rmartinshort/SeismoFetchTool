#!/bin/bash

#############################
#Makes a GMT map showing a users choice of station/network combination. This is a simple 'throwaway' map that is really
#just aiming to allow the user to check that they've selected the right data. May want to add the option to save? 
##############################3


gmt GMTset BASEMAP_TYPE_FANCY

stations=tmp_plotfile_stations.dat
events=tmp_plotfile_events.dat
#plates=/Users/rmartinshort/Documents/Berkeley/Cascadia_Splitting/usgs_plates.txt.GMTdat


R=-180/180/-80/80 #global, excluding poles
J=N10i #Robinson projection 
PS=tmpmap.ps 

#plot a global map

gmt pscoast -R$R -J$J -Bg -Dl -A10000 -Glightgreen -Sblue -Wthinnest -P --PS_MEDIA=Custom_12ix7i -K > $PS

#add on the USGS plates

#GMT psxy $plates -: -J$J -R$R -Wthin,red -O -V -K -Bg90/g180 >> $PS

#add on the users choice of events

gmt psxy $events -Sc0.15 -Gyellow -Wthin -J$J -R$R -O -K >> $PS

#add on the users choice of stations

gmt psxy $stations -St0.4 -Gred -Wthin,red -J$J -R$R -O -K >> $PS

#for use on mac
open $PS
#for use on linux
#evince $PS