---
layout: post
title: "Isabelle's Bad Opsec 3 [OSINT]"
description: "solved by skat, not_really"
---

### Writeup by skat

> Isabelle has a youtube video somewhere, something is hidden in it.
> 
> Solving Previous OSINT Chals will help you with this challenge
> 
> The first two characters of the internal of this flag are 'w3', it may not be plaintext. Additionally, the flag format may not be standard capitalization. Please be aware
> 
> Made By: Thomas

Now that we've found Isabelle's YouTube channel, it looks like we need to find a video and some information hidden in the video. As we saw in the previous level, Isabelle has [one video uploaded](https://www.youtube.com/watch?v=djhRaz3viU8).

Something I noticed about this level is that the captions were absent for the last second of the video. Immediately, this becomes a source of suspicion. For this level, I have to credit my teammate [[nope]] for discovering the hidden data inside of one of the caption files.

![](/img/uiuctf2020/img16.png)

I must admit that without my teammate [[nope]], I would not have gotten this. I was actually trying to perform all sorts of steganography on the video to see if there might have been something hidden in the video or audio streams.

**Applying this to real life OSINT now,** we learn that sometimes evidence may be left behind by the *community* surrounding a target and not necessarily by the target themselves. In this case, it was left behind in a community-driven set of captions for a video as opposed to being left behind by the target Isabelle herself. For example, if you're in an OSINT engagement and investigating a group of covert suspects that are roaming around an area, you might benefit from looking at photos geotagged near the area recently posted to social media to track their movement and path. OSINT, while it may have a target, can gather valuable information from sources other than the target themselves.
