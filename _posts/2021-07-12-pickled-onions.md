---
title: pickled-onions
author: not_really
categories: re
layout: post
---

> Kevin Higgs told me pickles can do anything!
>
> Author: KyleForkBomb
>
> Files: [pickled.py](/uploads/2021-07-12/pickled.py)

Recursive python pickle files

### Depth 1 (pickled.py):

```python
__import__('pickle').loads(b'(I128...')
```

At this layer we get a long string loading a long string. Whenever pickle loads it, it starts to execute code. Python comes with a pickle disassembler, so let's try using that.

#### 1. Write to file

```python
t = b'(I128...)'
f = open("pickled_l2.dat", "wb")
f.write(t)
f.close()
```

#### 2. Call pickletools

```
python -m pickletools pickled_l2.dat > pickled_l2.pkl
```

The `stack not empty after STOP` is normal.

### Depth 2 (pickled_l2.pkl):

```asm
     0: (    MARK
     1: I        INT        128
     6: I        INT        4
...
544265: I        INT        82
544269: I        INT        46
544273: t        TUPLE      (MARK at 0)
544274: p    PUT        69420
544281: c    GLOBAL     'pickle loads'
544295: c    GLOBAL     'builtins bytes'
544311: g    GET        69420
544318: \x85 TUPLE1
544319: R    REDUCE
544320: \x85 TUPLE1
544321: R    REDUCE
544322: .    STOP
```

'pickle loads' looks like it's loading another pickle file, so let's extract that into another file. I found it easiest to go into the original pickled_l2.dat file and replace all `I` with nothing, all newlines with `,`, then throw it into a python script and write out the contents.

#### 1. Write to file

```python
a=[128,4,99,112,105,99,107,108,...,82,46]
f = open("pickled_l3.dat","wb")
f.write(bytearray(a))
f.close()
```

#### 2. Call pickletools

```
python -m pickletools pickled_l3.dat > pickled_l3.pkl
```

### Depth 3 (pickled_l3.pkl):

The first half of the file has some constants and functions in pickle. You could decode them with pickletools, but it's pretty obvious what they're doing:

```python
def pickledhorseradish(): return pickledmacadamia.__add__(pickledbarberry)
def pickledcoconut(): return pickledmacadamia.__sub__(pickledbarberry)
def pickledlychee(): return pickledmacadamia.__xor__(pickledbarberry)
def pickledcrabapple(): return pickledmacadamia.__eq__(pickledbarberry)
def pickledportabella(): return pickledmacadamia.__ne__(pickledbarberry)
def pickledquince(): return pickledmacadamia.__le__(pickledbarberry)
def pickledeasternmayhawthorn(): return pickledmacadamia.__ge__(pickledbarberry)
def pickledmonstera(): return 1
def pickledcorneliancherry(): return 0
def pickledalligatorapple(): #???
def pickledboysenberry(): #very long function
```

Before we move onto the boysenberry function, we can also find that the input string is `pickledximenia` and its length should be 64:

```
119509: \x86     TUPLE2
119510: \x8c     SHORT_BINUNICODE 'pickledximenia'
119526: c        GLOBAL     'builtins input'
119542: \x8c     SHORT_BINUNICODE 'What is the flag? '
119562: \x85     TUPLE1
119563: R        REDUCE
...
119626: (    MARK
119627: \x8c     SHORT_BINUNICODE 'pickledburmesegrape'
119648: c        GLOBAL     'io pickledximenia.__len__'
119675: )        EMPTY_TUPLE
119676: R        REDUCE
...
119784: \x8c SHORT_BINUNICODE 'io'
119788: c    GLOBAL     'io pickledgarlic.__getitem__'
119818: c    GLOBAL     'io pickledburmesegrape.__eq__'
119849: I    INT        64
119853: \x85 TUPLE1
119854: R    REDUCE
```

#### 1. Write to file

```python
a=b'\x80\x04cpickle\nio\n(...dcedarbaycherry\n\x85R.'
f = open("pickled_l4.dat","wb")
f.write(a)
f.close()
```

#### 2. Call pickletools

```
python -m pickletools pickled_l4.dat > pickled_l4.pkl
```

### Depth 4 (pickled_l4.pkl):

There's a lot more pickle "programs" here, but really the one that has the start of the fun is in `pickledvoavanga`. It doesn't have a header, which is added from `pickledalligatorapple`. Instead of trying to understand what it was doing, I just called the original script, gave it a 64 length string, and printed the value.

```python
>>> exec(open("chall.py").read())
What is the flag? aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
Nope!
>>> import io
>>> io.pickledalligatorapple
b'\x80\x04I97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\nI97\n'
```

So it seems to pass in our string as INT values. We can dump these values and then take a look at the first function, `pickledvoavanga` (with `pickledalligatorapple` prepended).

### Depth 5 (pickledvoavanga.pkl)

At the start, we see the ints from `pickledalligatorapple`, but also some pops/puts. This looks like the function is selecting which of the characters to use from the input.

```
    0: \x80 PROTO      4
    2: I    INT        97
    6: I    INT        97
...
  246: I    INT        97
  250: I    INT        97
  254: I    INT        97
  258: 0    POP
  259: 0    POP
...
  265: 0    POP
  266: 0    POP
  267: p    PUT        1
  270: 0    POP
  271: 0    POP
...
  318: 0    POP
  319: 0    POP
  320: p    PUT        0
  323: 0    POP
  324: 0    POP
  325: 0    POP
  326: 0    POP
  327: 0    POP
```

Then there's the other logic

```
  328: c    GLOBAL     'pickle io'
  339: (    MARK
  340: \x8c     SHORT_BINUNICODE 'pickledmacadamia'
  358: g        GET        0
  361: \x8c     SHORT_BINUNICODE 'pickledbarberry'
  378: g        GET        1
  381: \x8c     SHORT_BINUNICODE 'pickledgarlic'
  396: \x8c     SHORT_BINUNICODE 'pickledcorneliancherry'
  420: \x8c     SHORT_BINUNICODE 'pickledarugula'
  436: \x86     TUPLE2
  437: d        DICT       (MARK at 339)
  438: b    BUILD
  439: c    GLOBAL     'pickle loads'
  453: \x8c SHORT_BINUNICODE 'io'
  457: c    GLOBAL     'io pickledgarlic.__getitem__'
  487: c    GLOBAL     'pickle loads'
  501: c    GLOBAL     'io pickledeasternmayhawthorn'
  531: \x85 TUPLE1
  532: R    REDUCE
```

Looks like a lot of these names are from the functions from `pickled_l3.pkl`. Let's try to decode some of these names to better understand what's going on.

```
pickledmacadamia - left argument
pickledbarberry - right argument
pickledgarlic - tuple of these two values:
  pickledcorneliancherry - return 0
  pickledarugula - next function in pickled_l4.pkl
pickledeasternmayhawthorn - pickledmacadamia >= pickledbarberry
```

So it looks like one character of the string is compared with another, and if it's valid, it continues on to the next function. We can write a script to read these functions, but there are actually two types of functions. Let's take a look at `pickledleeks`, the fourth function called.

```
  327: 0    POP
  328: c    GLOBAL     'pickle io'
  339: (    MARK
  340: \x8c     SHORT_BINUNICODE 'pickledmacadamia'
  358: g        GET        0
  361: \x8c     SHORT_BINUNICODE 'pickledbarberry'
  378: g        GET        1
  381: \x8c     SHORT_BINUNICODE 'pickledgarlic'
  396: \x8c     SHORT_BINUNICODE 'pickledcorneliancherry'
  420: \x8c     SHORT_BINUNICODE 'pickledjocote'
  435: \x86     TUPLE2
  436: d        DICT       (MARK at 339)
  437: b    BUILD
  438: c    GLOBAL     'pickle loads'
  452: \x8c SHORT_BINUNICODE 'io'
  456: c    GLOBAL     'io pickledgarlic.__getitem__'
  486: c    GLOBAL     'pickle io'
  497: (    MARK
  498: \x8c     SHORT_BINUNICODE 'pickledmacadamia'
  516: c        GLOBAL     'pickle loads'
  530: c        GLOBAL     'io pickledlychee'
  548: \x85     TUPLE1
  549: R        REDUCE
  550: \x8c     SHORT_BINUNICODE 'pickledbarberry'
  567: I        INT        0
  570: d        DICT       (MARK at 497)
  571: b    BUILD
  572: 0    POP
  573: c    GLOBAL     'pickle loads'
  587: c    GLOBAL     'io pickledcrabapple'
  608: \x85 TUPLE1
```

This one xors the first value with the second value, then compares it with the constant (0 on line 567). So we have to account for two types of checks being made.

#### 1. Dump all pickle functions script

Recursively dumps pickle "functions" starting at `pickled_l3.pkl`.

```python
import subprocess
def it(s):
    tmpName = f"{s}.dat"
    asmName = f"{s}.pkl"
    subprocess.run(["python", "-m", "pickletools", tmpName, "-o", asmName])
    f = open(asmName, "r")
    lines = f.readlines()
    content = [x.rstrip("\n") for x in lines]
    name = "idkwhatthelastnamewas"
    lastLine = ""
    #print(f"opening {asmName}")
    for line in lines:
        if "SHORT_BINUNICODE" in line:
            name = line.split("SHORT_BINUNICODE '", 1)[1][:-2]
        elif "SHORT_BINBYTES" in line or "BINBYTES" in line:
            dataName = f"__tmp_{name}.dat"
            df = open(dataName, "wb")
            s = line.split(" b'", 1)[1][:-2]
            if "pickledalligatorapple" in lastLine:
                s = "\\x80\\x04I97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\nI97\\n" + s
            df.write(eval("b'" + s + "'"))
            df.close()
            it(name)
        lastLine = line

it("pickled_l3")
```

#### 2. Parse all pickle functions and export to z3 script

This script does some wacky hacky text file parsing to generate conditions. Simple to do by hand, but I just felt like making a script. Expects the pickle "functions" from `pickled_l4.pkl` to be disassembled to `{functionname}.pkl`

```python
#quality code obv

def it(s):
    asmName = f"{s}.pkl"
    f = open(asmName, "r")
    lines = f.readlines()
    content = [x.rstrip("\n") for x in lines]
    name = "idkwhatthelastnamewas"
    lastLine = ""
    
    pushing = True
    popping = False
    coding = False
    
    fakeStack = []
    var0 = 0
    var1 = 0
    
    mode = 0
    
    #0 - entered first mark
    #1 - exited first mark
    #2 - entered second mark
    #3 - exited second mark
    mark = -1
    
    poppedValue = -1
    
    curCompName = "idkCompName"
    curOpName = "idkOpName"
    
    nextFunName = "dunnoNextFunName"
    
    for line in lines:
        if pushing:
            if "\\x80 PROTO" in line:
                pass
            elif "I    INT" in line:
                fakeStack.append(len(fakeStack))
            else:
                pushing = False
                popping = True
        if popping:
            if "POP" in line:
                poppedValue = fakeStack.pop()
            elif "PUT        0" in line:
                var0 = fakeStack[-1] #poppedValue
            elif "PUT        1" in line:
                var1 = fakeStack[-1]
            else:
                popping = False
                coding = True
        if "SHORT_BINUNICODE" in line:
            if "pickledmacadamia" in line:
                pass
            elif "pickledbarberry" in line:
                pass
            elif "pickledgarlic" in line:
                pass
            elif "pickledcorneliancherry" in line:
                pass
            else:
                if mode == 0:
                    nextFunName = line.split("SHORT_BINUNICODE '", 1)[1][:-2]
                    mode = 1
        elif "(    MARK" in line:
            mark += 1
        elif "b    BUILD" in line:
            mark += 1
        elif mark == 2 and "c        GLOBAL" in line:
            if "GLOBAL     'pickle loads'" in line:
                pass
            else:
                curOpName = line.split("GLOBAL     'io ", 1)[1][:-2]
        elif mark == 2 and "I        INT" in line:
            curOpValue = line.split("INT        ", 1)[1][:-1]
        elif (mark == 1 or mark == 3) and "c    GLOBAL" in line:
            if "GLOBAL     'io pickledgarlic.__getitem__'" in line:
                pass
            elif "GLOBAL     'pickle loads'" in line:
                pass
            elif "GLOBAL     'pickle io'" in line:
                pass
            else:
                curCompName = line.split("GLOBAL     'io ", 1)[1][:-2]
    
    if curOpName == "pickledhorseradish":
        curOpName = "+"
    elif curOpName == "pickledcoconut":
        curOpName = "-"
    elif curOpName == "pickledlychee":
        curOpName = "^"
        
    if curCompName == "pickledcrabapple":
        curCompName = "=="
    elif curCompName == "pickledportabella":
        curCompName = "!="
    elif curCompName == "pickledquince":
        curCompName = "<="
    elif curCompName == "pickledeasternmayhawthorn":
        curCompName = ">="
    
    if mark == 3: #has operation
        print(f"s.add((arr[{var0}] {curOpName} arr[{var1}]) {curCompName} {curOpValue}) # {s}")
    else:
        print(f"s.add(arr[{var0}] {curCompName} arr[{var1}]) # {s}")
    
    it(nextFunName)
        
it("pickledvoavanga")
```

#### 3. Z3 script

```python
from z3 import *

arr = [BitVec(f'{i}', 32) for i in range(64)]
s = Solver()

for i in range(64):
	s.add(arr[i] >= 32)
	s.add(arr[i] <= 127)

s.add(arr[4] >= arr[54]) # pickledvoavanga
s.add(arr[6] <= arr[14]) # pickledarugula
s.add(arr[36] >= arr[30]) # pickledhuckleberry
s.add((arr[28] ^ arr[34]) == 0) # pickledleeks
s.add((arr[23] + arr[7]) == 218) # pickledjocote
s.add((arr[55] ^ arr[31]) == 4) # pickledsugarapple
s.add(arr[58] != arr[18]) # pickledcollardgreens
s.add((arr[40] + arr[56]) == 207) # pickledpassionfruit
s.add((arr[29] - arr[51]) == 59) # pickledplum
s.add((arr[12] ^ arr[60]) == 71) # pickledeightballsquash
s.add(arr[48] <= arr[42]) # pickledchives
s.add((arr[19] + arr[16]) == 198) # pickledalfalfasprouts
s.add(arr[59] != arr[49]) # pickledneem
s.add((arr[61] - arr[43]) == 13) # pickledmelon
s.add(arr[21] != arr[46]) # pickledcherry
s.add(arr[39] != arr[13]) # pickledorange
s.add((arr[9] - arr[38]) == 65) # pickledfibroussatinash
s.add((arr[3] - arr[8]) == 8) # pickledorangelo
s.add((arr[17] - arr[26]) == 47) # pickledmountainsoursop
s.add((arr[45] - arr[20]) == 21) # pickledwildorange
s.add(arr[5] >= arr[37]) # pickledsycamorefig
s.add((arr[41] - arr[44]) == 68) # pickledthimbleberry
s.add((arr[47] + arr[24]) == 217) # pickledvineripetomatoes
s.add((arr[10] + arr[2]) == 201) # pickledbambooshoots
s.add((arr[25] ^ arr[22]) == 93) # pickledkidneybeans
s.add(arr[62] >= arr[52]) # pickledsweetlemon
s.add(arr[11] != arr[53]) # pickledjalapeno
s.add((arr[63] - arr[35]) == 26) # pickledpomcite
s.add((arr[33] - arr[50]) == 12) # pickledotaheiteapple
s.add(arr[15] != arr[0]) # pickledyumberry
s.add((arr[32] ^ arr[1]) == 51) # pickledsnowpeas
s.add(arr[57] != arr[27]) # pickledfennel
s.add((arr[2] ^ arr[34]) == 80) # pickledlangsat
s.add((arr[27] - arr[53]) == 0) # pickledcamucamu
s.add((arr[7] + arr[52]) == 219) # pickledcempedak
s.add(arr[23] <= arr[5]) # pickledjatoba
s.add(arr[49] <= arr[8]) # pickledmangosteen
s.add(arr[6] != arr[22]) # pickledgalia
s.add((arr[45] + arr[0]) == 218) # pickledemuapple
s.add(arr[30] == arr[14]) # pickledpeas
s.add((arr[63] + arr[10]) == 229) # pickledmandarin
s.add(arr[42] >= arr[19]) # pickledcabbage
s.add((arr[13] + arr[43]) == 148) # pickledpommecythere
s.add(arr[57] != arr[17]) # pickledkohlrabi
s.add((arr[24] - arr[44]) == 58) # pickledpodocarpus
s.add(arr[47] != arr[40]) # pickledsoursop
s.add(arr[9] >= arr[60]) # pickledkeppelfruit
s.add((arr[62] ^ arr[32]) == 47) # pickledackee
s.add((arr[20] + arr[21]) == 207) # pickledfijilongan
s.add(arr[28] <= arr[38]) # pickledgourds
s.add(arr[29] >= arr[11]) # pickledmarang
s.add((arr[46] + arr[26]) == 146) # pickledceylongooseberry
s.add((arr[4] + arr[15]) == 175) # pickledrimu
s.add((arr[31] ^ arr[48]) == 7) # pickledbearberry
s.add(arr[33] >= arr[18]) # pickleddavidsonsplum
s.add((arr[55] + arr[39]) == 143) # pickledillawarraplum
s.add(arr[36] != arr[58]) # pickledkandisfruit
s.add((arr[61] - arr[1]) == 0) # pickledkale
s.add(arr[50] != arr[41]) # pickledsnowberry
s.add((arr[37] + arr[12]) == 224) # pickledkiwi
s.add(arr[3] != arr[59]) # pickleduvagrape
s.add((arr[25] ^ arr[16]) == 51) # pickledlemon
s.add(arr[51] != arr[35]) # pickledaraza
s.add(arr[56] != arr[54]) # picklednativecherry
s.add((arr[23] ^ arr[61]) == 15) # pickledmaypop
s.add((arr[52] - arr[31]) == 48) # pickledpulasan
s.add((arr[37] + arr[36]) == 215) # pickledhawthorn
s.add((arr[57] - arr[60]) == 0) # pickledoregano
s.add((arr[45] - arr[17]) == 18) # pickledguanabana
s.add((arr[20] ^ arr[56]) == 50) # pickledindianalmond
s.add(arr[7] >= arr[43]) # pickledcacao
s.add(arr[33] >= arr[55]) # pickledgrape
s.add(arr[10] >= arr[2]) # pickledmameysapote
s.add(arr[54] >= arr[46]) # pickledgrenadilla
s.add((arr[41] - arr[11]) == 65) # pickledyamamomo
s.add((arr[1] + arr[34]) == 157) # pickledmanilatamarind
s.add(arr[50] != arr[28]) # pickledberry
s.add(arr[22] <= arr[44]) # pickledcanistel
s.add((arr[27] ^ arr[13]) == 106) # pickledchenet
s.add((arr[63] ^ arr[15]) == 73) # pickledgreens
s.add(arr[24] != arr[18]) # pickledhoneydewmelon
s.add(arr[40] <= arr[9]) # pickledprumnopitys
s.add((arr[29] - arr[26]) == 59) # pickledcurrant
s.add((arr[4] + arr[16]) == 218) # pickledcrowberry
s.add((arr[42] ^ arr[19]) == 19) # pickledlettuce
s.add((arr[12] ^ arr[62]) == 4) # pickledhogplum
s.add((arr[35] ^ arr[6]) == 83) # pickleddesertfig
s.add((arr[0] ^ arr[49]) == 85) # pickledsaskatoonberry
s.add((arr[51] + arr[3]) == 154) # pickledoilpalm
s.add(arr[25] >= arr[8]) # pickledgandaria
s.add((arr[59] - arr[32]) == 9) # pickledromainelettuce
s.add((arr[5] ^ arr[38]) == 93) # pickledcudrang
s.add((arr[14] - arr[53]) == 0) # pickledkakaduplum
s.add(arr[47] >= arr[30]) # pickleddateplum
s.add(arr[48] != arr[39]) # pickledcarambola
s.add((arr[58] ^ arr[21]) == 47) # pickledlongan
s.add(arr[0] <= arr[59]) # pickledlillypilly
s.add((arr[28] + arr[39]) == 144) # pickledamazongrape
s.add((arr[1] - arr[2]) == 11) # pickledmulberry
s.add(arr[42] != arr[53]) # pickledpintobeans
s.add(arr[51] <= arr[63]) # pickledcherimoya
s.add(arr[17] != arr[37]) # pickledgooseberry
s.add((arr[29] - arr[50]) == 10) # pickledeggplant
s.add((arr[6] ^ arr[55]) == 0) # pickledsweetappleberry
s.add((arr[40] ^ arr[31]) == 86) # pickledemblic
s.add((arr[62] ^ arr[49]) == 67) # pickledtamarind
s.add((arr[36] - arr[23]) == 8) # pickledafricancherryorange
s.add((arr[7] - arr[20]) == 24) # pickledgreenbeans
s.add((arr[32] + arr[57]) == 146) # pickledblackcherry
s.add((arr[19] - arr[14]) == 8) # pickledhoneysuckle
s.add((arr[9] - arr[44]) == 67) # pickledzhe
s.add(arr[56] != arr[21]) # pickledhardykiwi
s.add((arr[4] ^ arr[3]) == 28) # picklednungu
s.add(arr[24] != arr[43]) # pickledpummelo
s.add(arr[27] != arr[34]) # pickledcantaloupe
s.add((arr[54] ^ arr[13]) == 70) # pickledoystermushroom
s.add((arr[38] + arr[25]) == 159) # pickledhabenerochili
s.add((arr[35] ^ arr[5]) == 13) # pickledziziphus
s.add((arr[30] - arr[60]) == 44) # pickledgrapefruit
s.add(arr[12] >= arr[22]) # pickledendive
s.add((arr[11] ^ arr[58]) == 107) # pickledtaxusbaccata
s.add((arr[47] ^ arr[48]) == 93) # pickledsandpaperfig
s.add(arr[18] <= arr[16]) # pickledrhubarb
s.add((arr[45] ^ arr[61]) == 24) # pickledbabaco
s.add((arr[46] ^ arr[26]) == 108) # pickledredmulberry
s.add(arr[15] <= arr[52]) # pickledsalalberry
s.add(arr[33] >= arr[8]) # pickledturnip
s.add(arr[41] != arr[10]) # pickledstrawberryguava
s.add((arr[54] - arr[55]) == 67) # pickledprune
s.add((arr[49] ^ arr[14]) == 108) # pickledturnipgreens
s.add((arr[12] ^ arr[25]) == 24) # pickledpineapple
s.add(arr[30] != arr[40]) # picklednativecurrant
s.add(arr[13] != arr[59]) # pickledarhat
s.add((arr[46] - arr[39]) == 0) # pickledjenipapo
s.add((arr[27] - arr[28]) == 46) # pickleddurian
s.add((arr[56] + arr[63]) == 234) # pickledseagrape
s.add((arr[24] - arr[23]) == 8) # pickledclusterfig
s.add(arr[32] != arr[48]) # pickledpapaya
s.add((arr[61] + arr[4]) == 231) # pickledindianfig
s.add(arr[8] != arr[34]) # pickledsycamore
s.add((arr[11] - arr[31]) == 0) # pickledsweetsop
s.add(arr[5] != arr[42]) # pickledgrapple
s.add((arr[33] ^ arr[19]) == 23) # pickledjapanesebayberry
s.add(arr[17] >= arr[16]) # pickledmorinda
s.add((arr[1] - arr[15]) == 56) # pickledlapsi
s.add(arr[62] <= arr[7]) # pickledbolwarra
s.add((arr[45] + arr[58]) == 211) # pickleddate
s.add(arr[37] != arr[22]) # pickledzucchini
s.add(arr[38] != arr[47]) # pickledridgedgourd
s.add((arr[21] + arr[57]) == 163) # pickledoldworldsycamore
s.add((arr[36] ^ arr[10]) == 3) # pickledchinesemulberry
s.add((arr[43] - arr[6]) == 47) # pickledhominy
s.add(arr[9] >= arr[3]) # pickledfingerlime
s.add((arr[52] ^ arr[29]) == 10) # pickledburdekinplum
s.add(arr[26] <= arr[20]) # pickledgreengage
s.add(arr[50] != arr[60]) # pickledcardon
s.add((arr[0] ^ arr[35]) == 5) # pickledstrawberrypear
s.add((arr[2] + arr[53]) == 192) # pickledacai
s.add(arr[44] <= arr[18]) # pickledbeets
s.add((arr[51] ^ arr[41]) == 70) # pickledcalabashtree
s.add((arr[50] - arr[48]) == 49) # pickledsapodilla
s.add((arr[32] - arr[16]) == 0) # pickledcajamanga
s.add(arr[54] != arr[18]) # pickledparsley
s.add((arr[11] + arr[6]) == 100) # pickledblackberry
s.add((arr[45] + arr[61]) == 224) # pickledwintersquash
s.add(arr[20] != arr[63]) # pickledsprouts
s.add(arr[58] <= arr[56]) # pickledguarana
s.add((arr[15] ^ arr[35]) == 87) # pickledrangpur
s.add((arr[7] ^ arr[22]) == 70) # pickledredbayberry
s.add((arr[46] + arr[31]) == 147) # pickledmalayapple
s.add(arr[53] <= arr[0]) # pickledavocado
s.add(arr[12] >= arr[62]) # pickledsurinamcherry
s.add((arr[39] ^ arr[26]) == 108) # picklednaranjilla
s.add((arr[52] + arr[10]) == 204) # pickledambarella
s.add((arr[28] ^ arr[25]) == 93) # pickledbeansprouts
s.add(arr[17] <= arr[23]) # pickledmockbuckthorn
s.add((arr[60] - arr[57]) == 0) # pickledjapaneseraisin
s.add((arr[3] ^ arr[4]) == 28) # pickledhorsechestnut
s.add((arr[13] + arr[9]) == 169) # pickledescarole
s.add((arr[38] ^ arr[47]) == 93) # pickledcustardappl
s.add(arr[24] >= arr[2]) # pickledatemoya
s.add((arr[19] - arr[34]) == 54) # pickledbarbadian
s.add((arr[21] - arr[5]) == 2) # picklednageia
s.add((arr[43] + arr[33]) == 207) # pickledpigface
s.add((arr[27] - arr[44]) == 46) # pickledkeylime
s.add((arr[59] - arr[49]) == 53) # pickledlemonaspen
s.add((arr[8] ^ arr[14]) == 0) # pickledwhitemulberry
s.add((arr[29] - arr[40]) == 12) # pickledbitterorange
s.add(arr[12] != arr[31]) # pickledblackmulberry
s.add((arr[42] ^ arr[5]) == 26) # pickledbilimbi
s.add((arr[35] + arr[25]) == 207) # pickledwolfberry
s.add(arr[10] <= arr[36]) # pickledugni
s.add((arr[7] - arr[15]) == 67) # pickleddatepalm
s.add((arr[57] ^ arr[43]) == 108) # pickledsaskatoon
s.add((arr[60] ^ arr[49]) == 0) # pickledtomatillo
s.add((arr[21] - arr[46]) == 17) # pickledredmombin
s.add((arr[18] ^ arr[20]) == 110) # pickledwoodapple
s.add(arr[45] >= arr[17]) # pickledmelinjo
s.add((arr[26] ^ arr[1]) == 95) # pickledjicama
s.add((arr[38] ^ arr[37]) == 95) # pickledwongi
s.add((arr[40] ^ arr[16]) == 61) # pickledchard
s.add((arr[24] - arr[22]) == 58) # pickledseabuckthorn
s.add((arr[50] - arr[48]) == 49) # pickledsugarsnappeas
s.add((arr[41] + arr[13]) == 170) # pickledparsnip
s.add(arr[52] <= arr[54]) # pickledquenepa
s.add(arr[19] != arr[59]) # picklediceberglettuce
s.add((arr[61] ^ arr[55]) == 92) # pickledmushrooms
s.add((arr[23] - arr[27]) == 4) # pickledyellowsquash
s.add(arr[4] >= arr[53]) # pickledcranberry
s.add((arr[29] ^ arr[63]) == 19) # pickledsalmonberry
s.add((arr[9] - arr[47]) == 6) # pickledquandong
s.add((arr[2] - arr[39]) == 2) # pickledpomegranate
s.add((arr[8] - arr[11]) == 43) # pickledwintermelon
s.add((arr[3] - arr[0]) == 1) # pickledtangerine
s.add(arr[62] >= arr[34]) # pickledsantol
s.add(arr[30] != arr[44]) # pickledpricklypear
s.add(arr[33] != arr[6]) # pickleddesertlime
s.add((arr[56] - arr[32]) == 14) # pickledwaterapple
s.add(arr[51] != arr[14]) # picklededamame
s.add(arr[28] != arr[58]) # pickledmamoncillo
s.add((arr[39] - arr[58]) == 0) # pickledmuskmelons
s.add((arr[54] - arr[14]) == 20) # pickledwineberry
s.add((arr[61] ^ arr[51]) == 95) # pickledgreenpeas
s.add((arr[28] + arr[37]) == 157) # pickledbeans
s.add((arr[47] + arr[22]) == 159) # pickledgoumi
s.add(arr[6] <= arr[23]) # pickledcarob
s.add((arr[46] + arr[45]) == 211) # pickledtangelo
s.add((arr[26] - arr[49]) == 0) # pickledloganberry
s.add((arr[32] - arr[18]) == 46) # pickledbreadfruit
s.add((arr[21] ^ arr[50]) == 20) # picklednuts
s.add((arr[40] + arr[36]) == 205) # pickledyam
s.add((arr[53] + arr[8]) == 190) # pickledredcabbage
s.add(arr[11] != arr[33]) # pickledradicchio
s.add((arr[31] + arr[3]) == 155) # pickledcloudberry
s.add(arr[20] != arr[24]) # pickledrosemyrtle
s.add((arr[27] - arr[48]) == 44) # pickledlentils
s.add((arr[35] - arr[60]) == 48) # pickledyardlongbeans
s.add(arr[52] <= arr[63]) # pickledwaxapple
s.add((arr[2] + arr[25]) == 205) # picklednapa
s.add((arr[62] + arr[12]) == 228) # pickledvelvettamarind
s.add((arr[4] - arr[10]) == 19) # pickledjaboticaba
s.add((arr[29] ^ arr[9]) == 26) # picklednaranja
s.add(arr[43] <= arr[16]) # pickledgalaapple
s.add((arr[7] ^ arr[56]) == 26) # pickledmorels
s.add(arr[34] != arr[59]) # pickledbroccolirabe
s.add((arr[0] ^ arr[30]) == 57) # pickledgalendar

print(s.check())
model = s.model()
results = ([int(str(model[arr[i]])) for i in range(len(model))])

text = ""

for i in results:
    text += chr(i)

print(text)
```

>  `flag{n0w_th4t5_4_b1g_p1ckl3_1n_4_p1ckl3_but_1t_n33d3d_s0m3_h3lp}`