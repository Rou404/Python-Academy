# ================================================
# parallel_theory_and_exercises.py
# ================================================
"""
PARALLEL PROGRAMMING (Beginner-first, CPU-bound focus)

Key ideas:
- The GIL limits *threads* for CPU-bound work; use *processes* to run in parallel.
- Prefer stateless/pure worker functions that accept inputs and return results.
- Processes don’t share memory by default → arguments & results are *pickled*.
- Pickling and process startup have overhead → batch small tasks (chunksize).
- Choose workers ~ os.cpu_count() (often a good starting point).
- Always guard multiprocessing entry points with: if __name__ == "__main__": ...

What we’ll practice:
- Baseline sequential vs ProcessPoolExecutor
- ordered map vs unordered as_completed
- chunking (batching) to reduce overhead
- a tiny word-count “map/reduce” pattern
"""

from __future__ import annotations
import os, time, math, random
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import Counter
from typing import Iterable, List, Tuple

random.seed(0)


# ------------------------------
# Raw Processes: start/join
# ------------------------------
# WHAT/WHY (real use):
# - Shows the *lowest-level* parallel primitive: mp.Process + Queue for IPC.
# - Use when you need maximum control (custom startup, affinity, shared memory),
#   or to teach what pools do under the hood.
# - Real cases: long-running worker processes, custom pipelines, sandboxing tasks.
def proc_worker(i: int, q: "mp.Queue[int]"):
    # Each process has its own memory space; use IPC (Queue/Pipe) to communicate.
    q.put((os.getpid(), i*i))

def demo_raw_processes(n=6):
    print("\n--- Raw processes: Process.start() / join() ---")
    # ALWAYS protect entry point on Windows/macOS 'spawn':
    if __name__ == "__main__":
        q = mp.Queue()
        procs = [mp.Process(target=proc_worker, args=(i, q)) for i in range(n)]

        for p in procs:
            p.start()
        for p in procs:
            p.join()

        results = [q.get() for _ in procs]
        print("pid, value^2:", results)

# (Optional) run once at import so students see it work; comment out if you prefer.
demo_raw_processes()


# ------------------------------
# 0) CPU-bound example workload
# ------------------------------
# WHAT/WHY (real use):
# - A deliberately slow numeric function to simulate “CPU-bound” work.
# - Real cases: analytics, simulation, image/video processing, cryptography, ML preprocessing.
def count_primes(n: int) -> int:
    """Very naive prime counting (intentionally slow)."""
    def is_prime(x: int) -> bool:
        if x < 2: return False
        r = int(math.isqrt(x))
        for d in range(2, r + 1):
            if x % d == 0:
                return False
        return True
    return sum(1 for x in range(n) if is_prime(x))


# ------------------------------------
# 1) Sequential vs parallel (ordered)
# ------------------------------------
# WHAT/WHY (real use):
# - Baseline timing vs. ProcessPool map to show *true* speedup on multiple cores.
# - Use ordered map when you care about the result order matching inputs
#   (e.g., batch scoring that must line up with IDs).
def demo_sequential(ns=(55_000, 60_000, 62_000, 64_000)):
    print("\n--- Sequential baseline ---")
    t0 = time.perf_counter()
    results = [count_primes(n) for n in ns]
    dt = time.perf_counter() - t0
    print("results:", results)
    print(f"elapsed: {dt:.3f}s (pid={os.getpid()})")

def demo_process_pool_ordered(ns=(55_000, 60_000, 62_000, 64_000), workers=None):
    print("\n--- ProcessPoolExecutor: ordered map ---")
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        # map preserves input order
        results = list(pool.map(count_primes, ns))
    dt = time.perf_counter() - t0
    print("results:", results)
    print(f"elapsed: {dt:.3f}s with {workers or os.cpu_count()} workers")


# ---------------------------------------------------
# 2) Unordered collection (streaming as they finish)
# ---------------------------------------------------
# WHAT/WHY (real use):
# - Use as_completed when you want *responsiveness*: handle fast results ASAP,
#   show progress bars, stream partial results, or early-stop on certain outcomes.
# - Real cases: batch jobs with mixed runtimes, scraping/conversion pipelines.
def demo_process_pool_unordered(ns=(55_000, 60_000, 62_000, 64_000), workers=None):
    print("\n--- ProcessPoolExecutor: unordered as_completed ---")
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        fts = {pool.submit(count_primes, n): n for n in ns}
        results = []
        for ft in as_completed(fts):
            n = fts[ft]
            res = ft.result()
            print(f"finished n={n} -> {res}")
            results.append((n, res))
    dt = time.perf_counter() - t0
    results.sort()  # sort by n for display
    print("results (sorted):", results)
    print(f"elapsed: {dt:.3f}s")


# -----------------------
# 3) Chunking / batching
# -----------------------
# WHAT/WHY (real use):
# - Each task has overhead (pickling, scheduling, startup). Batch small inputs
#   into *chunks* to amortize overhead and boost throughput.
# - Real cases: tiny images/records/rows that are cheap individually but huge in count.
def chunked(seq: Iterable, size: int) -> Iterable[list]:
    buf = []
    for x in seq:
        buf.append(x)
        if len(buf) == size:
            yield buf
            buf = []
    if buf:
        yield buf

def count_primes_many(ns_chunk: list[int]) -> list[int]:
    """Worker that processes a chunk of inputs (reduces overhead)."""
    return [count_primes(n) for n in ns_chunk]

def demo_chunked_map(ns=(50_000, 52_000, 54_000, 56_000, 58_000, 60_000), chunksize=2, workers=None):
    print("\n--- Chunked parallel map ---")
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        chunk_results = list(pool.map(count_primes_many, chunked(ns, chunksize)))
    # flatten back to original order
    results = [r for chunk in chunk_results for r in chunk]
    dt = time.perf_counter() - t0
    print("results:", results)
    print(f"elapsed: {dt:.3f}s (chunksize={chunksize}, workers={workers or os.cpu_count()})")


# ---------------------------------
# 4) Tiny “map” word count
# ---------------------------------
# WHAT/WHY (real use):
# - Classic parallel pattern: map independent pieces → reduce (merge) results.
# - Real cases: log processing, text analytics, ETL, simple data science pipelines.
def wordcount_worker(text: str) -> Counter:
    words = [w.strip(".,!?:;\"'()[]").lower() for w in text.split()]
    return Counter(w for w in words if w)

def demo_wordcount_parallel():
    print("\n--- Parallel word count (map/reduce) ---")
    docs = [
        "Red fish blue fish.",
        "One fish two fish red fish blue fish.",
        "Fish are friends, not food.",
        "So many fish in the sea!"
    ]
    t0 = time.perf_counter()
    with ProcessPoolExecutor() as pool:
        parts = list(pool.map(wordcount_worker, docs))
    total = Counter()
    for c in parts:
        total.update(c)
    dt = time.perf_counter() - t0
    print("Top words:", total.most_common(5))
    print(f"elapsed: {dt:.3f}s")


# ----------------
# Run the demos
# ----------------
if __name__ == "__main__":
    # Keep inputs modest so it runs quickly in class.
    demo_sequential()
    demo_process_pool_ordered()
    demo_process_pool_unordered()
    demo_chunked_map()
    demo_wordcount_parallel()

