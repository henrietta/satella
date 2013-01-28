from threading import Thread, Lock

class BaseThread(Thread):
    """Thread with internal termination flag"""
    def __init__(self, *args, **kwargs):
        self._terminating = False
        Thread.__init__(self, *args, **kwargs)

    def terminate(self):
        """Sets internal termination flag"""
        self._terminating = True


class Monitor(object):
    """
    Base utility class for creating monitors (the synchronization thingies!)
    """
    def __init__(self):
        """You need to invoke this at your constructor"""
        self._monitor_lock = Lock()

    @staticmethod    
    def protect(fun):
        """
        This is a decorator. Class method decorated with that will lock the 
        global lock of given instance, making it threadsafe. Depending on 
        usage pattern of your class and it's data semantics, your performance
        may vary
        """
        def monitored(*args, **kwargs):
            with args[0]._monitor_lock:
                return fun(*args, **kwargs)
        return monitored


    class acquire(object):
        """
        Returns a context manager object that can lock another object,
        as long as that object is a monitor.

        Consider foo, which is a monitor. If you needed to lock it from
        outside, you would do:

            with Monitor.acquire(foo):
                .. do operations on foo that need mutual exclusion ..
        """
        def __init__(self, foo):
            self.foo = foo

        def __enter__(self):
            self.foo._monitor_lock.acquire()

        def __exit__(self, e1, e2, e3):
            self.foo._monitor_lock.release()
            return False
