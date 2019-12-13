# coding=UTF-8
"""
Allows you to preserve entire stack frame along with all variables (even
 pickles them).

After this, you can send this report somewhere. At target, it will be unpickled
 in a safe way
(without importing anything extra from environment). You can unpickle
particular variables stored,
but that may involve an import.

Use in such a way:

    try:
        ...
    except WhateverError as e:
        tp = Traceback()
        print(tp.pretty_print())
        # you can now pickle it if you wish to
"""
import inspect
import io
import types
import sys
import traceback
import zlib
import typing as tp

try:
    import cPickle as pickle
except ImportError:
    import pickle


class GenerationPolicy(object):
    """
    A policy that manages generating a traceback

    For a "default" policy it's pretty customizable

    Override if need be, and pass the class (or instance) to Traceback
    """

    def __init__(self, enable_pickling: bool = True,
                 compress_at: int = 128 * 1024,
                 repr_length_limit: int = 128 * 1024,
                 compression_level: int = 6):
        """
        :param enable_pickling: bool, whether to enable pickling at all
        :param compress_at: pickles longer than this (bytes) will be compressed
        :param repr_length_limit: maximum length of __repr__. None for no limit.
        :param compression_level: "1" is fastest, "9" is slowest
        """
        assert isinstance(compression_level, int) and 1 <= compression_level <= 9

        self.enable_pickling = enable_pickling
        self.compress_at = compress_at
        self.repr_length_limit = repr_length_limit
        self.compression_level = compression_level

    def should_pickle(self, value: tp.Any) -> bool:
        """
        Should this value be pickled?

        :param value: value candidate
        :return: bool
        """
        return self.enable_pickling

    def should_compress(self, pickledata: bytes) -> bool:
        """
        Should this pickle undergo compression?
        :param pickledata: pickle value
        :return: bool
        """
        return len(pickledata) > self.compress_at

    def get_compression_level(self, pickledata: bytes) -> int:
        """
        What compression level to use to pickle this?
        :param pickledata: bytes, pickle value
        :return: int, 1-9, where "1" is the fastest, and "9" is the slowest,
            but produces best compression
        """
        return self.compression_level

    def process_repr(self, r: str) -> str:
        """
        Process the string obtained from __repr__ing
        :param r: result of a __repr__ on value
        :return: processed result
        """
        if self.repr_length_limit is None:
            return r
        else:
            if len(r) > self.repr_length_limit:
                return r[:self.repr_length_limit] + u'...'
            else:
                return r


class StoredVariableValue:
    """
    Class used to store a variable value. Picklable.

    Attributes are:
        .repr - a text representation obtained using repr
        .typeinfo - a text representation of variable's type
        .pickle - bytes with pickled (optionally processed) value, or None if
            not available
        .pickle_type - what is stored in .pickle?
            None - nothing
            "pickle" - normal Python pickle
            "pickle/gzip" - Python pickle treated with zlib.compress
            "failed" - could not pickle, pickle contains a UTF-8 text with
                human-readable exception reason
            "failed/gzip" - compression failed, pickle contains a UTF-8 text with
                human-readable exception reason

    """
    __slots__ = ('repr', 'type_', 'pickle', 'pickle_type')

    def __init__(self, value: tp.Any, policy: tp.Optional[GenerationPolicy] = None):
        """
        If value cannot be pickled, it's repr will be at least preserved

        :param value: any Python value to preserve
        :param policy: policy to use (instance)
        """
        self.repr = repr(value)
        self.type_ = repr(type(value))

        policy = policy or GenerationPolicy()

        self.repr = policy.process_repr(self.repr)

        self.pickle = None
        self.pickle_type = None

        if policy.should_pickle(value):
            try:
                self.pickle = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
                self.pickle_type = 'pickle'
            except BaseException as e:
                # yes, they all can happen!
                self.pickle = repr((e,)+e.args).encode('utf8')
                self.pickle_type = "failed"
            else:
                if policy.should_compress(self.pickle):
                    try:
                        self.pickle = zlib.compress(
                            self.pickle,
                            policy.get_compression_level(
                                self.pickle))
                        self.pickle_type = "pickle/gzip"
                    except zlib.error as e:
                        self.pickle = ('failed to gzip, reason is %s' % (repr(e), )).encode('utf8')
                        self.pickle_type = "failed/gzip"

    def load_value(self):
        """
        Return the value that this represents.

        WARNING! This may result in importing things from environment, as
        pickle.loads will be called.

        :return: stored value - if picklable and was pickled
        :raises ValueError: value has failed to be pickled or was never pickled
        """
        if self.pickle_type is None:
            raise ValueError('value was never pickled')
        elif self.pickle_type == 'failed':
            raise ValueError(
                'Value has failed to be pickled, reason is %s' % (self.pickle,))
        elif self.pickle_type == 'pickle/gzip':
            pickle_ = zlib.decompress(self.pickle)
        elif self.pickle_type == 'pickle':
            pickle_ = self.pickle

        try:
            return pickle.loads(pickle_)
        except pickle.UnpicklingError:
            raise ValueError(
                'object picklable, but cannot load in this environment')


class StackFrame:
    """
    Class used to verily preserve stack frames. Picklable.
    """
    __slots__ = ('locals', 'globals', 'name', 'filename', 'lineno')

    def __init__(self, frame: "<class 'frame'>", policy: GenerationPolicy):
        """
        :type frame: Python stack frame
        """
        self.name = frame.f_code.co_name
        self.filename = frame.f_code.co_filename
        self.lineno = frame.f_lineno

        self.locals = {}
        for key, value in frame.f_locals.items():
            self.locals[key] = StoredVariableValue(value, policy)

        self.globals = {}
        for key, value in frame.f_globals.items():
            self.globals[key] = StoredVariableValue(value, policy)


class Traceback(object):
    """
    Class used to preserve exceptions and chains of stack frames.
     Picklable.
     """
    __slots__ = ('formatted_traceback', 'frames')

    def __init__(self, starting_frame: tp.Optional[types.FrameType] = None,
                 policy=GenerationPolicy):
        """
        To be invoked while processing an exception is in progress

        :param starting_frame: frame to start tracking the traceback from.
            Must be either None, in which case an exception must be in progress and will be taken
            else must be an instance of <class 'frame'>.
        :param policy: policy for traceback generation
        :raise ValueError: there is no traceback to get info from!
            Is any exception in process?
        """

        if inspect.isclass(policy):
            value_pickling_policy = policy()

        tb = sys.exc_info()[2]

        self.frames = []

        if starting_frame is None:
            if tb is None:
                raise ValueError('No traceback')
            while tb.tb_next:
                tb = tb.tb_next
            f = tb.tb_frame
        else:
            f = starting_frame

        while f:
            self.frames.append(StackFrame(f, value_pickling_policy))
            f = f.f_back

        self.formatted_traceback = str(traceback.format_exc())

    def pickle_to(self, stream: tp.BinaryIO) -> None:
        """Pickle self to target stream"""
        pickle.dump(self, stream, pickle.HIGHEST_PROTOCOL)

    def pickle(self) -> bytes:
        """Returns this instance, pickled"""
        bio = io.BytesIO()
        self.pickle_to(bio)
        return bio.getvalue()

    def pretty_format(self) -> str:
        """
        Return a multi-line, pretty-printed representation of all exception
        data.
        :return: text
        """
        bio = io.StringIO()
        self.pretty_print(bio)
        return bio.getvalue()

    def pretty_print(self, output: tp.TextIO = sys.stderr) -> None:
        """
        Pretty-print the exception
        :param output: a file-like object in text mode
        :return: unicode
        """
        k = []
        output.write(self.formatted_traceback)
        output.write(u'\n* Stack trace, innermost first\n')
        for frame in self.frames:
            output.write(u'** %s at %s:%s\n' % (
                frame.name, frame.filename, frame.lineno))
            for name, value in frame.locals.items():
                try:
                    output.write(u'*** %s: %s\n' % (name, value.repr))
                except BaseException as e:
                    output.write(u'*** %s: repr unavailable (due to locally raised %s)\n' % (name, repr(e)))
