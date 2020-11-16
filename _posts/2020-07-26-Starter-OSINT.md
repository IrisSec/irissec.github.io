---
title: Starter OSINT
author: skat
categories: osint
layout: post
---

> Our friend isabelle has recently gotten into cybersecurity, she made a point of it by rampantly tweeting about it. Maybe you can find some useful information ;).
> 
> While you may not need it, IsabelleBot has information that applies to this challenge.
> 
> Finishing the warmup OSINT chal will really help with all the other osint chals
> 
> The first two characters of the internal of this flag are 'g0', it may not be plaintext
> 
> Made By: Thomas (I like OSINT)

All OSINT operations have some sort of information as a starting point, a "given" if you will. What we know right now is that someone **named** "Isabelle" has gotten into **cybersecurity** and has been **tweeting** about it. This statement alone allows us to start with three pieces of valuable information:

1. They're named Isabelle.
2. They're into cybersecurity.
3. They're on Twitter.

There's also the additional clue from IsabelleBot located in the Discord server of the event, who seems to know something that can help us. After running the `!help` command on IsabelleBot, we get a list of commands she supports:

> Here's a list of all my commands:,eventtime, flag, help, ping, timeleft,
> You can send !help [command name] to get info on a specific command!
> 
> Oh yeah, there is also the hoodie command and the bet command. Ah yes. You can try networking with me with !socials.
> I also totally forgot the currency stuff. That's work,bet,transfer,balance,inventory,shop, and buy.

That `!socials` command looks really interesting, especially since we know that Isabelle is located on Twitter. When we run that command, she sends us another clue:

> I'm a hacker, but I'm also Isabelle. Maybe you could call me... IsabelleHacker? No, that sounds strange... Whatever, it will be something like that.

Now we know that her username is *like* "IsabelleHacker," and so we can deduce some possible usernames that she might use:

- IsabelleHacking
- IsabelleHack
- IsabelleSecurity
- HackingIsabelle
- HackerIsabelle
- SecurityIsabelle

After querying Twitter for users with usernames similar to this, we stumble upon a positive result from "HackerIsabelle."

![](/uploads/2020-07-26/img00.png)

Looks like we've found her! Let's do some digging into her account to see if anything interesting or valuable to us pops up. Something interesting about Twitter is that replies are automatically hidden from the primary profile page, and you actually have to go into "Tweets \& replies" in order to see replies *in addition* to regular tweets.

After some scrolling, we stumble upon the flag in a tweet.

![](/uploads/2020-07-26/img01.png)

Now that we've found the flag, let's shift focus from the competition's environment to the real-world environment. **How can this be applied in real life?**

In real life OSINT engagements, you'll often times have only a minimum amount of information to go off of. It's important that you can understand to the fullest extent possible the value of the information that you do have. I recall from the National Cyber League last season an OSINT challenge in which we were given a few vague pictures pointing to a location and the only things we could go off of were a few vague highway signs, but we were able to deduce the exact location based on the (cropped) texts of the signs, the rural-like backgrounds of the pictures, and hell, even the shape and color of the signs!

When you're given a starting point in an OSINT engagement, study it, understand it, and think of every single possible implication of the given information to the fullest extent possible in order to get your foot into the door of the investigation.
