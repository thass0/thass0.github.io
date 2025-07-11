---
layout: post
---

<h1 class="post-title">
  <a href="/key-and-me.html">Announcing KeyAnd.Me</a>
</h1>

<small>
    <time datetime="2025-07-11">11 Jul 2025</time>
</small>

Today my co-founders and I are sharing news about our new company: KeyAnd.Me. We offer a
privacy-first security service that empowers enterprises to keep their encryption safe.
Over the past months, we have assembled the world's largest database of leaked or otherwise
compromised private keys. With this data, we can tell you exactly which keys are safe to use
and which aren't.

I got the idea a while back when someone posted a mock website on Hacker News where
you could upload private keys to check if they were compromised. The website itself was
a joke because it was completely insecure, and uploading your private keys to it
would be a ridiculous mistake. But I immediately spotted the potential: What if we could make
a safe version of this? So I was quick to assemble a gifted team of young builders here
at ETH Zurich, and we got to work.

Our service was built from the ground up with security in mind. Most code is written in
safe Rust, with some components written in a custom Haskell DSL (Domain-Specific Language) which
allows us to formally verify their correctness. Clients upload their private keys to our
service along with optional metadata on usage patterns. We then look to see if any of the
client's keys have been compromised in a leak or if any of their keys collide with those of our
other clients. This has the synergetic effect that the security we provide improves with every
new client. And the best thing: Through multiple layers of encryption, we make sure that your
keys stay safe during the entire procedure --- not even we can see them.

Pre-seed funding has already been secured, and we're rolling out version 1.0 of our service
with local partners in Switzerland. 

Come join us for an unforgettable ride at [KeyAnd.Me](#). See you on the
other side.

