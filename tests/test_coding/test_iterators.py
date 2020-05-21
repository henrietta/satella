import unittest

from satella.coding import SelfClosingGenerator, hint_with_length


class TestIterators(unittest.TestCase):
    def test_hint_with_length(self):
        def generator():
            for i in range(1000):
                yield i

        g = hint_with_length(generator(), 1000)
        self.assertEqual(g.__length_hint__(), 1000)

    def test_self_closing_generator(self):

        a = {'done': False}

        def generator():
            for i in range(5):
                yield i
            a['done'] = True

        for i in SelfClosingGenerator(generator()):
            if i == 2:
                break

        self.assertTrue(a['done'])
