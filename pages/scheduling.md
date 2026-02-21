---
layout: post
title: Scheduling in a Bare-Metal Web Server
path: /scheduling.html
date: 21 Feb 2026
datetime: 2026-02-21
---

<details>
    <summary>Written without generative AI.</summary>
    I did not use generative AI to assist in writing this text. I'm sure this is evident
    from the way the prose sounds, although, of course, I would be happy if it had fewer
    rough edges.
</details>

The Tatix system is a kernel that's designed only to serve web pages. I tried to build it in
the Einsteinian fashion of "as simple as possible but no simpler". This means it's not code golf
trying to fit a web server and a bootloader in the last amount of code possible (I can certainly
think of some things I could strip if I wanted to). But, still, it should only have the features
necessary to serve web pages.

In this post, I discuss the design choices that went into the scheduler that is used in Tatix
and how explicit locking is avoided almost completely in the system.

## Why Every Server Needs a Scheduler

Why does Tatix need a scheduler at all? Say you want to write a server of some kind, be it
a web server handling HTTP requests or a kernel handling system calls. In this case, you need
to deal with concurrent requests from multiple clients. In the case of Tatix, I wanted to write
a web server that uses TCP. I will stick to this concrete setting but I think the reasoning can be
applied more broadly.

Consider two clients, client A and client B, who make concurrent requests to the server. Client A 
makes the first request and we can respond right away. In general, the response can be large, so
it may be transmitted as multiple TCP segments, each of which is retransmitted by the server
until the client acknowledges that it received the segment. TCP uses a sliding window as a means
of flow control, i.e. to avoid overwhelming the receiver with more data than it can reliably process
in a given amount of time. This means that the transmission process will look like this: we start
by sending segments to client A until the window is full. Then we wait to receive acknowledgements
from client A. Receiving acknowledgements frees up space in the window, which means we can send
a few more segments. This continues in a loop until all data has been transmitted and acknowledged.

In Tatix, the code we're talking about looks something like this. The `tcp_conn_send` function
returns 0 if the sliding window is full.
```c
static struct result web_respond_close(struct tcp_conn *conn, struct byte_view response, struct arena tmp)
{
    sz n_transmitted = 0;
    bool peer_closed_conn = false;

    while (!peer_closed_conn) {
        struct byte_view transmit = byte_view_skip(response, n_transmitted);
        struct result_sz res = tcp_conn_send(conn, transmit, &peer_closed_conn, tmp);
        if (res.is_error) {
            tcp_conn_close(&conn, tmp);
            return result_error(res.code);
        }

        n_transmitted += result_sz_checked(res);
        if (n_transmitted >= response.len)
            break;

        receive_acks_and_poll_retransmit(); // Pseudo-code. The actual implementation is revealed later.
    }

    return tcp_conn_close(&conn, tmp);
}
```

Let us assume that we are currently in the loop where we are transmitting data piece by piece.
At this point, client B comes in with a request of its own. We could wait until the response
for client A was fully served before responding to client B, but that might take a while if, e.g.,
there is a lot of packet loss on the connection to client A. What we really want is to serve
both client A and client B concurrently.

We are looking for a way to pause serving client A for a while so that we can serve client
B instead and return to client A afterward. We need to remember where we left off, so, for each
client, we need to store all the state that's passed to and kept in the `web_response_close`
function (i.e. `struct tcp_conn *conn`, `struct byte_view response`, and `n_transmitted` plus
the arena). Then we can add extra return statements to `web_respond_close` that return different
status codes and put a loop around `web_response_close` that calls it for each connection and
advances the state until all data was sent.

This solution works well in simple cases and I have seen this approach used in simple web
servers.[^1] The problem with this approach is that it doesn't scale well, because all concurrent
tasks have to be aware of each other. Consider that there must also be a mechanism to accept
incoming connections and that we need to perform a TCP handshake with the client before it
can be accepted. So this would also need to be added to the loop. And what about other
protocols like ARP or ICMP? Even more states to consider.

When you need to concurrently serve requests for different protocols from different layers
of the network stack, the approach of looping and switching on the state becomes very
complicated. Fortunately, there is a simple solution to this problem. It's an elegant
state-keeping machine that, among other things, decouples concurrent tasks from each
other; it's a scheduler.

## How a Cooperative Scheduler Works

A scheduler allows multiple tasks to run concurrently and, possibly, in parallel on multiple
hardware threads. In Tatix, however, I use only a single hardware thread, so we're only
talking about concurrency here. I will refer to the different threads of execution that
are managed by the scheduler as _tasks_ because I don't want to cause confusion with
true hardware threads that are executed in parallel.

The scheduler manages a number of tasks that are registered with it. It decides which
task should run at a given time and can pause a task's execution to resume it later
and to allow other tasks to run in the meantime. On x86, each task must have its own
stack and each task's registers must be saved and restored when it's paused and resumed.
The latter can be done by pushing the registers onto the stack before pausing the task
and popping the registers off the stack when resuming. The stack is used in this way to
store all the state associated with a task, agnostic to any details of how this
state looks.

The "cooperative" in cooperative scheduler means that a task cannot be interrupted
involuntarily. It must call into the scheduler explicitly to relinquish control. This is
in contrast to a preemptive scheduler, where execution is interrupted from time to time
(say by a timer interrupt) and it's possible that, during the interruption, the scheduler
decides that another task should run. When using a preemptive scheduler, code must be
written assuming it can be interrupted at any time. (This is the situation people often
think of when writing concurrent programs in, say, Linux userspace.)

Reasoning about code executed under a cooperative scheduler is much easier than reasoning
about code executed under a preemptive scheduler. Preemtive schedulers are most useful when
you can't trust the code you're executing to relinquish control voluntarily. In the context
of Tatix, I'm writing all the code myself so a cooperative scheduler is just fine.

This is what the interface to the cooperative scheduler used in Tatix looks like:

```c
struct sched_task {
    byte stack[TASK_STACK_SIZE];
    u64 *stack_ptr;

    struct time_ms wake_time;
    u16 id;

    sched_callback_func_t callback;
    void *context;

    struct dlist sleep_list;
};

void sched_init(void);
struct result sched_create_task(sched_callback_func_t callback, void *context);
void sleep_ms(struct time_ms duration);
```
The function `sched_init` must be called before using the scheduler for the first time.
Calling this function turns the calling thread of execution into the main task. At this point,
it's the only task that's running. Additional tasks are registered with `sched_create_task`.
Whenever this function is called, a new `struct sched_task` is created internally and added
to the doubly linked list `sleep_list`. The currently executing task can call `sleep_ms` to
enter the scheduler. `sleep_ms` will update the `wake_time` of the calling task and add the task
to the `sleep_list`. Then it picks the next task to run and context switches to this task.
After context switching, the newly running task is removed from the `sleep_list`. Tasks
are scheduled in round-robin fashion, so all tasks that are ready to execute are scheduled
one after the other. The internals require some architecture-specific magic, but overall
it's not too complicated.

Note that there is no locking used in the implementation of the scheduler. That's only
possible because it's cooperative. In a preemptive scheduler, you need locks to protect
critical sections, but, in a cooperative scheduler, they can be avoided by calling
`sleep_ms` outside of critical sections only.

## Using the Scheduler

Let's now see how the problem of state-keeping and handling concurrent requests is solved
in Tatix using the scheduler. This is how the `web_response_close` function really looks.
Nothing changed except we're calling into the scheduler instead of calling the 
`receive_acks_and_poll_retransmit()` pseudo-code from above.
```c
static struct result web_respond_close(struct tcp_conn *conn, struct byte_view response, struct arena tmp)
{
    sz n_transmitted = 0;
    bool peer_closed_conn = false;

    while (!peer_closed_conn) {
        struct byte_view transmit = byte_view_skip(response, n_transmitted);
        struct result_sz res = tcp_conn_send(conn, transmit, &peer_closed_conn, tmp);
        if (res.is_error) {
            tcp_conn_close(&conn, tmp);
            return result_error(res.code);
        }

        n_transmitted += result_sz_checked(res);
        if (n_transmitted >= response.len)
            break;

        sleep_ms(time_ms_new(10)); // Wait a bit for ACKs to arrive.
    }

    return tcp_conn_close(&conn, tmp);
}
```
During startup, a few tasks are created and any or all of them may be executed when
`sleep_ms` is called in `web_response_close` (except of course for the task from which
`web_response_close` was called). The key tasks are:

* `task_tcp_poll_retransmit`. This task calls into the TCP subsystem to retransmit all
  unacknowledged segments if their retransmission timer has run out.
* `task_net_receive`. This task checks if any data has been received by the ethernet
  driver. If so, it passes the data up the network stack.
* `task_web_listen`. This task runs the web server. It's the task from which
  `web_respond_close` is called.

This is an example of what the code for `task_tcp_poll_retransmit` looks like:
```c
static void task_tcp_poll_retransmit(void *ctx_ptr __unused)
{
    struct arena tmp = arena_new(option_byte_array_checked(kvalloc_alloc(0x2000, 64)));

    while (true) {
        struct result res = tcp_poll_retransmit(tmp);
        if (res.is_error)
            print_dbg(PDBG, STR("Error in TCP retransmission: %hu\n"), res.code);
        sleep_ms(time_ms_new(10));
    }
}
```
The function itself is called just once when the task executes for the first time.
From then on, the task is stuck in the `while` loop forever.

## Avoiding Explicit Locks

You might think that we need locks in the TCP subsystem because it can be entered
from three different tasks concurrently (`task_tcp_poll_retransmit`, `task_net_receive`,
and `task_web_listen` can all call into the TCP subsystem at some point). But that's
not true, actually. This feels like cheating, but let me explain why it works.[^2]

It all comes back to the fact that the scheduler is cooperative, meaning that tasks
can be switched only when a call to `sleep_ms` is made. Consider why locks are usually
required when multiple tasks call into the same subsystem. It's because, without a lock,
a task modifying the state of the subsystem might be interrupted while the state is in a
temporary, invalid state. Then another task is executed and finds the subsystem in the
invalid state. This can wreak havoc to the system as a whole.

But if `sleep_ms` is not called, execution is not interrupted. It's like all code between
two calls to `sleep_ms` is part of a big critical section that's guarded by a lock. There
are no calls to `sleep_ms` in the TCP subsystem, which means it's always entered and exited
in a valid state. There are just 9 calls to `sleep_ms` in the entire codebase, so it's easy
to make sure no global state is messed up.

I trired to come up with a simple rule for when calling `sleep_ms` is or isn't allowed. My
current best guess is: If a function (a) modifies global variables and (b) can be called from more
than one task, then it must not call `sleep_ms`. Otherwise, the call to `sleep_ms` would delimit
a critical section and, as the function modifies global variables, this means there is potential
for a task switch to happen in the process of the modification.


## A Note on Interrupts

I was lying before when I said execution can only be interrupted when `sleep_ms` is called.
Actually, there is a timer interrupt that fires periodically and the NIC also generates
interrupts when data arrives. The timer interrupt is a no-op so we can act like it doesn't
exist.

The ethernet driver code (`src/net/e1000.c` and `src/net/netdev.c`) uses a queue for
incoming packets. The interrupt handler of the e1000 NIC only interacts with the e1000 device
and with this queue. Accesses to the queue from outside the interrupt handler occur when
the `task_net_receive` task checks for new data. These accesses are indeed guarded by
disabling and enabling interrupts, which is functionally identical to locking and unlocking
the critical section of the queue.

---

[^1]: The reason why `select(2)`-based web servers work well is that most of the
state-keeping happens in the kernel, which has a scheduler.

[^2]: It feels so much like cheating, in fact, that I frequently doubt the correctness
of my approach. Like there must be a problem with this at some point! You should be extra
suspicious when you feel really smart about a solution you've found.


