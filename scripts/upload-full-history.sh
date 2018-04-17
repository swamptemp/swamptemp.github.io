#!/bin/bash
sleep 60
cd /home/pi/swamptemp.github.io/
R -f R/plot-full-history.R
git add images/full-history.png
git add images/full-humidity.png
git add data/
git commit -m "Add full history plots"
git push
