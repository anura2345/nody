# Nody 🚀

> **A high-performance C-accelerated Unrolled Linked List library for Python.**  
> *Combines the cache locality and rapid indexing of Arrays with the dynamic growth of Linked Lists.*

[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/anura2345/nody)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![C Backend](https://img.shields.io/badge/backend-MSVC%20%2F%20C99-red.svg)](https://en.wikipedia.org/wiki/C_(programming_language))
[![Release](https://img.shields.io/badge/status-Part%201%20(Foundational%20Core)-green.svg)]()

---

## 📌 About The Project (Part 1 Release)

**Nody** is an open-source data type library designed to solve a fundamental computer science tradeoff in Python:
- **Standard Python lists** store pointers to heap-allocated objects, causing cache misses and significant memory overhead.
- **Standard linked lists** suffer from pointer-chasing latency ($O(N)$ random access) and memory fragmentation.

**Nody** implements an **Unrolled Linked List** (Chunked Array List):
- **Behind the scenes:** Built in **pure, compiled C** (`nody_core.dll`). Nodes store contiguous arrays allocated directly on the C heap, linked by genuine memory address pointers (`struct CNode* next`, `struct CNode* prev`).
- **In front:** Clean, standard **Python syntax** (`list[i]`, `list.append()`, `list.insert()`, `list.pop()`, `len(list)`, `sum()`, etc.).

> **Note**: This repository represents **Part 1 (The Foundational Core)** of the project, establishing the core data structure, C backend, Python bindings, memory address traversal, and performance benchmarks.

---

## ⚙️ How It Works (Basic Mechanics)

The core principle behind Nody is hybrid traversal:

1. **Declared Fixed Array Per Node**:
   When you declare a `node_capacity` (e.g. `4`), each node allocates a fixed contiguous C array of that exact size.
2. **Linked List Across Nodes (Inter-Node Traversal)**:
   Nodes connect to each other via direct 32/64-bit memory addresses (`node.next` and `node.prev`). Traveling from one node block to another works just like a linked list (`current = current.next`).
3. **Array Indexing Inside Nodes (Intra-Node Traversal)**:
   Inside any single node, elements are stored sequentially in contiguous memory. Traversal inside a node works like an array (`node[i]`), taking full advantage of CPU L1/L2 cache prefetching and $O(1)$ indexing.
4. **Dynamic Node Splitting & Merging**:
   When inserting into a full node, Nody automatically splits the node and links a new node block into the chain. When popping leaves a node empty, it unlinks and frees the memory.

---

## 🧠 Memory Architecture Diagram

```text
       Inter-Node Traversal: Linked List (Pointers / Memory Addresses)
       ==============================================================
               
  [Node #0 @ 0x13d1310]          [Node #1 @ 0x13d12b0]          [Node #2 @ 0x13d1350]
+-------------------------+    +-------------------------+    +-------------------------+
| capacity: 4  | count: 4 |    | capacity: 4  | count: 4 |    | capacity: 4  | count: 2 |
|-------------------------|    |-------------------------|    |-------------------------|
| [ 10 | 20 | 30 | 40 ]   |--->| [ 50 | 60 | 70 | 80 ]   |--->| [ 90 | 100 |  _ |  _ ]  |
|  0    1    2    3       |    |  0    1    2    3       |    |  0    1    2    3       |
+-------------------------+    +-------------------------+    +-------------------------+
       |                                |                                |
       +--- Intra-Node Array Indexing --+                                |
       +--- Contiguous Heap Memory (Zero Python Boxing Overhead) --------+
```

---

## ⚡ Performance Benchmarks

Run `python benchmark.py` to compare Nody's C-engine against standard Python on **500,000 elements**:

| Operation (500,000 items) | Pure Python List | Nody Native C Core | Speedup |
| :--- | :--- | :--- | :--- |
| **Summation (`sum`)** | `2.27 ms` | **`0.54 ms`** | **4.2x Faster** |
| **In-Place Scaling (`x *= 2.5`)** | `21.16 ms` | **`0.48 ms`** | **44.2x Faster** |

---

## 🚀 Quickstart & Usage

### 1. High-Level C List (`CNodyList`)

```python
from nody import CNodyList

# Declare a fixed array capacity of 4 per node
lst = CNodyList(node_capacity=4, initial_data=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

# Pythonic indexing and slicing
print(lst[0])        # 10.0
print(lst[-1])       # 100.0
print(lst[2:6])      # [30.0, 40.0, 50.0, 60.0]

# Dynamic mutation (handles C node allocations and splits automatically)
lst.append(110.0)
lst.insert(2, 999.0)
popped_val = lst.pop()

# High-speed C-level vector operations
print("Sum :", lst.sum())
print("Min :", lst.min())
print("Max :", lst.max())

# In-place scaling at raw C speed (44x faster than Python loops)
lst.scale(2.5)

# Inspect the underlying native C heap addresses
print(lst.display_structure())
```

### Output of `display_structure()`:
```text
C-Node #0 @ 0x13d1310
  |-- prev address : NULL
  |-- array [4/4] : [10, 20, 30, 40]
  \-- next address : 0x13d12b0

  |
  v (native C pointer hop)

C-Node #1 @ 0x13d12b0
  |-- prev address : 0x13d1310
  |-- array [4/4] : [50, 60, 70, 80]
  \-- next address : 0x13d1350

  |
  v (native C pointer hop)

C-Node #2 @ 0x13d1350
  |-- prev address : 0x13d12b0
  |-- array [2/4] : [90, 100, _, _]
  \-- next address : NULL
```

---

### 2. Low-Level Manual Node Traversal (`Node`)

To directly inspect and travel between nodes using memory addresses:

```python
from nody import Node

# User declares fixed-size node capacity
capacity = 3
node1 = Node(capacity=capacity)
node1.append("Alpha")
node1.append("Beta")
node1.append("Gamma")

node2 = Node(capacity=capacity)
node2.append("Delta")

# Connect node1 to node2 via address pointer
node1.next = node2
node2.prev = node1

# Travel node-to-node like a linked list:
curr = node1
while curr is not None:
    print(f"\nAt Node Address: {curr.address} (next: {curr.next_address})")
    # Traverse inside node array like an array:
    for i in range(len(curr)):
        print(f"  array[{i}] = {curr[i]}")
    curr = curr.next
```

---

## 📁 Repository Structure

```text
nody/
├── c_src/
│   ├── nody_core.h          # C header declaring CNode and CNodyList structs
│   └── nody_core.c          # Pure C implementation (allocations, splits, math)
├── nody/
│   ├── __init__.py          # Unified package entry point
│   ├── c_binding.py         # ctypes bindings for C DLL
│   ├── node.py              # Pure Python Node implementation
│   ├── unrolled_list.py     # Pure Python Unrolled Linked List
│   └── nody_core.dll        # Compiled native Windows DLL (MSVC /O2)
├── tests/
│   ├── test_c_nody.py       # Unit tests for C backend
│   └── test_nody.py         # Unit tests for Python reference implementation
├── benchmark.py             # Performance benchmark suite (C vs Python)
├── build_c.py               # Automated compiler script (MSVC)
├── example.py               # Comprehensive demonstration script
├── pyproject.toml           # Packaging metadata
├── LICENSE                  # MIT License
└── README.md                # Project documentation
```

---

## 🛠️ Development & Building

1. **Run Tests**:
   ```bash
   python -m unittest discover tests
   ```

2. **Run Demonstration**:
   ```bash
   python example.py
   ```

3. **Run Performance Benchmarks**:
   ```bash
   python benchmark.py
   ```

4. **Recompile the Native C Core**:
   ```bash
   python build_c.py
   ```

---

## 🗺️ Roadmap (Part 2 & Beyond)

- [ ] **Part 2**: Support for arbitrary Python objects in C structs via `PyObject*`.
- [ ] **Part 3**: Multi-threading and thread-safe concurrent chunk traversals.
- [ ] **Part 4**: Persistent disk-backed paging for datasets larger than RAM.
- [ ] **Part 5**: PyPI distribution (`pip install nody`).

---

## 📄 License

This project is open-source under the [MIT License](LICENSE).  
Authored by **Anurag Mishra** ([@anura2345](https://github.com/anura2345)).
