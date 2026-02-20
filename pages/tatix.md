---
layout: post
title: The Tatix System
date: 18 Sep 2025
datetime: 2025-09-18
path: /tatix.html
---

This week I finished up an OS project I have been working on for over a year.
It's a from-scratch kernel designed to serve this blog. The project originated
from my interest in OS hacking. At some point, I decided I needed a goal to work
towards, and serving web pages seemed like a cool and difficult thing to do. The
project is done now because the system is at a point where it can (pretty
reliably) serve web pages. (I planned to use it for this blog, but I need a
dedicated server to run it, which is too expensive for my taste given it's just
for fun and nobody will use it).

In under 10k LOC (could be way lower, in fact), the system spans multiple layers,
starting at BIOS and going up to a web server. It features a TCP/IP stack, a RAM
file system, cooperative scheduling, drivers for typical PC hardware, and a library
with essential functions (allocations, strings, lists, buffers, printing, formatting,
etc.), among other things.

I wrote about the internals of the interesting parts of the
[GitHub page](https://github.com/thass0/tatix)<a class="archive-link" href="/archive/GitHub%20-%20thass0_tatix%3A%20From-scratch%20kernel%20built%20to%20serve%20web%20pages.html"></a>.

I was fortunate to do an internship at Unikraft last summer because, while working
there, I got to (somewhat) understand the design and internals of a production-grade
OS. Most of the code I wrote for Tatix was still new to me, but, at least, the
experience of working at Unikraft made the project more approachable.

OS programming has a unique coolness to it that made the project particularly fun.
This is the stuff powering computing globally, but it's hidden deep down the stack.
Still, it's where a lot of the heavy lifting takes place. The information density of
this kind of code is uniquely high. Into each line of code goes a lot of reading the
manual, thinking about how it interacts with other parts of the system, figuring out
a simple yet sufficient way to do it, and more.

My studies at ETH have gotten increasingly interesting and fun lately, and, despite
all the fun of working on Tatix, I'm glad it's done so I can focus on the next thing.
I thought about writing in more detail about the stuff I learned and the thoughts
that went into the design of the system. This may be worthwhile (I sure learned a lot),
but I have different things on my mind.

I will end with a note on the name. My dad is a computer scientist and, every time he
set up a new computer for me, he gave it the hostname "Tatix", as in my first name
merged with Unix. Now, the Tatix system has nothing to do with Unix, but, pretty early
on, I figured it would be a good name for my OS project.

