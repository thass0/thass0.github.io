---
layout: post
---

<h1 class="post-title">
    <a href="/can-you-use-a-class-in-c.html">Can You Use a Class in C?</a>
</h1>

<small>
    <time datetime="2023-08-11">11 Aug 2023</time>
</small>

Discussion: [Hacker News](https://news.ycombinator.com/item?id=37097775)<a class="archive-link" href="/archive/Can%20you%20use%20a%20class%20in%20C%20-%20Hacker%20News-2025-05-12T14_19_04Z.html"></a> \| [Lobsters](https://lobste.rs/s/tjkdv7/can_you_use_c_class_c)<a class="archive-link" href="/archive/Can%20you%20use%20a%20C%2B%2B%20class%20in%20C%20-%20Lobsters-2025-05-12T14_19_07Z.html"></a>

---

Recently, I've been [working on a C debugger](https://github.com/thass0/spray)<a class="archive-link" href="/archive/GitHub%20-%20thass0_spray%20-%20%20A%20x86_64%20Linux%20debugger%20🐛🐛🐛-2025-05-12T14_19_08Z.html"></a>. This requires reading and processing the DWARF debugging information that's part of the binary. Since this is a rather complex task, I figured I  might use a library that exports a nice interface to the debugging information.

One such library that I found early on was [libelfin](https://github.com/aclements/libelfin)<a class="archive-link" href="/archive/GitHub%20-%20aclements_libelfin%20-%20%20C%2B%2B11%20ELF_DWARF%20parser-2025-05-12T14_19_10Z.html"></a>. It wasn't perfect from that start because it is a bit dated now, only supporting DWARF 4 and missing features from the newer DWARF 5 standard, but I thought that I could work around this. The bigger problem was that libelfin is written in C++ while most the debugger is written in C.

It is pretty easy to call code written in C from C++ since a lot of C is still part of the subset of C that C++ supports. The problem with calling C++ code from C is that there are many features in C++ that C is missing. This means that the C++ interface must be simplified for C to be able to understand it.

# Handling objects

The most important concept in C++ that C is missing is true object orientation. That is, in C [you don't get a this pointer for free](https://eev.ee/blog/2013/03/03/the-controller-pattern-is-awful-and-other-oo-heresy/)<a class="archive-link" href="/archive/The%20controller%20pattern%20is%20awful%20%28and%20other%20OO%C2%A0heresy%29%20_%20fuzzy%20notepad-2025-05-12T14_19_15Z.html"></a>; you need to handle it manually.

Let's start with a simple example. Say we have a class that represents a [rational number](https://en.wikipedia.org/wiki/Rational_number) $r = p / q$ where $q \neq 0$. The declaration without any of the operations we need might look something like this, which will print `5 / 3` when we run it.
```c++
// rational.h

class Rational {
public:
  int _numer;
  int _denom;

  Rational(int numer, int denom)
    : _numer{numer}, _denom{denom} {}
};
```

This is how we might use it in C++:
```c++
// main.cc
#include <iostream>
#include "rational.h"

auto main() -> int {
  auto r = Rational(5, 3);
  std::cout << r._numer << " / " << r._denom << std::endl;
  return 0;
}
```

How do you write this as a C program using the `Rational` class? After all, there is no such thing as a class in C. To solve this issue we can rely on one of the primitives that most systems languages have in common by virtue of running to the same type of computer: the pointer. We will allocate an instance of our class on the heap and then give the C program a pointer to that instance. This way we can keep track of the object to manipulate it. It's also possible to use handles for this, but they are just [pointers with extra steps](https://floooh.github.io/2018/06/17/handles-vs-pointers.html)<a class="archive-link" href="/archive/Handles%20are%20the%20better%20pointers-2025-05-12T14_19_19Z.html"></a> and a bit overkill for us at this point.

The following is what we might want.
```c
// main.c
#include <stdio.h>
#include "rational.h"

int main(void) {
  void *r = make_rational(5, 3);
  printf("%d / %d\n", get_numer(r), get_denom(r));
  del_rational(&r);
  return 0;
}
```
We need to extend our interface with all the new functions to construct, access and manually delete instances of `Rational`.
```c++
// rational.h
class Rational { /* ... */ };

void *make_rational(int numer, int denom);
int get_numer(const void *r);
int get_denom(const void *r);
void del_rational(void **rp);
```
```c++
// rational.cc
#include "rational.h"
#include <cstdlib>

void *make_rational(int numer, int denom) {
  // Allocate an instance on the heap.
  Rational *r = static_cast<Rational*>(malloc(sizeof(Rational)));
  r->_numer = numer;
  r->_denom = denom;
  return r;
}

int get_numer(const void *r) {
  // Cast to access members.
  const Rational *_r = static_cast<const Rational*>(r);
  return _r->_numer;
}

int get_denom(const void *r) {
  const Rational *_r = static_cast<const Rational*>(r);
  return _r->_denom;
}

void del_rational(void **rp) {
  Rational *_r = static_cast<Rational*>(*rp);
  // Delete the instance on the heap.
  free(_r);

  // Delete the dangling pointer too.
  *rp = nullptr;
}

```
The trick is to **allocate instances on heap and then pass them around as `void` pointers**. We use C's `malloc` instead of the `new` operator because the `new` operator is a C++ only feature which raises a linker error. A good way to improve type safety is to `typedef` an opaque type to represent the class on the C side, as suggested in [this reply](https://github.com/thass0/blog-code/issues/1#issue-1848643298)<a class="archive-link" href="/archive/re.%20Can%20you%20use%20a%20C%2B%2B%20class%20in%20C%20·%20Issue%20%231%20·%20thass0_blog-code%20·%20GitHub-2025-05-12T14_19_20Z.html"></a>. This is the approach that we'll be using later on, so keep on reading. Alternatively, if you have control over all of the C++ code (i.e. you don't just wrap a library) you could follow [this Stack Overflow answer](https://stackoverflow.com/a/7281477) too.

Now, ignoring how incredibly unsafe all of this is, there is a bigger problem we must face: this is not even close to compiling!
The reason for this is that when we `#include "rational.h"` into `main.c`, we essentially copy all the contents of `rational.h` into the C source file. This means that we suddenly present the C compiler with a class declaration and other things that it doesn't understand because they are part of a totally different language.

We can use the C preprocessor to help us here. Using the `__cplusplus` macro, we can check whether to include the C++ parts in the interface. This way it's hidden from the C compiler but available to the C++ compiler.
```c++
// rational.h
#ifdef __cplusplus
class Rational {
public:
  int _numer;
  int _denom;

  Rational(int numer, int denom)
    : _numer{numer}, _denom{denom} {}
};
#endif  // __cplusplus

// ...
```
Using the two different compilers to build, the program could look like this: `g++ -c rational.cc && gcc main.c rational.o`.

Great it compiles! But uhh ... now the linker signals an error. There are two problems left to fix. Firstly C++ uses a different [ABI](https://en.wikipedia.org/wiki/Application_binary_interface) than C which means that the calling convention is different. Additionally, C++ compilers mangle the names of identifiers in the source code differently than C compilers do, so the linker can't find them. Fortunately, C is the *lingua franca* of computer programming so C++ compilers can adapt their behavior in both of these aspects to that of C compilers. To do so, we just **prefix all C++ declarations that should be used by C code with `extern "C"`**.

This is very simple to do in the `rational.cc` source file, but requires some extra smartness in `rational.h`. Again, `extern "C"` is only a C++ feature, so it cannot be part of the header when the C compiler is looking at it. The solution to this is to use the `__cplusplus` macro once more.
```c++
// rational.h
#ifdef __cplusplus
class Rational { /* ... */ };
#endif  // __cplusplus


#ifdef __cplusplus
extern "C" {
#endif  // __cplusplus

void *make_rational(int numer, int denom);
int get_numer(const void *r);
int get_denom(const void *r);
void del_rational(void **rp);

#ifdef __cplusplus
}  // extern "C"
#endif  // __cplusplus

```

This wraps all of the function definitions in an `extern "C"` block when the C++ compiler is looking at it. After making those changes to `rational.h` and `rational.cc` we get the following output.
```sh
g++ -c rational.cc
gcc main.c rational.o
./a.out
5 / 3
```

We successfully created a class in C++ that we can now use in C!

Now that we have covered how to use the preprocessor to change the content of a file based on the compiler that's looking at it, we can make the API a bit safer, too. To do that we create an opaque type that acts a proxy for the `Rational` class on the C side. By only declaring this type, the C compiler will ensure that the pointers passed around in the interface are all of the same type (i.e. `Rational`). However, it won't let you dereference the pointers because the type is never really defined.
```c++
#ifdef __cplusplus

class Rational {
	// ...
};

#else

// Opaque type as a C proxy for the class.
typedef struct Rational Rational;

#endif // __cplusplus
```
In addition to that we now replace all `void *` with `Rational *`. This will allow you to remote some of the `static_cast`s from the beginning.

# Linking the C++ standard library

Above, we used `malloc` and a cast to allocate the instance of `Rational` to prevent a linker error later on. If we had used `new` and `delete` instead (which is the proper C++ way), we would have gotten linker errors like this one:

```
rational.cc:(.text+0x15): undefined reference to `operator new(unsigned long)'
```

Usually in a C++ program, this issue doesn't arise because `new` and `delete` are provided in the C++ standard library. The problem is that we used a C compiler to build the executable, which doesn't link the C++ standard library by default. The solution is to **pass the linker flag `-lstdc++` to the compiler explicitly**.

With `new` we can also use normal C++ constructors, making everything more concise and safe:
```c++
// rational.cc
#include "rational.h"

extern "C" Rational *make_rational(int numer, int denom) {
  // Now we're using the constructor.
  Rational *r = new Rational(numer, denom);
  return r;
}

// ...

extern "C" void del_rational(Rational **rp) {
  delete *rp;
  *rp = nullptr;
}
```

# Handling exceptions

Exceptions are another feature of C++ that C doesn't have. If the C++ code we wrapped throws an exception, the whole program will crash without doing any cleanup. This can be addressed in multiple ways, one of which is to pass `-fno-exceptions` to the C++ compiler to abort if a library throws an exception and to reject code that uses exceptions. The more realistic and safe approach is to carefully **catch all exceptions at the language boundary**.

If you take another look at the definition of rational numbers above, you'll notice that we don't actually ensure that $q \neq 0$. This will become problematic if we try to implement rational number arithmetic for our class. We'll address this by throwing an exception in the constructor if the denominator is 0.
```c++
// rational.h
#ifdef __cplusplus

#include <stdexcept>

class Rational {
public:
  int _numer;
  int _denom;

  Rational(int numer, int denom) {
    this->_numer = numer;
    if (denom == 0) {
      throw std::domain_error("denominator is 0");
    } else {
      this->_denom = denom;
    }
  }
};
#endif  // __cplusplus

// ...
```

Since we know now that the constructor might throw, we catch all exceptions in the wrapper and return a `nullptr` in case of an exception. In general, it's often a good idea to catch anything and return a generic error value such as null. In addition to that, you could add infinitely more complex error-handling schemes at the language boundary.

```c++
// rational.cc
#include "rational.h"

extern "C" Rational *make_rational(int numer, int denom) {
  try {
    // Allocate an instance on the heap.
    Rational *r = new Rational(numer, denom);
    return r;
  } catch (...) {
    return nullptr;
  }
}
```

In such a simple case it's also feasible to check if the denominator is 0 in `make_rational` but that doesn't apply to more realistic examples.

You can download the code from this post [here](/public/code/2025-05-13-can-you-use-a-class-in-c.tar.gz).

