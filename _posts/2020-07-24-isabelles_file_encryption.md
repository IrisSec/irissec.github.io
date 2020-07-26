---
layout:      post
title:       "isabelles_file_encryption [crypto]"
description: "solved by not_really"
---

## Writeup by not_really

> Isabelle wanted to password-protect her files, but there wasn't any room in the budget for BitLocker! So she made her own program. But now she lost her password and can't decrypt one of her super important files! Can you help her out?
>
> Author: potatoboy69
>
> Files: [blackmail_encrypted](/img/uiuctf2020/blackmail_encrypted) [super_secret_encryption.py](/img/uiuctf2020/super_secret_encryption.py)

I'm bad at crypto but a lot of people had solved this problem, which means I could too, right?

Let's look at what we have.

```python
blackmail_encrytped: very long (51.6kb), all binary
super_secret_encryption.py:
#!/usr/bin/python

# password-protect your files with this super powerful encryption!
def super_secret_encryption(file_name, password):
  with open(file_name, "rb") as f:
    plaintext = f.read()
  
  assert(len(password) == 8) # I heard 8 character long passwords are super strong!
  assert(password.decode("utf-8").isalpha()) # The numbers on my keyboard don't work...
  assert(b"Isabelle" in plaintext) # Only encrypt files Isabelle has been mentioned in
  add_spice = lambda b: 0xff & ((b << 1) | (b >> 7))
  ciphertext = bytearray(add_spice(c) ^ password[i % len(password)] for i, c in enumerate(plaintext))

  with open(file_name + "_encrypted", "wb") as f:
    f.write(ciphertext)

# use this to decrypt the file with the same password!
def super_secret_decryption(file_name, password):
  with open(file_name + "_encrypted", "rb") as f:
    ciphertext = f.read()
  
  remove_spice = lambda b: 0xff & ((b >> 1) | (b << 7))
  plaintext = bytearray(remove_spice(c ^ password[i % len(password)]) for i, c in enumerate(ciphertext))

  with open(file_name + "_decrypted", "wb") as f:
    f.write(plaintext)

with open("password", "rb") as f: # I got too lazy typing it in each time
    password = f.read()
    # Make sure to encrypt the text in the middle!!!
    super_secret_encryption("blackmail", password)
    super_secret_decryption("blackmail", password)
```

An additional hint we got (from discord, I think?) was that most online programs are not going to be able to decode this. Interesting.

So let's write down everything we know about this "encryption".

```
xor related
password must be 8 characters
password must be only alphabet
plaintext must contain Isabelle
plaintext is "spiced" - counts by 2s up until 254, then counts by 2s again but starting at 1
```

The spice really isn't all that important as long as we know it's fully reversible. Something else interesting to know is that the plaintext must contain an 8 character long string, the same length as the password. My first thought was, "if the only difference from regular xor is just this 'spice', can't we just add spice logic into an xor decoder?"

Because I'm a no effort kind of guy, instead of writing my own, having it not work, and spend precious time debugging, I found an already written xor decoder at [this link](https://alamot.github.io/xor_kpa/). It takes in the encrypted message and a known plaintext and tries to decode the message.

Of course, that won't work out of the box because we still need to apply the spice. The top of the page says this:

```
plaintext ⊕ key = encrypted_text
encrypted_text ⊕ plaintext = key
encrypted_text ⊕ key = plaintext
```

Which will end up really being like this:

```
spice(plaintext) ⊕ key = encrypted_text
encrypted_text ⊕ spice(plaintext) = key
encrypted_text ⊕ key = spice(plaintext) (unspice plaintext here)
```

In the code, there are two xors to worry about, line 69 and line 82.

```python
69: partial_key += chr(ord(data[i+j]) ^ ord(known_plaintext[j]))
82: decrypted_text += chr(ord(data[x]) ^ ord(repeated_key[x]))
```

So we can replace the code with this:

```python
69: partial_key += chr(ord(data[i+j]) ^ ord(add_spice(known_plaintext[j])))
82: decrypted_text += remove_spice(chr(ord(data[x]) ^ ord(repeated_key[x])))
```

And of course, copy `add_spice` and `remove_spice` from the original source.

So all we have to do is just run the program and it will work, right?

Wrong.

Let's see what the output is:

![image-20200722135126088](/img/uiuctf2020/image-20200722135126088.png)

Oof, it didn't find anything. Is it because it just doesn't work at all? To test, I encoded my own message with password `HAhAMemE`:

> This is the story of a man named "Potato". Potato worked for a company in a big building where he was Employee #777. Employee #777's job was simple: he sat at his desk in Room 777 and he drew potatoes with his mouse. Orders came to him through a monitor on his desk telling him what potatoes to send, how big they needed to be, and in what order. This is what Employee #777 did every day of every month of every year, and although others may have considered it soul rending, Potato relished every moment that the orders came in, as though he had been made exactly for this job. And Potato was happy. And then one day, something very peculiar happened. Something that would forever change Potato; Something he would never quite forget. He had been at his desk for nearly an hour when he had realized not one single order had arrived on the monitor for him to follow. No one had shown up to give him instructions, call a meeting, or even say 'kawaii'. Never in all his years at the company had this happened, this complete isolation. Something was very clearly wrong. Shocked, frozen solid, Potato found himself unable to move for the longest time. But as he came to his wits and regained his senses, he got up from his desk and stepped out of his office. Btw, Isabelle did not write this message.

![image-20200722135758771](/img/uiuctf2020/image-20200722135758771.png)

Interestingly enough, we actually get the message this time. Turns out the original message has binary in it, but the script only prints messages if they are _all_ text.

Let's change line 90 to _only_ check if uiuctf{ is in the message.

```python
if "uiuctf{" in decrypted_text:
```

We got it!

![image-20200722140009928](/img/uiuctf2020/image-20200722140009928.png)

You're probably interested in what that image is though? Well, that image doesn't open, and there's tons of `EF BF BD` in the image. It's possible that the file never got correctly encoded and so we'll probably never see it.

Looking back, I definitely could've written my own script to xor decode (probably more educational) but what works works.