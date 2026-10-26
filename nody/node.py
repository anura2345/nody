from typing import Any, Optional, Iterator


class Node:
    """
    A single node in an Unrolled Linked List.

    Each node contains a fixed-capacity array (buffer), keeps track of how many
    elements are currently occupied, and stores memory references (addresses) to
    the next and previous nodes in the linked list.
    """

    def __init__(self, capacity: int):
        """
        Initialize a node with a fixed-size internal array.

        :param capacity: The fixed maximum number of elements this node array can hold.
        """
        if capacity <= 0:
            raise ValueError("Node capacity must be a positive integer (> 0).")

        self.capacity: int = capacity
        # Pre-allocated fixed-size array buffer
        self._array: list[Any] = [None] * capacity
        self.count: int = 0
        self.next: Optional["Node"] = None
        self.prev: Optional["Node"] = None

    @property
    def address(self) -> str:
        """Return the hexadecimal memory address of this node."""
        return hex(id(self))

    @property
    def next_address(self) -> Optional[str]:
        """Return the hexadecimal memory address of the next node, if present."""
        return hex(id(self.next)) if self.next is not None else None

    @property
    def prev_address(self) -> Optional[str]:
        """Return the hexadecimal memory address of the previous node, if present."""
        return hex(id(self.prev)) if self.prev is not None else None

    def is_full(self) -> bool:
        """Check if the internal array is at maximum capacity."""
        return self.count >= self.capacity

    def is_empty(self) -> bool:
        """Check if the internal array contains no elements."""
        return self.count == 0

    def append(self, value: Any) -> None:
        """
        Append a value to the internal array.
        Raises OverflowError if the node is already full.
        """
        if self.is_full():
            raise OverflowError(f"Node at {self.address} is full (capacity={self.capacity}).")
        self._array[self.count] = value
        self.count += 1

    def insert(self, index: int, value: Any) -> None:
        """
        Insert a value at a specific array index within this node.
        Shifts trailing elements to the right.
        """
        if self.is_full():
            raise OverflowError(f"Node at {self.address} is full (capacity={self.capacity}).")
        if not (0 <= index <= self.count):
            raise IndexError(f"Index {index} out of bounds for node with {self.count} items.")

        # Shift elements right inside the fixed-size array
        for i in range(self.count, index, -1):
            self._array[i] = self._array[i - 1]

        self._array[index] = value
        self.count += 1

    def pop(self, index: int = -1) -> Any:
        """
        Remove and return the element at the specified index within this node's array.
        Shifts trailing elements to the left. Defaults to the last item.
        """
        if self.is_empty():
            raise IndexError("Cannot pop from an empty node.")

        if index < 0:
            index += self.count
        if not (0 <= index < self.count):
            raise IndexError(f"Index {index} out of bounds for node with {self.count} items.")

        removed_value = self._array[index]

        # Shift elements left
        for i in range(index, self.count - 1):
            self._array[i] = self._array[i + 1]

        # Clear the vacated slot
        self._array[self.count - 1] = None
        self.count -= 1
        return removed_value

    def __getitem__(self, index: int) -> Any:
        """Access an element inside this node's array like a regular array: node[i]."""
        if index < 0:
            index += self.count
        if not (0 <= index < self.count):
            raise IndexError(f"Index {index} out of bounds for node with {self.count} items.")
        return self._array[index]

    def __setitem__(self, index: int, value: Any) -> None:
        """Update an element inside this node's array: node[i] = val."""
        if index < 0:
            index += self.count
        if not (0 <= index < self.count):
            raise IndexError(f"Index {index} out of bounds for node with {self.count} items.")
        self._array[index] = value

    def __len__(self) -> int:
        """Return the number of active elements in this node's array."""
        return self.count

    def __iter__(self) -> Iterator[Any]:
        """Traverse elements inside this node's array sequentially like an array."""
        for i in range(self.count):
            yield self._array[i]

    def to_list(self) -> list[Any]:
        """Return the active elements in this node as a standard Python list."""
        return self._array[: self.count]

    def raw_array(self) -> list[Any]:
        """Return a copy of the underlying fixed-size buffer, including empty slots."""
        return list(self._array)

    def __repr__(self) -> str:
        slots = [repr(self._array[i]) if i < self.count else "_" for i in range(self.capacity)]
        return (
            f"Node(addr={self.address}, capacity={self.capacity}, count={self.count}, "
            f"array=[{', '.join(slots)}], next={self.next_address})"
        )
