#!/bin/bash

cd /home/pi/swamptemp.github.io/
git add images/full-history.png
git add images/full-humidity.png
git add data/
git commit -m "Add data files"
git push
