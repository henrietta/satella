import logging
import unittest

from satella.coding.sequences import choose, infinite_counter, take_n, is_instance, is_last, \
    add_next, half_product, skip_first, zip_shifted, stop_after

logger = logging.getLogger(__name__)


class TestSequences(unittest.TestCase):

    def test_stop_after(self):
        a = [1,2,3,4,5,6,7]
        a = list(stop_after(a, 2))
        self.assertEqual([1, 2], a)

    def test_zip_shifted(self):
        a = list(zip_shifted(([1, 2, 3, 4], 1), [1, 2, 3, 4]))
        self.assertEqual(a, [(2, 1), (3, 2), (4, 3), (1, 4)])

    def test_zip_shifted_negative(self):
        a = list(zip_shifted(([1, 2, 3, 4], -1), [1, 2, 3, 4]))
        self.assertEqual(a, [(4, 1), (1, 2), (2, 3), (3, 4)])

    def test_skip_first(self):
        a = [1, 2, 3, 4, 5]
        b = list(skip_first(a, 1))
        self.assertEqual(b, [2, 3, 4, 5])

    def test_half_product(self):
        a = set(half_product([1, 2, 3], [1, 2, 3]))
        b = set([(1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3)])
        self.assertEqual(a, b)

    def test_add_next(self):
        self.assertEqual(list(add_next([1, 2, 3, 4, 5])),
                         [(1, 2), (2, 3), (3, 4), (4, 5), (5, None)])
        self.assertEqual(list(add_next([1])), [(1, None)])
        self.assertEqual(list(add_next([])), [])

    def test_add_next_wrap_over(self):
        self.assertEqual(list(add_next([1, 2, 3, 4, 5], True)),
                         [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1)])

    def test_is_last(self):
        for is_last_flag, elem in is_last([1, 2, 3, 4, 5]):
            self.assertTrue(not is_last_flag ^ (elem == 5))

    def test_take_n(self):
        subset = take_n(infinite_counter(), 10)
        for a, b in zip(range(10), subset):
            self.assertEqual(a, b)

    def test_infinite_counter(self):
        p = infinite_counter(1)
        for i in range(1, 10):
            a = next(p)
            self.assertEqual(a, i)

    def test_choose(self):
        self.assertEqual(choose(lambda x: x == 2, [1, 2, 3, 4, 5]), 2)
        self.assertRaises(ValueError, lambda: choose(lambda x: x % 2 == 0, [1, 2, 3, 4, 5]))
        self.assertRaises(ValueError, lambda: choose(lambda x: x == 0, [1, 2, 3, 4, 5]))

    def test_is_instance(self):
        objects = [object(), object(), [], [], object()]
        self.assertEqual(len(list(filter(is_instance(list), objects))), 2)
