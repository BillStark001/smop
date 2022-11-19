from smop.node.base import *
from smop.node.stmt import *


class func_stmt(stmt, recordtype("func_stmt",
                                 """
                                ident
                                ret
                                args
                                modif
                                stmt_list
                                use_nargin
                                """,
                                 default=None)):
    pass

class lambda_expr(func_stmt):
    pass

class function(stmt, recordtype("function", "head body")):
    pass


# function argument restriction related

class func_arg_restr(stmt, recordtype("func_arg_restr", "dim cls val defVal")):
    pass

class func_args(stmt, recordtype("func_args", "modif restrs")):
    pass
