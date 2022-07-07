#!/usr/bin/env python3
import json
import requests
from datetime import datetime, timedelta
from tldextract.tldextract import extract

url = 'https://openphish.com/feed.txt'
expiry = 180
changelog = 'changelog.md'
metadata = 'metadata.json'
output = 'openphish.txt'


def extract_fqdn(fqdn):
    '''Extract the FQDN from the URL'''
    parts = extract(fqdn)
    if parts.subdomain == '' or parts.subdomain == None:
        return f"{parts.domain}.{parts.suffix}"

    return f"{parts.subdomain}.{parts.domain}.{parts.suffix}"


def set_from_lines(lines):
    '''Transform the list of lines from the feed into a set of FQDNs'''
    sites = set()
    for line in lines:
        reflow = extract_fqdn(line)
        # leverage artifact form tldextract that returns IP address as subdomain
        # and causes a trailing `.` from extract_fqdn. PiHole can't use these.
        if reflow.endswith('.'):
            continue
        sites.add(reflow)

    return sites


def get_openphish(url):
    '''Get the current OpenPhish feed and return a list'''
    req = requests.get(url)
    feed = set_from_lines(req.text.splitlines())

    return feed


def write_feed(feed):
    '''Write the feed to the file to be consumed'''
    with open(output, 'w') as f:
        print(f'# Generated from {url} on {datetime.utcnow()}', file=f)
        for site in sorted(feed):
            print(site, file=f)


def write_changelog(changelog=changelog, adds=set([]), expire=set([]), now=datetime.utcnow()):
    '''Write the changelog. Exit without changes if adds and expire are empty'''
    # nothing to see here, move along
    if len(adds) == 0 and len(expire) == 0:
        return

    with open(changelog, 'a') as cl:
        print(f'### {now} Changelog\n', file=cl)
        if len(adds) != 0:
            print(f'  - Adding {len(adds)}', file=cl)

        if len(expire) != 0:
            print(f'  - Expired {len(expire)}', file=cl)

        print('', file=cl)


def build_feed(feed, metadata=metadata, expiry=expiry, changelog=changelog):
    '''Build the feed by comparing inbound entries against historical metadata.
    If the item exists, the timestamp is updated. If the item does not exist,
    add the item to the dict as a new entry. If the entriy has not been seen for
    more than 'n' days, remove it as it is inactive.'''
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
            meta[site]["observations"] += 1
        else:
            # add a new fqdn
            init = {"first_seen": now_ts, "last_seen": now_ts, "observations": 1}
            meta[site] = init
            adds.add(site)

    expire = set()
    for site, times in meta.items():
        last_seen_dt = datetime.fromtimestamp(times['last_seen'])
        delta = now_dt - last_seen_dt
        if delta.days > expiry:
            # you can't delete while iterating
            expire.add(site)

    write_changelog(adds=adds, expire=expire, now=now_dt)

    with open(metadata, 'w') as fm:
        json.dump(meta, fm, sort_keys=True, indent=4)

    return set(meta.keys())


live_feed = get_openphish(url)
feed = build_feed(live_feed)
write_feed(feed)
