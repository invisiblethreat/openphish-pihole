#!/usr/bin/env python3
import json
import requests
from datetime import datetime, timedelta
from tldextract.tldextract import extract

url = 'https://openphish.com/feed.txt'
expiry = 120
changelog = 'changelog.md'
metadata = 'metadata.json'
output = 'openphish.txt'

def extract_fqdn(fqdn):
    parts = extract(fqdn)
    if parts.subdomain == '' or parts.subdomain == None:
        return f"{parts.domain}.{parts.suffix}"

    return f"{parts.subdomain}.{parts.domain}.{parts.suffix}"


def set_from_lines(lines):
    sites = set()
    for line in lines:
        reflow = extract_fqdn(line)
        # leverage artifact form tldextract that returns IP address as subdomain
        # and causes a trailing `.` from extract_fqdn. PiHole can't use these.
        if line.endswith('.'):
            continue
        sites.add(reflow)

    return sites

def get_openphish(url):
    req = requests.get(url)
    feed = set_from_lines(req.text.splitlines())

    return feed


def write_feed(feed):
    with open(output, 'w') as f:
        print(f'# Generated from {url} on {datetime.utcnow()}', file=f)
        for site in sorted(feed):
            print(site, file=f)

def build_feed(feed, metadata=metadata, expiry=expiry, changelog=changelog):
    # load metadata
    with open(metadata, 'r') as fm:
        meta = json.load(fm)

    now_dt = datetime.utcnow()
    now_ts = now_dt.timestamp()

    adds = set()

    # check to see if site is already in the list
    for site in feed:
        if site in meta:
            # Keep the finding active
            meta[site]["last_seen"] = now_ts
        else:
            # add a new fqdn
            init = {"first_seen": now_ts, "last_seen": now_ts}
            meta[site] = init
            adds.add(site)

    expire = set()
    for site, times in meta.items():
        last_seen_dt = datetime.fromtimestamp(times['last_seen'])
        delta = now_dt - last_seen_dt
        if delta.days > expiry:
            # you can't delete while iterating
            expire.add(site)

    with open(changelog, 'a') as cl:
        print(f'### {now_dt} Changelog\n\n#### Adding\n', file=cl)
        for add in sorted(adds):
            print(f"  - {add}", file=cl)
        print('\n#### Expiring\n', file=cl)
        for expired in sorted(expire):
            del(meta[expired])
            print(f"  - {expired}", file=cl)

        print('', file=cl)

    with open(metadata, 'w') as fm:
        json.dump(meta, fm, sort_keys=True, indent=4)

    return set(meta.keys())

live_feed = get_openphish(url)
feed = build_feed(live_feed)
write_feed(feed)
