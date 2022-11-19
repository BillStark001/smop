from smop.node.base import *
from smop.node.expr import *

#####################
#
#  ATOMS

class atom(node):
    pass

class string(atom, recordtype("string", "value lineno lexpos", default=None)):
    def __str__(self):
        return "'%s'" % self.value

class logical(atom, recordtype("logical", "value lineno lexpos", default=None)):
    pass

class number(atom, recordtype("number", "value lineno lexpos", default=None)):
    def __str__(self):
        return str(self.value)

class ident(atom, recordtype("ident", "name lineno column lexpos defs props init",
                             default=None)):
    def __str__(self):
        return self.name

class param(ident):
    pass

# structs

class concat_list(node,list):
    pass

class global_list(node,list):
    """space-separated list of variables used in GLOBAL statement"""
    pass

#######################################333
#
# FUNCALL

class funcall(node,recordtype("funcall","func_expr args nargout",default=None)):
    """Funcall instances represent 
    (a) Array references, both lhs and rhs
    (b) Function call expressions
    """
    def __str__(self):
        return "%s(%s)" % (str(self.func_expr),
                           str(self.args))

class builtins(funcall):
    """
    Builtin functions are represented as subclasses
    of class builtins.  Application of a function to
    specific arguments is represented as its instance.
    For example, builtin function foo is represented
    as class foo(builtins), and foo(x) is represented
    as foo(x).
    """

    def __init__(self,*args,**kwargs):
        """
        If a built-in function _foo takes three arguments
        a, b, and c, we can just say _foo(a,b,c) and let
        the constructor take care of proper structuring of
        the node (like expr_list around the arguments, etc.
        """
        funcall.__init__(self,
             func_expr=None,
             args=expr_list(args),
             **kwargs)
        #import pdb; pdb.set_trace()
        #self.func_expr.defs = set(self.func_expr)

    def __repr__(self):
        return "np.%s%s" % (self.__class__,repr(self.args))

    def __str__(self):
        return "np.%s(%s)" % (self.__class__.__name__,
                              str(self.args))

class arrayref(funcall):
    def __repr__(self):
        return "%s%s[%s]" % (self.__class__, 
                             self.func_expr,
                             self.args)


# names in caps correspond to fortran funcs
builtins_list = [
#    "ABS",
#    "ALL",
#    "ANY",
#    "CEILING",
#    "FIND",
#    "ISNAN",
#    "MAXVAL",
#    "MINVAL",
#    "MODULO",
#    "RAND",
#    "RESHAPE",
#    "SHAPE",
#    "SIGN",
#    "SIZE",
#    "SUM",

    #"abs",
    "add", # synthetic opcode
    #"all",
    #"any",
    "cellfun",
    #"ceil",
    "clazz",
    #"cumprod",
    #"cumsum",
    #"diff",
    #"dot",      # Exists in numpy. Implements matlab .*
    #"exist",
    "false",
    #"fclose",
    #"find",
    #"findone",  # same as find, but returns ONE result
    #"floor",
    #"fopen",
    "getfield",
    "inf", "inf0",
    #"isempty",
    #"isequal",
    "isinf",
    "isnan",
    #"length",
    #"load",
    #"lower",
    #"max",
    #"min",
    #"mod",
    #"nnz",
    #"numel",
    #"ones",
    #"rand",
    #"range_",   # synthetic opcode
    "ravel",   # synthetic opcode
    #"rem",
    #"save",
    "setfield",
    #"sign",
    #"size",
    #"sort",
    #"strcmp",
    #"strcmpi",
    "sub", # synthetic opcode for subtract
    #"sum",
    "transpose",
    #"true",
    #"zeros",
]

for name in builtins_list:
    globals()[name] = type(name, (builtins,), {})

#class cellarrayref(node,recordtype("cellarrayref","ident args")):
class cellarrayref(funcall):
    pass

class cellarray(expr):
    pass

class matrix(builtins):
    """
    Anything enclosed in square brackets counts as matrix
    >>> print matrix([1,2,3])
    [1,2,3]
    >>> print matrix()
    []
    """
#    def __init__(self,args=expr_list()):
#        expr.__init__(self,op="[]",args=args)
#    def __str__(self):
#        return "[%s]" % ",".join([str(t) for t in self.args])

@extend(number)
@extend(string)
def is_const(self):
    return True
@extend(matrix)
def is_const(self):
    return not self.args or self.args[0].is_const()
# vim: ts=8:sw=4:et