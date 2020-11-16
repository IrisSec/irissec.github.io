---
title: coelacanth_vault
author: skat
categories: crypto
layout: post
---

> Why would you waste your time catching more than one coelacanth?
> 
> nc chal.uiuc.tf 2004
> 
> Author: potatoboy69

Having solved this challenge was really significant to me as someone who's never considered mathematics to be a personal strength. I have a massive appreciation for mathematics, yes, but it's not particularly a *passion* of mine as it is a passion for others. Solving this cryptography challenge helped alleviate some of the impostor syndrome I experience as someone who is usually the youngest and least experienced guy in any math class or environment at my university.

I've included the challenge's attached source code in case you'd like to attempt it for yourself. You can find it here: [coelacanth\_vault.py](/img/uiuctf2020/coelacanth_vault.py) (SHA1: 335c2bf1c838f90d07f8de8e61a420ebb51de4a1)

A few days after the end of the competition, I emailed my friend Kevin Dao, a mathematics undergraduate at the University of California, San Diego, about this challenge and how I solved it. A (revised) excerpt of my email to him is included below:

> A random, relatively large, non-prime number is generated. For example: 24141917630136328546962. This is the secret and the user does not know what this number is. Let's call it s for secret. The point of the challenge is to find out what s is.
>
> To help find s, the user is given 9 pairs of numbers (r, p),  where r is the result of s mod p, and p is a randomly generated 8-bit prime number. For example, these 9 given pairs may be: (122, 233), (144, 241), (9, 199), (10, 137), (21, 223), (84, 163), (182, 239), (89, 179), (68, 227). In other words, s mod 233 = 122, s mod 241 = 144, s mod 199 = 9, ...
>
> After doing a lot of digging, I found out that the Chinese remainder theorem would help me solve this problem. In the example pairs above, the family of solutions to x ≡ 122 (mod 233), x ≡ 141 (mod 241), x ≡ 9 (mod 199), ... would be expressed by 364288974528818568854 + 540400651263807044957\*n. The number s mentioned earlier is indeed a member of this family of solutions. The challenge gave us 250 tries to get it right, so for this challenge I tested out values of n from 1 to 250 until I eventually got the number right.
>
> I've attached the challenge if you'd like to give it a try. It's a Python program. The initial question when it asks, "How many coelacanth have you caught?" is just asking you for how many pairs you'd like. I'd recommend 9 as this is the maximum the program allows and if I'm not mistaken, the more pairs we have, the more accurately we can to deduce s.

An excerpt of his response is included below:

> I'm glad you are asking about the Chinese Remainder Theorem because it is just a special case of a result in Ring Theory. More specifically, it is a special case of a result in Commutative Ring Theory / Commutative Algebra which is precisely the field I am interested in as well (alongside my main interest in Algebraic Geometry). 
> 
> Okay, so there are two ways to understand the Chinese Remainder Theorem. The number theoretic case with modular congruences is the number theoretic case which uses Bezout's Theorem. In commutative ring theory, we replace the integers with a more general object called a "commutative ring" which has a lot of the key properties of the integers.
> 
> I wrote up a quick piece of exposition which I've attached in this email. There are also a number of expositions on the topic. I think Rosen's text has a section on the theorem. Keith Conrad's expository paper (attached) is also very good, but a bit heavy on notation. I hope they are helpful. The only issue I have with them is that they focus on the number theoretic aspect (which I do appreciate). The result can be generalized and so my piece of exposition is going to give you a bit of a crash course on basic commutative ring theory.

Fascinating! I admit that I was surprised by the depth associated with the Chinese remainder theorem as I thought it was just a clever "math hack" similar to how Japanese multiplication is a clever "math hack."

If you'd like to read Dao's exposition or Conrad's paper, you can see them here: [Dao](/img/uiuctf2020/CRT-KevinDao.pdf), [Conrad](/img/uiuctf2020/CRT-KeithConrad.pdf). Credits to Kevin Dao, undergraduate at the University of California, San Diego, and Keith Conrad, a professor at the University of Connecticut, respectively. Keep in mind that Kevin wrote this in a single morning after having received my email. Mathematicians amaze me.

Feel free to give either or both papers a read. For the purposes of this writeup, I'm going to be giving an ELI5 explanation and massively oversimplifying.

The Chinese remainder theorem basically allows us to solve for an unknown number, let's call it x, when given a multiple congruences x ≡ a (mod b). In other words, if we don't know what a number is but we know the remainders of that number divided by different primes (well, they really only have to be coprime to each other), then we can mathematically compute the family of solutions that the unknown number is a member of.

Let's do an example with a smaller number like x = 26734. Suppose we don't know what this number is, but we know that x mod 13 = 6, x mod 29 = 25, and x mod 7 = 1. This can be rewritten as the system of congruences x ≡ 6 (mod 13), x ≡ 25 (mod 29), and x ≡ 1 (mod 7).

We'll start with the congruence with the largest modulus and slowly work to the congruence with the smallest modulus. Starting at x ≡ 25 (mod 29), we can rewrite this as x = 29j + 25 where j is an integer. Hopefully this makes sense so far, because if the remainder of x divided by 29 is 25, then it must logically be true that x is a multiple of 29 (hence 29j) plus that remainder 25.

Substituting x into the congruence with the next largest modulus, if x = 29j + 25 and x ≡ 6 (mod 13), then it must therefore be true that 29j + 25 ≡ 6 (mod 13). This can be simplified to j ≡ 11 (mod 13), which can be rewritten like we did earlier as j = 13k + 11.

We now take j = 13k + 11 and substitute it into x = 29j + 25, so x = 29(13k + 11) + 25, which simplifies to x = 377k + 344.

We rinse and repeat once more for the last congruence, x ≡ 1 (mod 7). If x = 377k + 344 and x ≡ 1 (mod 7), then it must be true that 377k + 344 ≡ 1 (mod 7), which can be simplified to k ≡ 0 (mod 7), which can be rewritten as k = 7l + 0.

We will once again substitute this result into our original equation for x. If x = 377k + 344 and k = 7l, then x = 377(7l) + 344, which can be simplified to x = 2639l + 344. We are now complete and this expression represents the family of solutions to our system of congruences. When we let l be 0, x = 344, and 344 mod 13 = 6, 344 mod 29 = 25, and 344 mod = 1 are all true. Everything checks out!

Our desired answer, x = 26734, appears when l = 10. The math once again checks out!

I understand that reading math might be a bit difficult, so I went ahead and recorded this video to help you see the Chinese remainder theorem in action:

<iframe width="560" height="315" src="https://www.youtube.com/embed/lw-oBDiBleI" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

Going back to the challenge now, we simply just apply this same procedure to larger numbers. It's very easy to just use an online calculator like [this one](https://comnuan.com/cmnn02/cmnn0200a/cmnn0200a.php), but I highly recommend anyone reading this to try to understand the math because it truly is very neat!

For the record, the flag was `uiuctf{small_oysters_expire_quick}`. This was a very fun challenge and I learned something new!
