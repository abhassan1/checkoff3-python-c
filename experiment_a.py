import sys, time, timeit, random
import numpy as np

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000_000
py_list = list(range(N))
np_arr = np.arange(N, dtype=np.int64)

def best_of(fn, runs=5):
    best = float("inf")
    for _ in range(runs):
        t = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - t)
    return best

def loop_sum(xs):
    total = 0
    for x in xs:
        total += x
    return total

# sanity check: every method must agree before we trust its timing
expected = N * (N - 1) // 2
assert loop_sum(py_list) == expected
assert sum(py_list) == expected
assert int(np.sum(np_arr)) == expected
assert loop_sum(np_arr) == expected

print(f"--- {N:,} elements (best of runs, seconds) ---")
print("python loop over list   :", best_of(lambda: loop_sum(py_list), 3))
print("builtin sum over list   :", best_of(lambda: sum(py_list), 3))
print("np.sum over ndarray     :", best_of(lambda: np.sum(np_arr), 5))
print("python loop over ndarray:", best_of(lambda: loop_sum(np_arr), 3))

print("--- memory ---")
print("one int object          :", sys.getsizeof(py_list[-1]), "bytes")
print("list's pointer array    :", sys.getsizeof(py_list) / N, "bytes per element")
print("ndarray                 :", np_arr.nbytes / N, "bytes per element")

print("--- tiny arrays (100k calls, seconds) ---")
small_list = list(range(10))
small_arr = np.arange(10, dtype=np.int64)
print("sum(small_list)         :", timeit.timeit(lambda: sum(small_list), number=100_000))
print("np.sum(small_arr)       :", timeit.timeit(lambda: np.sum(small_arr), number=100_000))

print("--- optional: does memory order matter? ---")
shuffled = py_list[:]
random.shuffle(shuffled)
print("sum(list), in order     :", best_of(lambda: sum(py_list), 3))
print("sum(list), shuffled     :", best_of(lambda: sum(shuffled), 3))