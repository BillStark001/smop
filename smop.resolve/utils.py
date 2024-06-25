import networkx as nx

from smop.resolve.base import *

# network


def as_networkx(t: node.node) -> nx.DiGraph:
    G = nx.DiGraph()
    for u in node.postorder(t):
        if u.__class__ in (node.ident, node.param):
            uu = "%s_%s_%s" % (u.name, u.lineno, u.column)
            # label = "%s\\n%s" % (uu, u.props if u.props else "")
            G.add_node(uu, ident=u)
            if u.defs:
                for v in u.defs:
                    if v.__class__ is node.ident:
                        vv = "%s_%s_%s" % (v.name, v.lineno, v.column)
                        G.add_node(vv, ident=v)
                        if u.lexpos < v.lexpos:
                            G.add_edge(uu, vv, color="red")
                        else:
                            G.add_edge(uu, vv, color="black")
    return G



# rewrite


'''

def peep(parsetree):
    for u in parsetree:
        to_arrayref(u)
        colon_indices_and_expressions(u)
        end_expressions(u)
        let_statement(u)



def end_expressions(u):
    if u.__class__ in (node.arrayref, node.cellarrayref):
        if w.__class__ is node.expr and w.op == "end":
            w.args[0] = u.func_expr
            w.args[1] = node.number(i)  # FIXME
            
'''

def to_arrayref(u):
    """
    To the parser, funcall is indistinguishable
    from rhs array reference.  But LHS references
    can be converted to arrayref nodes.
    """
    if u.__class__ is node.funcall:
        try:
            if u.func_expr.props in "UR":  # upd,ref
                u.__class__ = node.arrayref
        except:
            pass  # FIXME


def colon_subscripts(u):
    """
    Array colon subscripts foo(1:10) and colon expressions 1:10 look
    too similar to each other.  Now is the time to find out who is who.
    """
    if u.__class__ in (node.arrayref, node.cellarrayref):
        for w in u.args:
            if w.__class__ is node.expr and w.op == ":":
                w._replace(op="::")


def let_statement(u):
    """
    If LHS is a plain variable, and RHS is a matrix
    enclosed in square brackets, replace the matrix
    expr with a funcall.
    """
    if u.__class__ is node.let:
        if (u.ret.__class__ is node.ident and
                u.args.__class__ is node.matrix):
            u.args = node.funcall(func_expr=node.ident("matlabarray"),
                                  args=node.expr_list([u.args]))
