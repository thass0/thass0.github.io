---
layout: default
title: Archive
---

<h1 class="post-title">
  <a href="/archive.html">Link Archive</a>
</h1>

I maintain an archive of pages that I link to in my posts in the `/static/archive` directory of
this website. The web changes all the time and there is no way to be sure that content I once
linked to will remain accessible in the future. To protect against this, I download copies of
most pages that I link to and save them in `/static/archive`. This way, I can be confident
that future readers of my blog will have access to all relevant information. The archive will
only disappear when the rest of my blog does.

The command I use to archive web pages is:
```shell
monolith --isolate --no-js --output static/archive/%title%-%timestamp%.html <URL>
```
The Monolith software can be downloaded on [its GitHub page](https://github.com/Y2Z/monolith).

**DISCLAIMER:** All archived materials were created by their respective authors and are subject to their
original licenses and terms. If you are the copyright holder of any content and would like it removed,
please contact me.
