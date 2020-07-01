import signal
import time
import logging

import typing as tp

logger = logging.getLogger(__name__)
end = False


def __sighandler(a, b):
    logger.warning('Handling a signal')
    global end
    end = True


def hang_until_sig(extra_signals: tp.Optional[tp.List[int]] = None) -> None:
    """
    Will hang until this process receives SIGTERM or SIGINT.
    If you pass extra signal IDs (signal.SIG*) with extra_signals,
    then also on those signals this call will release.

    :param extra_signals: a list of extra signals to listen to
    """
    global end
    extra_signals = extra_signals or ()

    signal.signal(signal.SIGTERM, __sighandler)
    signal.signal(signal.SIGINT, __sighandler)
    for s in extra_signals:
        signal.signal(s, __sighandler)

    while not end:
        time.sleep(0.5)

    end = False  # reset for next use
