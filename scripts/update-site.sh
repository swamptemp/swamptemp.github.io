#!/bin/bash

sleep 15
cd /home/pi/swamptemp.github.io
git add temperature.js
git add images/history.png
git add images/humidity.png 
git commit -m "Update live temperature on site"
git push
