from typing import Callable, Any, TypeVar

R = TypeVar('R')
CR = Callable[..., R]

def extend(cls: Any) -> Callable[[CR], CR]:
    def decorate(f: CR) -> CR:
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
