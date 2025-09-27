"""
INTEGRATING LOW-LEVEL LANGUAGES IN PYTHON

What we'll cover:
- ctypes  : Call C functions from shared libraries you already have.
- cffi    : Declare C types/APIs in Python, call them, and manage C data.
- Cython  : Write Python-like code that compiles to a C extension for speed.

Rules of thumb (when to use what):
- Call existing C APIs with minimal setup? → ctypes or cffi (ABI mode).
- Need strong C type checking / allocate C structs easily? → cffi.
- Want to speed up tight Python loops or wrap your own C code? → Cython.
- Cross-platform note: Shared library names differ (libc/libm vs msvcrt/ucrtbase).
"""

from __future__ import annotations
import os, sys, textwrap, ctypes, ctypes.util


# ============================================================
# A) ctypes — Call C functions from shared libraries
# ============================================================
# WHAT/WHY (real use):
# - Quickest way to call into existing C libraries (no compilation step).
# - Real cases: call libc functions (printf/strlen/memset), OS APIs, simple wrappers
#   around numeric kernels already exposed from a .so/.dll.

import os, ctypes, ctypes.util

if os.name == "nt":  # Windows
    libc = ctypes.CDLL("msvcrt.dll")
else:  # Linux / macOS
    libc = ctypes.CDLL(ctypes.util.find_library("c"))

# call printf
printf = libc.printf
printf.restype = ctypes.c_int
printf.argtypes = [ctypes.c_char_p]
printf(b"[ctypes] hello from C printf!\n")


# ============================================================
# B) cffi — C declarations & C data from Python (C Foreign Function Interface)
# ============================================================
# WHAT/WHY (real use):
# - Write C signatures and structs in Python, then call into a library (ABI mode)
#   or compile a small C shim (API mode; out-of-line).
# - Real cases: safer & clearer type declarations than ctypes; allocate C structs
#   (ffi.new) and pass to functions; wrap smaller C headers without writing glue.

import os, cffi

ffi = cffi.FFI()
ffi.cdef("int puts(const char *s);")

if os.name == "nt":
    libc = ffi.dlopen("msvcrt.dll")
else:
    libc = ffi.dlopen(None)

libc.puts(b"[cffi] hello from puts")



# TODO : Implement differente sorting algorithms in python and Cython and compare performance. Use matplotlib for visualization.
