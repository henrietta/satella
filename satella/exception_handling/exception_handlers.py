import types
import typing as tp
from abc import abstractmethod

__all__ = [
    'BaseExceptionHandler',
    'FunctionExceptionHandler',
    'exception_handler',
    'ALWAYS_FIRST',
    'ALWAYS_LAST',
    'NORMAL_PRIORITY',
    'ExceptionHandlerCallable'
]

ALWAYS_FIRST = -1000
NORMAL_PRIORITY = 0
ALWAYS_LAST = 1000

ExceptionHandlerCallable = tp.Callable[[type, BaseException, types.TracebackType], bool]


class BaseExceptionHandler:
    def __init__(self, priority=NORMAL_PRIORITY):
        """
        Instantiate an exception handler with provided priority.
        Handlers with smaller priorities run sooner.

        :param priority: Priority to use for this handler
        """
        self.priority = priority

    def install(self) -> 'BaseExceptionHandler':
        """
        Register this handler to run upon exceptions
        """
        from .global_eh import GlobalExcepthook
        GlobalExcepthook().add_hook(self)
        return self

    def uninstall(self):
        """
        Unregister this handler to run on exceptions
        """
        from .global_eh import GlobalExcepthook
        GlobalExcepthook().remove_hook(self)

    @abstractmethod
    def handle_exception(self, type_: tp.Callable[[type, BaseException, types.TracebackType], None], value,
                         traceback: types.TracebackType) -> tp.Optional[bool]:
        """
        Return True to intercept the exception, so that it won't be propagated to other handlers.
        """
        pass


class FunctionExceptionHandler(BaseExceptionHandler):
    """
    A exception handler to make callables of given signature into Satella's exception handlers.

    Your exception handler must return a bool, whether to intercept the exception and not propagate it.
    """

    def __init__(self, fun: ExceptionHandlerCallable, priority: int = NORMAL_PRIORITY):
        super(FunctionExceptionHandler, self).__init__(priority)
        self.fun = fun

    def handle_exception(self, type_, value, traceback):
        if type_ == SystemExit:
            return
        return self.fun(type_, value, traceback)


def exception_handler(priority: int = NORMAL_PRIORITY):
    """
    Convert a callable to an FunctionExceptionHandler. Usage

    >>> @exception_handler(priority=-10)
    >>> def handle_exc(type_, val, traceback):
    >>>     ...

    :return: ExceptionHandler instance
    """

    if not isinstance(priority, int):
        raise TypeError('Did you forget to use it as @exception_handler() ?')

    def outer(fun: ExceptionHandlerCallable) -> FunctionExceptionHandler:
        return FunctionExceptionHandler(fun, priority=priority)

    return outer
