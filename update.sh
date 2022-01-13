#!/bin/bash
today=$(date +%F)

python3 openphish-pihole.py

git add .
git commit -m "Update for $today"
output=$(git push >/dev/null)

# let cron generate a message if things go poorly
if [ "$?" != "0" ]; then
  echo $output
fi
