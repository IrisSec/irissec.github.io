---
layout:      post
title:       "Raymonds Recovery [forensics]"
description: "solved by skat"
---

This one is easy. To extract the file system, you can use 7-zip on windows or

`mkdir raymonds_fs_out; sudo mount -o loop raymonds_fs raymonds_fs_out` on linux.

The hint suggests that we're looking for a png, so let's look at the headers.

`for file in *; do echo $file; xxd $file | head -1; done` will look at the top bytes of each file in the folder. For each file, it prints the filename and uses xxd to print the hex with head -1 to print only the first line.

```
7e8bc0dde7339e79edf3a1627ce76b50
00000000: e000 104a 4649 4600 0101 0200 1c00 1c00  ...JFIF.........
also_not_the_flag
00000000: e000 104a 4649 4600 0101 0100 6000 6000  ...JFIF.....`.`.
another_nice_drawing
00000000: e000 104a 4649 4600 0101 0000 0100 0100  ...JFIF.........
art_at_its_finest
00000000: e000 104a 4649 4600 0101 0000 0100 0100  ...JFIF.........
blathers
00000000: 0000 104a 4649 4600 0101 0000 0100 0100  ...JFIF.........
cool_hat
00000000: ffd8 ffe0 0010 4a46 4946 0001 0101 015e  ......JFIF.....^
definitely_not_the_flag
00000000: 2d31 2e33 0a25 c4e5 f2e5 eba7 f3a0 d0c4  -1.3.%..........
even_more_fanart
00000000: db00 4300 0806 0607 0605 0807 0707 0909  ..C.............
even_MORE_fancy
00000000: ffd8 ffdb 0043 0006 0405 0605 0406 0605  .....C..........
fanart
00000000: e000 104a 4649 4600 0101 0000 0100 0100  ...JFIF.........
fancy_shoes
00000000: ffd8 ffe0 0010 4a46 4946 0001 0101 0048  ......JFIF.....H
fos6fy0qcbq41
00000000: e000 104a 4649 4600 0101 0000 0100 0100  ...JFIF.........
gift_from_judy
00000000: e000 104a 4649 4600 0101 0000 0100 0100  ...JFIF.........
goals
00000000: e000 104a 4649 4600 0101 0100 6000 6000  ...JFIF.....`.`.
great_design
00000000: 2d31 2e33 0d0a 25e2 e3cf d30d 0a0d 0a31  -1.3..%........1
I_love_my_fans
00000000: e000 104a 4649 4600 0101 0000 0100 0100  ...JFIF.........
lost+found
xxd: Is a directory
might_be_the_flag_but_you_dont_know
00000000: 2d31 2e33 0a25 c4e5 f2e5 eba7 f3a0 d0c4  -1.3.%..........
more_fanart
00000000: e000 104a 4649 4600 0101 0100 4800 4800  ...JFIF.....H.H.
more_hats
00000000: ffd8 ffe0 0010 4a46 4946 0001 0101 0060  ......JFIF.....`
my_fav_art
00000000: 0000 000d 4948 4452 0000 0280 0000 0280  ....IHDR........
office_art
00000000: e000 104a 4649 4600 0101 0101 2c01 2c00  ...JFIF.....,.,.
office_supplies_art
00000000: e000 104a 4649 4600 0101 0000 0100 0100  ...JFIF.........
read_later
00000000: 2d31 2e33 0a25 c4e5 f2e5 eba7 f3a0 d0c4  -1.3.%..........
really_important
00000000: e000 104a 4649 4600 0101 0000 0100 0100  ...JFIF.........
self_portrait
00000000: e000 104a 4649 4600 0101 0000 0100 0100  ...JFIF.........
style_inspo
00000000: e000 104a 4649 4600 0101 0101 2c01 2c00  ...JFIF.....,.,.
very_important_records
00000000: 2d31 2e33 0a25 c4e5 f2e5 eba7 f3a0 d0c4  -1.3.%..........
```

JFIF is a jpeg, so we can cross those off the list.

```
definitely_not_the_flag
00000000: 2d31 2e33 0a25 c4e5 f2e5 eba7 f3a0 d0c4  -1.3.%..........
even_more_fanart
00000000: db00 4300 0806 0607 0605 0807 0707 0909  ..C.............
even_MORE_fancy
00000000: ffd8 ffdb 0043 0006 0405 0605 0406 0605  .....C..........
great_design
00000000: 2d31 2e33 0d0a 25e2 e3cf d30d 0a0d 0a31  -1.3..%........1
might_be_the_flag_but_you_dont_know
00000000: 2d31 2e33 0a25 c4e5 f2e5 eba7 f3a0 d0c4  -1.3.%..........
my_fav_art
00000000: 0000 000d 4948 4452 0000 0280 0000 0280  ....IHDR........
read_later
00000000: 2d31 2e33 0a25 c4e5 f2e5 eba7 f3a0 d0c4  -1.3.%..........
very_important_records
00000000: 2d31 2e33 0a25 c4e5 f2e5 eba7 f3a0 d0c4  -1.3.%..........
```

Aha, we see IHDR, but it doesn't have the PNG magic. Let's see what the image looks like right now.

![image-20200721204648751](/img/uiuctf2020/image-20200721204648751.png)

And then we can open any other png we have lying around to see what it looks like.

![image-20200721204823436](/img/uiuctf2020/image-20200721204823436.png)

Aha, this image has eight extra bytes that my_fav_art doesn't have. Let's copy them and put them into my_fav_art.

![image-20200721204731703](/img/uiuctf2020/image-20200721204731703.png)

After renaming it to .png we get this.

![image-20200721205012522](/img/uiuctf2020/image-20200721205012522.png)