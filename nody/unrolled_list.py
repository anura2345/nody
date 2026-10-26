from typing import Any, Iterable, Iterator, Optional, Union
from .node import Node


class NodyList:
    """
    An Unrolled Linked List (Chunked Array Linked List) data type.

    Combines the flexibility of a Linked List with the fast cache-friendly
    iteration and contiguous memory layout of an Array:
      - Inter-node traversal: jumps from one node to another via node addresses (pointers).
      - Intra-node traversal: travels sequentially within each node's fixed-size array.
    """

    def __init__(
        self,
        node_capacity: int = 4,
        initial_data: Optional[Iterable[Any]] = None,
    ):
        """
        Initialize the NodyList with a fixed array capacity for each node.

        :param node_capacity: Fixed size of the internal array inside each node.
        :param initial_data: Optional iterable of elements to populate into the list.
        """
        if node_capacity <= 0:
            raise ValueError("node_capacity must be a positive integer (> 0).")

        self.node_capacity: int = node_capacity
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self._total_count: int = 0

        if initial_data is not None:
            for item in initial_data:
                self.append(item)

    @classmethod
    def from_capacity(cls, capacity: int) -> "NodyList":
        """Factory method to declare an empty NodyList with a specific node capacity."""
        return cls(node_capacity=capacity)

    @property
    def total_nodes(self) -> int:
        """Count how many node blocks currently exist in the chain."""
        count = 0
        curr = self.head
        while curr is not None:
            count += 1
            curr = curr.next
        return count

    def is_empty(self) -> bool:
        """Return True if the list contains no elements."""
        return self._total_count == 0

    def append(self, value: Any) -> None:
        """
        Append a value to the end of the unrolled linked list.
        If the current tail node is full, a new node with the fixed capacity is allocated
        and linked to the end.
        """
        if self.head is None:
            new_node = Node(self.node_capacity)
            self.head = new_node
            self.tail = new_node
        elif self.tail.is_full():
            new_node = Node(self.node_capacity)
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node

        self.tail.append(value)
        self._total_count += 1

    def prepend(self, value: Any) -> None:
        """
        Prepend a value to the front of the list.
        If the head node is full, a new node is allocated and linked at the head.
        """
        if self.head is None:
            new_node = Node(self.node_capacity)
            self.head = new_node
            self.tail = new_node
            self.head.append(value)
        elif not self.head.is_full():
            self.head.insert(0, value)
        else:
            new_node = Node(self.node_capacity)
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
            self.head.append(value)

        self._total_count += 1

    def _locate(self, index: int) -> tuple[Node, int]:
        """
        Traverse the linked list to find the (node, local_index) corresponding
        to a global 0-based index.
        """
        if index < 0:
            index += self._total_count
        if not (0 <= index < self._total_count):
            raise IndexError(f"List index {index} out of range (length {self._total_count}).")

        # Optimize search direction: from head if closer to start, from tail if closer to end
        if index < self._total_count // 2:
            curr = self.head
            accum = 0
            while curr is not None:
                if accum + curr.count > index:
                    return curr, index - accum
                accum += curr.count
                curr = curr.next
        else:
            curr = self.tail
            accum = self._total_count
            while curr is not None:
                accum -= curr.count
                if index >= accum:
                    return curr, index - accum
                curr = curr.prev

        raise RuntimeError("Failed to locate index in chain.")

    def __getitem__(self, index: Union[int, slice]) -> Any:
        """
        Access element(s) by index or slice:
          - nody_list[i]
          - nody_list[start:stop:step]
        """
        if isinstance(index, slice):
            indices = range(*index.indices(self._total_count))
            return [self[i] for i in indices]

        node, local_idx = self._locate(index)
        return node[local_idx]

    def __setitem__(self, index: int, value: Any) -> None:
        """Set the element at the specified global index: nody_list[i] = val."""
        node, local_idx = self._locate(index)
        node[local_idx] = value

    def insert(self, index: int, value: Any) -> None:
        """
        Insert an element at a global index.
        If the target node array is full, the node is split to make room,
        maintaining the fixed-size array constraint across all nodes.
        """
        if index < 0:
            index += self._total_count
        if index < 0:
            index = 0
        if index >= self._total_count:
            self.append(value)
            return

        target_node, local_idx = self._locate(index)

        if not target_node.is_full():
            target_node.insert(local_idx, value)
        else:
            # Target node is full: split it into two nodes
            new_node = Node(self.node_capacity)
            new_node.next = target_node.next
            new_node.prev = target_node
            if target_node.next is not None:
                target_node.next.prev = new_node
            else:
                self.tail = new_node
            target_node.next = new_node

            # Move half the elements to new_node
            mid = target_node.count // 2
            items_to_move = target_node.to_list()[mid:]
            for _ in range(len(items_to_move)):
                target_node.pop()

            for item in items_to_move:
                new_node.append(item)

            # Insert value into the appropriate node
            if local_idx <= target_node.count:
                target_node.insert(local_idx, value)
            else:
                new_node.insert(local_idx - target_node.count, value)

        self._total_count += 1

    def pop(self, index: int = -1) -> Any:
        """
        Remove and return the item at global index (default last item).
        If a node array becomes completely empty, the node is unlinked from the chain.
        """
        if self._total_count == 0:
            raise IndexError("Cannot pop from an empty NodyList.")

        if index < 0:
            index += self._total_count
        if not (0 <= index < self._total_count):
            raise IndexError(f"List index {index} out of range (length {self._total_count}).")

        target_node, local_idx = self._locate(index)
        val = target_node.pop(local_idx)
        self._total_count -= 1

        # If node is now empty and not the only node, unlink it
        if target_node.is_empty() and self.head is not self.tail:
            if target_node.prev is not None:
                target_node.prev.next = target_node.next
            else:
                self.head = target_node.next

            if target_node.next is not None:
                target_node.next.prev = target_node.prev
            else:
                self.tail = target_node.prev

        return val

    def remove(self, value: Any) -> None:
        """Remove the first occurrence of value."""
        curr = self.head
        global_idx = 0
        while curr is not None:
            for local_idx in range(curr.count):
                if curr[local_idx] == value:
                    self.pop(global_idx)
                    return
                global_idx += 1
            curr = curr.next
        raise ValueError(f"{value!r} not in list")

    def clear(self) -> None:
        """Remove all elements from the list."""
        self.head = None
        self.tail = None
        self._total_count = 0

    def nodes(self) -> Iterator[Node]:
        """
        Generator yielding each Node in the linked list sequentially.
        Allows users to explicitly travel from node to node via pointers/addresses.
        """
        curr = self.head
        while curr is not None:
            yield curr
            curr = curr.next

    def __iter__(self) -> Iterator[Any]:
        """
        Traverse the list:
          1. Walks node-by-node across the linked list.
          2. Inside each node, iterates through its array elements.
        """
        curr = self.head
        while curr is not None:
            for elem in curr:
                yield elem
            curr = curr.next

    def __reversed__(self) -> Iterator[Any]:
        """Traverse backward from tail to head."""
        curr = self.tail
        while curr is not None:
            for elem in reversed(curr.to_list()):
                yield elem
            curr = curr.prev

    def __len__(self) -> int:
        """Return the total number of items stored across all nodes."""
        return self._total_count

    def to_list(self) -> list[Any]:
        """Convert all elements into a standard flat Python list."""
        return list(self)

    def display_structure(self) -> str:
        """
        Generate a human-readable visual diagram showing:
          - Each Node's memory address
          - Its internal fixed-size array slots
          - The linked pointer connections between nodes.
        """
        if self.head is None:
            return "NodyList(empty) -> None"

        lines = []
        curr = self.head
        idx = 0
        while curr is not None:
            slots = [
                str(curr._array[i]) if i < curr.count else "_"
                for i in range(curr.capacity)
            ]
            array_str = f"[{', '.join(slots)}]"
            next_str = curr.next.address if curr.next else "None"
            prev_str = curr.prev.address if curr.prev else "None"
            lines.append(
                f"Node #{idx} @ {curr.address}\n"
                f"  |-- prev address : {prev_str}\n"
                f"  |-- array [{curr.count}/{curr.capacity}] : {array_str}\n"
                f"  \\-- next address : {next_str}"
            )
            curr = curr.next
            idx += 1

        return "\n\n  |\n  v (linked list connection)\n\n".join(lines)

    def __repr__(self) -> str:
        return f"NodyList(capacity={self.node_capacity}, size={self._total_count}, items={list(self)!r})"
