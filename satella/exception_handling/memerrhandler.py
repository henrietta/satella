import logging
import sys
import time

from satella.posix import suicide
from .exception_handlers import BaseExceptionHandler, ALWAYS_FIRST

logger = logging.getLogger(__name__)


class MemoryErrorExceptionHandler(BaseExceptionHandler):
    def __init__(self, custom_hook=lambda type, value, traceback: None,
                 killpg=False):
        """
        :param killpg: kill entire process group, if applicable
        """
        super(MemoryErrorExceptionHandler, self).__init__()
        self.priority = ALWAYS_FIRST  # always run first!
        self._free_on_memoryerror = {'a': bytearray(1024 * 2)}
        self.custom_hook = custom_hook
        self.killpg = killpg
        self.installed = False

    def install(self):
        if self.installed:
            raise RuntimeError('already installed')

        from .global_eh import GlobalExcepthook
        GlobalExcepthook().add_hook(self)

    def handle_exception(self, type, value, traceback) -> bool:
        if not issubclass(type, MemoryError):
            return False

        del self._free_on_memoryerror['a']

        try:
            self.custom_hook(type, value, traceback)
        except:
            pass

        try:
            sys.stderr.write(
                'satella.exception_handling: MemoryError seen, killing\n')
            sys.stderr.flush()
        except (IOError, OSError):
            pass

        suicide(self.killpg)

        time.sleep(5)
        return True