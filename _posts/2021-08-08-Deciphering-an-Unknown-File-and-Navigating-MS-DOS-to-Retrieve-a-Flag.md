---
title: Deciphering an Unknown File and Navigating MS-DOS to Retrieve a Flag
author: skat
categories: forensics
layout: post
---

*This writeup is also readable on my [GitHub repository](https://github.com/shawnduong/zero-to-hero-hacking/blob/master/writeups/closed/2021-uiuctf.md) and [personal website](https://shawnd.xyz/blog/2021-08-19/Deciphering-an-Unknown-File-and-Navigating-MS-DOS-to-Retrieve-a-Flag).*

This is a writeup for a great forensics challenge that I did at UIUCTF 2021 where I found yet another reason to despise Microsoft -- something I openly welcome! This challenge involves an unknown file format, navigating MS-DOS, uncovering hints communicated through IRC logs, and finally performing the necessary actions to retrieve a flag by recovering a deleted file.

## forensics/SUPER

*Challenge written by WhiteHoodHacker.*

> HOT

Files: [`SUPERHOT`](/uploads/2021-08-08/SUPERHOT)

Checksum (SHA-1):

```
7c1d4e72a35cb9152bee0fa3e611ea8ce0ae44ff  SUPERHOT
```

As with any challenge, let's first get oriented by finding out what kind of file we're dealing with. It doesn't seem like we have a straight objective given to us just yet, so maybe we'll stumble on it later once we start digging around. Let's find out what kind of `file` this is:

```sh
[skat@anubis:~/work/UIUCTF] $ file SUPERHOT
SUPERHOT: data
```

Oh, well it looks like `file` is unable to recognize what kind of format it is. Let's have a look at the hexdump associated with this file and see if there's anything weird going on with the file format. We can view this file's hexdump with `xxd`:

```sh
[skat@anubis:~/work/UIUCTF] $ xxd SUPERHOT
```

<img src="/uploads/2021-08-08/s_img00.png" style="height: 1024px; width: auto"/>

This is the part in the writeup where I make an obligatory [SUPERHOT](https://www.youtube.com/watch?v=vrS86l_CtAY) joke: Superhot is the most innovative shooter I've played in years!

Stating the obvious here: the file is nearly chock-full of "SUPERHOT." Confused for a little while, I vaguely recalled how similar this seemed to a challenge that I did with my team a few seasons ago at the National Cyber League involving a database file that had been repeatedly XORed, relying on the idea that most hackers should know that null bytes are extremely common in any file format in order to put 2 and 2 together to realize that the repeating data was the XOR key, and that the original file could be recovered by just XORing it with the key again. My teammates had the same idea circulating:

<img src="/uploads/2021-08-08/s_img01.png" style="height: 415px; width: auto"/>

"SUPERHOT" always being aligned was vital to making the XOR work since "SUPERHOT" XOR "SUPERHOT" would nullify the bytes, and any misalignment could cause catastrophic, snowballing failure down the line. zkldi was able to verify that all "SUPERHOT" started at some offset satisfying i = (0 + 8n) and ended at some offset satisfying i = (7 + 8n), where n begins at 0 and extends for the length of the file. With this, I spun up some quick Python and recovered the original file:

```python
#!/usr/bin/env python3

KEY = b"SUPERHOT"

def main():

    data = open("./SUPERHOT", "rb").read()
    out  = bytearray()

    for i in range(len(data)):
        out.append(data[i] ^ KEY[i % len(KEY)])

    open("./out", "wb").write(out)

if __name__ == "__main__":
    main()
```

It takes just a second to run the script until we get...

```sh
[skat@anubis:~/work/UIUCTF] $ ./script.py
[skat@anubis:~/work/UIUCTF] $ ls
out  script.py  SUPERHOT
[skat@anubis:~/work/UIUCTF] $ file out
out: data
```

Well that seems disappointing at first glance, but closer inspection of the file header reveals that `file`'s signature detection has just simply failed -- we have, in actuality, recovered some sort of distinguishable format!

```sh
[skat@anubis:~/work/UIUCTF] $ xxd out | head -10
00000000: 636f 6e65 6374 6978 0000 0002 0001 0000  conectix........
00000010: 0000 0000 0000 0200 2866 3c22 7662 6f78  ........(f<"vbox
00000020: 0006 0001 5769 326b 0000 0000 8000 0000  ....Wi2k........
00000030: 0000 0000 8000 0000 1041 103f 0000 0003  .........A.?....
00000040: ffff eeeb 1c9c fe70 17f7 6e4e 8837 f2e8  .......p..nN.7..
00000050: e545 0548 0000 0000 0000 0000 0000 0000  .E.H............
00000060: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000070: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000080: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000090: 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

The "vbox" string would suggest some kind of virtualization going on with VirtualBox, and the "conectix" stumped me for a little bit until I stumbled on [this Wikipedia article.](https://web.archive.org/web/20210731052020/https://en.wikipedia.org/wiki/Windows_Virtual_PC) The moment I saw that Microsoft was involved, I grew a few grey hairs. To put simply:

<center>
	<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/RZ5DgkoLuGI" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</center>
<br>

I sent it to the rest of the team so that we could have some more hands on deck:

<img src="/uploads/2021-08-08/s_img02.png" style="height: 345px; width: auto"/>

Before loading it up in a virtual machine, I wanted to see if anything could be recovered from it through static analysis. Running `strings` to recover plaintext strings, as well as carving the file based on signatures with `binwalk`, I discovered what seemed to be some interesting IRC chat logs:

```
[13:33] *** Joins: white (whitehoodhacker@sigpwny)
[13:33] <white> Dude, you should play SUPERHOT, it's the most innovative game I've played in years!
[13:33] <white> I'll send it to your file server
[13:35] <someradgamer> epic I'll check it out
[13:38] <someradgamer> why does the setup create so many folders?
[13:38] <someradgamer> I have to change directories so many times to reach superhot.exe
[13:39] <white> Have you tried it yet?
[13:40] <someradgamer> yeah, it's just some dumb title screen, how do I play?
[13:40] <white> That *is* the game
[13:40] <white> you just keep repeating the title
[13:45] <white> oh I almost forgot to mention
[13:46] <white> there's a bug where if you SUPERHOT too much, it will SUPERHOT your entire PC
[13:47] <someradgamer> wait what
[13:48] <someradgamer> that doesn't sound HOT
[13:48] <someradgamer> I'm SUPER deleting this now
[13:48] <someradgamer> what the HOT is happening to my SUPER computer!?
[13:48] <SUPERHOT> SUPERHOT SUPERHOT SUPERHOT
[SU:PE] <RHOT> SUPERHOT SUPERHOT SU
PERHOT SUPERHOT
```

It looks like someradgamer installed SUPERHOT to their system, which had set up a bunch of directories during setup. They then tried to delete the file shortly before their entire computer got SUPERHOTed against their will, likely leading to the initial premise of the challenge and the source of the file we got in the first place. If we were to recover this file, perhaps we could see what someradgamer saw moments before their computer got SUPERHOTed.

Let's load this up into VirtualBox and have a look:

<img src="/uploads/2021-08-08/s_img03.png" style="height: 536px; width: auto"/>

As mentioned in the IRC chat logs, there is a long chain of directories created during setup. We have a linear directory tree that we can then travel down until eventually reaching the bottom and finding an empty directory:

<img src="/uploads/2021-08-08/s_img04.png" style="height: 533px; width: auto"/>

I was stuck here for a while until my memory jumped back to this specific message from the IRC chat logs:

```
[13:48] <someradgamer> I'm SUPER deleting this now
```

Doing research brings me to [an article on MS-DOS's `UNDELETE` command.](https://web.archive.org/web/20210212013430/https://easydos.com/undelete.html) Going off of this hunch, I try to see if there's anything to undelete at the bottom of this directory tree. Sure enough, we recovered something!

<img src="/uploads/2021-08-08/s_img05.png" style="height: 535px; width: auto"/>

Invoking the recovered file by its name, we start running the game. It says "SUPER" and then prompts us for some input. The correct response is "HOT," which will then give us the flag:

<img src="/uploads/2021-08-08/s_img06.png" style="height: 534px; width: auto"/>

Frankly, the real challenge was MS-DOS; it took me an embarrassingly long amount of time to figure out how to work the completely unintuitive and clunky MS-DOS system, giving me yet another reason to despise Microsoft! -- not to imply that I'm short on reasons already.

Overall, this was a pretty great challenge! I recalled on my experience with a similar challenge from the National Cyber League a few seasons ago, worked with my team to successfully confirm our hypothesis, and then spent hours -- and I truly mean hours -- trying to figure out how to work MS-DOS while also keeping in mind the IRC chat logs uncovered through static analysis. Although the original premise might not be something I would expect to find in the real-life work of a digital forensics professional, the idea of performing static analysis on the resultant file and navigating through a disk image absolutely is. This challenge was pretty fun and most importantly for me, gave me more ammunition to criticize Microsoft with.
