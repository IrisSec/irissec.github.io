---
title: corCTF 2023 - vmquack's vectorized vices
author: not_really
categories: re
layout: post
---

# rev/vmquack's vectorized vices

> The quacking duck mob at your local pond are now really mad! You broke  their vm based anti-quack system for two years in a row! However, don't rest easy - one of their brightest quackers have designed something absolutely devious with a revamped compiler, inspired after reading a textbook on SIMD programming. Now, the ducks  are confident that their vector based obfuscation scheme will  quack your sanity. Can you quack their quackme now?
>
> Note that this challenge requires AVX-512 F, CD, DQ, BW, and was  verified to work on a Cascade Lake system. The challenge is completely doable and even developed under [Intel SDE](https://www.intel.com/content/www/us/en/developer/articles/tool/software-development-emulator.html).
>
> To help you get started with deobfuscating the VM, we have decided to provide a sample C program (quicksort) along with its obfuscated version.
>
> **By:** FizzBuzz101, anematode

![image-20230730190142707](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230730190142707.png)

It's your standard flag checker. Trade offer: you provide license key, I give you flag.

## Tooling

Sadly, my computer can't run it natively:

![image-20230730201509416](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230730201509416.png)

The description says you can run it on Intel SDE, which works and thankfully has a gdb server. While I'm thankful its gdb server is painless out of the box, I normally use IDA Freeware for debugging since, in my opinion, it's the most stable debugger. It doesn't have GDB in freeware, so once I have a challenge where I have to attach to a remote, I have to switch to the normal GDB. And besides, IDA's decompilation was completely unhelpful:

![image-20230730210826278](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230730210826278.png)

Yeah, very helpful IDA...

And Ghidra didn't even try to disassemble the program:

![image-20230730210924297](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230730210924297.png)

Surprisingly, binja gave actually good results, so that's what I used for the rest of the chal:

![image-20230730211303573](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230730211303573.png)

Sadly, binja's debugger connects to the gdb server, but fails to run the binary. So yep, terminal debugging it is.

## The obfuscator

The challenge provides a sample program, `quicksort` and its source `quicksort.c`. I didn't spend much time here, but I did find a few things.

### Some background on AVX-512 registers

Almost all of the operations performed on the AVX-512 registers (called zmmXX) are as qwords, so we can think of them like arrays of eight 8-byte numbers. In fact, this is how binja shows it:

![image-20230731201224959](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230731201224959.png)

The purpose of SIMD registers is so you can do the same operation on all numbers in a register or registers. So adding two registers fully is more like adding the numbers in each array with each other. ** However, you can apply a "mask" which means only certain elements will be affected. So for example, fully adding two registers might look like this:

```
zmm0[0] = zmm1[0] + zmm2[0]
zmm0[1] = zmm1[1] + zmm2[1]
... etc
zmm0[7] = zmm1[7] + zmm2[7]
```

But a mask of `0b00001010` would be like this:

```
zmm0[1] = zmm1[1] + zmm2[1]
zmm0[3] = zmm1[3] + zmm2[3]
```

In the case of the obfuscator, when a mask was involved, I only ever saw it mask to one item which makes things a bit easier. Also to note, `k0` is the mask register which means "no mask".

### Some common operations

```
mask = _load_mask8(address)
  - Pretty obvious, loads a mask from the address
zmmA = _mm512_mask_compress_epi64(mask, zmmB)
  - Because our mask is only one element, this is basically zmmA[0] = zmmB[log2(mask)]
zmmA = _mm512_broadcastq_epi64(mask, xmmB)
  - Moves the first element of xmmB (which is the same as the first element of zmmB) to every mask elements in zmmA
    If mask is k0, it copies to every element in zmmA
resMask = _mm512_cmp_epi64_mask(mask, zmmA, zmmB, op)
  - Does a compare operation between zmmA and zmmB (see intrinsics guide below for op) and stores results in resMask
flags = _ktest_mask8_u8(mask, mask)
  - flags = mask == 0
```

There are some other ones but they're pretty obvious (add, sub, etc.) The intel intrinsics guide is always helpful for looking up how each instruction works: https://www.intel.com/content/www/us/en/docs/intrinsics-guide/index.html

### Quicksort example

Here's an example of the loop at the top of the main loop:

![image-20230731203948972](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230731203948972.png)

```assembly
k5 = 1
k6 = 64
zmm31[0] = zmm22[6] ; log2(64) = 6
zmm31[0..7] = zmm31[0]
k2 = zmm31[0] >= zmm17[0] ; log2(1) = 0
rflags = k2 == 0
if (rflags) ...
```

This is just a really complicated way to say `zmm31[0] >= zmm22[6]`. The reason `mask_compress` and `broadcastq` is needed is because the instructions only let you do operations at the same index in the register but not at different indices. So, the code copies the 7th element of `zmm22` to all elements of `zmm31`, so no matter what index we want to access from `zmm17`, the corresponding value in `zmm31` will always be the same: `zmm22[6]`.

## First pass of the code

Okay, now that we understand a little about how this obfuscator rolls, let's look at the main function. There's four called functions, each with their own AVX instructions. Maybe it'd be better to figure out which function is the flag checker and which functions are the fancy ASCII art printing ones.

![image-20230731194642831](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230731194642831.png)

Instead of trying to guess what's going on, why not debug it?

![VirtualBoxVM_qI8A8qIvaW](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\VirtualBoxVM_qI8A8qIvaW.gif)

This helps out a lot. The first function call doesn't seem to do anything (at least that we can see), but the second function call prints the text, the third function call reads input, and the fourth one presumably checks the flag. So it's probably a safe bet to look in `sub_3133a120` for the flag checker.

While I was annotating the data pointers in binja, I found some suspicious constants:

![image-20230731205402728](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230731205402728.png)

`0x41 -> 0x5a` are A-Z, `0x30 -> 0x39` are 0-9, and `0x2d` is -. And since the program is looking for a "license key", it'd look like these are our restrictions. Out of the two function calls in `checkFlag_3133a120`, one of them is `sub_313381d0` which uses all of those constants. So I'll call it `checkChars`.

![image-20230731205631853](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230731205631853.png)

Something else I found while debugging around the function is that it seems to return the length of the string. Following the trail of register sets, we see the return value `rax` is eventually compared with 100 (end of first block). If it's not 100, it sets `zmm24` to 0 (end of second block). Is this the fail condition?

Look at the return:

![image-20230731210043566](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230731210043566.png)

Yep, `zmm24` needs to stay 1 until the end of the function.

The only other way to fail is here:

![image-20230731210540637](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230731210540637.png)

This seems to happen right before returning, so most likely the encrypted input is being compared with the correct answer and if any of them are wrong, the win flag is set to false.

Here's a closer look at those blocks:

![image-20230731210735104](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230731210735104.png)

Without decoding the whole thing, we can see at a glance that `var_328[i]` and `3139c7c0[i]` xor'd with `0xdeadbeefbaadf00d` and then compared. `3139c7c0` looks like this:

![image-20230731211153383](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230731211153383.png)

This is probably our target array (xor'd with `0xdeadbeefbaadf00d`).

Time to game this with the debugger. What's the first item in var_328 if we fill the input with all AAAAs?

![image-20230731212057880](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230731212057880.png)

Okay, 4356. What about with all BBBBs?

![image-20230731212213228](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230731212213228.png)

And all CCCCs?

![image-20230731212506934](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230731212506934.png)

It looks like there's a pattern here...

```
4489-4356 = 133
4624-4489 = 135
4761-4624 = 137
```

And the pattern goes on. So I came up with `charCode^2 + 2*charCode + 1`. (`0x41^2 + 2*0x41 + 1 = 4356` as we expect.) However, it's not all that easy. I noticed that it's not the first character in the input that controls that first number, but rather 91st ** (double check this), meaning the input is scrambled somehow. To add to that, the function seems to change on the second iteration:

![image-20230731213145499](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230731213145499.png)

Uh oh...

To make things quicker, I wrote a GDB script to print the value at each iteration:

![image-20230802204112836](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230802204112836.png)

Hm, that's not great. After playing around with the input, I see that there's ten different transformations the input can go through. Time to figure out how they're scrambled and what the transformations are.

## Finding the pattern

The above code isn't the only one reading from `var_328`, there's one more that reads and writes to it:

![image-20230802205151962](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230802205151962.png)

If we follow the chain, we can see that the second to last line modifies the value in `var_328` with the result from `doThing_31338e20`, the only other function call in the main flag checker function. The `doThing` function is very long. Very long:

![image-20230803212634558](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230803212634558.png)

My reaction:

<img src="C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230803212754321.png" alt="image-20230803212754321" style="zoom:50%;" />

While reading it isn't the first thing on my mind, printing out the values it reads and writes are interesting (read is first, then value written is second):

![image-20230802210420896](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230802210420896.png)

Now there's more of a pattern. There's one item of one pattern followed by two items of another pattern, then three items of another pattern, and so on. The indices it reads from `var_328` are also in a pattern. 0, 1, 10, 2, 11, 20... It looks something like this:

```python
scramble_list = [
    [0], # pattern 1 (x^2 + 2*x + 1)
    [1,10], # pattern 2
    [2,11,20], # pattern 3
    [3,12,21,30], # pattern 4
    [4,13,22,31,40], # pattern 5
    [5,14,23,32,41,50], # pattern 6
    [6,15,24,33,42,51,60], # pattern 7
    [7,16,25,34,43,52,61,70], # pattern 8
    [8,17,26,35,44,53,62,71,80], # pattern 9
    [9,18,27,36,45,54,63,72,81,90], # pattern 10
    [19,28,37,46,55,64,73,82,91], # pattern 10
    [29,38,47,56,65,74,83,92], # pattern 9
    [39,48,57,66,75,84,93], # pattern 8
    [49,58,67,76,85,94], # pattern 7
    [59,68,77,86,95], # pattern 6
    [69,78,87,96], # pattern 5
    [79,88,97], # pattern 4
    [89,98], # pattern 3
    [99] # pattern 2
]
```

I figured out the first pattern by eyeballing it, so maybe it was possible to get the others by guessing them too? I started to write a script to set the first element of each pattern to 0, the second to 1, the third to 2, etc. in hopes that I could see a reoccurring pattern. The problem was, `var_328` turns out to be still scrambled. The indices in the above table isn't enough, it's scrambled twice.

So how do you solve it? By putting 100 unique characters into the input and checking where they come out in `var_328`. It turns out there's not quite 100 printable characters, so I overwrote the input's memory with the bytes 0-99.

![image-20230802211528000](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230802211528000.png)

Great, now we have a second list that the input is scrambled into before it gets fed into `doThing`.

```python
scramble_list_2 = [
    [90], # pattern 1 (x^2 + 2*x + 1)
    [80,63], # pattern 2
    [89,99,25], # pattern 3
    [68,87,46,53], # pattern 4
    [85,51,43,39,10], # pattern 5
    [31,79,27,23,13,47], # pattern 6
    [5,2,20,81,58,75,93], # pattern 7
    [70,95,49,29,7,41,84,66], # pattern 8
    [11,14,15,4,60,6,36,64,88], # pattern 9
    [35,0,56,54,98,94,97,74,67,19], # pattern 10
    [37,9,92,62,17,45,52,12,24], # pattern 10
    [73,21,40,28,3,48,59,72], # pattern 9
    [32,26,71,55,61,44,1], # pattern 8
    [78,77,82,42,8,65], # pattern 7
    [34,30,22,16,69], # pattern 6
    [76,57,91,86], # pattern 5
    [50,83,96], # pattern 4
    [38,33], # pattern 3
    [18] # pattern 2
]
```

With that, I brute forced each of the patterns and spent a few hours guessing how it was transformed. I asked ChatGPT a few times, and while it was mostly unhelpful, it did get it a few times. I eventually ended up with this:

```python
def fun1(x):
    return x**2 + 2*x + 1
def fun2(x):
    return x ^ 0xdefaced
def fun3(x):
    return (x-2)**3
def fun4(x):
    # I tweaked this number until it seemed right
    return math.floor(212.43 * x)
def fun5(x):
    return (x+3)**4
def fun6(x):
    return 131072 * x
def fun7(x):
    return (x-4)**3
def fun8(x):
    return x * 0x80000000000
def fun9(x):
    return x**2 + 10*x + 25
def fun10(x):
    return (x**2 + x) // 2
```

If I was not totally sleep deprived I probably would've automated every 0-255 and used a lookup table instead of spending two hours trying to guess the functions. In any case, that gave me the flag:

```python
import math

scramble_list_b = [
    [90], # x^2 + 2x + 1
    [80,63], # 0xdefaced xor x
    [89,99,25], # (x-2)^3
    [68,87,46,53], # floor(212.43*x)
    [85,51,43,39,10], # (x+3)^4
    [31,79,27,23,13,47], # 131072*x
    [5,2,20,81,58,75,93], # (x-4)^3
    [70,95,49,29,7,41,84,66], # x * 0x80000000000
    [11,14,15,4,60,6,36,64,88], # x^2 + 10x + 25
    [35,0,56,54,98,94,97,74,67,19], # (x^2 + x) / 2
    [37,9,92,62,17,45,52,12,24], # (x^2 + x) / 2
    [73,21,40,28,3,48,59,72], # x^2 + 10x + 25
    [32,26,71,55,61,44,1], # x * 0x80000000000
    [78,77,82,42,8,65], # (x-4)^3
    [34,30,22,16,69], # 131072*x
    [76,57,91,86], # (x+3)^4
    [50,83,96], # floor(212.43*x)
    [38,33], # (x-2)^3
    [18] # 0xdefaced xor x
]

scramble_list_a = [
    [0], # x^2 + 2x + 1
    [1,10], # 0xdefaced xor x
    [2,11,20], # (x-2)^3
    [3,12,21,30], # floor(212.43*x)
    [4,13,22,31,40], # (x+3)^4
    [5,14,23,32,41,50], # 131072*x
    [6,15,24,33,42,51,60], # (x-4)^3
    [7,16,25,34,43,52,61,70], # x * 0x80000000000
    [8,17,26,35,44,53,62,71,80], # x^2 + 10x + 25
    [9,18,27,36,45,54,63,72,81,90], # (x^2 + x) / 2
    [19,28,37,46,55,64,73,82,91], # (x^2 + x) / 2
    [29,38,47,56,65,74,83,92], # x^2 + 10x + 25
    [39,48,57,66,75,84,93], # x * 0x80000000000
    [49,58,67,76,85,94], # (x-4)^3
    [59,68,77,86,95], # 131072*x
    [69,78,87,96], # (x+3)^4
    [79,88,97], # floor(212.43*x)
    [89,98], # (x-2)^3
    [99] # 0xdefaced xor x
]

def fun1(x):
    return x**2 + 2*x + 1

def fun2(x):
    return x ^ 0xdefaced

def fun3(x):
    return (x-2)**3

def fun4(x):
    return math.floor(212.43 * x)

def fun5(x):
    return (x+3)**4

def fun6(x):
    return 131072 * x

def fun7(x):
    return (x-4)**3

def fun8(x):
    return x * 0x80000000000

def fun9(x):
    return x**2 + 10*x + 25

def fun10(x):
    return (x**2 + x) // 2

fun_list = [
    fun1,  fun2, fun3, fun4, fun5, fun6, fun7, fun8, fun9, fun10,
    fun10, fun9, fun8, fun7, fun6, fun5, fun4, fun3, fun2
]

target = [
    7921, 233811128, 79507, 18056, 47458321,
    10878976, 314432, 580542139465728, 3481, 1540,
    233811131, 148877, 11683, 59969536, 5898240,
    493039, 448600744132608, 6889, 3486, 1176,
    117649, 19118, 74805201, 8650752, 250047,
    395824185999360, 8281, 2211, 1035, 3600,
    16569, 5308416, 11534336, 614125, 395824185999360,
    3136, 1275, 1275, 5184, 756463999909888,
    8503056, 8912896, 328509, 659706976665600, 6241,
    1326, 2850, 7056, 431008558088192, 274625,
    11665408, 140608, 624522604576768, 7569, 2415,
    1431, 7744, 738871813865472, 343000, 8650752,
    300763, 747667906887680, 7569, 1326, 1653,
    5476, 466192930177024, 493039, 11141120, 45212176,
    580542139465728, 6724, 2850, 1485, 3844,
    431008558088192, 343000, 9175040, 62742241, 18268,
    2809, 3741, 2926, 2500, 492581209243648,
    614125, 11796480, 9150625, 15719, 421875,
    1035, 1485, 3600, 457396837154816, 132651,
    5898240, 21381376, 10409, 614125, 233811104
]

def find_index(idx):
    for i in range(len(scramble_list_a)):
        if idx in scramble_list_a[i]:
            return i

def find_ans_index(idx):
    for i in range(len(scramble_list_a)):
        if idx in scramble_list_a[i]:
            x = scramble_list_a[i].index(idx)
            return scramble_list_b[i][x]

items = ['?']*100

for i in range(100):
    this_target = target[i]
    fun = fun_list[find_index(i)]
    found = False
    for c in range(255):
        v = fun(c)        
        if v == this_target:
            items[find_ans_index(i)] = chr(c)
            found = True
            break
    
    if not found:
        print("/")
        break
    
print("".join(items))
```

![image-20230802212659088](C:\Users\nesquack\Documents\GitReposLocal\irissec.github.io\uploads\2023-07-30\2023-07-30-vmquacks-vectorized-vices\image-20230802212659088.png)

## Decoding it the right way

Okay, that was pretty anticlimactic... I sort of brushed over me figuring out each function but I didn't think it was interesting enough to include in the writeup. It was me subtracting items from each other and checking if they were growing linearly or not. Not particularly interesting. Instead, I'd like to use this space up to talk about how you were probably _supposed_ to do it by reading the code.