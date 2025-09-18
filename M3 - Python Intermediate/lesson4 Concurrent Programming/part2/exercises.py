# ==============================================================
# concurrency_lesson2_exercises.py
# Lesson 2 — Concurrency in Python (EXERCISES ONLY)
# --------------------------------------------------------------
# Complete the TODOs. Keep runs short; prefer small inputs.
# ==============================================================

from __future__ import annotations
import os, time, random, math, threading, queue
from concurrent.futures import ThreadPoolExecutor, as_completed

random.seed(0)


# --------------------------------------------------------------
# E1 (Core, Sync) — Race condition & Lock
# Goal: Show racy counter vs. lock-protected counter.
# --------------------------------------------------------------

_counter = 0
_lock = threading.Lock()

def _inc(times: int, safe: bool):
    global _counter
    for _ in range(times):
        if safe:
            # TODO: protect this critical section
            _counter += 1
        else:
            tmp = _counter
            tmp += 1
            time.sleep(0.00005)  # exaggerate interleaving
            _counter = tmp

def e1_race_and_fix(workers=8, per_worker=2000) -> tuple[int, int]:
    """
    TODO:
    - Run once with safe=False (expect wrong), return final count
    - Reset and run with safe=True (expect workers*per_worker), return final count
    - Return (racy_result, safe_result)
    """
    ...
    # return racy, safe


# --------------------------------------------------------------
# E2 (Bonus, I/O) — Timeouts and cancellations
# Goal: Submit many I/O jobs; cancel the ones that exceed a timeout.
# --------------------------------------------------------------

def slow_io(i: int, low=0.1, high=0.8) -> float:
    d = random.uniform(low, high)
    time.sleep(d)
    return d

def e2_timeouts_cancel(n=12, timeout=0.35) -> dict[str, int]:
    """
    TODO:
    - Submit slow_io(i) to a ThreadPoolExecutor
    - Iterate futures with as_completed; for each, try result(timeout=...)
      (or call result() only if future.done()); cancel slow ones
    - Return {"completed": X, "cancelled": Y}
    """
    ...
    # return {"completed": completed, "cancelled": cancelled}


# --------------------------------------------------------------
# E3 (Raw Threads) — start/join mini thread pool by hand
# Goal: N workers pull ints from queue and append "done <i>" to results.
# --------------------------------------------------------------

def e3_handmade_thread_pool(items: list[int], workers=4) -> list[str]:
    """
    TODO:
    - Create queue.Queue and push all items + one SENTINEL per worker
    - Spawn `workers` threads; each pulls from queue:
        if SENTINEL -> task_done and break
        else -> simulate I/O (small sleep), append f"done {i}" to results, task_done
    - Join threads; return results (order doesn't matter)
    """
    ...
    # return results


# ----------------
# Self-check area
# ----------------
def _safe_run(name, fn, *args, **kwargs):
    try:
        print(f"\n[{name}]")
        out = fn(*args, **kwargs)
        print("->", out)
    except Exception as e:
        print(f"{name} not complete yet:", e)

if __name__ == "__main__":
    # Keep inputs modest to run quickly during class.
    _safe_run("E1 race_and_fix", e1_race_and_fix)


    _safe_run("E2 timeouts_cancel", e2_timeouts_cancel, 10, 0.35)

    # Raw threads mini pool
    _safe_run("E3 handmade_thread_pool", e3_handmade_thread_pool, list(range(12)), 4)
