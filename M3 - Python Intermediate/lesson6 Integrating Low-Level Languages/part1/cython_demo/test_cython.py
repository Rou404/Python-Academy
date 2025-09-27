"""
pip install -U pip setuptools wheel cython
pip install .
"""

import array
import array
import mymod

print("=== Testing mymod ===")

# --- Test c_add ---
print("[Cython] c_add(2, 3) =", mymod.c_add(2, 3))
print("[Cython] c_add(-5, 10) =", mymod.c_add(-5, 10))

# --- Test inc ---
print("[Cython] inc(10) =", mymod.inc(10))
print("[Cython] inc(-1) =", mymod.inc(-1))

# --- Prepare arrays for dot_i64 and sum_i64 ---
a = array.array("l", [1, 2, 3])
b = array.array("l", [4, 5, 6])

# --- Test dot_i64 ---
print("[Cython] dot_i64([1,2,3], [4,5,6]) =", mymod.dot_i64(a, b))
# Manual check: 1*4 + 2*5 + 3*6 = 32

# --- Test sum_i64 ---
print("[Cython] sum_i64([1,2,3]) =", mymod.sum_i64(a))
print("[Cython] sum_i64([4,5,6]) =", mymod.sum_i64(b))
