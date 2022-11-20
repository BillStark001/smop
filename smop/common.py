from typing import Callable, Any, TypeVar
from typing_extensions import Protocol

R = TypeVar('R')
T = TypeVar('T')
CR = Callable[[T], R]

class ExtensionFunction(Protocol):
    def __call__(self, arg1: T, *args, **kwargs) -> R: ...

def extend(cls: T) -> Callable[[ExtensionFunction], ExtensionFunction]:
    def decorate(f: ExtensionFunction) -> ExtensionFunction:
        setattr(cls, f.__name__, f)
        return f
    return decorate


def exceptions(f):
    return f

    def wrapper(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except:
            print("%s.%s()" % (self.__class__.__name__, f.__name__))
            raise
    wrapper.__name__ = f.__name__
    wrapper.__doc__ = f.__doc__
    return wrapper
