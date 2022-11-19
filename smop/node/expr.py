from smop.node.base import *

########################## EXPR

class expr(node, recordtype("expr", "op args")):
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
    def __str__(self):
        return ",".join([str(t) for t in self])

    def __repr__(self):
        return "expr_list(%s)" % list.__repr__(self)


@extend(expr_list)
def is_const(self):
    return all(t.is_const() for t in self)
