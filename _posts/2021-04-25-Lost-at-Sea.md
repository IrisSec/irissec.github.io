---
title: WPICTF 2021 - Lost at Sea
author: F4_U57
categories: forensics
layout: post
---

# Lost at Sea

> I lost me sea shanties! They are one of the few things that make me happy during the pandemic... and I accidentally deleted them. Here is the disk image. I think there's someone talking about a flag in each of the shanties, if you can manage to recover them.
>
> When you hear the flag ("W P I open curly bracket..."), submit it in all caps and don't include spaces
>
> Files: [me-shanties-disk_img.zip](/uploads/2021-04-25/me-shanties-disk_img.zip)

We were given a disk image, so I opened it in `FTK Imager` and extracted the deleted files.

![](/uploads/2021-04-25/img1.png)

As you can see, we got some audio files.

Each audio file contains the same robotic voice saying the flag out loud, but a different song track. You can hear parts of it: "W P I open curly bracket..." but, it's hard to hear the flag over the song.

I figured I need to isolate the robotic voice to hear the entire flag.

Initially, I had no idea how, but I eventually figured it out after a bit of Googling.

## Isolating the robotic voice

I had to download the original song track.

I opened the original song track and modified song track (one of the deleted audio files) in `Audacity`.

Using the Time Shift Tool within `Audacity`, I aligned them using parts without the robotic voice.

You can align them roughly at the start, then zoom in to align them perfectly. (This part is important, if they are not aligned, this method will not work.)

![](/uploads/2021-04-25/img2.png)

After alignment, select the original song track (double click or Clt-A on it) and invert it (Effect ---> Invert).

Now, select and mix them together (Tracks --> Mix --> Mix and Render).

![](/uploads/2021-04-25/img3.png)

Most of the music is now gone, you should only have the vocals and robotic voice.

You can go further by going to (Effect ---> Voice Reduction and Isolation) and playing around with the slider.

![](/uploads/2021-04-25/img4.png)

That entire process does `modified soundtrack - original soundtrack`, which would highlight the modified parts.

Finally, the robotic voice is much louder.

Flag: `WPI{ICOMEFROMTHEDAYSOFTHEPIRATEBAYWHEREWEWOULDTORRENTANDLEECHALLDAY}`
