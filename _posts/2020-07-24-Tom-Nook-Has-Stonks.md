---
layout:      post
title:       "Tom Nook Has Stonks [warmup]"
description: "solved by not_really"
---

## Writeup by not_really

Just do the code but in reverse.

```python
print('Input a Number Below to guess how many bells Tom Nook has :)')
guess = None
try:
  guess = int(input())
except:
  print("No silly that is wrong, you need a number.")
  exit()
try:
    for tax3 in range(0,1234):
        guess -= 1337 + tax3
    guess = str(hex(int(guess)))[2:]; guess = str(guess[4:8]) + str(guess[0:4])
    guess = int(guess,16)
    for tax4 in range(18,30,2):
        guess = int((str(hex(guess)[2:])[::-1]),16) - tax4 * 1000
    for tax5 in range(0,1000,5):
        for tax4 in range(10,40,10):
            guess -= tax5 * tax4
    guess = str(hex(guess)[2:])
    guess = [int(guess[i:i+2],16) for i in range(0,len(guess),2)];guess[1] /= 2
    guess[0] *= 3;guess[1] -= 18;guess[3] -= 30
    guess[0] += int((ord('j') - ord('J')) / (ord('E') - ord('e')));guess[2] += ord('b')
    guess[0] += int((ord('g') - ord('G')) / (ord('z') - ord('Z')) * ord('c') - ord('a'))
    guess = [hex(int(g)) for g in guess][::-1]
    guess[3] = hex(int(guess[3],16) + 32)


    final = ''
    for i in range(len(guess)):
        final += chr(int(guess[i],16))


    if final == 'Lmao':
        print("Nice you got it, your flag is the value you initally got in the form 'uiuctf{NUMBER_YOU_GOT}'")
    else:
        print("Good try but your ending value was " + final + " try again <3")
        print("\n")
except:
    print("Your guess was so wrong you broke the guessing machine. Good try, but try again <3")
```

Let's clean it a little bit (remove semicolons and such).

```python
print('Input a Number Below to guess how many bells Tom Nook has :)')
guess = None
try:
  guess = int(input())
except:
  print("No silly that is wrong, you need a number.")
  exit()
try:
    for tax3 in range(0,1234):
        guess -= 1337 + tax3
    
    guess = str(hex(int(guess)))[2:]
    guess = str(guess[4:8]) + str(guess[0:4])
    guess = int(guess,16)
    
    for tax4 in range(18,30,2):
        guess = int((str(hex(guess)[2:])[::-1]),16) - tax4 * 1000
    
    for tax5 in range(0,1000,5):
        for tax4 in range(10,40,10):
            guess -= tax5 * tax4
    
    guess = str(hex(guess)[2:])
    guess = [int(guess[i:i+2],16) for i in range(0,len(guess),2)]
    guess[1] /= 2
    guess[0] *= 3
    guess[1] -= 18
    guess[3] -= 30
    guess[0] += int((ord('j') - ord('J')) / (ord('E') - ord('e')))
    guess[2] += ord('b')
    guess[0] += int((ord('g') - ord('G')) / (ord('z') - ord('Z')) * ord('c') - ord('a'))
    guess = [hex(int(g)) for g in guess][::-1]
    guess[3] = hex(int(guess[3],16) + 32)

    final = ''
    for i in range(len(guess)):
        final += chr(int(guess[i],16))

    if final == 'Lmao':
        print("Nice you got it, your flag is the value you initally got in the form 'uiuctf{NUMBER_YOU_GOT}'")
    else:
        print("Good try but your ending value was " + final + " try again <3")
        print("\n")
except:
    print("Your guess was so wrong you broke the guessing machine. Good try, but try again <3")
```

Now time to simplify.

----

```python
for tax3 in range(0,1234):
    guess -= 1337 + tax3
```

is the same as

```python
guess -= 2410619
```

If you're too lazy to understand these blocks, set guess to 0 and run the code:

```python
>>> guess = 0
>>> for tax3 in range(0,1234):
...     guess -= 1337 + tax3
...
>>> guess
-2410619
>>>
```

----

```python
guess = str(hex(int(guess)))[2:]
guess = str(guess[4:8]) + str(guess[0:4])
guess = int(guess,16)
```

is the same as

```python
((guess << 16) & 0xffffffff) | (guess >> 16)
```

This swaps the first and last 2 bytes (for example, 0x12345678 becomes 0x56781234).

---

```python
for tax4 in range(18,30,2):
    guess = int((str(hex(guess)[2:])[::-1]),16) - tax4 * 1000
```

is the same as

```python
guess = int((str(hex(guess)[2:])[::-1]),16) - 18000
guess = int((str(hex(guess)[2:])[::-1]),16) - 20000
guess = int((str(hex(guess)[2:])[::-1]),16) - 22000
guess = int((str(hex(guess)[2:])[::-1]),16) - 24000
guess = int((str(hex(guess)[2:])[::-1]),16) - 26000
guess = int((str(hex(guess)[2:])[::-1]),16) - 28000
```

This swaps the hex chars (for example, 0x12345678 becomes 0x87654321) and subs `tax4 * 1000`.

---

```python
for tax5 in range(0,1000,5):
    for tax4 in range(10,40,10):
        guess -= tax5 * tax4
```

is the same as

```python
guess -= 5970000
```

---

```python
guess = str(hex(guess)[2:])
guess = [int(guess[i:i+2],16) for i in range(0,len(guess),2)]
```

converts each byte of guess to an array of ints.

For example, 0x12345678 becomes `[0x12, 0x34, 0x56, 0x78]`.

---

```python
guess[1] /= 2
guess[0] *= 3
guess[1] -= 18
guess[3] -= 30
guess[0] += int((ord('j') - ord('J')) / (ord('E') - ord('e')))
guess[2] += ord('b')
guess[0] += int((ord('g') - ord('G')) / (ord('z') - ord('Z')) * ord('c') - ord('a'))
```

can be simplified down to

```python
guess[0] = (guess[0] * 3) + 1
guess[1] = (guess[1] / 2) - 18
guess[2] += 98
guess[3] -= 30
```

Again, you can just paste one of those int/ord blocks into python and it will give you the constant value it is.

---

```python
guess = [hex(int(g)) for g in guess][::-1]
```

flips the items of the array and converts each int to a hex string.

For example, `[0x12, 0x34, 0x56, 0x78]` becomes `["0x78", "0x56", "0x34", "0x12"]`.

---

```python
guess[3] = hex(int(guess[3],16) + 32)
```

adds 32 to the last value of the guess array and converts it back to hex.

---

```python
final = ''
    for i in range(len(guess)):
        final += chr(int(guess[i],16))
```

converts the array of hex chars to a string.

---

Here's the final pseudo code:

```python
guess -= 2410619
guess = swapFirstAndLast2Bytes(guess)
guess = flipHexChars(guess) - 18000
guess = flipHexChars(guess) - 20000
guess = flipHexChars(guess) - 22000
guess = flipHexChars(guess) - 24000
guess = flipHexChars(guess) - 26000
guess = flipHexChars(guess) - 28000
guess -= 5970000
guess = intToIntArray(guess)
guess[0] = (guess[0] * 3) + 1
guess[1] = (guess[1] / 2) - 18
guess[2] += 98
guess[3] -= 30
guess = reverseArray(intArrayToHexArray(guess))
"Lmao" == hexArrayToString(guess)
```

Time to work it backwards. Here it is worked out if reversed.

```python
guess -= 2410619 # guess == 0x4D1EE0DD (1293869277)
guess = swapFirstAndLast2Bytes(guess) # guess == 0x4CFA1862
guess = flipHexChars(guess) - 18000 # guess == 0x18624CFA
guess = flipHexChars(guess) - 20000 # guess == 0xAFC3E031
guess = flipHexChars(guess) - 22000 # guess == 0x130DEEDA
guess = flipHexChars(guess) - 24000 # guess == 0xADEE7A41
guess = flipHexChars(guess) - 26000 # guess == 0x14A7911A
guess = flipHexChars(guess) - 28000 # guess == 0xA11914B1
guess -= 5970000 # guess == 0x1B4123BA
guess = intToIntArray(guess) # guess == 0x1AE60B6A
guess[0] = (guess[0] * 3) + 1 # guess == [0x1A, 0xE6, 0x0B, 0x6A]
guess[1] = (guess[1] / 2) - 18 # guess == [0x4F, 0xE6, 0x0B, 0x6A]
guess[2] += 98 # guess == [0x4F, 0x61, 0x0B, 0x6A]
guess[3] -= 30 # guess == [0x4F, 0x61, 0x6D, 0x6A]
guess = reverseArray(intArrayToHexArray(guess)) # guess == [0x4F, 0x61, 0x6D, 0x4C]
guess[3] = hex(int(guess[3],16) + 32) # guess == ["0x4C", "0x6D", "0x61", "0x4F"]
"Lmao" == hexArrayToString(guess) # guess == ["0x4C", "0x6D", "0x61", "0x6F"]
```

I did it by hand because it wasn't that much (actually it was, stupid) but we could write a script to do this.

```python
def stringToHexArray(text):
    out = []
    for c in text:
        out.append(hex(ord(c)))
    return out

def reverseArray(arr):
    return arr[::-1]

def hexArrayToIntArray(arr):
    return [int(g, 16) for g in arr]

def intArrayToInt(arr):
    return (arr[0] << (8*3)) | (arr[1] << (8*2)) | (arr[2] << (8*1)) | arr[3]

def flipHexChars(val):
    return int((str(hex(val)[2:])[::-1]),16)

def swapFirstAndLast2Bytes(val):
    return ((val << 16) & 0xffffffff) | (val >> 16)

guess = stringToHexArray("Lmao")
guess[3] = hex(int(guess[3],16) - 32)
guess = reverseArray(hexArrayToIntArray(guess))
guess[3] += 30
guess[2] -= 98
guess[1] = (guess[1] + 18) * 2
guess[0] = int((guess[0] - 1) / 3)
guess = intArrayToInt(guess)
guess += 5970000
for i in range(28000, 16000, -2000):
    guess += i
    guess = flipHexChars(guess)

guess = swapFirstAndLast2Bytes(guess)
guess += 2410619
print(guess) # 1293869277
```

---

In the livestream after the ctf ended, it was noted that there were multiple solutions:

```
1293869277
1293869278
20665749147
```

The 78 one seems likely with the divide stuff going on, but what about that last one?

Let's take a look by printing out the steps.

```
1293869277
after tax3: 1291458658
after first/last 2 byte swap: 18624cfa

20665749147
after tax3: 20663338528
after first/last 2 byte swap: 18624cfa
```

It doesn't take long before they start to match.

The difference? Let's look at after tax3 in hex:

```
1293869277
after tax3: 1291458658 0x4CFA1862

20665749147
after tax3: 20663338528 0x4CFA18620
```

Of course we only do byte swaps with the first two and last to hex values, so the 0 is chopped off.

Just to make sure, let's check 1293869278.

```
1293869277
after tax3: 1291458658
after first/last 2 byte swap: 18624cfa
hex: 409095418
after tax4: 457253818
after tax5: 451283818
after hex: 1ae60b6a
after array ops: [79, 97.0, 109, 76]
after hex flip: ['0x4c', '0x6d', '0x61', '0x4f']

1293869278
after tax3: 1291458659
after first/last 2 byte swap: 18634cfa
hex: 409160954
after tax4: 457319354
after tax5: 451349354
after hex: 1ae70b6a
after array ops: [79, 97.5, 109, 76]
after hex flip: ['0x4c', '0x6d', '0x61', '0x4f']
```

Yep, definitely from `guess[1] /= 2` and int flooring going on here.