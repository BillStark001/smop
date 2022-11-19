import copy
from smop.recipes import recordtype
from collections import namedtuple

# def preorder(u):
#     if isinstance(u,traversable):
#         yield u
#         for n in u:
#             for t in preorder(n):
#                 yield t

def decode(self):
    r = ""
    s = self.name
    while s:
        if len(s) >= 2 and s[0] == "_":
            r += s[1].upper()
            s = s[2:]
        else:
            r += s[0].lower()
            s = s[1:]
    return r

def encode(s):
    return "".join(c+"_" if c.isupper() or c=="_" else c.upper() for c in s)

def postorder(u):
    if isinstance(u,node):
        for v in u:
            for t in postorder(v):
                yield t
        yield u # returns only traversible objects

def extend(cls):
    return lambda f: (setattr(cls,f.__name__,f) or f)

def exceptions(f):
    return f
    def wrapper(self,*args,**kwargs):
        try:
            return f(self,*args,**kwargs)
        except:
            print("%s.%s()" % (self.__class__.__name__, f.__name__))
            raise
    wrapper.__name__ = f.__name__
    wrapper.__doc__ = f.__doc__
    return wrapper

class node(object):
    def become(self,other):
        class Wrapper(self.__class__):
            def __copy__(self):
                other = object.__getattribute__(self,"other")
                return copy.copy(other)
            def __getattribute__(self,name):
                other = object.__getattribute__(self,"other")
                return getattr(other,name)
            def __setattr__(self,name,value):
                other = object.__getattribute__(self,"other")
                return setattr(other,name,value)
            def __iter__(self):
                other = object.__getattribute__(self,"other")
                return iter(other)
            #def __hash__(self):
            #    other = object.__getattribute__(self,"other")
            #    return id(other)
            def __repr__(self):
                other = object.__getattribute__(self,"other")
                return repr(other)
            def __len__(self):
                other = object.__getattribute__(self,"other")
                return len(other)
        assert self != other
        self.other = other
        self.__class__ = Wrapper

    def _type(self):
        raise AttributeError("_type")


@extend(node)
def is_const(self):
    return False