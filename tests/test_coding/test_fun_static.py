import unittest
from threading import Thread
from time import sleep
import six
from six.moves.queue import Queue

from satella.coding import static_var


class FunTestTest(unittest.TestCase):
    def test_fun_static_function(self):
        @static_var("counter", 2)
        def static_fun(a):
            static_fun.counter += 1
            return a

        static_fun(2)
        static_fun(3)
        self.assertEquals(static_fun.counter, 4)

    @unittest.skipIf(six.PY2, 'Syntax unsupported on Python 2')
    def test_fun_static_method(self):
        class MyClass(object):
            @static_var("counter", 2)
            def my_method(self):
                MyClass.my_method.counter += 1
                return a

        a = MyClass()
        a.my_method()
        a.my_method()
        self.assertEquals(MyClass.my_method.counter, 4)
