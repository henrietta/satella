import logging
import typing as tp
import warnings
import itertools

logger = logging.getLogger(__name__)


def infinite_counter(start_at: int = 0, step: int = 1) -> tp.Generator[int, None, None]:
    """
    Infinite counter, starting at start_at

    :param start_at: value at which to start counting. It will be yielded as first
    :param step: step by which to progress the counter
    """
    warnings.warn('This is deprecated, use itertools.count() instead', DeprecationWarning)
    i = start_at
    while True:
        yield i
        i += step


def is_instance(classes: tp.Union[tp.Tuple[type, ...], type]) -> tp.Callable[[object], bool]:
    def inner(object_):
        return isinstance(object_, classes)
    inner.__doc__ = """Return a bool telling if object is of type %s""" % (repr(classes), )
    return inner


T = tp.TypeVar('T')

IteratorOrIterable = tp.Union[tp.Iterator[T], tp.Iterable[T]]


def zip_shifted(*args: tp.Union[IteratorOrIterable[T], tp.Tuple[IteratorOrIterable[T], int]]) -> \
        tp.Iterator[tp.Tuple[T, ...]]:
    """
    Construct an iterator, just like zip but first by cycling it's elements by it's shift factor.
    Elements will be shifted by a certain factor, this means that they will appear earlier.

    Example:

    >>> zip_shifted(([1, 2, 3, 4], 1), ([1, 2, 3, 4], 0)) == [(2, 1), (3, 2), (4, 3), (1, 4)]

    This will work on arbitrary iterators and iterables.

    Shift can be negative, in which case the last elements will appear sooner, eg.

    >>> zip_shifted(([1, 2, 3, 4], -1), ([1, 2, 3, 4], 0)) == [(4, 1), (1, 2), (2, 3), (3, 4)]

    However note that this will result in iterators which have negative shift to be readed entirely
    into memory (converted internally to lists). This can be avoided by passing in a Reversible iterable.

    The resulting iterator will be as long as the shortest sequence.
    :param args: a tuple with the iterator/iterable and amount of shift. If a non-tuple is given,
        it is assumed that the shift is zero.
    """

    iterators = []  # type: tp.List[tp.Union[tp.Tuple[tp.Iterator[T], tp.List[T]], tp.Iterator[T]]
    for row in args:
        if not isinstance(row, tuple):
            iterators.append(row)
        else:
            iterable, shift = row
            if shift >= 0:
                iterator = iter(iterable)
                if shift < 0:
                    raise ValueError('Negative shift given!')
                elements = []
                for i in range(shift):
                    elements.append(next(iterator))
                iterators.append(itertools.chain(iterator, elements))
            else:
                if isinstance(iterable, tp.Reversible):
                    rev_iterable = reversed(iterable)
                    elements = take_n(rev_iterable, -shift)
                    elements = reversed(elements)
                    iterators.append(itertools.chain(elements, iterable))
                else:
                    iterator = list(iterable)
                    iterator = iterator[shift:] + iterator[:shift]  # shift's already negative
                    iterators.append(iterator)

    return zip(*iterators)


def skip_first(iterator: IteratorOrIterable, n: int) -> tp.Iterator[T]:
    """
    Skip first n elements from given iterator
    """
    iterator = iter(iterator)
    for i in range(n):
        next(iterator)
    yield from iterator


def stop_after(iterator: IteratorOrIterable[T], n: int) -> tp.Iterator[T]:
    """
    Stop this iterator after returning n elements, even if it's longer than that.

    :param iterator: iterator or iterable to examine
    :param n: elements to return
    """
    iterator = iter(iterator)
    for i in range(n):
        yield next(iterator)


def take_n(iterator: IteratorOrIterable, n: int, skip: int = 0) -> tp.List[T]:
    """
    Take (first) n elements of an iterator, or the entire iterator, whichever comes first

    :param iterator: iterator to take from
    :param n: amount of elements to take
    :param skip: elements from the start to skip
    :return: list of length n (or shorter)
    """
    iterator = iter(iterator)
    for i in range(skip):
        next(iterator)

    output = []
    for i in range(n):
        try:
            output.append(next(iterator))
        except StopIteration:
            return output
    return output
