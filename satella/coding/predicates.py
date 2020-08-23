import typing as tp
import operator

__all__ = ['x']


def _nop(v):
    return v


def make_operation_two_args(operation_two_args: tp.Callable[[tp.Any, tp.Any], tp.Any],
                            docstring: tp.Optional[str] = None,
                            swap_order: bool = True):
    def operation(self, a) -> 'Predicate':
        if isinstance(a, Predicate):
            if not swap_order:
                def op(v):
                    return operation_two_args(self(v), a(v))
            else:
                def op(v):
                    return operation_two_args(a(v), self(v))
        else:
            if not swap_order:
                def op(v):
                    return operation_two_args(self(v), a)
            else:
                def op(v):
                    return operation_two_args(a, self(v))
        return Predicate(op)
    if docstring:
        operation.__doc__ = docstring
    return operation


def make_operation_single_arg(operation,
                              docstring: tp.Optional[str] = None):
    def operation_v(self) -> 'Predicate':
        def operate(v):
            return operation(v)
        return Predicate(operate)
    if docstring:
        operation_v.__doc__ = docstring
    return operation_v


def _has_keys(a, keys):
    for key in keys:
        if key not in a:
            return False
    return True


def _one_of(a, values):
    return a in values


class Predicate:
    """
    A shorthand to create lambdas using such statements, for example:

    >>> add_two = x + 2
    >>> assert add_two(2) == 4
    """
    __slots__ = ('operation', )

    def __init__(self, operation: tp.Callable[[tp.Any], tp.Any] = _nop):
        self.operation = operation

    def __call__(self, v):
        return self.operation(v)

    def has_keys(self, *keys) -> 'Predicate':
        """
        Return a predicate checking whether this value has provided keys
        """
        return make_operation_two_args(_has_keys)(self, keys)

    def one_of(self, *values) -> 'Predicate':
        """
        Return a predicate checking if x is amongst values
        """
        return make_operation_two_args(_one_of)(self, values)

    inside = make_operation_two_args(operator.contains,
                                     'Return a predicate checking if x is inside value')

    instanceof = make_operation_two_args(isinstance,
                                         'Return a predicate checking whether this value '
                                         'is an instance of instance')

    length = make_operation_single_arg(len, 'Return a predicate returning length of it''s argument')

    __contains__ = make_operation_two_args(operator.contains)
    __getattr__ = make_operation_two_args(getattr)
    __getitem__ = make_operation_two_args(operator.getitem)
    __eq__ = make_operation_two_args(operator.eq)
    __ne__ = make_operation_two_args(operator.ne)
    __lt__ = make_operation_two_args(operator.lt)
    __gt__ = make_operation_two_args(operator.gt)
    __le__ = make_operation_two_args(operator.le)
    __ge__ = make_operation_two_args(operator.ge)
    __add__ = make_operation_two_args(operator.add)
    __sub__ = make_operation_two_args(operator.sub)
    __mul__ = make_operation_two_args(operator.mul)
    __matmul__ = make_operation_two_args(operator.matmul)
    __and__ = make_operation_two_args(operator.and_)
    __or__ = make_operation_two_args(operator.or_)
    __rshift__ = make_operation_two_args(operator.rshift)
    __lshift__ = make_operation_two_args(operator.lshift)
    __xor__ = make_operation_two_args(operator.xor)
    __truediv__ = make_operation_two_args(operator.__truediv__)
    __floordiv__ = make_operation_two_args(operator.floordiv)
    __mod__ = make_operation_two_args(operator.mod)
    __radd__ = make_operation_two_args(operator.add, swap_order=True)
    __rsub__ = make_operation_two_args(operator.sub, swap_order=True)
    __rmul__ = make_operation_two_args(operator.mul, swap_order=True)
    __rmatmul__ = make_operation_two_args(operator.matmul, swap_order=True)
    __rand__ = make_operation_two_args(operator.and_, swap_order=True)
    __ror__ = make_operation_two_args(operator.or_, swap_order=True)
    __rrshift__ = make_operation_two_args(operator.rshift, swap_order=True)
    __rlshift__ = make_operation_two_args(operator.lshift, swap_order=True)
    __rxor__ = make_operation_two_args(operator.xor, swap_order=True)
    __rtruediv__ = make_operation_two_args(operator.__truediv__, swap_order=True)
    __rfloordiv__ = make_operation_two_args(operator.floordiv, swap_order=True)
    __rmod__ = make_operation_two_args(operator.mod, swap_order=True)
    __neg__ = make_operation_single_arg(operator.neg)
    __pow__ = make_operation_two_args(operator.pow)
    __invert__ = make_operation_single_arg(operator.invert)
    __abs__ = make_operation_single_arg(abs)


x = Predicate()