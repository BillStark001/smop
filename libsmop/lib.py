# SMOP compiler runtime support library
# Copyright 2014 Victor Leikehman

# MIT license

# numpy related

import numpy as np

from numpy.fft import fft2
from numpy.linalg import inv
from numpy.linalg import qr as _qr
from numpy import rint as fix

# scipy related

try:
    from scipy.linalg import schur as _schur
except ImportError:
    pass

try:
    from scipy.io import loadmat
except:
    pass

from scipy.special import gamma


from libsmop.array import matlabarray, cellarray, char

NA = np.NaN


abs = np.abs
all = np.all
any = np.any


def arange(start, stop, step=1, **kwargs):
    """
    >>> a=arange(1,10) # 1:10
    >>> size(a)
    matlabarray([[ 1, 10]])
    """
    expand_value = 1 if step > 0 else -1
    return matlabarray(np.arange(start,
                                 stop+expand_value,
                                 step,
                                 **kwargs).reshape(1, -1), **kwargs)


def concat(args):
    """
    >>> concat([1,2,3,4,5] , [1,2,3,4,5]])
    [1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
    """
    import pdb
    pdb.set_trace()
    t = [matlabarray(a) for a in args]
    return np.concatenate(t)


def ceil(a):
    return np.ceil(a)


def cell(*args):
    if len(args) == 1:
        args += args
    return cellarray(np.zeros(args, dtype=object, order="F"))



def copy(a):
    return matlabarray(np.asanyarray(a).copy(order="F"))


def deal(a, **kwargs):
    #import pdb; pdb.set_trace()
    return tuple([ai for ai in a.flat])


def disp(*args):
    print(args)


def eig(a):
    u, v = np.linalg.eig(a)
    return u.T


def logical_not(a):
    return np.logical_not(a)


def logical_and(a, b):
    return np.logical_and(a, b)


def logical_or(a, b):
    return np.logical_or(a, b)


def false(*args):
    if not args:
        return False  # or matlabarray(False) ???
    if len(args) == 1:
        args += args
    return np.zeros(args, dtype=bool, order="F")


def find(a, n=None, d=None, nargout=1):
    if d:
        raise NotImplementedError

    # there is no promise that nonzero or flatnonzero
    # use or will use indexing of the argument without
    # converting it to array first.  So we use asarray
    # instead of asanyarray
    if nargout == 1:
        i = np.flatnonzero(np.asarray(a)).reshape(1, -1)+1
        if n is not None:
            i = i.take(n)
        return matlabarray(i)
    if nargout == 2:
        i, j = np.nonzero(np.asarray(a))
        if n is not None:
            i = i.take(n)
            j = j.take(n)
        return (matlabarray((i+1).reshape(-1, 1)),
                matlabarray((j+1).reshape(-1, 1)))
    raise NotImplementedError


def floor(a):
    return int(np.floor(a))


# implemented in "scripts/set/intersect.m"
#def intersect(a,b,nargout=1):
#    if nargout == 1:
#        c = sorted(set(a) & set(b))
#        if isinstance(a,str):
#            return "".join(c)
#        elif isinstance(a,list):
#            return c
#        else:
#            # FIXME: the result is a column vector if
#            # both args are column vectors; otherwise row vector
#            return np.array(c)
#    raise NotImplementedError
#


def iscellstr(a):
    # TODO return isinstance(a,cellarray) and all(ischar(t) for t in a.flat)
    return isinstance(a, cellarray) and all(isinstance(t, str) for t in a.flat)


def ischar(a):
    try:
        return a.dtype == "|S1"
    except AttributeError:
        return False
# ----------------------------------------------------


def isempty(a):
    try:
        return 0 in np.asarray(a).shape
    except AttributeError:
        return False


def isequal(a, b):
    return np.array_equal(np.asanyarray(a),
                          np.asanyarray(b))


def isfield(a, b):
    return str(b) in a.__dict__.keys()


def ismatrix(a):
    return True


def isnumeric(a):
    return np.asarray(a).dtype in (int, float)


def isscalar(a):
    """np.isscalar returns True if a.__class__ is a scalar
    type (i.e., int, and also immutable containers str and
    tuple, but not list.) Our requirements are different"""
    try:
        return a.size == 1
    except AttributeError:
        return np.isscalar(a)





try:
    def load(a):
        return loadmat(a)  # FIXME
except:
    pass


def max(a, d=0, nargout=0):
    if d or nargout:
        raise NotImplementedError
    return np.amax(a)


def min(a, d=0, nargout=0):
    if d or nargout:
        raise NotImplementedError
    return np.amin(a)


def mod(a, b):
    try:
        return a % b
    except ZeroDivisionError:
        return a


def ndims(a):
    return np.asarray(a).ndim


def numel(a):
    return np.asarray(a).size


def ones(*args, **kwargs):
    if not args:
        return 1
    if len(args) == 1:
        args += args
    return matlabarray(np.ones(args, order="F", **kwargs))

#def primes2(upto):
#    primes=np.arange(2,upto+1)
#    isprime=np.ones(upto-1,dtype=bool)
#    for factor in primes[:int(math.sqrt(upto))]:
#        if isprime[factor-2]: isprime[factor*2-2::factor]=0
#    return primes[isprime]
#
#def primes(*args):
#    return _primes.primes(*args)


def qr(a):
    return matlabarray(_qr(np.asarray(a)))


def rand(*args, **kwargs):
    if not args:
        return np.random.rand()
    if len(args) == 1:
        args += args
    try:
        return np.random.rand(np.prod(args)).reshape(args, order="F")
    except:
        pass


def assert_(a, b=None, c=None):
    if c:
        if c >= 0:
            assert (abs(a-b) < c).all()
        else:
            assert (abs(a-b) < abs(b*c)).all()
    elif b is None:
        assert a
    else:
        #assert isequal(a,b),(a,b)
        #assert not any(a-b == 0)
        assert (a == b).all()


def shared(a):
    pass


def rand(*args, **kwargs):
    """from core aka libsmop.py"""
    return np.random.rand()
    # if not args:
    #     return np.random.rand()
    # if len(args) == 1:
    #     args += args
    # try:
    #     return np.random.rand(np.prod(args)).reshape(args,order="F")
    # except:
    #     pass


def randn(*args, **kwargs):
    if not args:
        return np.random.randn()
    if len(args) == 1:
        args += args
    try:
        return np.random.randn(np.prod(args)).reshape(args, order="F")
    except:
        pass


def ravel(a):
    return np.asanyarray(a).reshape(-1, 1)


def roots(a):
    return matlabarray(np.roots(np.asarray(a).ravel()))


def round(a):
    return np.round(np.asanyarray(a))


def rows(a):
    return np.asarray(a).shape[0]


def schur(a):
    return matlabarray(_schur(np.asarray(a)))


def size(a, b=0, nargout=1):
    """
    >>> size(zeros(3,3)) + 1
    matlabarray([[4, 4]])
    """
    s = np.asarray(a).shape
    if s is ():
        return 1 if b else (1,)*nargout
    # a is not a scalar
    try:
        if b:
            return s[b-1]
        else:
            return matlabarray(s) if nargout <= 1 else s
    except IndexError:
        return 1


def size_equal(a, b):
    if a.size != b.size:
        return False
    for i in range(len(a.shape)):
        if a.shape[i] != b.shape[i]:
            return False
    return True



def strcmp(a, b):
    return str(a) == str(b)


def strread(s, format="", nargout=1):
    if format == "":
        a = [float(x) for x in s.split()]
        return tuple(a) if nargout > 1 else np.asanyarray([a])
    raise NotImplementedError


def strrep(a, b, c):
    return str(a).replace(str(b), str(c))


def sum(a, dim=None):
    if dim is None:
        return np.asanyarray(a).sum()
    else:
        return np.asanyarray(a).sum(dim-1)


def toupper(a):
    return char(str(a.data).upper())


true = True



def true(*args):
    if len(args) == 1:
        args += args
    return matlabarray(np.ones(args, dtype=bool, order="F"))


def version():
    return char('0.29')


def zeros(*args, **kwargs):
    if not args:
        return 0.0
    if len(args) == 1:
        args += args
    return matlabarray(np.zeros(args, **kwargs))


def isa(a, b):
    return True


def print_usage():
    raise Exception


def function(f):
    def helper(*args, **kwargs):
        helper.nargin = len(args)
        helper.varargin = cellarray(args)
        return f(*args, **kwargs)
    return helper


def isreal(a):
    return True


eps = np.finfo(float).eps


#print(np.finfo(np.float32).eps)

#if __name__ == "__main__":
#    import doctest
#    doctest.testmod()

# vim:et:sw=4:si:tw=60
