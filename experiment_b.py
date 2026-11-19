import ctypes, os, sys, time
import numpy as np

N = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000

# 1. Load the compiled C library (.dylib on Mac, .so on Linux).
ext = ".dylib" if sys.platform == "darwin" else ".so"
here = os.path.dirname(os.path.abspath(__file__))
LIB_PATH = os.path.join(here, "c", "libsumlib" + ext)
lib = ctypes.CDLL(LIB_PATH)

# 2. Tell ctypes each function's signature. The compiled library only
#    contains names and addresses, not argument or return types.
lib.sum_array.argtypes = [ctypes.POINTER(ctypes.c_int64), ctypes.c_int64]
lib.sum_array.restype = ctypes.c_int64
lib.add.argtypes = [ctypes.c_int64, ctypes.c_int64]
lib.add.restype = ctypes.c_int64

arr = np.arange(N, dtype=np.int64)
py_list = list(range(N))
# Pointer to NumPy's raw buffer: handing it to C copies nothing.
ptr = arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64))

def best_of(fn, runs=5):
    best = float("inf")
    for _ in range(runs):
        t = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - t)
    return best

def python_loop():
    total = 0
    for x in py_list:
        total += x
    return total

def c_call_per_element():
    add = lib.add
    total = 0
    for x in py_list:
        total = add(total, x)       # crosses Python -> C once per element
    return total

def c_whole_array():
    return lib.sum_array(ptr, N)    # crosses Python -> C once

expected = N * (N - 1) // 2
assert python_loop() == expected
assert c_call_per_element() == expected
assert c_whole_array() == expected
assert int(np.sum(arr)) == expected

print(f"--- {N:,} elements (best of runs, seconds) ---")
results = {
    "pure Python loop            ": best_of(python_loop, 3),
    "Python loop calling C add() ": best_of(c_call_per_element, 3),
    "ONE call to C sum_array()   ": best_of(c_whole_array, 5),
    "np.sum                      ": best_of(lambda: np.sum(arr), 5),
}
for name, secs in results.items():
    print(f"{name}: {secs:.6f} s   ({secs / N * 1e9:.2f} ns per element)")

print("--- what if we forget restype? ---")
lib_bad = ctypes.CDLL(LIB_PATH)              # a fresh handle with no signatures set
lib_bad.sum_array.argtypes = [ctypes.POINTER(ctypes.c_int64), ctypes.c_int64]
# restype NOT set: ctypes assumes the function returns a 32-bit int
print("correct answer      :", expected)
print("without restype     :", lib_bad.sum_array(ptr, N))