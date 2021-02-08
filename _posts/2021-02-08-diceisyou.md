---
title: dice-is-you
author: not_really
categories: re
layout: post
---

# dice-is-you

![dice-1](/uploads/2021-02-08/dice-1.png)

_First blood... that was fast_

A baba is you clone but with dice I guess.

It's an SDL game written in C and compiled in wasm.

I talked with a few people in discord who said wasm2c works with ghidra, but I usually just use wasm2wat and wasm-decompile to modify and read code.

### The game

The game works just like Baba is You, you use the `IS` blocks to make certain things do certain other things. So in the screenshot above, pushing `THONK` out of the way and replacing it with `DICE` let's "`YOU`" become the dice on the right and get the flag. Sadly the last level is a bit different and doesn't really use these mechanics.

![dice-2](/uploads/2021-02-08/dice-2.png)

It took me a bit to realize, but the examples at the bottom with the two purple arrows show a passing condition and a failing condition. If you put some correct combination of characters together, you can make the arrow and characters light up. We probably need to get all the arrows on the top to light up to make the X turn into a check.

If we browse around a bit, we can find these functions in the wasm (with a few comments):

```js
function check_code(a:int, b:int, c:int, d:int):int //main checking code
function get_code_value(a:int):int //gets code represented by block
function code(a:int, b:int, c:int, d:int, e:int):int //checks with code values
```

Let's look at `check_code` first.

```js
function check_code(a:int, b:int, c:int, d:int):int {
  var e:int = g_a;
  var f:int = 32;
  var g:int = e - f;
  var dc:int = g;
  if (dc < g_c) { handle_stack_overflow() }
  g_a = dc;
  label B_a:
  g[6]:int = a;
  g[5]:int = b;
  g[4]:int = c;
  g[3]:int = d;
  var h:{ a:int } = g[4]:int;
  var i:int = h.a;
  var j:int = get_code_value(i);
  g[11]:byte = j;
  var k:int = g[4]:int;
  var l:int = k[1]:int;
  var m:int = get_code_value(l);
  g[10]:byte = m;
  var n:int = g[4]:int;
  var o:int = n[2]:int;
  var p:int = get_code_value(o);
  g[9]:byte = p;
  var q:int = g[4]:int;
  var r:int = q[3]:int;
  var s:int = get_code_value(r);
  g[8]:byte = s;
  var t:int = g[4]:int;
  var u:int = t[4]:int;
  var v:int = get_code_value(u);
  g[7]:byte = v;
  var w:int = g[11]:ubyte;
  var x:int = 255;
  var y:int = w & x;
  if (eqz(y)) goto B_e;
  var z:int = g[10]:ubyte;
  var aa:int = 255;
  var ba:int = z & aa;
  if (eqz(ba)) goto B_e;
  var ca:int = g[9]:ubyte;
  var da:int = 255;
  var ea:int = ca & da;
  if (eqz(ea)) goto B_e;
  var fa:int = g[8]:ubyte;
  var ga:int = 255;
  var ha:int = fa & ga;
  if (eqz(ha)) goto B_e;
  var ia:int = g[7]:ubyte;
  var ja:int = 255;
  var ka:int = ia & ja;
  if (ka) goto B_d;
  label B_e:
  var la:int = 0;
  var ma:int = 1;
  var na:int = la & ma;
  g[31]:byte = na;
  goto B_c;
  label B_d:
  var oa:int = g[11]:ubyte;
  var pa:int = g[10]:ubyte;
  var qa:int = g[9]:ubyte;
  var ra:int = g[8]:ubyte;
  var sa:int = g[7]:ubyte;
  var ta:int = 255;
  var ua:int = oa & ta;
  var va:int = 255;
  var wa:int = pa & va;
  var xa:int = 255;
  var ya:int = qa & xa;
  var za:int = 255;
  var ab:int = ra & za;
  var bb:int = 255;
  var cb:int = sa & bb;
  var db:int = code(ua, wa, ya, ab, cb);
  g[6]:byte = db;
  var eb:int = g[6]:ubyte;
  var fb:int = 255;
  var gb:int = eb & fb;
  if (gb) goto B_f;
  //pass
  var hb:int = 1;
  var ib:int = 1;
  var jb:{ a:int } = g[4]:int;
  var kb:int = jb.a;
  kb[45]:byte = ib;
  var lb:int = g[4]:int;
  var mb:int = lb[1]:int;
  mb[45]:byte = ib;
  var nb:int = g[4]:int;
  var ob:int = nb[2]:int;
  ob[45]:byte = ib;
  var pb:int = g[4]:int;
  var qb:int = pb[3]:int;
  qb[45]:byte = ib;
  var rb:int = g[4]:int;
  var sb:int = rb[4]:int;
  sb[45]:byte = ib;
  var tb:int = 1;
  var ub:int = hb & tb;
  g[31]:byte = ub;
  goto B_c;
  label B_f: //fail
  var vb:int = 0;
  var wb:int = 1;
  var xb:int = vb & wb;
  g[31]:byte = xb;
  //////////////////////////
  label B_c:
  var yb:int = g[31]:ubyte;
  var zb:int = 1;
  var ac:int = yb & zb;
  var bc:int = 32;
  var cc:int = g + bc;
  var ec:int = cc;
  if (ec < g_c) { handle_stack_overflow() }
  g_a = ec;
  label B_g:
  return ac;
}
```

When reading decompiled wasm output, it's best not to get overwhelmed. Try to see what functions are being called, and then take a guess about what's going on, then see if it checks out.

For me, it's easiest to start with the win condition then work backwards from there. The return value is `ac` which comes from `yb` which comes from `g[31]` which comes from two places.

* On the bottom, where I wrote `fail`, `g[31]` is set to `vb` which is 0. So that's going to return false.
* On the other hand, above that, `g[31]` is set to `ub` which is set to `hb` which is 1. So that passes.

The condition to go down the pass branch is that `gb == 0` which comes from `g[6]` which comes from `db` which comes from calling `code()`. The values from `code` are `g[7]`-`g[11]`, and at the very top you can see those come from `get_code_value` five times.  So the code we care about probably is something like this: 

```js
function check_code(a, b, c, d, e) {
    var codeA = get_code_value(a);
    var codeB = get_code_value(b);
    var codeC = get_code_value(c);
    var codeD = get_code_value(d);
    var codeE = get_code_value(e);
    var finalCode = code(codeA, codeB, codeC, codeD, codeE);
    return finalCode == 0;
}
```

Where a, b, c, d, and e somehow represent the block types.

Let's see what's in `get_code_value`.

```js
function get_code_value(a:int):int {
  var b:int = g_a;
  var c:int = 16;
  var d:int = b - c;
  d[2]:int = a;
  var e:int = d[2]:int;
  var f:int = e[1]:int;
  var g:int = -138;
  var h:int = f + g;
  var i:int = 210;
  h > i;
  br_table[B_f, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b,
           B_r, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b,
           B_c, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b,
           B_l, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b,
           B_i, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b,
           B_g, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b,
           B_j, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b,
           B_z, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b,
           B_h, B_b, B_b, B_b, B_b, B_b, B_y, B_b, B_b, B_b, B_b, B_b,
           B_m, B_b, B_b, B_b, B_b, B_b, B_x, B_b, B_b, B_b, B_b, B_b,
           B_k, B_b, B_b, B_b, B_b, B_b, B_w, B_b, B_b, B_b, B_b, B_b,
           B_b, B_b, B_b, B_b, B_b, B_b, B_u, B_b, B_b, B_b, B_b, B_b,
           B_b, B_b, B_b, B_b, B_b, B_b, B_aa, B_b, B_b, B_b, B_b, B_b,
           B_q, B_b, B_b, B_b, B_b, B_b, B_t, B_b, B_b, B_b, B_b, B_b,
           B_o, B_b, B_b, B_b, B_b, B_b, B_p, B_b, B_b, B_b, B_b, B_b,
           B_v, B_b, B_b, B_b, B_b, B_b, B_e, B_b, B_b, B_b, B_b, B_b,
           B_d, B_b, B_b, B_b, B_b, B_b, B_n, B_b, B_b, B_b, B_b, B_b,
           B_b, B_b, B_b, B_b, B_b, B_b, B_s, ..B_b](
    h)   
  label B_aa:
  var j:int = 1;
  d[15]:byte = j;
  goto B_a;
  label B_z:
  var k:int = 5;
  d[15]:byte = k;
  goto B_a;
  label B_y:
  var l:int = 18;
  d[15]:byte = l;
  goto B_a;
  label B_x:
  var m:int = 25;
  d[15]:byte = m;
  goto B_a;
  label B_w:
  var n:int = 48;
  d[15]:byte = n;
  goto B_a;
  label B_v:
  var o:int = 49;
  d[15]:byte = o;
  goto B_a;
  label B_u:
  var p:int = 55;
  d[15]:byte = p;
  goto B_a;
  label B_t:
  var q:int = 61;
  d[15]:byte = q;
  goto B_a;
  label B_s:
  var r:int = 96;
  d[15]:byte = r;
  goto B_a;
  label B_r:
  var s:int = 119;
  d[15]:byte = s;
  goto B_a;
  label B_q:
  var t:int = 120;
  d[15]:byte = t;
  goto B_a;
  label B_p:
  var u:int = 135;
  d[15]:byte = u;
  goto B_a;
  label B_o:
  var v:int = 138;
  d[15]:byte = v;
  goto B_a;
  label B_n:
  var w:int = 148;
  d[15]:byte = w;
  goto B_a;
  label B_m:
  var x:int = 150;
  d[15]:byte = x;
  goto B_a;
  label B_l:
  var y:int = 160;
  d[15]:byte = y;
  goto B_a;
  label B_k:
  var z:int = 163;
  d[15]:byte = z;
  goto B_a;
  label B_j:
  var aa:int = 171;
  d[15]:byte = aa;
  goto B_a;
  label B_i:
  var ba:int = 179;
  d[15]:byte = ba;
  goto B_a;
  label B_h:
  var ca:int = 183;
  d[15]:byte = ca;
  goto B_a;
  label B_g:
  var da:int = 189;
  d[15]:byte = da;
  goto B_a;
  label B_f:
  var ea:int = 192;
  d[15]:byte = ea;
  goto B_a;
  label B_e:
  var fa:int = 194;
  d[15]:byte = fa;
  goto B_a;
  label B_d:
  var ga:int = 212;
  d[15]:byte = ga;
  goto B_a;
  label B_c:
  var ha:int = 247;
  d[15]:byte = ha;
  goto B_a;
  label B_b:
  var ia:int = 0;
  d[15]:byte = ia;
  label B_a:
  var ja:int = d[15]:ubyte;
  var ka:int = 255;
  var la:int = ja & ka;
  return la;
}
```

This one seems pretty messy, but it looks like some sort of jump table. I realized there's a pattern in the table that helped me realize this represents the sprite ids.

```
                              B_f, B_b, B_b, B_b, B_b, B_b,
B_b, B_b, B_b, B_b, B_b, B_b, B_r, B_b, B_b, B_b, B_b, B_b,
B_b, B_b, B_b, B_b, B_b, B_b, B_c, B_b, B_b, B_b, B_b, B_b,
B_b, B_b, B_b, B_b, B_b, B_b, B_l, B_b, B_b, B_b, B_b, B_b,
B_b, B_b, B_b, B_b, B_b, B_b, B_i, B_b, B_b, B_b, B_b, B_b,
B_b, B_b, B_b, B_b, B_b, B_b, B_g, B_b, B_b, B_b, B_b, B_b,
B_b, B_b, B_b, B_b, B_b, B_b, B_j, B_b, B_b, B_b, B_b, B_b,
B_b, B_b, B_b, B_b, B_b, B_b, B_z, B_b, B_b, B_b, B_b, B_b,
B_b, B_b, B_b, B_b, B_b, B_b, B_h, B_b, B_b, B_b, B_b, B_b,
B_y, B_b, B_b, B_b, B_b, B_b, B_m, B_b, B_b, B_b, B_b, B_b,
B_x, B_b, B_b, B_b, B_b, B_b, B_k, B_b, B_b, B_b, B_b, B_b,
B_w, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b,
B_u, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b,
B_aa,B_b, B_b, B_b, B_b, B_b, B_q, B_b, B_b, B_b, B_b, B_b,
B_t, B_b, B_b, B_b, B_b, B_b, B_o, B_b, B_b, B_b, B_b, B_b,
B_p, B_b, B_b, B_b, B_b, B_b, B_v, B_b, B_b, B_b, B_b, B_b,
B_e, B_b, B_b, B_b, B_b, B_b, B_d, B_b, B_b, B_b, B_b, B_b,
B_n, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b,
B_s, B_b, ...
```

If you look at the spritesheet:

![app.data](/uploads/2021-02-08/dice-app.data.png)

You can see how the table lines up with the sprite sheet starting with the white hollow triangle. It skips the purple arrows and x/check marks (`B_b`). So it looks like each sprite gets a value represented with it by jumping to a certain place in the code and setting the value to return. Problem is, we don't want to have to do all of this manually, right?

Enter closure compiler. It's not the best method, but it works here. What we can do is convert all of the jumps into variables, move it to above the array, and closure compiler can simplify it.

Here's how to do that.

1. Find and replace `:\r\n  var .*:int` with nothing
2. Find and replace `\r\n  d\[15\]:byte = .*;\r\n  goto B_a;\r\n  label` with `\r\nvar `
3. Move the variables to the top and make `br_table` to a variable

If you did it right, you get

```js
var B_aa = 1;
var  B_z = 5;
var  B_y = 18;
var  B_x = 25;
var  B_w = 48;
var  B_v = 49;
var  B_u = 55;
var  B_t = 61;
var  B_s = 96;
var  B_r = 119;
var  B_q = 120;
var  B_p = 135;
var  B_o = 138;
var  B_n = 148;
var  B_m = 150;
var  B_l = 160;
var  B_k = 163;
var  B_j = 171;
var  B_i = 179;
var  B_h = 183;
var  B_g = 189;
var  B_f = 192;
var  B_e = 194;
var  B_d = 212;
var  B_c = 247;
var  B_b = 0;
var br_table = [B_f, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b,
B_r, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_c, B_b, B_b,
B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_l, B_b, B_b, B_b, B_b, B_b,
B_b, B_b, B_b, B_b, B_b, B_b, B_i, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b,
B_b, B_b, B_b, B_g, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b,
B_j, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_z, B_b, B_b,
B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_h, B_b, B_b, B_b, B_b, B_b,
B_y, B_b, B_b, B_b, B_b, B_b, B_m, B_b, B_b, B_b, B_b, B_b, B_x, B_b, B_b,
B_b, B_b, B_b, B_k, B_b, B_b, B_b, B_b, B_b, B_w, B_b, B_b, B_b, B_b, B_b,
B_b, B_b, B_b, B_b, B_b, B_b, B_u, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b,
B_b, B_b, B_b, B_aa, B_b, B_b, B_b, B_b, B_b, B_q, B_b, B_b, B_b, B_b, B_b,
B_t, B_b, B_b, B_b, B_b, B_b, B_o, B_b, B_b, B_b, B_b, B_b, B_p, B_b, B_b,
B_b, B_b, B_b, B_v, B_b, B_b, B_b, B_b, B_b, B_e, B_b, B_b, B_b, B_b, B_b,
B_d, B_b, B_b, B_b, B_b, B_b, B_n, B_b, B_b, B_b, B_b, B_b, B_b, B_b, B_b,
B_b, B_b, B_b, B_s, B_b];
alert(br_table); //prevent optos in closure
alert(br_table);
```

Throw it in closure on advanced pretty print to get an array like this (after me formatting it):

```
                        192,000,000,000,000,000,
000,000,000,000,000,000,119,000,000,000,000,000,
000,000,000,000,000,000,247,000,000,000,000,000,
000,000,000,000,000,000,160,000,000,000,000,000,
000,000,000,000,000,000,179,000,000,000,000,000,
000,000,000,000,000,000,189,000,000,000,000,000,
000,000,000,000,000,000,171,000,000,000,000,000,
000,000,000,000,000,000,005,000,000,000,000,000,
000,000,000,000,000,000,183,000,000,000,000,000,
018,000,000,000,000,000,150,000,000,000,000,000,
025,000,000,000,000,000,163,000,000,000,000,000,
048,000,000,000,000,000,000,000,000,000,000,000,
055,000,000,000,000,000,000,000,000,000,000,000,
001,000,000,000,000,000,120,000,000,000,000,000,
061,000,000,000,000,000,138,000,000,000,000,000,
135,000,000,000,000,000,049,000,000,000,000,000,
194,000,000,000,000,000,212,000,000,000,000,000,
148,000,000,000,000,000,000,000,000,000,000,000,
096,000...
```

So now we know what value each sprite is.

Finally time for code.

```js
function code(a:int, b:int, c:int, d:int, e:int):int {
  var f:int = g_a;
  var g:int = 16;
  var h:int = f - g;
  h[15]:byte = a;
  h[14]:byte = b;
  h[13]:byte = c;
  h[12]:byte = d;
  h[11]:byte = e;
  var i:int = h[15]:ubyte;
  var j:int = 255;
  var k:int = i & j;
  var l:int = 42;
  var m:int = k * l;
  var n:int = h[14]:ubyte;
  var o:int = 255;
  var p:int = n & o;
  var q:int = 1337;
  var r:int = p * q;
  var s:int = m + r;
  var t:int = h[13]:ubyte;
  var u:int = 255;
  var v:int = t & u;
  var w:int = s + v;
  var x:int = h[13]:ubyte;
  var y:int = 255;
  var z:int = x & y;
  var aa:int = h[12]:ubyte;
  var ba:int = 255;
  var ca:int = aa & ba;
  var da:int = z ^ ca;
  var ea:int = w + da;
  var fa:int = h[11]:ubyte;
  var ga:int = 255;
  var ha:int = fa & ga;
  var ia:int = 1;
  var ja:int = ha << ia;
  var ka:int = ea + ja;
  var la:int = 255;
  var ma:int = ka & la;
  return ma;
}
```

`code` takes our five values from earlier. To help us again, we'll make it look like javascript and then give it to closure compiler to simplify. All you need to do here is replace `:int` with nothing and replace `h[11]`-`h[15]` with `a`-`e`. Once you put that through closure, you'll get this:

```js
function codef(a, b, c, d, e) {
  return 42 * (a & 255) + 1337 * (b & 255) + (c & 255) + ((c & 255) ^ (d & 255)) + ((e & 255) << 1) & 255;
}
```

That's a little better. Somehow, with this function, we need to get the values equal to 0.

Why try to figure it out when you can just chuck it into z3.

Here's the conditions:

```
* 25 values
* All values show up only once
* Five of the values are already confirmed
* Check must pass in all 10 directions
```

Here's the code that I used:

```python
from z3 import *
ar = [BitVec(f'{i}', 8) for i in range(25)]
s = Solver()

# our possible options
for i in range(25):
    s.add(Or(ar[i] == 192, ar[i] == 119, ar[i] == 247, ar[i] == 160, ar[i] == 179,
             ar[i] == 189, ar[i] == 171, ar[i] == 5, ar[i] == 183, ar[i] == 18,
             ar[i] == 150, ar[i] == 25, ar[i] == 163, ar[i] == 48, ar[i] == 55,
             ar[i] == 1, ar[i] == 120, ar[i] == 61, ar[i] == 138, ar[i] == 135,
             ar[i] == 49, ar[i] == 194, ar[i] == 212, ar[i] == 148, ar[i] == 96))

# the five tiles already on the board
s.add(ar[0+0] == 212)
s.add(ar[1+0] == 194)
s.add(ar[2+0] == 189)
s.add(ar[0+1*5] == 48)
s.add(ar[0+2*5] == 192)

# horizontal checks all pass
for i in range(5):
    s.add((42 * (ar[0+i*5] & 255) + 1337 * (ar[1+i*5] & 255) + (ar[2+i*5] & 255) + ((ar[2+i*5] & 255) ^ (ar[3+i*5] & 255)) + ((ar[4+i*5] & 255) << 1) & 255) == 0)

# vertical passes all check
for i in range(5):
    s.add((42 * (ar[0+i] & 255) + 1337 * (ar[5+i] & 255) + (ar[10+i] & 255) + ((ar[10+i] & 255) ^ (ar[15+i] & 255)) + ((ar[20+i] & 255) << 1) & 255) == 0)

# all values in array are unique
s.add(Distinct(ar))

print(s.check())
model = s.model()
print(model)
results = ([int(str(model[ar[i]])) for i in range(len(model))])

from_value = [192,119,247,160,179,189,171,5,183,18,150,25,163,48,55,1,120,61,138,135,49,194,212,148,96]
to_spriteid = [138,150,162,174,186,198,210,222,234,240,246,252,258,264,276,288,294,300,306,312,318,324,330,336,348]

for i in range(5):
    print(f"{to_spriteid[from_value.index(results[0+i*5])]} {to_spriteid[from_value.index(results[1+i*5])]} {to_spriteid[from_value.index(results[2+i*5])]} {to_spriteid[from_value.index(results[3+i*5])]} {to_spriteid[from_value.index(results[4+i*5])]}")
```

Output:

```
330 324 198 174 246
264 162 312 288 306
138 186 150 234 276
348 210 252 300 294
336 318 222 258 240
```

Here's a table to go from sprite id to sprite description:

```
/\ 138
[/] 150
Z 162
+ 174
[] 186
+o+ 198
-o- 210
R   222
T   234
C   240
^   246
D   252
/   258
E   264
|   276
_|  288
I   294
/\F 300
K   306
J   312
F   318
X   324
Y   330
N   336
G   348
```

![dice-3](/uploads/2021-02-08/dice-3.png)

I placed these by editing the wat because I was too lazy to move the blocks during testing, that's why there's still blocks on the right.

