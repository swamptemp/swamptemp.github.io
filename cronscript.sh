#!/bin/bash

cd /home/pi/swamptemp.github.io/

# Get temperature:
python get-temp.py

sleep 2
R -f plot-history.R

# Push to website
sleep 15
git add temperature.js
git add history.png
git add humidity.png 
git commit -m "Update live temperature on site"
git push
