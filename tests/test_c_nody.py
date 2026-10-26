import unittest
from nody import CNodyList, CNodeRef, C_BACKEND_AVAILABLE


@unittest.skipUnless(C_BACKEND_AVAILABLE, "C backend DLL not compiled or available")
class TestCNody(unittest.TestCase):
    def test_c_node_ref_basic(self):
        node = CNodeRef.create(capacity=3)
        self.assertTrue(node.address.startswith("0x"))
        self.assertIsNone(node.next_address)
        self.assertIsNone(node.prev_address)

        node.append(10.5)
        node.append(20.5)
        self.assertAlmostEqual(node[0], 10.5)
        self.assertAlmostEqual(node[1], 20.5)

        node[0] = 99.0
        self.assertAlmostEqual(node[0], 99.0)

    def test_c_nody_list_basic(self):
        lst = CNodyList(node_capacity=4)
        self.assertEqual(len(lst), 0)
        self.assertEqual(lst.total_nodes, 0)

        for i in range(1, 10):  # 9 elements -> 3 nodes: [4, 4, 1]
            lst.append(i)

        self.assertEqual(len(lst), 9)
        self.assertEqual(lst.total_nodes, 3)
        self.assertEqual(lst[0], 1.0)
        self.assertEqual(lst[8], 9.0)
        self.assertEqual(lst[-1], 9.0)

    def test_c_nody_slicing(self):
        lst = CNodyList(node_capacity=3, initial_data=range(10))
        self.assertEqual(lst[2:6], [2.0, 3.0, 4.0, 5.0])
        self.assertEqual(lst[-3:], [7.0, 8.0, 9.0])

    def test_c_nody_prepend(self):
        lst = CNodyList(node_capacity=3)
        lst.prepend(1.0)
        lst.prepend(2.0)
        lst.prepend(3.0)
        lst.prepend(4.0)
        self.assertEqual(lst.to_list(), [4.0, 3.0, 2.0, 1.0])

    def test_c_nody_insert_split(self):
        lst = CNodyList(node_capacity=4, initial_data=[10, 20, 30, 40])
        self.assertEqual(lst.total_nodes, 1)

        # Inserting into full node triggers C node split
        lst.insert(2, 25)
        self.assertEqual(lst.to_list(), [10.0, 20.0, 25.0, 30.0, 40.0])
        self.assertGreater(lst.total_nodes, 1)

    def test_c_nody_pop(self):
        lst = CNodyList(node_capacity=2, initial_data=[10, 20, 30, 40])
        self.assertEqual(lst.total_nodes, 2)
        val = lst.pop()
        self.assertEqual(val, 40.0)
        val2 = lst.pop()
        self.assertEqual(val2, 30.0)
        self.assertEqual(lst.total_nodes, 1)

    def test_c_nody_native_math(self):
        lst = CNodyList(node_capacity=5, initial_data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertAlmostEqual(lst.sum(), 55.0)
        self.assertAlmostEqual(lst.min(), 1.0)
        self.assertAlmostEqual(lst.max(), 10.0)

        lst.scale(2.0)
        self.assertAlmostEqual(lst.sum(), 110.0)
        self.assertAlmostEqual(lst.min(), 2.0)
        self.assertAlmostEqual(lst.max(), 20.0)

    def test_c_nody_bulk_extend(self):
        lst = CNodyList(node_capacity=100)
        data = list(range(1000))
        lst.extend(data)
        self.assertEqual(len(lst), 1000)
        self.assertEqual(lst.to_list(), [float(x) for x in data])


if __name__ == "__main__":
    unittest.main()
