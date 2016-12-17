#!/bin/bash
#Script that runs the seismofetch program
seismodir="/Users/rmartinshort/Documents/Berkeley/SeismoFetch/seismofetch"
echo '

Running SeismoFetch program. Useful information about the progress of your request will appear in the terminal

'
cd $seismodir
python GUI_layout.py
