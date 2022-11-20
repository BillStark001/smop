from typing import List, Optional

from smop.node.base import *

########################## EXPR

# recordtype("expr", "op args")
class expr(node):
    op: str
    args: 'expr_list'
    
    def __init__(self, op: str, args: 'expr_list'):
        assert op is not None and op.strip() != '', 'empty operator'
        assert isinstance(args, expr_list), 'bad argument type'
        self.op = op
        self.args = args
        
    
    def __str__(self):
        if self.op == ".":
            return "%s%s" % (str(self.args[0]), self.args[1])
        if self.op == "parens":
            return "(%s)" % str(self.args[0])
        if not self.args:
            return str(self.op)
        if len(self.args) == 1:
            return "%s%s" % (self.op, self.args[0])
        if len(self.args) == 2:
            return "%s%s%s" % (self.args[0]._backend(),
                               self.op,
                               self.args[1]._backend())
        ret = "%s=" % str(self.ret) if self.ret else ""
        return ret+"%s(%s)" % (self.op,
                               ",".join([str(t) for t in self.args]))


class expr_list(node, list):
    
    def assert_len(self, l: int, info: Optional[str] = None):
        assert len(self) == l, info or 'wrong length: %d' % len(self)
    
    def __str__(self):
        return ", ".join([str(t) for t in self])

    def __repr__(self):
        return "expr_list(%s)" % list.__repr__(self)


@extend(expr_list)
def is_const(self):
    return all(t.is_const() for t in self)
