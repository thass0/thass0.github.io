---
layout: post
---

<h1 class="post-title">
  <a href="/principled-blogging.html">Principled Blogging</a>
</h1>

<small>
    <time datetime="2025-04-12">12 Apr 2025</time>
</small>

Before building your blog, first note that the web is kind of crappy today.
I'm not claiming it's ever been better. It may well be that it has always been
this crappy or worse, even. The web is full of SEO-optimized spam, ads, and
tracking. There are some walled gardens that take care to fight spam and even
try to provide "interesting" content, but they are, well, walled gardens and
generally work towards getting you addicted to their service in order to sell
even more ads.

Fortunately for us, there is the "small web" -- the part of the internet made
up of personal blogs and other kinds of privately run, small-scale websites
that are primarily operated for a fun. There is nothing wrong with making a
profit on the web, of course. There are great for-profit services, like
[Migadu](https://migadu.com/), that offer a high-quality product without any
fuzz. But most web enterprises have converged to an enshittified state that
makes them all indistinguishable and equally unusable.

The issue is that many of these companies maximize profits by finding exploits
in the system. Instead of trying to provide the best product they can in good
faith, they abuse and manipulate to increase profits. This behavior feels like a
natural succession to the advent of advertising in the 1960s, when companies
struggled to sell stuff that nobody needed and hence had to create new desires.

# Analytics

Ask yourself where the trend to collect analytics on everything that happens
on the web comes from. ... Done? It's the same process that has led to the
enshittification of the web. Companies collect as much user data as possible
on their websites to manipulate users into desired behaviors, like buying a
product. Optimizing the website sounds like a great way to improve company
success, doesn't it? Except the wrong metric is being optimized. While revenue
may go up, improving the website to make more users buy a product doesn't
increase the value provided by the product at all. It's all useless work in
the sense that useful work means providing more value for the same price.

A company does need *some* information about their customers, of course, so they
know what to produce. But do they need to track every single move you make on
their website, or even track you through the entire web? No, they don't.

They why would we want to engage in this practice on our personal websites? The only
other reason I can think of is vanity. It feels good to see the number of visitors
go up. I checked my phone all the time when I had made a popular tweet before deleting
my account. I also had analytics on my blog only so I could boast with the number
of visitors my blog has had (I have since removed these analytics).

Well guess what: vanity is generally not something to be too proud of. If
it's only for vanity, think hard about including analytics on your blog.
Personally, I need to admit that I'm really susceptible to this kind of
thing, so it may be different for you. But my ego inflates a ton when I
see a number go up. And I have a strong suspicion I'm not the only person
to struggle with this.

So, you should probably remove analytics from your blog. Or, if
you insist on having analytics, please do something privacy-friendly,
like [the way Bear does it](https://herman.bearblog.dev/how-bear-does-analytics-with-css/).

#  Accessibility

The obvious case for accessibility is that your website should be usable
for people who are, for example, visually impaired. Please don't
be lazy and add sensible alt texts to images, etc. that allow
people to have a good experience reading your posts even if they
can't look at the images themselves.

Not only are you allowing visually impaired people to have a good
time on your website, you are also allowing people with a bad
internet connection or slow device to enjoy your content.

Some [experiments by Dan Luu](https://danluu.com/slow-device/) indicate
that people living outside the wealthy countries can barely use some
of the most popular web services because they are engineered in a decadent
way by people who unconsciously assume all of their users own an iPhone.

Somehow, startup landing pages are the worst offenders here. The reason
for this probably is that all people working in venture capital that I
have met use current-generation MacBooks. Is it really a hard requirement
that your [landing](https://www.browserbase.com/) [page](https://www.arago.inc/)
makes my laptop fans ramp up?

You don't need to make your website minimalist, like many of the
people who agree with me on the above points do. It's enough to put
some thought into the performance of your page in terms of both space
and time. Should the client load megabytes of data for your blog
if the total number of characters ever written on your blog is only in
the thousands?

On my blog, the rendered pages are only about 35% bigger than the
Markdown sources. And when I include images and the like, it's closer
to a 10% increase from source to built page.

Compare this to a random post on Substack that was just on Hacker News,
where the total size of the HTML was somehow ten times that of the word
count. And now think how much -- from the user's point of view -- the
experience of reading the content of the post is better on Substack as
compared to reading it on my blog. A randomly chosen user may prefer
Substack for it's more elaborate design, but they probably won't like
it _ten times_ better.

To show that you don't need to make a minimalist site, I want to point
out that WordPress and Ghost do pretty well on the benchmarks by Dan Luu
that I linked above. If you put some thought and care into it, it's easy
to make an involved site with all the fancy blogging features you want
that's still nice to use.

# Tooling

I have personally taken tooling to a form of extreme. My blog is quite
minimal, and, except for the Markdown to HTML conversion, the
entire site generation is covered by a
[120-line Python script](https://github.com/thass0/thass0.github.io/blob/465907cc883bc4134ecb01516fd505ff53b94547/generate.py).
The only dependency of my blog that doesn't come pre-installed
with Ubuntu is Cmark, the reference implementation of the CommonMark
Markdown specification. It's fast, well-tested, fuzzed, and actively
maintained. Before that, I used Jekyll to generate my blog, but
it has way more features than are necessary for a simple site like
mine, and it broke all the time because of Ruby dependency issues,
and GitHub is using an older version of Jekyll than me. Now, site
generation is quicker than before and never breaks.

I've spent years on Hacker News reading blogs on a daily basis,
and I have rarely seen a blog that strictly requires more
complex tooling than mine. A blog post is usually just the output of
converting a Markdown file to HTML with some styles added to
it. If you're not running [Gwern.net](https://gwern.net/),
think what strict requirements force you to use Jekyll, your
favorite JS bloat (sorry for my bias), or whatever.

Software people seem to like using tools that are super complex
because it's what the big dogs use. But these tools are often
overblown, and you'd be better off if you'd just write the stuff
yourself. At least think carefully before using someone else's
code. This is what responsible engineers do, [right?](https://en.wikipedia.org/wiki/Npm_left-pad_incident)

# Now what?

I don't want you to create a minimal blog like mine. But I want to
encourage you to think a little before starting to program, and to
be mindful about both the technical and the non-technical choices
that go into making your website. A personal blog is completely
*yours*. No one is telling you what to do with it; you are completely
responsible for everything on there. Hence, you should take care to
make it reflect your standards and values. Are you ignorant and lazy?
How do you feel about web bloat? How much do you care about your readers?
Do you want to put love into your personal website?

Asking these questions led me to turn my blog into the most simple
thing I could end up with that I still find pretty to look at and
nice to read.

Finally, is there any reason that these arguments don't apply to
all other websites too?

