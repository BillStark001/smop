from smop.node.base import *
from smop.node.stmt import *
from smop.node.types import expr, expr_list, ident


class func_stmt(stmt, recordtype("func_stmt",
                                 """
                                ident
                                ret
                                args
                                modif
                                stmt_list
                                decorator_list
                                use_nargin
                                use_varargin
                                """,
                                 default=None)):
    pass

class lambda_expr(func_stmt):
    pass

class func_superclass_handle(expr):
    def __init__(self, name, cname):
        super().__init__(op="@", args=expr_list([name, cname]))
    pass

# function argument restriction related

class func_arg_restr(stmt, recordtype("func_arg_restr", "name dim cls val defVal")):
    name: ident
    cls: ident
    
    pass

class func_args(stmt, recordtype("func_args", "modif restrs extstmt")):
    pass
