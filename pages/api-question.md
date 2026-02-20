---
layout: post
title: Are Good APIs All You Need To Be Memory-Safe?
date: 28 Nov 2025
datetime: 2025-11-28
path: /api-question.html
---

It's well-known that
[roughly 70%](https://www.memorysafety.org/docs/memory-safety/#how-common-are-memory-safety-vulnerabilities)
<a class="archive-link" href="/archive/What%20is%20memory%20safety%20and%20why%20does%20it%20matter%20-%20Prossimo-2025-11-28T21_43_44Z.html"></a>
of vulnerabilities are due to memory safety issues. A popular proposal for addressing this problem
is incrementally moving to memory-safe languages, such as Rust, Java, Python, Haskell, etc. Rust
in particular is a hot topic because it can be compiled into binaries with small runtimes just
like C and C++ can, but it offers compiler-enforced safety guarantees.

The downside of these compiler-enforced guarantees is poor ergonomics and language complexity.
These lead programmers to reintroduce some issues memory safety is meant to solve. They
do this when a direct solution to their problem is hard or impossible to express in the language. 

Consider an example from
[a 2018 talk](https://kyren.github.io/2018/09/14/rustconf-talk.html)
<a class="archive-link" href="/archive/My%20RustConf%202018%20Closing%20Keynote-2025-11-28T21_44_57Z.html"></a>
about
writing games in Rust versus C++. This is one iteration the speaker suggests for representing
the state of the game:

```rust
struct GameState {
    assets: Assets,

    entities: Vec<Option<Entity>>,
    players: Vec<EntityIndex>,
    
    ...
}
```

The problem with this design is that you need to allocate and free entries in the entities array.
The Rust borrow checker has been circumvented by introducing what is basically a custom heap. You
are left with the same issues that the OS-provided heap has: use after free, double free, data
corruption, and so on.

The speaker does suggest a solution to these concerns, but it comes down to adding allocator
logic. This means we're still left with custom memory management.

I am not arguing that the entity system proposed in the talk is poorly designed. I've seen something
like it in Robert Nystrom's
[Game Programming Patterns](https://gameprogrammingpatterns.com/data-locality.html)
<a class="archive-link" href="/archive/Data%20Locality%20%C2%B7%20Optimization%20Patterns%20%C2%B7%20Game%20Programming%20Patterns-2025-11-28T21_45_15Z.html"></a>,
and in
[Handles are the better pointers](https://floooh.github.io/2018/06/17/handles-vs-pointers.html)
<a class="archive-link" href="/archive/Handles%20are%20the%20better%20pointers-2025-11-28T21_45_25Z.html"></a>,
Andre Weissflog recommends similar designs. So it's clearly working for some people.

My point is that low-level control and automatic memory management are incompatible, at least to some
degree. This is a basic argument, but it implies that compiler-enforced safety guarantees are
hard (i.e., too hard) to implement in languages catering to low-level programmers, such as Rust.
In the game programming example, you want speed, so you cannot wrap all data in boxes and call it
a day. But you cannot use Rust's references either, because borrow rules are too hard to deal with.

It would be fun to make up a model in which it can be proven that compiler-enforced memory safety
and low-level control are incompatible. I just need to choose the right model to make my point.

Maybe the only thing you need to make low-level systems memory safe are well-designed APIs.
Interfaces, that is, that encourage good behavior and lead you to avoid errors. If you have them,
you can skip the incremental correctness proofs that Rust has. In fact, Rust itself is a stellar
example of a language with many well-designed APIs in the standard library, and this clearly
counts towards its safety.

The Zig language seems to follow an approach that's in line with what I'm suggesting here, but
I have not looked into it further. Regardless, in
[How (memory) safe is zig?](https://www.scattered-thoughts.net/writing/how-safe-is-zig/)
<a class="archive-link" href="/archive/How%20%28memory%29%20safe%20is%20zig-2025-11-28T21_45_43Z.html"></a>
Jamie Brandon writes, "Zig removes some of the most egregious footguns from c, has better defaults,
makes some good practices more ergonomic, and benefits from a fresh start in the standard library
(eg using slices everywhere)." This is what I'm thinking of.

I hope that Zig gains popularity so that in 10--20 years I can check the data on vulnerabilities
in Zig applications to see if I'm right.

---

I like the reasoning above because it avoids what Andrew Lilley Brinker termed the "get good"
fallacy. In
[Memory Safety for Skeptics](https://queue.acm.org/detail.cfm?id=3773095)
<a class="archive-link" href="/archive/Memory%20Safety%20for%20Skeptics%20-%20ACM%20Queue.html"></a>
he writes:

> There is a common reply in conversations about memory safety, coming from the most hardcore
> skeptics: Programmers should just write better code. They argue, explicitly or implicitly,
> that programmers who benefit from the guardrails of memory safety are bad programmers, and
> that real programmers are sufficiently skilled that they do not need a machine double-checking
> their work.
>
> Let's be clear: This is anti-intellectual nonsense—macho self-aggrandizement masquerading as a
> serious technical argument. You should not take it seriously and should consider someone
> advancing this argument as fundamentally unserious and to be ignored.
>
> There is no step function in quality of work in the history of human achievement that happened
> because people one day woke up and decided to be better at their jobs. Improvements in
> productivity or quality or reductions in error and harm happen because of the invention of new
> techniques, processes, and tools.

This fits what I have observed in discussions on Hacker News and Lobsters. The way it's phrased
is also beautifully pointed.


