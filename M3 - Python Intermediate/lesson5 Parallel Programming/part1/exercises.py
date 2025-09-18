from __future__ import annotations
import os, time, math, random
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Iterable, List

random.seed(0)

# ------------------------------
# Helpers: timer + chunking
# ------------------------------
class timer:
    def __init__(self, label: str): self.label = label
    def __enter__(self):
        self.t0 = time.perf_counter()
        print(f"\n[{self.label}] starting…")
    def __exit__(self, *exc):
        dt = time.perf_counter() - self.t0
        print(f"[{self.label}] done in {dt:.3f}s")

def chunked(seq: Iterable, size: int) -> Iterable[list]:
    buf = []
    for x in seq:
        buf.append(x)
        if len(buf) == size:
            yield buf; buf = []
    if buf:
        yield buf

# ------------------------------
# Shared CPU-bound workers
# ------------------------------
def count_primes(n: int) -> int:
    """CPU-heavy toy: count primes below n (naive)."""
    def is_prime(x: int) -> bool:
        if x < 2: return False
        r = int(math.isqrt(x))
        for d in range(2, r + 1):
            if x % d == 0: return False
        return True
    return sum(1 for x in range(n) if is_prime(x))

def square_then_fib(n: int) -> int:
    """Another CPU-ish worker for EX2 context."""
    # square + tiny fib—cheap but illustrative when batched
    s = n * n
    a, b = 0, 1
    for _ in range(250):  # keep small so demo runs fast
        a, b = b, a + b
    return s + a

def wordcount_worker(text: str) -> Counter:
    words = [w.strip(".,!?:;\"'()[]").lower() for w in text.split()]
    return Counter(w for w in words if w)

# =========================================================
# EX1 — as_completed with order restore (Model Scoring)
# Context:
#   Imagine "batch scoring" a model for many inputs. You want to STREAM
#   results as soon as they’re ready (progress), but the returned list
#   must align with the original input order for downstream joins.
# Worker used here: count_primes (stands in for “score_one(input)”)
# =========================================================

def ex1_sequential(ns=(40_000, 42_000, 44_000, 46_000)) -> list[int]:
    """Baseline: compute in order, single process."""
    return [count_primes(n) for n in ns]

def ex1_todo(ns=(40_000, 42_000, 44_000, 46_000), workers=None) -> list[int]:
    """
    TODO:
    - Submit count_primes(n) for each n using ProcessPoolExecutor(max_workers=workers).
    - Use as_completed to print results as they finish:  print(f"done n={n} -> {res}")
    - BUT return results in input order. Hint: keep a dict Future->index, then
      store res at results[idx].
    """
    ...

# =========================================================
# EX2 — chunked_parallel_map (ETL / Data prep)
# Context:
#   You have a HUGE list of small records; launching a separate process
#   per record wastes time in pickling + scheduling. Batch (chunk) small
#   items so each worker handles a *list* at once.
# Worker here: square_then_fib (stands in for “transform(record)”)
# =========================================================

def ex2_sequential(fn, iterable: Iterable) -> list:
    return [fn(x) for x in iterable]

def ex2_todo(fn, iterable: Iterable, chunksize=16, workers=None) -> list:
    """
    TODO:
    - Split 'iterable' into lists of length 'chunksize' (use chunked()).
    - Define batch_fn(chunk) that applies 'fn' to each element and returns a list.
    - Use ProcessPoolExecutor to map batch_fn over chunks.
    - Flatten the chunk results so the output order matches the input order.
    """
    ...

# =========================================================
# EX3 — parallel word count (Map/Reduce for logs)
# Context:
#   You collect many log files (documents). Map: count words per doc in
#   parallel. Reduce: merge partial Counters into one global histogram.
# Worker here: wordcount_worker (returns Counter for a document)
# =========================================================

def ex3_sequential(docs: list[str]) -> Counter:
    total = Counter()
    for txt in docs:
        total.update(wordcount_worker(txt))
    return total

def ex3_todo(docs: list[str]) -> Counter:
    """
    TODO:
    - Use ProcessPoolExecutor to map wordcount_worker across docs.
    - Reduce by summing/merging all Counters into one and return it.
    """
    ...

# =========================================================
# Tiny driver with baselines to compare
# =========================================================
if __name__ == "__main__":
    # EX1: model scoring stand-in
    ns = (40_000, 42_000, 44_000, 46_000)
    with timer("EX1 sequential baseline"):
        baseline1 = ex1_sequential(ns)
        print("seq:", baseline1)

    with timer("EX1 parallel (as_completed, ordered return)"):
        par1 = ex1_todo(ns, workers=os.cpu_count())
        print("par:", par1)

    # EX2: ETL transform stand-in
    data = list(range(2_000))  # many small items → benefits from chunking
    with timer("EX2 sequential baseline"):
        baseline2 = ex2_sequential(square_then_fib, data)
        print("seq sample:", baseline2[:8], "…")

    with timer("EX2 parallel (chunked)"):
        par2 = ex2_todo(square_then_fib, data, chunksize=64, workers=os.cpu_count())
        print("par sample:", par2[:8], "…")

    # EX3: word count stand-in
    DOCS = [
        "Error: disk full. Error again.",
        "Warning… ok. Error happens here.",
        "Fish fish fish. Red fish blue fish.",
        "So many words, so little time.",
    ] * 50  # scale a bit to see the benefit
    with timer("EX3 sequential baseline"):
        baseline3 = ex3_sequential(DOCS)
        print("top words:", baseline3.most_common(5))

    with timer("EX3 parallel (map/reduce)"):
        par3 = ex3_todo(DOCS)
        print("top words:", par3.most_common(5))
