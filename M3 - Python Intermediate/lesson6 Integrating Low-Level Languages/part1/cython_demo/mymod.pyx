#cython: language_level=3

cpdef int c_add(int a, int b):
    """Return a + b"""
    return a + b

cpdef long dot_i64(long[:] a, long[:] b):
    """Tiny dot product over 1D memoryviews"""
    cdef Py_ssize_t i, n = a.shape[0]
    cdef long acc = 0
    for i in range(n):
        acc += a[i] * b[i]
    return acc

# === Exercises ===
cpdef int inc(int x):
    """Return x + 1"""
    return x + 1

cpdef long sum_i64(long[:] a):
    """Return sum of array"""
    cdef Py_ssize_t i, n = a.shape[0]
    cdef long acc = 0
    for i in range(n):
        acc += a[i]
    return acc
