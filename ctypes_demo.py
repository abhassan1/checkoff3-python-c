import ctypes, os, sys
import numpy as np

# 1. Find and load the compiled library
ext = ".dylib" if sys.platform == "darwin" else ".so"
here = os.path.dirname(os.path.abspath(__file__))
lib = ctypes.CDLL(os.path.join(here, "c", "libsumlib" + ext))

# 2. Declare each function's signature
lib.add.argtypes = [ctypes.c_int64, ctypes.c_int64]
lib.add.restype = ctypes.c_int64
lib.sum_array.argtypes = [ctypes.POINTER(ctypes.c_int64), ctypes.c_int64]
lib.sum_array.restype = ctypes.c_int64

# 3. Call the simple function
print("add(2, 3) =", lib.add(2, 3))

# 4. Call sum_array on a NumPy array
arr = np.array([1, 2, 3, 4, 5], dtype=np.int64)
ptr = arr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64))
print("address of array's buffer:", hex(arr.ctypes.data))
print("sum_array([1..5]) =", lib.sum_array(ptr, len(arr)))