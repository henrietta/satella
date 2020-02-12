import json
import typing as tp
from abc import ABCMeta, abstractmethod

__all__ = ['JSONEncoder', 'JSONAble', 'json_encode']


class JSONAble(metaclass=ABCMeta):
    @abstractmethod
    def to_json(self) -> tp.Union[list, dict, str, int, float, None]:
        """Return a JSON-able representation of this object"""


class JSONEncoder(json.JSONEncoder):
    """
    This encoder will encode everything!
    """
    def default(self, o) -> str:
        if hasattr(o, 'to_json'):
            return o.to_json()
        try:
            return super().default(o)
        except TypeError:
            dct = {}
            for k, v in o.__dict__.items():
                dct[k] = repr(v)
            return dct


def json_encode(x) -> str:
    """
    Convert an object to JSON. Will properly handle subclasses of JSONAble

    :param x: object to convert
    """
    return JSONEncoder().encode(x)
