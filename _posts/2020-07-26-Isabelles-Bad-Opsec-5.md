---
layout: post
title: "Isabelle's Bad Opsec 5 [OSINT]"
description: "solved by skat"
---

### Writeup by skat

> Isabelle had one more secret on her youtube account, but it was embarrassing.
> 
> Finishing previous OSINT Chals will assist you with this challenge
> 
> The first two characters of the internal of this flag are 'hi', it may not be plaintext
> 
> The flag capitalization may be different, please be aware

The words that pop out to me here are "had" and "was." These words imply that this secret used to be there, but isn't anymore. Is there a way to access previous versions of a web page?

Yes, yes there is! The [Wayback Machine](https://archive.org/) is a project by Archive.org that saves snapshots of web pages at different points in time. Let's see if a historical snapshot of her YouTube channel is available.

As of writing this, the snapshot has unfortunately been removed so I cannot provide a screenshot. However, the solution was to view the historical snapshot of the site and the flag is hidden in the URL of the "My website" link seen in Opsec 2. The flag this time was `UIUCTF{hidd3n_buT_neVeR_g0n3}`.

**In real-life OSINT engagements,** we learn that it's possible to recover historical data on the internet. If a website tried to "scrub" some data, it's possible that a snapshot of it pre-scrub might be saved somewhere on the internet. Viewing this historical snapshot can uncover things like addresses, links, incriminating texts and documents, etc.
