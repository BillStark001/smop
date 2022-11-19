from smop.node.base import *
from smop.node.stmt import *
from smop.node.types import expr, expr_list


class func_stmt(stmt, recordtype("func_stmt",
                                 """
                                ident
                                ret
                                args
                                modif
                                stmt_list
                                use_nargin
                                use_varargin
                                """,
                                 default=None)):
    pass

class lambda_expr(func_stmt):
    pass

class function(stmt, recordtype("function", "head body")):
    pass

class func_superclass_handle(expr):
    def __init__(self, name, cname):
        super().__init__(op="@", args=expr_list([name, cname]))
    pass

# function argument restriction related

class func_arg_restr(stmt, recordtype("func_arg_restr", "dim cls val defVal")):
    pass

class func_args(stmt, recordtype("func_args", "modif restrs")):
    pass
