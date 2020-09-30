from abc import ABCMeta, abstractmethod

from satella.coding.decorators.decorators import wraps

__all__ = ['Loadable', 'must_be_loaded']

class Loadable(metaclass=ABCMeta):
    """
    Any class that can be loaded lazily.

    It's keyword argument, load_lazy is expected to control lazy loading. If set to True,
    DB will be hit as a part of this object's constructor.

    If False, you will need to load it on-demand via must_be_loaded decorator.
    """

    __slots__ = ('_loaded',)

    def __init__(self, load_lazy: bool = False):
        self._loaded: bool = False
        if not load_lazy:
            self.refresh()

    @abstractmethod
    def refresh(self, load_from=None) -> None:
        """
        Optionally provide a class to load this class from.

        Override me, calling me in a super method.

        :param load_from: serialized object. If not given, the DB will be hit
        """
        self._loaded = True


def must_be_loaded(fun):
    """
    A decorator for Loadable's methods.

    Assures that .refresh() is called prior to executing that method, ie. the object
    is loaded from the DB
    """

    @wraps(fun)
    def inner(self, *args, **kwargs):
        assert isinstance(self,
                          Loadable), 'must_be_loaded called with a class that does not subclass ' \
                                     'Loadable'
        if not self._loaded:
            self.refresh()
        return fun(self, *args, **kwargs)

    return inner
