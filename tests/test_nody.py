import unittest
from nody import Node, PyNodyList as NodyList


class TestNode(unittest.TestCase):
    def test_node_init(self):
        node = Node(capacity=3)
        self.assertEqual(node.capacity, 3)
        self.assertEqual(node.count, 0)
        self.assertTrue(node.is_empty())
        self.assertFalse(node.is_full())
        self.assertEqual(len(node), 0)
        self.assertIsNotNone(node.address)
        self.assertTrue(node.address.startswith("0x"))

    def test_invalid_capacity(self):
        with self.assertRaises(ValueError):
            Node(capacity=0)
        with self.assertRaises(ValueError):
            Node(capacity=-5)

    def test_node_append_and_full(self):
        node = Node(capacity=2)
        node.append(10)
        node.append(20)
        self.assertTrue(node.is_full())
        self.assertEqual(len(node), 2)
        self.assertEqual(node.to_list(), [10, 20])

        with self.assertRaises(OverflowError):
            node.append(30)

    def test_node_indexing_and_iteration(self):
        node = Node(capacity=4)
        node.append("apple")
        node.append("banana")
        self.assertEqual(node[0], "apple")
        self.assertEqual(node[1], "banana")
        self.assertEqual(node[-1], "banana")

        node[0] = "avocado"
        self.assertEqual(node[0], "avocado")

        with self.assertRaises(IndexError):
            _ = node[5]

        # Iteration traverses inside node array
        self.assertEqual(list(node), ["avocado", "banana"])

    def test_node_pop_and_insert(self):
        node = Node(capacity=4)
        node.append(1)
        node.append(3)
        node.insert(1, 2)
        self.assertEqual(node.to_list(), [1, 2, 3])

        popped = node.pop(1)
        self.assertEqual(popped, 2)
        self.assertEqual(node.to_list(), [1, 3])


class TestNodyList(unittest.TestCase):
    def test_empty_list(self):
        lst = NodyList(node_capacity=3)
        self.assertEqual(len(lst), 0)
        self.assertTrue(lst.is_empty())
        self.assertEqual(lst.to_list(), [])
        self.assertEqual(lst.total_nodes, 0)

    def test_append_creates_new_nodes(self):
        lst = NodyList(node_capacity=3)
        for i in range(1, 8):  # 7 items -> 3 nodes: [1,2,3], [4,5,6], [7]
            lst.append(i)

        self.assertEqual(len(lst), 7)
        self.assertEqual(lst.total_nodes, 3)
        self.assertEqual(lst.to_list(), [1, 2, 3, 4, 5, 6, 7])

        # Verify linked list pointers and node traversal
        nodes = list(lst.nodes())
        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0].next, nodes[1])
        self.assertEqual(nodes[1].next, nodes[2])
        self.assertIsNone(nodes[2].next)
        self.assertEqual(nodes[1].prev, nodes[0])
        self.assertEqual(nodes[2].prev, nodes[1])

        # Verify array contents inside each node
        self.assertEqual(nodes[0].to_list(), [1, 2, 3])
        self.assertEqual(nodes[1].to_list(), [4, 5, 6])
        self.assertEqual(nodes[2].to_list(), [7])

    def test_indexing_and_slicing(self):
        lst = NodyList(node_capacity=3, initial_data=range(10))
        self.assertEqual(lst[0], 0)
        self.assertEqual(lst[5], 5)
        self.assertEqual(lst[9], 9)
        self.assertEqual(lst[-1], 9)
        self.assertEqual(lst[-3], 7)

        lst[5] = 99
        self.assertEqual(lst[5], 99)

        # Slicing
        self.assertEqual(lst[2:6], [2, 3, 4, 99])

    def test_prepend(self):
        lst = NodyList(node_capacity=2)
        lst.prepend(1)
        lst.prepend(2)
        lst.prepend(3)
        self.assertEqual(lst.to_list(), [3, 2, 1])

    def test_insert_and_node_split(self):
        lst = NodyList(node_capacity=3, initial_data=[10, 20, 30])
        self.assertEqual(lst.total_nodes, 1)

        # Inserting into a full node should split the node
        lst.insert(1, 15)
        self.assertEqual(lst.to_list(), [10, 15, 20, 30])
        self.assertGreater(lst.total_nodes, 1)

    def test_pop_and_cleanup(self):
        lst = NodyList(node_capacity=2, initial_data=[10, 20, 30, 40])
        self.assertEqual(lst.total_nodes, 2)

        val = lst.pop()
        self.assertEqual(val, 40)
        val2 = lst.pop()
        self.assertEqual(val2, 30)

        # Emptied node should be unlinked
        self.assertEqual(lst.total_nodes, 1)
        self.assertEqual(lst.to_list(), [10, 20])

    def test_traversal_mechanics(self):
        """Test user requirement: travel node-to-node like a linked list, and inside each node like an array."""
        lst = NodyList(node_capacity=3, initial_data=["A", "B", "C", "D", "E"])

        visited_nodes = []
        visited_elements = []

        curr_node = lst.head
        while curr_node is not None:
            visited_nodes.append(curr_node.address)
            # Traverse inside node array
            for i in range(len(curr_node)):
                visited_elements.append(curr_node[i])
            # Jump to next node array using address/pointer
            curr_node = curr_node.next

        self.assertEqual(len(visited_nodes), 2)
        self.assertEqual(visited_elements, ["A", "B", "C", "D", "E"])

    def test_display_structure(self):
        lst = NodyList(node_capacity=3, initial_data=[1, 2, 3, 4])
        diagram = lst.display_structure()
        self.assertIn("Node #0", diagram)
        self.assertIn("Node #1", diagram)
        self.assertIn("linked list connection", diagram)


if __name__ == "__main__":
    unittest.main()
