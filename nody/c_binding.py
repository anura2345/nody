import ctypes
import os
from typing import Any, Iterable, Iterator, Optional, Union

# Locate the compiled native C dynamic library
_DIR = os.path.dirname(os.path.abspath(__file__))
_DLL_PATH = os.path.join(_DIR, "nody_core.dll")

if not os.path.exists(_DLL_PATH):
    raise FileNotFoundError(
        f"Native C library not found at {_DLL_PATH}. Please compile with MSVC or run build_c.py."
    )

_lib = ctypes.CDLL(_DLL_PATH)

# --- Define C Function Signatures ---

# CNode pointers
_lib.cnode_create.argtypes = [ctypes.c_size_t]
_lib.cnode_create.restype = ctypes.c_void_p

_lib.cnode_free.argtypes = [ctypes.c_void_p]
_lib.cnode_free.restype = None

_lib.cnode_append.argtypes = [ctypes.c_void_p, ctypes.c_double]
_lib.cnode_append.restype = ctypes.c_int

_lib.cnode_insert.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_double]
_lib.cnode_insert.restype = ctypes.c_int

_lib.cnode_pop.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_double)]
_lib.cnode_pop.restype = ctypes.c_int

_lib.cnode_get.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_double)]
_lib.cnode_get.restype = ctypes.c_int

_lib.cnode_set.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_double]
_lib.cnode_set.restype = ctypes.c_int

_lib.cnode_get_address.argtypes = [ctypes.c_void_p]
_lib.cnode_get_address.restype = ctypes.c_size_t

_lib.cnode_get_next_address.argtypes = [ctypes.c_void_p]
_lib.cnode_get_next_address.restype = ctypes.c_size_t

_lib.cnode_get_prev_address.argtypes = [ctypes.c_void_p]
_lib.cnode_get_prev_address.restype = ctypes.c_size_t

_lib.cnode_get_raw_array.argtypes = [ctypes.c_void_p]
_lib.cnode_get_raw_array.restype = ctypes.POINTER(ctypes.c_double)

# CNodyList pointers
_lib.cnody_create.argtypes = [ctypes.c_size_t]
_lib.cnody_create.restype = ctypes.c_void_p

_lib.cnody_free.argtypes = [ctypes.c_void_p]
_lib.cnody_free.restype = None

_lib.cnody_append.argtypes = [ctypes.c_void_p, ctypes.c_double]
_lib.cnody_append.restype = ctypes.c_int

_lib.cnody_prepend.argtypes = [ctypes.c_void_p, ctypes.c_double]
_lib.cnody_prepend.restype = ctypes.c_int

_lib.cnody_insert.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_double]
_lib.cnody_insert.restype = ctypes.c_int

_lib.cnody_pop.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_double)]
_lib.cnody_pop.restype = ctypes.c_int

_lib.cnody_get.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_double)]
_lib.cnody_get.restype = ctypes.c_int

_lib.cnody_set.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_double]
_lib.cnody_set.restype = ctypes.c_int

_lib.cnody_len.argtypes = [ctypes.c_void_p]
_lib.cnody_len.restype = ctypes.c_size_t

_lib.cnody_node_count.argtypes = [ctypes.c_void_p]
_lib.cnody_node_count.restype = ctypes.c_size_t

_lib.cnody_clear.argtypes = [ctypes.c_void_p]
_lib.cnody_clear.restype = None

# High-speed batch & math C operations
_lib.cnody_append_batch.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
_lib.cnody_append_batch.restype = None

_lib.cnody_to_buffer.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_double), ctypes.c_size_t]
_lib.cnody_to_buffer.restype = ctypes.c_size_t

_lib.cnody_sum.argtypes = [ctypes.c_void_p]
_lib.cnody_sum.restype = ctypes.c_double

_lib.cnody_min.argtypes = [ctypes.c_void_p]
_lib.cnody_min.restype = ctypes.c_double

_lib.cnody_max.argtypes = [ctypes.c_void_p]
_lib.cnody_max.restype = ctypes.c_double

_lib.cnody_scale.argtypes = [ctypes.c_void_p, ctypes.c_double]
_lib.cnody_scale.restype = None


class CNodeRef:
    """
    Python handle to a native CNode struct allocated in C memory.
    """

    def __init__(self, ptr: int, capacity: int, owns_memory: bool = False):
        if not ptr:
            raise ValueError("Invalid null pointer for CNode.")
        self._ptr = ptr
        self.capacity = capacity
        self._owns_memory = owns_memory

    @classmethod
    def create(cls, capacity: int) -> "CNodeRef":
        if capacity <= 0:
            raise ValueError("Capacity must be positive.")
        ptr = _lib.cnode_create(capacity)
        if not ptr:
            raise MemoryError("Failed to allocate CNode in native C heap.")
        return cls(ptr, capacity, owns_memory=True)

    def __del__(self):
        if self._owns_memory and self._ptr:
            _lib.cnode_free(self._ptr)
            self._ptr = 0

    @property
    def address(self) -> str:
        """Hexadecimal native memory address of the CNode."""
        return hex(_lib.cnode_get_address(self._ptr))

    @property
    def next_address(self) -> Optional[str]:
        addr = _lib.cnode_get_next_address(self._ptr)
        return hex(addr) if addr else None

    @property
    def prev_address(self) -> Optional[str]:
        addr = _lib.cnode_get_prev_address(self._ptr)
        return hex(addr) if addr else None

    def append(self, value: float) -> None:
        ok = _lib.cnode_append(self._ptr, float(value))
        if not ok:
            raise OverflowError(f"CNode at {self.address} is full.")

    def __getitem__(self, index: int) -> float:
        out_val = ctypes.c_double()
        ok = _lib.cnode_get(self._ptr, index, ctypes.byref(out_val))
        if not ok:
            raise IndexError(f"Index {index} out of range in CNode array.")
        return out_val.value

    def __setitem__(self, index: int, value: float) -> None:
        ok = _lib.cnode_set(self._ptr, index, float(value))
        if not ok:
            raise IndexError(f"Index {index} out of range in CNode array.")


class CNodyList:
    """
    High-Performance Unrolled Linked List backed by native compiled C.
    Gives pure C speed while offering standard Python syntax:
      - append, insert, pop, slicing, len, iter
      - native C sum(), min(), max(), scale()
      - direct memory access and address inspection
    """

    def __init__(
        self,
        node_capacity: int = 64,
        initial_data: Optional[Iterable[Union[int, float]]] = None,
    ):
        if node_capacity <= 0:
            raise ValueError("node_capacity must be > 0.")
        self.node_capacity = node_capacity
        self._ptr = _lib.cnody_create(node_capacity)
        if not self._ptr:
            raise MemoryError("Failed to allocate CNodyList in C heap.")

        if initial_data is not None:
            self.extend(initial_data)

    def __del__(self):
        if hasattr(self, "_ptr") and self._ptr:
            _lib.cnody_free(self._ptr)
            self._ptr = 0

    def __len__(self) -> int:
        return _lib.cnody_len(self._ptr)

    @property
    def total_nodes(self) -> int:
        """Count of allocated C node chunks."""
        return _lib.cnody_node_count(self._ptr)

    def is_empty(self) -> bool:
        """Return True if list has no elements."""
        return len(self) == 0

    def nodes(self) -> Iterator[CNodeRef]:
        """
        Yield CNodeRef objects wrapping each native C node in the linked list chain.
        """
        class CNodeRaw(ctypes.Structure):
            pass

        CNodeRaw._fields_ = [
            ("capacity", ctypes.c_size_t),
            ("count", ctypes.c_size_t),
            ("array", ctypes.POINTER(ctypes.c_double)),
            ("next", ctypes.POINTER(CNodeRaw)),
            ("prev", ctypes.POINTER(CNodeRaw)),
        ]

        class CNodyListRaw(ctypes.Structure):
            _fields_ = [
                ("node_capacity", ctypes.c_size_t),
                ("total_count", ctypes.c_size_t),
                ("total_nodes", ctypes.c_size_t),
                ("head", ctypes.POINTER(CNodeRaw)),
                ("tail", ctypes.POINTER(CNodeRaw)),
            ]

        raw_list = ctypes.cast(self._ptr, ctypes.POINTER(CNodyListRaw)).contents
        curr_ptr = raw_list.head
        while curr_ptr:
            yield CNodeRef(ctypes.addressof(curr_ptr.contents), self.node_capacity, owns_memory=False)
            curr_ptr = curr_ptr.contents.next

    def append(self, value: Union[int, float]) -> None:
        """Append a value at native C speed."""
        ok = _lib.cnody_append(self._ptr, float(value))
        if not ok:
            raise MemoryError("C failed to allocate or append to list.")

    def prepend(self, value: Union[int, float]) -> None:
        """Prepend a value at native C speed."""
        ok = _lib.cnody_prepend(self._ptr, float(value))
        if not ok:
            raise MemoryError("C failed to prepend.")

    def insert(self, index: int, value: Union[int, float]) -> None:
        """Insert at global index. Automatically splits C node when full."""
        n = len(self)
        if index < 0:
            index += n
        if index < 0:
            index = 0
        if index >= n:
            self.append(value)
            return

        ok = _lib.cnody_insert(self._ptr, index, float(value))
        if not ok:
            raise RuntimeError("Failed to insert into C list.")

    def pop(self, index: int = -1) -> float:
        """Remove and return element at global index (default last item)."""
        n = len(self)
        if n == 0:
            raise IndexError("Cannot pop from empty list.")
        if index < 0:
            index += n
        if not (0 <= index < n):
            raise IndexError("Pop index out of range.")

        out_val = ctypes.c_double()
        ok = _lib.cnody_pop(self._ptr, index, ctypes.byref(out_val))
        if not ok:
            raise RuntimeError("Failed to pop item.")
        return out_val.value

    def extend(self, values: Iterable[Union[int, float]]) -> None:
        """
        Fast bulk insertion: converts Python iterable to a C array buffer
        and appends via raw memcpy inside C in one shot.
        """
        data = [float(v) for v in values]
        if not data:
            return
        c_arr = (ctypes.c_double * len(data))(*data)
        _lib.cnody_append_batch(self._ptr, c_arr, len(data))

    def __getitem__(self, index: Union[int, slice]) -> Union[float, list[float]]:
        n = len(self)
        if isinstance(index, slice):
            indices = range(*index.indices(n))
            return [self[i] for i in indices]

        if index < 0:
            index += n
        if not (0 <= index < n):
            raise IndexError(f"List index {index} out of range (len {n}).")

        out_val = ctypes.c_double()
        ok = _lib.cnody_get(self._ptr, index, ctypes.byref(out_val))
        if not ok:
            raise IndexError(f"Failed to retrieve index {index}.")
        return out_val.value

    def __setitem__(self, index: int, value: Union[int, float]) -> None:
        n = len(self)
        if index < 0:
            index += n
        if not (0 <= index < n):
            raise IndexError(f"List index {index} out of range (len {n}).")

        ok = _lib.cnody_set(self._ptr, index, float(value))
        if not ok:
            raise IndexError(f"Failed to set index {index}.")

    def clear(self) -> None:
        """Clear all nodes in native C memory."""
        _lib.cnody_clear(self._ptr)

    def to_list(self) -> list[float]:
        """
        Blazing fast conversion to Python list using single C-level memory copy.
        """
        n = len(self)
        if n == 0:
            return []
        buf = (ctypes.c_double * n)()
        copied = _lib.cnody_to_buffer(self._ptr, buf, n)
        return list(buf[:copied])

    def __iter__(self) -> Iterator[float]:
        for val in self.to_list():
            yield val

    # --- Blazing-fast native C mathematical functions ---

    def sum(self) -> float:
        """Compute the sum of all elements inside compiled C (SIMD/cache-friendly)."""
        return _lib.cnody_sum(self._ptr)

    def min(self) -> float:
        """Compute minimum element inside compiled C."""
        if len(self) == 0:
            raise ValueError("min() arg is an empty sequence")
        return _lib.cnody_min(self._ptr)

    def max(self) -> float:
        """Compute maximum element inside compiled C."""
        if len(self) == 0:
            raise ValueError("max() arg is an empty sequence")
        return _lib.cnody_max(self._ptr)

    def scale(self, factor: float) -> None:
        """Multiply all elements by factor in-place at raw C speed."""
        _lib.cnody_scale(self._ptr, float(factor))

    def display_structure(self) -> str:
        """
        Inspect the underlying C memory layout:
        Prints each C node's actual heap address, capacity, and linked list pointers.
        """
        # Read internal CNode structs by walking pointers from head
        # We can read the head pointer offset from CNodyList struct
        class CNodeRaw(ctypes.Structure):
            pass

        CNodeRaw._fields_ = [
            ("capacity", ctypes.c_size_t),
            ("count", ctypes.c_size_t),
            ("array", ctypes.POINTER(ctypes.c_double)),
            ("next", ctypes.POINTER(CNodeRaw)),
            ("prev", ctypes.POINTER(CNodeRaw)),
        ]

        class CNodyListRaw(ctypes.Structure):
            _fields_ = [
                ("node_capacity", ctypes.c_size_t),
                ("total_count", ctypes.c_size_t),
                ("total_nodes", ctypes.c_size_t),
                ("head", ctypes.POINTER(CNodeRaw)),
                ("tail", ctypes.POINTER(CNodeRaw)),
            ]

        raw_list = ctypes.cast(self._ptr, ctypes.POINTER(CNodyListRaw)).contents
        if not raw_list.head:
            return "CNodyList(empty) -> NULL"

        lines = []
        curr_ptr = raw_list.head
        idx = 0
        while curr_ptr:
            curr = curr_ptr.contents
            # Extract array slots
            slots = []
            for i in range(curr.capacity):
                if i < curr.count:
                    slots.append(f"{curr.array[i]:.2f}".rstrip("0").rstrip("."))
                else:
                    slots.append("_")

            addr_str = hex(ctypes.addressof(curr))
            next_addr = hex(ctypes.addressof(curr.next.contents)) if curr.next else "NULL"
            prev_addr = hex(ctypes.addressof(curr.prev.contents)) if curr.prev else "NULL"

            lines.append(
                f"C-Node #{idx} @ {addr_str}\n"
                f"  |-- prev address : {prev_addr}\n"
                f"  |-- array [{curr.count}/{curr.capacity}] : [{', '.join(slots)}]\n"
                f"  \\-- next address : {next_addr}"
            )
            curr_ptr = curr.next
            idx += 1

        return "\n\n  |\n  v (native C pointer hop)\n\n".join(lines)

    def __repr__(self) -> str:
        preview = self[:5]
        suffix = "..." if len(self) > 5 else ""
        return f"CNodyList(capacity={self.node_capacity}, len={len(self)}, items={preview}{suffix})"
