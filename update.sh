#!/bin/bash
today=$(date +%F)
python3 openphish-pihole.py

git add openphish.txt
git commit -m "Update for $today"
git push
