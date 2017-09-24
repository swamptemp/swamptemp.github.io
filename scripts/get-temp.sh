#!/bin/bash

cd /home/pi/swamptemp.github.io/python

# Get temperature:
python get-temp.py

sleep 2
cd ..
R -f R/plot-history.R

