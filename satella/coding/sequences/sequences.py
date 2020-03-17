import logging
import typing as tp

logger = logging.getLogger(__name__)

__all__ = ['is_last']
T = tp.TypeVar('T')
U = tp.TypeVar('U')


# shamelessly copied from https://medium.com/better-programming/is-this-the-last-element-of-my-python-for-loop-784f5ff90bb5
def is_last(lst: tp.Iterable[T]) -> tp.Generator[tp.Tuple[bool, T], None, None]:
    """
    Return every element of the list, alongside a flag telling is this the last element.

    Use like:

    >>> for is_last, element in is_last(my_list):
    >>> if is_last:
    >>>     ...

    :param lst: list to iterate thru
    :return: a generator returning (bool, T)
    """
    iterable = iter(lst)
    ret_var = next(iterable)
    for val in iterable:
        yield False, ret_var
        ret_var = val
    yield True, ret_var


def add_next(lst: tp.Iterable[T], wrap_over: bool = False) -> tp.Generator[
    tp.Tuple[T, tp.Optional[T]], None, None]:
    """
    Yields a 2-tuple of given iterable, presenting the next element as second element of the tuple.

    The last element will be the last element alongside with a None, if wrap_over is False, or the
    first element if wrap_over was True

    Example:

    >>> list(add_next([1, 2, 3, 4, 5])) == [(1, 2), (2, 3), (3, 4), (4, 5), (5, None)]
    >>> list(add_next([1, 2, 3, 4, 5], True)) == [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1)]

    :param lst: iterable to iterate over
    :param wrap_over: whether to attach the first element to the pair of the last element instead
        of None
    """
    iterator = iter(lst)
    try:
        first_val = prev_val = next(iterator)
    except StopIteration:
        return
    for val in iterator:
        yield prev_val, val
        prev_val = val
    if wrap_over:
        yield prev_val, first_val
    else:
        yield prev_val, None


def half_product(seq1: tp.Iterable[T], seq2: tp.Iterable[U]) -> tp.Generator[
    tp.Tuple[T, U], None, None]:
    """
    Generate half of the Cartesian product of both sequences.

    Useful when you have a commutative operation that you'd like to execute on both elements
    (eg. checking for collisions).

    Example:

    >>> list(half_cartesian([1, 2, 3], [1, 2, 3])) == \
    >>>     [(1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3)]

    :param seq1: First sequence
    :param seq2: Second sequence
    """
    for i, elem1 in enumerate(seq1):
        for j, elem2 in enumerate(seq2):
            if j >= i:
                yield elem1, elem2


def group_quantity(length: int, seq: tp.Iterable[T]) -> tp.Generator[tp.List[T], None, None]:
    """
    Slice an iterable into lists containing at most len entries.

    Eg.

    >>> assert list(group_quantity(3, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])) == [[1, 2, 3], [4, 5, 6],
    >>>                                                                     [7, 8, 9], [10]]

    :param length: length for the returning sequences
    :param seq: sequence to split
    """
    entries = []
    for elem in seq:
        if len(entries) < length:
            entries.append(elem)
        else:
            yield entries
            entries = [elem]
    if entries:
        yield entries
