#!/bin/bash
today=$(date +%F)

python3 openphish-pihole.py

git add .
commit=$(git commit -m "Update for $today" 2>&1)
output=$(git push 2>&1)

# let cron generate a message if things go poorly
if [ "$?" != "0" ]; then
  echo "Commit message:\n$commit\n\nPush response:\n$output"
else
  curl -s 'http://172.18.0.35:3001/api/push/8aQF38JkuW?msg=OK&ping=' > /dev/null
fi
