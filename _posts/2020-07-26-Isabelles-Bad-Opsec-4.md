---
title: Isabelle's Bad OPSEC 4
author: skat
categories: osint
layout: post
---

> Isabelle hid one more secret somewhere on her youtube channel! Can you find it!?
> 
> Finishing previous OSINT Chals will assist you with this challenge
> 
> The first two characters of the internal of this flag are 'th', it may not be plaintext
> 
> Additionally, the flag format may not be standard capitalization. Please be aware
> 
> Made By: Thomas [Authors Note] I love this chal because I used it IRL to find out who someone cyberbullying a friend was. It's real OSINT -Thomas

We're not given much more to go off of here except for the fact that it's somewhere on her YouTube channel. I admit that this is actually one of the more difficult OSINT challenges in this series, and was actually the one that I finished last. This was truly a subtle challenge.

Looking at the YouTube channel, we notice something strange. Can you see it?

![](/img/uiuctf2020/img14.png)

The channel banner image is very oddly cropped, to say the least. Something interesting about YouTube (and many sites, actually) is that it serves a different version of a webpage depending on your user agent. If you're on a smartphone, then the dimensions of the smartphone are taken into account and you're served a website tailored to your smaller screen. On a standard laptop monitor like mine, I'm served a version of the website tailored to my screen size. In each of these differently-tailored versions of the same website, images can likewise be cropped.

Would it be possible to retrieve the full image somehow? Simply inspecting the element using the Chrome and opening up the URL to the image just brings us to the post-cropped version.

![](/img/uiuctf2020/img17.jpg)

Upon looking at the source code of the page and looking for banners, we notice that YouTube does indeed serve different banners based on whether you're on mobile, a desktop, or a television. We can see the URL to the banner that they serve to televisions after a closer look.

![](/img/uiuctf2020/img18.png)

Going there brings us to the flag!

![](/img/uiuctf2020/img19.jpg)

I again must admit that this was difficult and a real step away from the obvious due to how incredibly subtle it is. What I was actually initially trying to do was use the account's Google Plus ID, a hidden artifact of a long-dead legacy in YouTube, to track Isabelle's activity across the internet, such as seeing her Google Maps reviews for instance.

You can see her Google ID here, hidden away in the source code and forgotten to be scrubbed by YouTube developers for years, still leaving a legacy in the source code:

![](/img/uiuctf2020/img20.png)

Using the Google Plus ID, `100881987903947537523`, we can track the account's activity across different Google platforms such as Maps reviews. Isabelle's can be found at [google.com/maps/contrib/100881987903947537523/reviews/](https://www.google.com/maps/contrib/100881987903947537523/reviews/). 

![](/img/uiuctf2020/img21.png)

Once again, this wasn't the solution. This was just something that I tried and discovered about Google platforms, and possibly something that I'll be incorporating into real-life OSINT engagements in the future. Imagine going to someone's YouTube channel, getting their Google Plus ID, and then getting their approximate location based on their Google Maps reviews! This might make for an interesting future challenge if any potential CTF organizers are reading this (*hint hint, nudge nudge*).

**Applying the solution to real-life OSINT now,** we learn that you should explore features provided to different platforms in order to gain a fuller picture of your target. Here, different images were served to mobile, desktop, and television users. In a real-life engagement, some information might only be accessible to mobile users, or only to desktop users, or only to television users, or any other variant of this that you can think of. Snapchat, for example, is a mobile-focused platform and you won't get very far with it from your laptop. This is not to say that you need to own different devices! User-agent spoofing is very much real, as are emulators and virtual machines. Like we saw here, we were able to access information served to television devices by carefully studying the YouTube platform through inspecting the website source code.
