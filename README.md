# openphish-pihole

## tl; dr- Add this to Pihole

`https://raw.githubusercontent.com/invisiblethreat/openphish-pihole/main/openphish.txt`

## Details

Using the feed at https://openphish.com/phishing_feeds.html to generate a Pihole
compatible blocklist that is updated twice-daily. This matches the update
cadence of the upstream feed.

## Processing

The upstream list is URLs, and upon examination, regardless of the path, there
is value in blocking the entire domain. The one known class of false-positive
that is created when extracting the domain from the URL is URL shorteners, like
bit.ly. This is acceptable for the conferred protection and is not corrected for
at this time. Permitting URL shorteners explicitly will overcome this.

## Expiry

The feed is currently configured to retain all domains for 180 days.
`metadata.json` is useful for understanding the age and last observation of the
domain in question.

## Growth/Size

The retention is set to 180 days on this list, and having finally crossed the
180 day mark, the list has now started to expire domains that haven't been
re-observed. At this time, 2022-07-07, the list contains 95k entries.
