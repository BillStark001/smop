from smop.node.base import *

from typing import Optional, List

###########################
#
#  STATEMENTS
#


class stmt(node):
    pass


class stmt_list(node, list):
    def __str__(self):
        return "\n".join([str(t) for t in self])

    def __repr__(self):
        return "stmt_list(%s)" % list.__repr__(self)

    def append(self, s):
        assert isinstance(s, node), s.__class__
        list.append(self, s)


# class call_stmt(stmt,recordtype("call_stmt","func_expr args ret")):
#     """Sometimes called multiple assignment, call statements represent
#     something like [x,y]=foo(a,b,c); Note the square brackets around
#     the lhs.
#     SEE ALSO: funcall,let
#     """
#     def __str__(self):
#         return "%s=%s(%s)" % (str(self.ret),
#                               str(self.func_expr),
#                               str(self.args))

# recordtype("let", "ret args lineno lexpos nargout", default=None)
class let(stmt):
    """
    Assignment statement, except [x,y] = foo(x,y,z),
    which is handled by call_stmt.
    """

    def __init__(self, ret: node, args: node, 
                 lineno: int = -1, lexpos: int = -1, nargout: int = -1):
        self.ret = ret
        self.args = args
        self.lineno = lineno
        self.lexpos = lexpos
        self.nargout = nargout

    def __str__(self):
        return "%s = %s" % (str(self.ret), str(self.args))


class for_stmt(stmt, recordtype("for_stmt", "ident expr stmt_list")):
    pass


class DO_STMT(stmt, recordtype("DO_STMT", "ident start stop stmt_list")):
    pass

# We generate where_stmt to implement A(B==C) = D


class where_stmt(stmt, recordtype("where_stmt", "cond_expr stmt_list")):
    pass


class if_stmt(stmt, recordtype("if_stmt", "cond_expr then_stmt else_stmt")):
    pass


class global_stmt(stmt, recordtype("global_stmt", "global_list")):
    def __str__(self):
        return "global %s" % str(self.global_list)


class persistent_stmt(stmt, recordtype("persistent_stmt", "global_list")):
    def __str__(self):
        return "global %s" % str(self.global_list)


class return_stmt(stmt, namedtuple("return_stmt", "")):
    def __str__(self):
        return "return"


class comment_stmt(stmt, namedtuple("comment_stmt", "value")):
    def __str__(self):
        return self.value


class end_stmt(stmt, namedtuple("end_stmt", "dummy")):
    def __str__(self):
        return "end"


class continue_stmt(stmt, namedtuple("continue_stmt", "dummy")):
    def __str__(self):
        return "continue"


class break_stmt(stmt, namedtuple("break_stmt", "dummy")):
    def __str__(self):
        return "break"


class pass_stmt(stmt, namedtuple("pass_stmt", "")):
    def __str__(self):
        return "pass"


class null_stmt(stmt, namedtuple("null_stmt", "")):
    def __str__(self):
        return ";"


class expr_stmt(stmt, node, recordtype("expr_stmt", "expr")):
    expr: node
    def __str__(self):
        return str(self.expr)


class while_stmt(stmt, node, recordtype("while_stmt", "cond_expr stmt_list")):
    pass


class try_catch(stmt, recordtype("try_catch", "try_stmt catch_stmt finally_stmt")):
    pass


class allocate_stmt(stmt, recordtype("allocate_stmt",
                                     "ident args")):
    pass
