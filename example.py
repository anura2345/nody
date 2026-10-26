"""
Example demonstration of Nody:
- Native C backend (compiled C DLL with /O2 optimization).
- Pythonic frontend syntax.
- Fixed-size array per node.
- True C pointers (memory addresses) between nodes.
- Contiguous C array indexing inside each node.
"""

from nody import NodyList, CNodyList, Node, C_BACKEND_AVAILABLE


def demo_c_backend():
    print("=" * 65)
    print("1. NATIVE C-BACKEND UNROLLED LIST (PURE C SPEED)")
    print("=" * 65)

    if not C_BACKEND_AVAILABLE:
        print("C backend DLL not found. Run: python build_c.py")
        return

    # User defines fixed-size array capacity per node (e.g. 4)
    capacity = 4
    data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    print(f"Creating CNodyList with fixed node_capacity = {capacity}")
    print(f"Inserting data: {data}\n")

    c_list = CNodyList(node_capacity=capacity, initial_data=data)

    print("C Memory Structure (True Native Heap Addresses & Pointers):")
    print(c_list.display_structure())

    print("\n--- Python Syntax with C Speed ---")
    print(f"Direct Index [0]  : {c_list[0]}")
    print(f"Direct Index [5]  : {c_list[5]}")
    print(f"Negative Index [-1]: {c_list[-1]}")
    print(f"Slice [2:6]       : {c_list[2:6]}")

    print("\n--- Native C Mathematical Functions (Zero Python Overhead) ---")
    print(f"Sum (computed in C)  : {c_list.sum()}")
    print(f"Min (computed in C)  : {c_list.min()}")
    print(f"Max (computed in C)  : {c_list.max()}")

    print("\nScaling all elements by 2.0 directly inside C heap memory...")
    c_list.scale(2.0)
    print(f"Updated Sum in C     : {c_list.sum()}")
    print(f"Elements as Py list  : {c_list.to_list()}")

    print("\n--- Popping & Dynamic Node Splitting ---")
    print(f"Popped last item: {c_list.pop()}")
    print("Inserting 999.0 at index 2 (splits C node if full)...")
    c_list.insert(2, 999.0)
    print(f"Length: {len(c_list)}, Total C Nodes: {c_list.total_nodes}")


def demo_node_by_node_traversal():
    print("\n" + "=" * 65)
    print("2. TRAVEL NODE-TO-NODE VIA ADDRESSES, TRAVERSE INSIDE VIA ARRAY")
    print("=" * 65)

    # Creating manual node arrays to demonstrate the exact pointer mechanism
    capacity = 3
    node1 = Node(capacity=capacity)
    node1.append("Alpha")
    node1.append("Beta")
    node1.append("Gamma")

    node2 = Node(capacity=capacity)
    node2.append("Delta")
    node2.append("Epsilon")

    # Connect node1 to node2 via address pointer
    node1.next = node2
    node2.prev = node1

    print(f"Node 1 Address: {node1.address} (points to: {node1.next_address})")
    print(f"Node 2 Address: {node2.address} (points to: {node2.next_address})\n")

    curr = node1
    idx = 0
    while curr is not None:
        print(f"--> Jumped to Node #{idx} at address {curr.address}")
        # Array traversal inside the node
        for i in range(len(curr)):
            print(f"    array[{i}] = {curr[i]}")
        # Linked list traversal to next node
        curr = curr.next
        idx += 1


if __name__ == "__main__":
    demo_c_backend()
    demo_node_by_node_traversal()
