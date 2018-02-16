# coding=UTF-8
from __future__ import print_function, absolute_import, division

import functools
import logging

logger = logging.getLogger(__name__)

__all__ = [
    'silence',
    'rethrow_as'
]


def silence_excs(*exc_types):
    """
    Silence given exception types.

    Can be either a decorator or a context manager
    """
    return rethrow_as(exc_types, None)


class rethrow_as(object):
    """
    Transform some exceptions into others.

    Either a decorator or a context manager
    """

    def __init__(self, *pairs, **kwargs):
        """
        Pass tuples of (exception to catch - exception to transform to).

        New exception will be created by calling exception to transform to with
        repr of current one.

        You can also provide just two exceptions, eg.

          rethrow_as(NameError, ValueError)

        If the second value is a None, exception will be silenced.

        :param exception_preprocessor: other callable/1 to use instead od repr.
            Should return a text
        """

        # You can also provide just two exceptions

        two_entries_provided = True

        if len(pairs) != 2:
            two_entries_provided = False
        else:
            a, b = pairs
            if isinstance(b, (tuple, list)):
                two_entries_provided = False
            elif not ((b is None) or (issubclass(b, BaseException))):
                two_entries_provided = False

        if two_entries_provided:
            self.mapping = [(a, b)]
        else:
            self.mapping = list(pairs)

        self.exception_preprocessor = kwargs.get('exception_preprocessor', repr)

    def __call__(self, fun):
        @functools.wraps(fun)
        def inner(*args, **kwargs):
            with self:
                return fun(*args, **kwargs)

        return inner

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for from_, to in self.mapping:
            if issubclass(exc_type, from_):
                if to is None:
                    return True
                else:
                    raise to(self.exception_preprocessor(exc_val))
