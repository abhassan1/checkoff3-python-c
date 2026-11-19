# Python Libraries Implemented in C

## Overview
Python is popular for numerical work, but a plain Python loop is slow: every number is a heap-allocated object, and every addition goes through the interpreter. Libraries like NumPy avoid this by moving the heavy loops into compiled C code that works on raw, contiguous memory. This repository looks at why that makes such a big difference, and how Python and C communicate.

## What I explored

### Why plain Python loops are slow
In CPython, every integer is a heap-allocated object with a reference count and
a type pointer (`sys.getsizeof` reports 28 bytes for one int on my machine,
versus 8 bytes for a C `int64_t`). A Python list does not store the numbers, but
pointers to those objects, so reading element `i` means following a pointer.
On every loop iteration, Python also checks the types of both operands, creates
a new int object for the result, updates reference counts (and frees the old
total when its count reaches zero), and dispatches bytecode through the
interpreter. I use **overhead** to mean all of this work that is not the
addition itself. The addition is one CPU instruction, but Python pays this cost
on every element.

### How NumPy avoids it
A NumPy array is a C struct with a small header (data pointer, dtype, shape,
strides) pointing at one contiguous block of raw values, like a C array. When I
call `np.sum(arr)`, Python pays its overhead once to call the function. The
dtype is checked once, and a C loop that was compiled for that type runs over
the raw buffer, with no per-element objects, type checks or interpreter. Only
the final result gets wrapped into a Python object. NumPy's documentation
describes the same idea: the looping happens in pre-compiled C code.

### How Python calls C
I wrote two small C functions (`c/sumlib.c`): `sum_array`, which loops over an
array, and `add`, which adds two numbers. I compiled them into a shared library
and loaded it from Python with `ctypes`. The compiled library contains only
function names and addresses, not types (I checked with `nm`), so ctypes needs
`argtypes` and `restype` to know each function's signature. NumPy's buffer can
be passed to C as a pointer without copying. Because a C pointer carries only an
address, the length `n` must be passed separately.

### The experiments
- **`experiment_a.py`:** times a Python loop, `sum()`, and `np.sum` over 10
  million integers, also looping over an ndarray, memory per element, tiny
  10-element arrays, and a shuffled-vs-in-order list.
- **`ctypes_demo.py`:** calls my C functions from Python as a first check.
- **`experiment_b.py`:** compares a pure Python loop, a Python loop that calls
  the C `add()` once per element, one call to C `sum_array()`, and `np.sum`, and
  shows what happens if `restype` is left out.

## Key discoveries

1. **Moving the loop into C is what makes NumPy fast.** Over 10 million
   elements, `np.sum` took 0.00123 s versus 0.153 s for a Python loop (about
   124x faster). Both compute the same result, but one runs a C loop over raw
   contiguous values and the other pays interpreter and object overhead on
   every element.
2. **Calling C is not automatically faster; crossing the boundary has a cost.**
   A Python loop calling a trivial C `add()` once per element took about 315 ns
   per element, versus about 16 ns for pure Python (about 20x slower). The cost
   of each Python-to-C call is far larger than the addition itself. One call to
   C `sum_array()` over the whole array took 0.000093 s for 1 million elements,
   tying with `np.sum` (0.000092 s), so for this simple operation NumPy's speed
   comes from a C loop over contiguous memory like the one I wrote.
3. **NumPy's advantage disappears if the loop stays in Python.** Looping over an
   ndarray with a Python `for` loop took 0.365 s, about 2.4x slower than looping
   over a list, because each iteration has to create a new NumPy scalar object.
   And on a 10-element array, `np.sum` was about 10.7x slower than `sum()` on a
   list (about 800 ns vs 75 ns per call) because of NumPy's fixed per-call cost.
4. **ctypes has no safety net.** Without `restype`, ctypes assumed a 32-bit
   return value, so the correct sum `499999500000` came back as `1783293664`
   (the low 32 bits) with no error.
5. **Memory layout seems to matter.** Summing a list whose pointers were
   shuffled took 0.156 s versus 0.0319 s in order (about 4.9x), consistent with
   cache and pointer-chasing effects, though timing alone doesn't prove the
   cause.

## Repository contents
```
README.md
requirements.txt
experiment_a.py      # Python loop vs NumPy
ctypes_demo.py       # calling C from Python
experiment_b.py      # cost of crossing the Python/C boundary
c/sumlib.c           # the C functions
results/             # saved output from my runs
slides/              # presentation slides
```

## How to run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Build the C library (the compiled file is not committed)
clang -O2 -shared -fPIC -o c/libsumlib.dylib c/sumlib.c    # macOS
# gcc -O2 -shared -fPIC -o c/libsumlib.so c/sumlib.c        # Linux

python experiment_a.py 2000000   # quick run
python experiment_a.py           # full run (10M elements, needs a few hundred MB of RAM)
python ctypes_demo.py
python experiment_b.py           # 1M elements
```

## Methodology notes

- Timings use the best (minimum) of several runs measured with
  `time.perf_counter()`, as the Python `timeit` documentation recommends,
  because slower runs are usually caused by other processes. Each script also
  checks that every method computes the same sum before timing it.
- Experiment A uses 10 million elements. The tiny-array test (10 elements)
  reports the total for 100,000 calls via `timeit`. Experiment B uses
  1 million elements.
- Results come from one machine (Apple M2, Python 3.13.9) and will differ on
  other hardware and Python versions. The raw output of my runs is in `results/`.
- The shuffle result is consistent with cache effects, but timing alone does
  not prove the cause.

## Resources

- Python `timeit` docs: https://docs.python.org/3/library/timeit.html
- NumPy, "What is NumPy?" (see "Why is NumPy fast?"): https://numpy.org/doc/stable/user/whatisnumpy.html
- CPython internals, reference counting: https://sources.debian.org/src/python3.14/3.14.0-5/InternalDocs/garbage_collector.md
- Python `ctypes` docs: https://docs.python.org/3/library/ctypes.html

## Slides

See the `slides/` folder.