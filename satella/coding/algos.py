# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging
import types
import copy
import itertools
from .typecheck import typed


def _merge(v1, v2):
    if isinstance(v1, dict) and isinstance(v2, dict):
        v1.update(v2)
        return v1

    if isinstance(v1, list) and isinstance(v2, list):
        v1.extend(v2)
        return v2

    raise TypeError


@typed(dict, dict, returns=dict)
def merge_dicts(first, second):

    for key in second.keys():
        try:
            first[key] = _merge(first[key], second[key])
        except (TypeError, KeyError) as e:       # overwrite, not a list or dict, or no key in first
            print(e)
            first[key] = second[key]

    return first
