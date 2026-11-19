# Written Reflection

## How I engaged with AI
I started by telling Claude my background (I know C, pointers and basic memory
management, but not assembly) and that I knew nothing about this topic, so I
wanted to understand the concepts before running any experiments. From there I
used the conversation like a tutor. When something wasn't clear I asked
follow-ups, like what cache locality and prefetching actually are, what
reference counts are and why Python updates them, and what "overhead" really
means. I also tested my own understanding by explaining things back in my own
words, and Claude pointed out where I had it wrong. Later I wrote and ran the
experiments myself on my own machine, then pasted my output back to talk
through what the numbers meant.

## Prompts I used
1. **Learn first, then experiment:** "i know nothing about this topic so lets
   learn it first, instead of going straight to the experiment, can you explain
   and explore how libraries like NumPy achieve high performance by implementing
   computationally intensive operations in C. Investigate how Python programs
   can call functions written in C and why this approach can improve
   performance." This gave me the mental model (boxed objects, contiguous
   arrays, the cost of crossing from Python to C) before I touched any code.
2. **Questioning the experiment:** "is this valid experiement as where did u
   derive this from, is there a source where u got this from". Claude admitted
   it had designed the experiment itself, ran it to check that it works, and
   found sources (the `timeit`, NumPy and CPython docs). That helped me
   separate what was backed by sources from what I had to verify myself.
3. **Explaining back and getting corrected:** "as a C pointer only carries the
   address, C has no way of knowing how many elements the array has, if n is
   passed separately the array doesnt decay to a pointer". The first half was
   right, but I had cause and effect backwards: the array decays to a pointer
   no matter what, and `n` is passed separately *because* of that.

## What I'd do differently
- Start earlier. I did most of this the night before my slot, which made me
  rush.
- Read the check questions more carefully. I misread one of them and answered
  the wrong scenario (a single C call instead of one call per element).
- Ask for sources and verify claims sooner, instead of only after I'd already
  built on them.

## Conversation link
https://claude.ai/share/d812f72b-8e6e-41c0-8587-27340189cbb4