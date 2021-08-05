> The local speakeasy has a password to get in. Can you guess it?
>
> Author: 2much4u
>
> Files: [speakeasy.exe](/uploads/2021-08-03/speakeasy.exe)

```
>speakeasy
The year is 1923.
You recently moved to Chicago and your friend told you about the local speakeasy.
Great! But, this friend left out one key detail...
The password to get in!

Good evening. Welcome to the juice joint.
My apologies, but I can't let you in without the password.
I know you want to get zozzled just like everyone else, but I can't just let you walk in here.

You fumble your words and muster out...
uiuctf{lol pls tell me the flag}

Go chase yourself, bull!
Come back with a warrant
```

The exe given is a ginormous 1mb file that appears to be vmprotect because of the large .vmp0 section. While searching around, I couldn't find anything to disassemble or decompile the vmprotect instructions, so I tried figuring out how it worked on my own. I spent a good thirty minutes before I gave up and resorted to debugging though.

## Quick look at code

Here's the main function:

```c
void main() {
    char inp[112];

    thunk_FUN_14012b2bb();
    printf("\x1b[1m");
    slowPrint("The year is 1923.\n");
    slowPrint("You recently moved to Chicago and your friend told you about the local speakeasy.\n");
    slowPrint("Great! But, this friend left out one key detail");
    slowPrint(".");
    slowPrint(".");
    slowPrint(".\n");
    slowPrint("The password to get in!\n\n");
    printf("\x1b[22m");
    printf("\x1b[33m");
    slowPrint("Good evening. Welcome to the juice joint.\n");
    slowPrint("My apologies, but I can't let you in without the password.\n");
    slowPrint("I know you want to get zozzled just like everyone else, but I"
	          "can't just let you walk in here.\n\n");
    printf("\x1b[1m");
    slowPrint("You fumble your words and muster out");
    printf("\x1b[37m");
    slowPrint(".");
    slowPrint(".");
    slowPrint(".\n");
    printf("\x1b[0m");
    FUN_140005820(inp); //read input?
    FUN_140001630(inp); //check input?
    thunk_FUN_14012b29a();
    printf("\x1b[0m");
    return;
}
```

The output prints really slow, so I'll do the same thing as last year and change the print function to sleep 0 milliseconds.

```c
void slowPrint(char* param_1) {
    size_t sVar1;
    FILE* _File;
    int local_18 = 0;
    while (true) {
        sVar1 = strlen(param_1);
        if (sVar1 <= (ulonglong)(longlong)local_18)
            break;
        thunk_FUN_140003e0c(param_1[local_18]);
        _File = (FILE*)__acrt_iob_func(1);
        fflush(_File);
        Sleep(40);
        local_18++;
    }
    Sleep(200);
    return;
}
```

As usual, I just search for the bytes in a hex editor and replace it by hand since I can't trust Ghidra's instruction patcher.

`FUN_140005820` and `FUN_140001630` seem complicated, so let's check what they do in a debugger first.

## Debugging

If we type something into the input, we can see that `FUN_140005820` is checking input. Not bad so far.

![speakeasy-1](/uploads/2021-08-03/speakeasy-1.png)

And after running `FUN_140001630`, we see that the flag is checked as incorrect. Looks like we can ignore whatever magic is happening in `thunk_FUN_14012b29a`.

![speakeasy-2](/uploads/2021-08-03/speakeasy-2.png)

Here's the `checkInp` function.

```c
void checkInp(char* inp) {
    byte local_38 [40];
    
    for (byte local_48 = 0; local_48 < 40; local_48++) {
        ulonglong in_RDX = (ulonglong)(byte)inp[local_48];
        byte bVar1 = thunk_FUN_140028270((ulonglong)local_48, in_RDX);
        local_38[local_48] = bVar1;
    }
    
    byte local_47 = 0;
    while (true) {
        ulonglong local_40 = (ulonglong)local_47;
        size_t sVar2 = strlen(inp);
        if (sVar2 <= local_40)
            break;
        ulonglong in_RDX = (ulonglong)local_38[local_47];
        byte bVar1 = thunk_FUN_1400262c9((ulonglong)local_47, in_RDX);
        local_38[local_47] = bVar1;
        local_47++;
    }
    thunk_FUN_14012b360(local_38, in_RDX);
    return;
}
```

The `thunk` functions all seem to be calls to vmprotect functions? So we probably don't want to get into those. One thing really nice about this is that it seems to read each character of the input individually (for 40 bytes?) and do two operations on it (`thunk_FUN_140028270` and `thunk_FUN_1400262c9`). 

After those two first functions, the input becomes encrypted into this:

![speakeasy-3](/uploads/2021-08-03/speakeasy-3.png)

But what are we trying to match with? We can set a breakpoint on the encrypted input to find out.

![speakeasy-4](/uploads/2021-08-03/speakeasy-4.png)

Looks like it's just comparing with some other bytes and the 8th byte is different, so it looks like `uiuctf{` is right. Maybe these bytes can be found in the file?

![speakeasy-5](/uploads/2021-08-03/speakeasy-5.png)

Sure enough, it's reading from the dos header. So we can guess that the twice encrypted input is compared against these bytes.

## Omega dumb solution to this challenge

I was solving this challenge at 2am and my brain was not at high capacity, so I took a rather strange approach to this problem. I wanted to just brute force input and compare the output against the `3D 44` bit from the dos header. Easy enough, gdb python has us covered (ida freeware does not have python built in).

There's a few issues I ran into.

One is that I don't know how to use gdb without symbols, and for whatever reason, trying to set a breakpoint at an address and running gdb relocates the code but doesn't relocate the breakpoint. So I had to turn off aslr in windows ([disable aslr for easier malware debugging](https://oalabs.openanalysis.net/2019/06/12/disable-aslr-for-easier-malware-debugging/) thanks seraphin) so I could set breakpoints on actual addresses.

Second is that for whatever reason, `run <<< somestring` (run with stdin) does not work on windows. I reused a gdb python script from a linux chall that worked great, but for whatever reason it doesn't work in windows. That's sort of a big deal because there's no good way to script input into the program. If I was on linux, I could use pwntools and give the process stdin that way. Most likely there is some other kind of windows program that can do what pwntools does, but I decided to try and generate a bunch of gdb lines to copy and paste into the terminal.

```python
genstr = list("uiuctf{aaaaaaaaaaaaaaaaaaaaaaaaaa}")
alpa = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-"
for i in range(7, 34):
    for j in alpa:
        gsc = list(genstr)
        gsc[i] = j
        gscs = "".join(gsc)
        print("echo " + str(ord(j)) + " >> gdbout.txt")
        print("gdb -q -x gdbsolvese.py >> gdbout.txt")
        print(gscs)

```

The issue with this is that the gdb script can't tell if the input was correct or not, so I just have to go into the gdbout.txt log later and piece it together manually.

Not only that, but for whatever reason cmd and windows terminal both mess up when you try to paste big clipboards.

![speakeasy-6](/uploads/2021-08-03/speakeasy-6.png)

So I grabbed a random ahk script from the internet to paste clipboard lines with a delay.

Once all of that was done, I could finally run the script. It simply checks for the return value from `thunk_FUN_1400262c9` and compares it with the corr array values. If it's right, it says "is correct!" and I can ctrl+f for it in the output.

```python
import gdb

#dos header bytes
corr = [61, 68, 113, 137, 213, 193, 54, 166, 131, 131, 223, 198, 150, 169, 32, 87, 116, 228, 222, 180, 215, 166, 70, 51, 66, 138, 219, 118, 30, 11, 174, 250, 118, 105, 109, 111, 100, 101, 46, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def readReg(reg):
    gdbValue = gdb.selected_frame().read_register(reg)
    return int(gdbValue.cast(gdb.lookup_type("long")))
    
def setBreakEvent(callback, addr):
    class GdbPyBreakpoint(gdb.Breakpoint):
        def __init__(self, callback, addr):
            super(GdbPyBreakpoint, self).__init__("*" + hex(addr), type=gdb.BP_BREAKPOINT, internal=False)
            self.callback = callback
            
        def stop(self):
            pos = readReg("rip")
            res = self.callback(pos)
            return False
            
    GdbPyBreakpoint(callback, addr)

i = 0
def byteSetEvent(addr):
    global i
    c = readReg("rax")&0xff
    if corr[i] == c and i > 6:
        print(f"{i} is correct!")
    i += 1

def endEvent(addr):
    gdb.execute("quit")

#from ida
setBreakEvent(byteSetEvent, 0x7FF6B57B16D1) #right after thunk_FUN_1400262c9
setBreakEvent(endEvent, 0x7FF6B57B1837) #end of main

gdb.execute("set pagination off")
gdb.execute("file speakeasy-faster.exe")
gdb.execute(f"run")
```

Output:

```
uiuctf{Daaaaaaaaaaaaaaaaaaaaaaaaa}
7 is correct!
32 is correct!
uiuctf{a0aaaaaaaaaaaaaaaaaaaaaaaa}
8 is correct!
32 is correct!
uiuctf{aanaaaaaaaaaaaaaaaaaaaaaaa}
9 is correct!
32 is correct!
uiuctf{aaataaaaaaaaaaaaaaaaaaaaaa}
10 is correct!
32 is correct!
uiuctf{aaaa_aaaaaaaaaaaaaaaaaaaaa}
11 is correct!
32 is correct!
uiuctf{aaaaabaaaaaaaaaaaaaaaaaaaa}
12 is correct!
32 is correct!
uiuctf{aaaaaa3aaaaaaaaaaaaaaaaaaa}
13 is correct!
32 is correct!
uiuctf{aaaaaaa_aaaaaaaaaaaaaaaaaa}
14 is correct!
32 is correct!
uiuctf{aaaaaaaa@aaaaaaaaaaaaaaaaa}
15 is correct!
32 is correct!
uiuctf{aaaaaaaaa_aaaaaaaaaaaaaaaa}
16 is correct!
32 is correct!
uiuctf{aaaaaaaaaaWaaaaaaaaaaaaaaa}
17 is correct!
32 is correct!
uiuctf{aaaaaaaaaaa3aaaaaaaaaaaaaa}
18 is correct!
32 is correct!
uiuctf{aaaaaaaaaaaaTaaaaaaaaaaaaa}
19 is correct!
32 is correct!
uiuctf{aaaaaaaaaaaaa_aaaaaaaaaaaa}
20 is correct!
32 is correct!
uiuctf{aaaaaaaaaaaaaabaaaaaaaaaaa}
21 is correct!
32 is correct!
uiuctf{aaaaaaaaaaaaaaalaaaaaaaaaa}
22 is correct!
32 is correct!
uiuctf{aaaaaaaaaaaaaaaa4aaaaaaaaa}
23 is correct!
32 is correct!
uiuctf{aaaaaaaaaaaaaaaaanaaaaaaaa}
24 is correct!
32 is correct!
uiuctf{aaaaaaaaaaaaaaaaaaKaaaaaaa}
25 is correct!
32 is correct!
uiuctf{aaaaaaaaaaaaaaaaaaa3aaaaaa}
26 is correct!
32 is correct!
uiuctf{aaaaaaaaaaaaaaaaaaaataaaaa}
27 is correct!
32 is correct!
uiuctf{aaaaaaaaaaaaaaaaaaaaa_aaaa}
28 is correct!
32 is correct!
uiuctf{aaaaaaaaaaaaaaaaaaaaaa6aaa}
29 is correct!
32 is correct!
uiuctf{aaaaaaaaaaaaaaaaaaaaaaanaa}
30 is correct!
32 is correct!
uiuctf{aaaaaaaaaaaaaaaaaaaaaaaa7a}
31 is correct!
32 is correct!
uiuctf{aaaaaaaaaaaaaaaaaaaaaaaaaa}
32 is correct!
```

Bad idea to use `a` , but we got the flag anyway: `uiuctf{D0nt_b3_@_W3T_bl4nK3t_6n7a}`!

## Slightly better solution

Instead of brute forcing ever single character and using weird hacks like running ahk to paste the clipboard into a cmd window, we can run the function on multiple inputs to see if it's a simple xor. Gdb wasn't correctly calling the function, but IDA was able to do it fine.

``` 
thunk_FUN_140028270(0, alphabetChar) //tested w/ abcdef
36,39,38,33,32,35
thunk_FUN_140028270(1, alphabetChar)
82,81,80,87,86,85
thunk_FUN_140028270(2, alphabetChar)
20,23,22,17,16,19
thunk_FUN_140028270(3, alphabetChar)
198,197,196,195,194,193
```

Wow, it really does just look like a simple xor. If we xor 'a' with 36, 82, 20, and 198, we get `45 33 75 A7`. And surprise, we can find these bytes and more in the executable.

![speakeasy-7](/uploads/2021-08-03/speakeasy-7.png)

And for the other function:

```
thunk_FUN_1400262c9(0, alphabetChar) //abcdef
108,111,110,105,104,107
thunk_FUN_1400262c9(1, alphabetChar) //abcdef
127,124,125,122,123,120
```

If we xor 'a' with 108 and 127 we get `0D 1E ...` which sadly doesn't exist in the file. There must be some shenanigans going on here, so let's set breakpoints on all of the strings around the one we found in `thunk_FUN_140028270`.

![speakeasy-8](/uploads/2021-08-03/speakeasy-8.png)

Bingo, looks like we found the other array. Also, it looks like the values are shifted once to the right (0x1b >> 1 = 0x0d).

```python
xor = [
    0x45, 0x33, 0x75, 0xA7, 0xA2, 0xD9, 0x64, 0xE5, 0xE2, 0xC6, 0x88, 0xF9,
    0xD2, 0xFA, 0x0F, 0x15, 0x7C, 0xBA, 0xD0, 0xC4, 0xF4, 0xB4, 0x2D, 0x42,
    0x79, 0xF5, 0xFB, 0x03, 0x56, 0x54, 0xC0, 0xC8, 0x0F, 0x04
]

xor2 = [
    0x1B, 0x3D, 0xE2, 0x9B, 0x07, 0xFD, 0x52, 0x0F, 0xA3, 0x57, 0x46, 0xC1,
    0x4C, 0xC1, 0xE0, 0x05, 0xAF, 0x12, 0x7A, 0x48, 0xF8, 0xE0, 0x0E, 0x8B,
    0xAA, 0x68, 0x27, 0x03, 0x2F, 0xD2, 0x01, 0x0B, 0x30, 0x21
]

match = [
    0x3D, 0x44, 0x71, 0x89, 0xD5, 0xC1, 0x36, 0xA6, 0x83, 0x83, 0xDF, 0xC6,
    0x96, 0xA9, 0x20, 0x57, 0x74, 0xE4, 0xDE, 0xB4, 0xD7, 0xA6, 0x46, 0x33,
    0x42, 0x8A, 0xDB, 0x76, 0x1E, 0x0B, 0xAE, 0xFA, 0x76, 0x69
]

res = ""

for i in range(len(xor2)):
    xor2[i] >>= 1

for i in range(len(match)):
    res += chr(xor[i] ^ xor2[i] ^ match[i])

print(res)
```

If the vm code was any more complicated, this probably wouldn't have worked.

## Intended solution

Despite my googling efforts, I did not find any tools to make the vm code readable. However, it was pointed out at the end that the intended solution _is_ to use something: [NoVmp](https://github.com/can1357/NoVmp). After running it on the executable, it dumps some vtil files which can be opened in [VTIL-Utils](https://github.com/vtil-project/VTIL-Utils).

```assembly
//thunk_FUN_140028270
 | | Entry point VIP:       0x2180e
 | | Stack pointer:         0x8
 | | Already visited?:      N
 | | ------------------------
 | | 0000: [ PSEUDO ]     +0x8     lddq     t120         $sp          0x0
 | | 0001: [ PSEUDO ]     +0x8     movq     t126         &&base
 | | 0002: [ PSEUDO ]     +0x8     addq     t126         0x14378
 | | 0003: [ PSEUDO ]     +0x8     movb     t124         rcx:8
 | | 0004: [ PSEUDO ]     +0x8     addq     t126         t124
 | | 0005: [ PSEUDO ]     +0x8     lddb     t127:8       t126         0x0
 | | 0006: [ PSEUDO ]     +0x8     movb     rax          t127:8
 | | 0007: [ PSEUDO ]     +0x8     movb     t128         rdx:8
 | | 0008: [ PSEUDO ]     +0x8     xorq     rax          t128
 | | 0009: [ PSEUDO ]     +0x8     vexitq   t120
```

```assembly
//thunk_FUN_1400262c9
 | | Entry point VIP:       0x26c2b
 | | Stack pointer:         0x8
 | | Already visited?:      N
 | | ------------------------
 | | 0000: [ PSEUDO ]     +0x8     lddq     t144         $sp          0x0
 | | 0001: [ PSEUDO ]     +0x8     movq     t150         &&base
 | | 0002: [ PSEUDO ]     +0x8     addq     t150         0x143c8
 | | 0003: [ PSEUDO ]     +0x8     movb     t148         rcx:8
 | | 0004: [ PSEUDO ]     +0x8     addq     t150         t148
 | | 0005: [ PSEUDO ]     +0x8     lddb     t151:8       t150         0x0
 | | 0006: [ PSEUDO ]     +0x8     movb     rax          t151:8
 | | 0007: [ PSEUDO ]     +0x8     shrq     rax          0x1
 | | 0008: [ PSEUDO ]     +0x8     movb     t153         rdx:8
 | | 0009: [ PSEUDO ]     +0x8     xorq     rax          t153
 | | 0010: [ PSEUDO ]     +0x8     vexitq   t144
```

From here we can see the very obvious xor with values from 0x14378 and 0x143c8.

> ```
> The year is 1923.
> You recently moved to Chicago and your friend told you about the local speakeasy.
> Great! But, this friend left out one key detail...
> The password to get in!
> 
> Good evening. Welcome to the juice joint.
> My apologies, but I can't let you in without the password.
> I know you want to get zozzled just like everyone else, but I can't just let you walk in here.
> 
> You fumble your words and muster out...
> uiuctf{D0nt_b3_@_W3T_bl4nK3t_6n7a}
> 
> Welcome!
> Have a good time and don't go half-seas over
> ```