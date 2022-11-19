import numpy as np
import sys
from libsmop.base import *


class matlabarray(np.ndarray):
    """
    >>> matlabarray()
    matlabarray([], shape=(0, 0), dtype=float64)
    >>> matlabarray([arange(1,5), arange(1,5)])
    matlabarray([1, 2, 3, 4, 5, 1, 2, 3, 4, 5])
    >>> matlabarray(["hello","world"])
    matlabarray("helloworld")
    """

    def __new__(cls, a=[], dtype=None):
        obj = np.array(a,
                       dtype=dtype,
                       copy=False,
                       order="F",
                       ndmin=2).view(cls).copy(order="F")
        if obj.size == 0:
            obj.shape = (0, 0)
        return obj

    #def __array_finalize__(self,obj):

    def __copy__(self):
        return np.ndarray.copy(self, order="F")

    def __iter__(self):
        """ must define iter or char won't work"""
        return np.asarray(self).__iter__()

    def compute_indices(self, index):
        if not isinstance(index, tuple):
           index = index,
        if len(index) != 1 and len(index) != self.ndim:
            raise IndexError
        indices = []
        for i, ix in enumerate(index):
            if ix.__class__ is end:
                indices.append(self.shape[i]-1+ix.n)
            elif ix.__class__ is slice:
                if self.size == 0 and ix.stop is None:
                    raise IndexError
                if len(index) == 1:
                    n = self.size
                else:
                    n = self.shape[i]
                indices.append(np.arange((ix.start or 1)-1,
                                         ix.stop or n,
                                         ix.step or 1,
                                         dtype=int))
            else:
                try:
                    indices.append(int(ix)-1)
                except:
                    indices.append(np.asarray(ix).astype("int32")-1)
        if len(indices) == 2 and isvector(indices[0]) and isvector(indices[1]):
            indices[0].shape = (-1, 1)
            indices[1].shape = (-1,)
        return tuple(indices)

    def __getslice__(self, i, j):
        if i == 0 and j == sys.maxsize:
            return self.reshape(-1, 1, order="F")
        return self.__getitem__(slice(i, j))

    def __getitem__(self, index):
        return matlabarray(self.get(index))

    def get(self, index):
        #import pdb; pdb.set_trace()
        indices = self.compute_indices(index)
        if len(indices) == 1:
            return np.ndarray.__getitem__(self.reshape(-1, order="F"), indices)
        else:
            return np.ndarray.__getitem__(self, indices)

    def __setslice__(self, i, j, value):
        if i == 0 and j == sys.maxsize:
            index = slice(None, None)
        else:
            index = slice(i, j)
        self.__setitem__(index, value)

    def sizeof(self, ix):
        if isinstance(ix, int):
            n = ix+1
        elif isinstance(ix, slice):
            n = ix.stop
        elif isinstance(ix, (list, np.ndarray)):
            n = max(ix)+1
        else:
            assert 0, ix
        if not isinstance(n, int):
            raise IndexError
        return n

    def __setitem__(self, index, value):
        #import pdb; pdb.set_trace()
        indices = self.compute_indices(index)
        try:
            if len(indices) == 1:
                np.asarray(self).reshape(-1,
                                         order="F").__setitem__(indices, value)
            else:
                np.asarray(self).__setitem__(indices, value)
        except (ValueError, IndexError):
            #import pdb; pdb.set_trace()
            if not self.size:
                new_shape = [self.sizeof(s) for s in indices]
                self.resize(new_shape, refcheck=0)
                np.asarray(self).__setitem__(indices, value)
            elif len(indices) == 1:
                # One-dimensional resize is only implemented for
                # two cases:
                #
                # a. empty matrices having shape [0 0]. These
                #    matries may be resized to any shape.  A[B]=C
                #    where A=[], and B is specific -- A[1:10]=C
                #    rather than A[:]=C or A[1:end]=C
                if self.size and not isvector_or_scalar(self):
                    raise IndexError("One-dimensional resize "
                                     "works only on vectors, and "
                                     "row and column matrices")
                # One dimensional resize of scalars creates row matrices
                # ai = 3
                # a(4) = 1
                # 3 0 0 1
                n = self.sizeof(indices[0])  # zero-based
                if max(self.shape) == 1:
                    new_shape = list(self.shape)
                    new_shape[-1] = n
                else:
                    new_shape = [(1 if s == 1 else n) for s in self.shape]
                self.resize(new_shape, refcheck=0)
                np.asarray(self).reshape(-1,
                                         order="F").__setitem__(indices, value)
            else:
                new_shape = list(self.shape)
                if self.flags["C_CONTIGUOUS"]:
                    new_shape[0] = self.sizeof(indices[0])
                elif self.flags["F_CONTIGUOUS"]:
                    new_shape[-1] = self.sizeof(indices[-1])
                self.resize(new_shape, refcheck=0)
                np.asarray(self).__setitem__(indices, value)

    def __repr__(self):
        return self.__class__.__name__ + repr(np.asarray(self))[5:]

    def __str__(self):
        return str(np.asarray(self))

    def __add__(self, other):
        return matlabarray(np.asarray(self)+np.asarray(other))

    def __neg__(self):
        return matlabarray(np.asarray(self).__neg__())


class cellarray(matlabarray):
    """
    Cell array corresponds to matlab ``{}``


    """

    def __new__(cls, a=[]):
        """
        Create a cell array and initialize it with a.
        Without arguments, create an empty cell array.

        Parameters:
        a : list, ndarray, matlabarray, etc.

        >>> a=cellarray([123,"hello"])
        >>> print a.shape
        (1, 2)

        >>> print a[1]
        123

        >>> print a[2]
        hello
        """
        obj = np.array(a,
                       dtype=object,
                       order="F",
                       ndmin=2).view(cls).copy(order="F")
        if obj.size == 0:
            obj.shape = (0, 0)
        return obj

    def __getitem__(self, index):
        return self.get(index)

#    def __str__(self):
#        if self.ndim == 0:
#            return ""
#        if self.ndim == 1:
#            return "".join(s for s in self)
#        if self.ndim == 2:
#            return "\n".join("".join(s) for s in self)
#        raise NotImplementedError


class cellstr(matlabarray):
    """
    >>> s=cellstr(char('helloworldkitty').reshape(3,5))
    >>> s
    cellstr([['hello', 'world', 'kitty']], dtype=object)
    >>> print s
    hello
    world
    kitty
    >>> s.shape
    (1, 3)
    """

    def __new__(cls, a):
        """
        Given a two-dimensional char object,
        create a cell array where each cell contains
        a line.
        """
        obj = np.array(["".join(s) for s in a],
                       dtype=object,
                       copy=False,
                       order="C",
                       ndmin=2).view(cls).copy(order="F")
        if obj.size == 0:
            obj.shape = (0, 0)
        return obj

    def __str__(self):
        return "\n".join("".join(s) for s in self.reshape(-1))

    def __getitem__(self, index):
        return self.get(index)


class char(matlabarray):
    """
    class char is a rectangular string matrix, which
    inherits from matlabarray all its features except
    dtype.

    >>> s=char()
    >>> s.shape
    (0, 0)

    >>> s=char('helloworld')
    >>> reshape(s, [2,5])
    hlool
    elwrd

    >>> s=char([104, 101, 108, 108, 111, 119, 111, 114, 108, 100])
    >>> s.shape = 2,5
    >>> print s
    hello
    world
    """

    def __new__(cls, a=""):
        if not isinstance(a, str):
            a = "".join([chr(c) for c in a])
        obj = np.array(list(a),
                       dtype='|S1',
                       copy=False,
                       order="F",
                       ndmin=2).view(cls).copy(order="F")
        if obj.size == 0:
            obj.shape = (0, 0)
        return obj

    def __getitem__(self, index):
        return self.get(index)

    def __str__(self):
        if self.ndim == 0:
            return ""
        if self.ndim == 1:
            return "".join(s for s in self)
        if self.ndim == 2:
            return "\n".join("".join(s) for s in self)
        raise NotImplementedError
