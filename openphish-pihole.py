#!/usr/bin/env python3
import requests
from datetime import datetime
from tldextract.tldextract import extract

url = 'https://openphish.com/feed.txt'
def extract_fqdn(fqdn):
    parts = extract(fqdn)
    if parts.subdomain == '' or parts.subdomain == None:
        return f"{parts.domain}.{parts.suffix}"

    return f"{parts.subdomain}.{parts.domain}.{parts.suffix}"


def list_from_lines(lines):
    sites = set()
    for line in lines:
        reflow = extract_fqdn(line)
        sites.add(reflow)
    return sites


req = requests.get(url)


feed = list_from_lines(req.text.splitlines())

with open('openphish.txt', 'w') as f:
    print(f'# Generated from {url} on {datetime.utcnow()}', file=f)
    for site in sorted(feed):
        print(site, file=f)
