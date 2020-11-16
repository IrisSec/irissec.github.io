---
title: Isabelle's Bad OPSEC 2
author: skat
categories: osint
layout: post
---

> Wow holy heck Isabelle's OPSEC is really bad. She was trying to make a custom youtube api but it didnt work. Can you find her channel??
> 
> Finishing Isabelle's Opsec 1 will may you with this challenge
> 
> The first two characters of the internal of this flag are 'l3', it may not be plaintext Additionally, the flag format may not be standard capitalization. Please be aware
> 
> Made By: Thomas

Looks like we need to find Isabelle's YouTube channel now. The challenge description mentions that she was trying to make a custom YouTube API, which was something that we actually saw in the last challenge as another repository on Isabelle's GitHub account. Let's go ahead and see what that repository has to offer.

![](/img/uiuctf2020/img12.png)

Having a look through the commit log and seeing the most recent commit brings us to this:

![](/img/uiuctf2020/img13.png)

It looks like we've found a channel ID that was deleted in a commit. On YouTube, channel URLs are in the format `www.youtube.com/channel/<ID>`, so let's so ahead and see if that channel exists. Upon visiting the expected channel URL, we can see that the channel does indeed exist.

![](/img/uiuctf2020/img14.png)

After exploring her channel for a little bit, we see some outgoing links to her Twitter and website.

![](/img/uiuctf2020/img15.png)

Clicking on the link to her website brings us to the following: `https://uiuc.tf/?flag=uiuctf%7Bl3g3nd_oF_zeld@_m0re_like_l3gend_0f_l1nk!%7D`

Looks like the flag is in the URL! All we have to do before submitting is change `%7B` and `%7D`, which are just [percent encoded](https://en.wikipedia.org/wiki/Percent-encoding), into their ASCII `{` and `}` counterparts, respectively.

**So what have we learned?** Perhaps the most important lesson is understanding the importance of understanding data leakage. It might surprise you, but it's actually incredibly common for people to accidentally leave out API keys, SSH keys, or other sensitive information and then try to fix it with just a new commit. *One of the many intended features of git is the ability to explore a repository at a previous point in time.* Data leakage is very real, and understanding how you can detect and interpret data leakage can be a valuable skill during OSINT operations to better assess a target.
