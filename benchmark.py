"""
Performance Benchmark: Native C Unrolled List (CNodyList) vs Pure Python.
Demonstrates the raw C speed advantage while using clean Python syntax.
"""

import time
from nody import CNodyList, PyNodyList


def run_benchmark():
    N = 500_000
    chunk_size = 128

    print("=" * 65)
    print(f"BENCHMARK: N = {N:,} elements (Node Array Chunk Size = {chunk_size})")
    print("=" * 65)

    data = [float(i) for i in range(N)]

    # --- 1. BULK INSERTION / CREATION SPEED ---
    print("\n[1] Appending / Bulk Construction:")

    # Pure Python List
    t0 = time.perf_counter()
    py_list = list(data)
    t_py_list = time.perf_counter() - t0
    print(f"  - Built-in Python list : {t_py_list*1000:8.2f} ms")

    # Native C-backend Unrolled List
    t0 = time.perf_counter()
    c_nody = CNodyList(node_capacity=chunk_size)
    c_nody.extend(data)
    t_c_nody = time.perf_counter() - t0
    print(f"  - Native C NodyList    : {t_c_nody*1000:8.2f} ms")

    # --- 2. SUMMATION SPEED ---
    print("\n[2] Summation across 500,000 elements:")

    # Python built-in sum()
    t0 = time.perf_counter()
    py_sum = sum(py_list)
    t_py_sum = time.perf_counter() - t0
    print(f"  - Python sum(list)     : {t_py_sum*1000:8.2f} ms (Result = {py_sum:,.0f})")

    # Native C sum()
    t0 = time.perf_counter()
    c_sum = c_nody.sum()
    t_c_sum = time.perf_counter() - t0
    print(f"  - Native C nody.sum()  : {t_c_sum*1000:8.2f} ms (Result = {c_sum:,.0f})")

    speedup_sum = t_py_sum / t_c_sum if t_c_sum > 0 else float("inf")
    print(f"  >>> SPEEDUP: Native C is {speedup_sum:.1f}x FASTER than Python sum!")

    # --- 3. IN-PLACE SCALING / TRANSFORM SPEED ---
    print("\n[3] In-Place Vector Scaling (x *= 2.5):")

    # Python comprehension
    t0 = time.perf_counter()
    py_list = [x * 2.5 for x in py_list]
    t_py_scale = time.perf_counter() - t0
    print(f"  - Python list loop     : {t_py_scale*1000:8.2f} ms")

    # Native C scale()
    t0 = time.perf_counter()
    c_nody.scale(2.5)
    t_c_scale = time.perf_counter() - t0
    print(f"  - Native C nody.scale(): {t_c_scale*1000:8.2f} ms")

    speedup_scale = t_py_scale / t_c_scale if t_c_scale > 0 else float("inf")
    print(f"  >>> SPEEDUP: Native C is {speedup_scale:.1f}x FASTER than Python loop!")

    print("\n" + "=" * 65)
    print("SUMMARY:")
    print("Behind the scenes, all array traversal & pointers execute in pure C.")
    print("In front, you write clean, standard Python syntax.")
    print("=" * 65)


if __name__ == "__main__":
    run_benchmark()
