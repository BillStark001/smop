from smop.resolve.base import *
from smop.resolve.symtab import *
from smop.resolve.utils import *

def do_resolve(t, symtab: SymTab):
    return t._resolve(symtab=symtab)

def resolve(
    t: node.node, 
    symtab: Optional[SymTab] = None) -> nx.DiGraph:
    
    if symtab is None:
        symtab = SymTab()
        
    do_resolve(t, symtab)
    
    G = as_networkx(t)
    for n in G.nodes():
        
        u = G.nodes[n]["ident"]
        if u.props:
            pass
        elif G.out_edges(n) and G.in_edges(n):
            u.props = "U"  # upd
        elif G.in_edges(n):
            u.props = "D"  # def
        elif G.out_edges(n):
            u.props = "R"  # ref
        else:
            u.props = "F"  # ???
        G.nodes[n]["label"] = "%s\\n%s" % (n, u.props)
    return G