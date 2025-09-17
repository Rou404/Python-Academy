"""
CONCURRENCY FUNDAMENTALS (Threads only)


WHAT THIS LESSON COVERS:
- Concurrency vs. Parallelism (high level)
- Raw threads: Thread.start() / Thread.join()
- ThreadPoolExecutor for I/O-bound work
- Futures API: submit, map, as_completed
- Data races & Lock basics
- Producer/Consumer with queue.Queue + the sentinel pattern

TEACHER TAKEAWAY:
- Threads help when tasks spend time WAITING (network, disk, I/O, sleep).
- Due to the GIL, threads do not speed up Python CPU math — that’s for processes.
"""

from __future__ import annotations
import os
import time
import random
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed

random.seed(0)

# ------------------------------
# 0) KEY IDEAS (cheat-sheet)
# ------------------------------

# Concurrency: Do multiple tasks seemingly at once by interleaving steps.
# Threads (in CPython): great for I/O-bound tasks (waiting on network/disk/sleep).
# GIL: Only one thread executes Python bytecode at a time → no CPU speedups.
# Futures API:
#   - executor.submit(fn, *args) -> Future (start work, get a handle)
#   - executor.map(fn, iterable) -> results in input order
#   - as_completed(futures)      -> futures as they finish (completion order)
#   - future.result()            -> return value or re-raise worker exception


# ===============================================================
# 1) RAW THREADS: START / JOIN
# ===============================================================
# WHAT THIS SHOWS:
#   The lifecycle of a thread: create → start() → join(). Results come back in
#   whatever order threads finish; you manage the list/locking yourself.
#
# WHY IT MATTERS:
#   Understanding start/join demystifies what ThreadPool does for you and
#   makes it easier to debug real-world issues.

def th_worker(i: int, out: list[int]):
    """Pretend I/O by sleeping, then append a result."""
    time.sleep(0.2)
    out.append(i)

def demo_raw_threads(n=6):
    results: list[int] = []
    threads: list[threading.Thread] = []

    print("\n--- Raw threads: Thread.start() / join() ---")
    for i in range(n):
        t = threading.Thread(target=th_worker, args=(i, results))
        t.start()
        threads.append(t)

    # Wait for all threads to finish
    for t in threads:
        t.join()

    print("results (unordered):", results)
    print("any alive after join?:", any(t.is_alive() for t in threads))


# ===============================================================
# 2) THREAD POOL (I/O-BOUND): MAP (ORDERED) & AS_COMPLETED
# ===============================================================
# WHAT THIS SHOWS:
#   Two ways to collect results from a thread pool.
#   - map(): returns results in the same order as inputs (simplest).
#   - as_completed(): yields results as soon as each task finishes (great for streaming/logging).
#
# WHY IT MATTERS:
#   Picking ordered vs. completion-ordered collection changes responsiveness.

def fake_io(task_id: int) -> str:
    """Simulate I/O latency and return a small message."""
    time.sleep(random.uniform(0.15, 0.30))
    return f"pid={os.getpid()} task={task_id}"

def demo_threadpool_map(n=8):
    print("\n--- ThreadPoolExecutor: map (ordered results) ---")
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(fake_io, range(n)))  # preserves input order
    print("results:", results)
    print(f"elapsed: {time.perf_counter() - t0:.3f}s")

def demo_threadpool_as_completed(n=8):
    print("\n--- ThreadPoolExecutor: as_completed (completion order) ---")
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(fake_io, i) for i in range(n)]
        finished_in = []
        for fut in as_completed(futures):       # yields as each finishes
            r = fut.result()                    # also re-raises worker exceptions here
            finished_in.append(r)
            print("done:", r)
    print("completion order:", finished_in)


# ===============================================================
# 3) DATA RACES & LOCKS
# ===============================================================
# WHAT THIS SHOWS:
#   Multiple threads writing a shared variable without synchronization
#   can lose updates (race condition). A Lock fixes it by making the
#   critical section atomic (one thread at a time).
#
# WHY IT MATTERS:
#   Many “weird” concurrency bugs are just races. Students should be
#   able to recognize the pattern and know the fix.

counter = 0
lock = threading.Lock()

def increment_racy(times: int):
    """Increment a shared counter WITHOUT a lock (racy)."""
    global counter
    for _ in range(times):
        local = counter
        local += 1
        time.sleep(0.0001)  # exaggerate the race
        counter = local

def increment_safe(times: int):
    """Increment a shared counter WITH a lock (safe)."""
    global counter
    for _ in range(times):
        with lock:
            counter += 1

def demo_race_and_lock():
    global counter
    print("\n--- Race condition demo (and fix with Lock) ---")

    counter = 0
    threads = [threading.Thread(target=increment_racy, args=(1000,)) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    print("racy result (expect 5000):", counter)

    counter = 0
    threads = [threading.Thread(target=increment_safe, args=(1000,)) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    print("with Lock result:", counter)


# ===============================================================
# 4) PRODUCER / CONSUMER WITH queue.Queue
# ===============================================================
# WHAT THIS SHOWS:
#   A thread-safe queue connecting producers and consumers, plus the
#   “sentinel” technique to signal consumers to exit cleanly.
#
# WHY IT MATTERS:
#   Queues decouple work creation from work processing and eliminate
#   many race conditions by avoiding shared mutable structures.

SENTINEL = object()

def producer(q, count=12):
    """Put items 0...count-1 on the queue (simulated I/O), then a sentinel."""
    for i in range(count):
        time.sleep(0.03)     # simulate I/O delay
        q.put(i)
    q.put(SENTINEL)

def consumer(q):
    """Consume until sentinel; keep a small total to verify processing."""
    total = 0
    while True:
        item = q.get()
        if item is SENTINEL:
            q.task_done()
            break
        total += item
        q.task_done()
    print("[consumer] total:", total)

def demo_queue():
    print("\n--- Producer/Consumer with queue.Queue ---")
    q = queue.Queue()
    th_prod = threading.Thread(target=producer, args=(q, 20))
    th_cons = threading.Thread(target=consumer, args=(q,))
    th_prod.start(); th_cons.start()
    th_prod.join()
    q.join()       # wait until all items processed (task_done() balances put())
    th_cons.join()


# -------------
# Run the demos
# -------------
if __name__ == "__main__":
    demo_raw_threads()
    demo_threadpool_map()
    demo_threadpool_as_completed()
    demo_race_and_lock()
    demo_queue()

