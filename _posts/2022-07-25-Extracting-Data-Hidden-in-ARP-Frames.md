---
title: Extracting Data Hidden in ARP Frames
author: skat
categories: forensics
layout: post
---

*This writeup is also readable on my [GitHub repository](https://github.com/shawnduong/zero-to-hero-hacking/blob/master/writeups/closed/2022-imaginaryctf.md) and [personal website](https://shawnd.xyz/blog/2022-07-28/Extracting-Data-Hidden-in-ARP-Frames).*

This is one of my three writeups from ImaginaryCTF. This particular challenge deals with data being discreetly embedded in link layer (layer 2) ARP frames in a given pcapng file, and my solution involved extracting all relevant ARP frames with Python and reassembling the data.

## forensics/tARP

*Challenge written by Eth007.*

> It helps to have a rain tarp when there's bad weather.

Files: [`tarp.pcapng`](/uploads/2022-07-25/01/tarp.pcapng)

Checksum (SHA-1):

```
3cb62d7136be8ca3ad2838c2fd2e1358dc570c63  tarp.pcapng
```

To start, we can begin with a cursory analysis of the given pcapng file:

![](/uploads/2022-07-25/01/img00.png)

There are 30791 frames in the pcapng with the bulk of them being QUIC (**Q**uick **U**DP **I**nternet **C**onnections) and ARP (**A**ddress **R**esolution **P**rotocol). 22137 (71.89%) of these contain IPv4 data, 20456 (92.41%) of which are UDP and the remainder being TCP.

Scrolling through the pcapng, something interesting becomes apparent amid a sudden rapid torrent of ARP frames:

![](/uploads/2022-07-25/01/img01.png)

The frame destinations being `00:00:00:00:00:00` may look strange at first, but this is actually rather standard for ARP and is an acceptable broadcast address in addition to the also common `FF:FF:FF:FF:FF:FF`, depending on the specific implementation; this is not abnormal. What *is* abnormal, however, are (1) the seeming randomness of the target IPs that `F6:6B:50:99:AA:10` are trying to resolve, (2) the speed at which the frames are being transmitted, and (3) the lack of responses to these ARP requests.

A closer inspection of some of these frames reveals what appears to be plaintext data:

![](/uploads/2022-07-25/01/img02.png)

The target IP address of this ARP request, `2F 75 73 72`, translates to `/usr` in ASCII. Indeed, scrolling through these frames makes it clear that some sort of data is being transmitted, hidden in the target IPs of ARP requests originating from this host:

![](/uploads/2022-07-25/01/img03.gif)

Curious to explore this, an attack plan is devised: read all broadcasted ARP frames originating from `F6:6B:50:99:AA:10` and write the last 4 bytes of each frame (the target IP) to a buffer, and finally write the buffer to a file for further analysis. My tool of choice for quick scripting like this is, as usual, Python:

```python
#!/usr/bin/env python3

from scapy.all import *

def main():

    frames = rdpcap("./tarp.pcapng")
    arp = [f for f in frames if ARP in f and
        f.src == "f6:6b:50:99:aa:10" and f.dst == "00:00:00:00:00:00"]

    data = b""

    for f in arp:
        data += bytes(f.payload)[-4:]

    with open("./output.bin", "wb") as f:
        f.write(data)

    print("Data written to ./output.bin")

if __name__ == "__main__":
    main()
```

Running this script and then carving the resultant file, sure enough, finds a PNG:

![](/uploads/2022-07-25/01/img04.png)

This PNG, however, cannot be viewed quite yet due to a CRC error in the IEND chunk. I can already tell from experience that this is usually due to some extra data in the IEND chunk, probably from some subsequent frames unrelated to the PNG:

![](/uploads/2022-07-25/01/img05.png)

Viewing the PNG's IEND chunk under a hex editor, we can see that there are indeed 4 extra bytes following the true end of the PNG. Removal of these bytes result in the computed CRC matching the expected CRC, and the PNG can now be viewed normally:

![](/uploads/2022-07-25/01/img06.png)

![](/uploads/2022-07-25/01/img07.png)

This was a very cool challenge and it's definitely not unheard of in the real world to hide data in other protocols! I love seeing networking anywhere in CTFs, so this challenge was a lot of fun to do. By analyzing a pcapng and noticing an irregularity in ARP frames, we quickly extracted, analyzed, and viewed data discreetly embedded in a link layer (layer 2) protocol.

Happy hacking!
