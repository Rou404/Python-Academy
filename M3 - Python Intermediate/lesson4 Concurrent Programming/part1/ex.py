# GOAL:
#   Each exercise shows a tiny sequential "app". Your job:
#   1) Keep the behavior the same.
#   2) Use threads to make it faster/more responsive for I/O-bound work.
#
# TOOLS YOU'LL USE:
#   - threading.Thread(start/join)
#   - concurrent.futures.ThreadPoolExecutor (submit/map/as_completed)
#   - queue.Queue with a SENTINEL for producer/consumer
#
# NOTE:
#   We simulate I/O with time.sleep so runs are quick and results are visible.
# ==============================================================

from __future__ import annotations
import os
import time
import random
import threading
import queue
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

random.seed(0)

# --------------------------------------------------------------
# Helper: simple timer context
# --------------------------------------------------------------
class timer:
    def __init__(self, label):
        self.label = label
    def __enter__(self):
        self.t0 = time.perf_counter()
        print(f"\n[{self.label}] starting …")
    def __exit__(self, *exc):
        dt = time.perf_counter() - self.t0
        print(f"[{self.label}] done in {dt:.3f}s")

# ==============================================================
# EX1 — “Fetch” pages
# WHAT: A tiny sequential fetcher that sleeps to mimic network latency.
# WHY: Threads can overlap the waiting time and finish sooner.
# TASK: Implement threaded_fetch with ThreadPoolExecutor.
# ==============================================================

def fake_fetch(url: str):
    time.sleep(random.uniform(0.15, 0.35))  # pretend network
    return f"{url} OK (pid={os.getpid()})"

def sequential_fetch(urls: List[str]):
    out = []
    for u in urls:
        out.append(fake_fetch(u))
    return out

def threaded_fetch(urls: List[str]):
    """
    TODO:
    - Use ThreadPoolExecutor(max_workers=8).
    - Submit fake_fetch for each URL.
    - Collect results in *completion* order (as they finish) and return that list.
    - Also print each result as soon as you get it to visualize the interleaving.
    """
    # Hints:
    #   with ThreadPoolExecutor(max_workers=8) as pool:
    #       futures = [pool.submit(...)]
    #       for ft in as_completed(futures):
    #           ...
    results= []
    ...
    return results

def demo_ex1():
    urls = [f"https://ex{i}.test" for i in range(10)]
    with timer("EX1 sequential"):
        print(sequential_fetch(urls))
    with timer("EX1 threaded"):
        print(threaded_fetch(urls))

# ==============================================================
# EX2 — “Thumbnailer”
# WHAT: Pretend to resize images (sleep). Sequential baseline given.
# WHY: Same work, but thread pool should finish faster for many files.
# TASK: Implement threaded_thumbnailer preserving input order (use map).
# ==============================================================

def process_image(filename: str) -> str:
    time.sleep(random.uniform(0.10, 0.25))  # pretend disk+CPU light work
    return f"thumb({filename})"

def sequential_thumbnailer(files: List[str]) -> List[str]:
    return [process_image(f) for f in files]

def threaded_thumbnailer(files: List[str]) -> List[str]:
    """
    TODO:
    - Use ThreadPoolExecutor().
    - Use pool.map() to preserve *input order*.
    - Return the list of results.
    """
    ...

def demo_ex2():
    files = [f"img_{i}.jpg" for i in range(12)]
    with timer("EX2 sequential"):
        print(sequential_thumbnailer(files))
    with timer("EX2 threaded"):
        print(threaded_thumbnailer(files))


# ==============================================================
# EX3 — Producer/Consumer (one of each)
# WHAT: Producer makes numbers 0..n-1; consumer sums them.
# WHY: Queue decouples the two and avoids sharing lists directly.
# TASK: Implement the two threads with a queue and a SENTINEL.
# ==============================================================

SENTINEL = object()

def ex3_run(n=30) -> int:
    """
    TODO:
    - Create q = queue.Queue().
    - Producer: put 0..n-1 onto q, then SENTINEL.
    - Consumer: take from q until SENTINEL, keep a running total, then break.
    - Use q.task_done()/q.join() so main knows when all items are processed.
    - Return the consumer’s total.
    """
    q = queue.Queue()
    total_holder = {"value": 0}

    def producer():
        ...
    def consumer():
        ...
    # Start threads, join producer, q.join(), join consumer, return total_holder["value"]
    ...
    return total_holder["value"]

def demo_ex3():
    with timer("EX3 producer/consumer"):
        total = ex3_run(40)
        print("total =", total)

# ==============================================================
# EX4 — Log scan (tiny “app”)
# WHAT: Scan a list of in-memory “files” (strings) and count ERROR lines.
# WHY: IO-bound scanning is a good fit for threads; easy pattern with pool.map.
# TASK: Implement threaded_log_scan using ThreadPoolExecutor.map.
# ==============================================================

SAMPLE_LOGS = [
    "INFO boot\nINFO up\nERROR fail x\nINFO done\n",
    "INFO start\nINFO work\nINFO work\nERROR boom\nERROR boom2\n",
    "ERROR only\nERROR again\n",
    "INFO nothing here\n",
]

def count_errors(text: str) -> int:
    time.sleep(random.uniform(0.05, 0.12))  # pretend file read/parse
    return sum(1 for line in text.splitlines() if line.startswith("ERROR"))

def sequential_log_scan(logs: List[str]) -> int:
    return sum(count_errors(txt) for txt in logs)

def threaded_log_scan(logs: List[str]) -> int:
    """
    TODO:
    - Use ThreadPoolExecutor(max_workers=4).
    - Map count_errors over logs and sum the results.
    - Return the total error count.
    """
    ...

def demo_ex4():
    with timer("EX4 sequential"):
        print("errors:", sequential_log_scan(SAMPLE_LOGS))
    with timer("EX4 threaded"):
        print("errors:", threaded_log_scan(SAMPLE_LOGS))

# ==============================================================
# Self-check runner (keeps inputs small and fast)
# ==============================================================


if __name__ == "__main__":
    demo_ex1()
    demo_ex2()
    demo_ex3()
    demo_ex4()
