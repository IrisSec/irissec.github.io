---
title: Isabelle's Bad OPSEC 1
author: skat
categories: osint
layout: post
---

> Isabelle has some really bad opsec! She left some code up on a repo that definitely shouldnt be public. Find the naughty code and claim your prize.
> 
> Finishing the warmup OSINT chal will really help with this chal
> 
> The first two characters of the internal of this flag are 'c0', it may not be plaintext Additionally, the flag format may not be standard capitalization. Please be aware
> 
> Made By: Thomas

We are now told that Isabelle has left some code up on a repository that is publicly accessible. Because we were able to get our foot in the door by finding her Twitter in the previous challenge, we can deduce from another tweet that she has a GitHub account. For the uninitiated, GitHub is one such website hosting git repositories for code. The information from this tweet is consistent with the information from the challenge description suggesting she has a code repository somewhere:

![](/uploads/2020-07-26/img02.png)

The next step is to find out where her GitHub is. A quick search of "HackerIsabelle" returns no positive results. We can again use her tweets to deduce some facts about her.

Clue #1: her Twitter bio referencing "0x15ABE11E."

![](/uploads/2020-07-26/img03.png)

Clue #2: a tweet referencing "0x15ABE11E."

![](/uploads/2020-07-26/img04.png)

Clue #3: a tweet again referencing "0x15ABE11E."

![](/uploads/2020-07-26/img05.png)

From clues #1-3, we can deduce that "0x15ABE11E" may be a possible alias and possibly a username that she might use, or if not then at least another string she might mention elsewhere.

Clue #4: a reference to "mimidogz" and an error.

![](/uploads/2020-07-26/img06.png)

There are a few more references to mimidogz, but this is perhaps the most significant one as the error referenced suggests that mimidogz is a program. We can deduce that this may be the name of a project that Isabelle is working on.

Clue #5: a tweet referencing "IsabelleOnSecurity."

![](/uploads/2020-07-26/img07.png)

From this clue, we can deduce that "IsabelleOnSecurity" is a possible username.

From these three sets of clues, we can query GitHub for any one of "0x15ABE11E," "mimidogz," or "IsabelleOnSecurity" to reach her GitHub profile.

![](/uploads/2020-07-26/img08.png)

Looking into "mimidogz," we arrive at a code repository.

![](/uploads/2020-07-26/img09.png)

Looking into the `dogz.py` program, we find an interesting chunk of code from lines 40-41.

```python
# Driver Code 
  DRIVER_CODE = "c3BhZ2hldHRp=="
```

This base64 string just decodes to "spaghetti," but could it have been something else in a previous version of this project? When we check the blame for this file, we can see that the driver code was not always that string.

![](/uploads/2020-07-26/img10.png)

Checking out that specific commit allows us to see the changes made.

![](/uploads/2020-07-26/img11.png)

A quick base64 decoding of the string from the older version gives us the flag.

```
[skat@osiris:~] $ echo "dWl1Y3Rme2MwbU0xdF90b195b3VyX2RyM0BtNSF9==" | base64 -d 2>/dev/null
uiuctf{c0mM1t_to_your_dr3@m5!}
```

**Let's talk about how these techniques and tactics can be applied to real life OSINT engagements now.** It's very common in a real life engagement to have to pivot from one platform to another. In this case, it was from Twitter to GitHub. Users might not have the same username from platform to platform, but there are plenty of ways to find them. On many platforms, you can perform a search by email address or phone number. Here, we were able to use deductive reasoning in order to accomplish this.

Something that I've noticed about people is that *we talk a lot*. You don't need to phish out someone's answers to their security questions because they'll oftentimes just give it to you! Whether it's birthdays, their favorite bands, their favorite cars or their elementary schools or the names of their first pets, it usually only takes a few minutes of scrolling through their online activity to find this information *because they don't keep it a secret to begin with*. Because Isabelle was publicly talking about her project, we were able to pivot from Twitter to GitHub by knowing the name of the project as well as some other tidbits of information about her such as potential usernames.

In a real life OSINT engagement, *it is important to understand the value of a person's ego*. By paying attention to someone's likes, dislikes, projects, friends, background, etc. you can learn a lot about a target. Is your engagement against a drug ring? Check out their social media friends and follows. Check out their Instagram highlights where they openly flaunt around gang and drug paraphernalia. A person's ego can fuel their pride but it can also fuel your operation.

> "To the people in the audience, the h4x0rz, lose the ego ... Cred is your enemy, don't talk about the s\*\*\* that you're doing."
> \- Zoz, DEFCON 22 "Don't F\*\*\* It Up!"
