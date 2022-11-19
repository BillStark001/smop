import time
import builtins

import numpy as np


def isvector_or_scalar(a):
    """
    one-dimensional arrays having shape [N],
    row and column matrices having shape [1 N] and
    [N 1] correspondingly, and their generalizations
    having shape [1 1 ... N ... 1 1 1].
    Scalars have shape [1 1 ... 1].
    Empty arrays dont count
    """
    try:
        return a.size and a.ndim-a.shape.count(1) <= 1
    except:
        return False


def isvector(a):
    """
    one-dimensional arrays having shape [N],
    row and column matrices having shape [1 N] and
    [N 1] correspondingly, and their generalizations
    having shape [1 1 ... N ... 1 1 1]
    """
    try:
        return a.ndim-a.shape.count(1) == 1
    except:
        return False


class end(object):
    def __add__(self, n):
        self.n = n
        return self

    def __sub__(self, n):
        self.n = -n
        return self


class struct(object):
    def __init__(self, *args):
        for i in range(0, len(args), 2):
            setattr(self, str(args[i]), args[i+1])


def tic():
    return time.clock()


def toc(t):
    return time.clock()-t


def length(a):
    try:
        return builtins.max(np.asarray(a).shape)
    except ValueError:
        return 1


sort = builtins.sorted


def error(s):
    raise s


def clc():
    pass
