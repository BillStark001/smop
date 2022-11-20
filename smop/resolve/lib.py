

from smop.resolve.base import *
from smop.resolve.symtab import *


@extend(node.ident)
def _resolve(self: node.ident, symtab: SymTab):
    rec = symtab.find_or_create(self.name)
    rec.add_ident(self)
    '''
    if self.defs is None:
        self.defs = []
    try:
        self.defs += symtab[self.name]
    except KeyError:
        # defs == set() means name used, but not defined
        pass
    '''
    

@extend(node.ident)
def _lhs_resolve(self: node.ident, symtab: SymTab):
    symtab[self.name] = [self]



@extend(node.expr)
def _resolve(self: node.node, symtab: SymTab):
    
    if self.op == '.':
        pass
    
    for expr in self.args:
        expr._resolve(symtab)


@extend(node.expr)
def _lhs_resolve(self: node.expr, symtab: SymTab):
    if self.op == ".":  # see setfield
        self.args._resolve(symtab)
        self.args[0]._lhs_resolve(symtab)
    elif self.op == "[]":
        for arg in self.args:
            arg._lhs_resolve(symtab)



@extend(node.arrayref)
@extend(node.cellarrayref)
@extend(node.funcall)
def _lhs_resolve(self: node.node, symtab: SymTab):
    # Definitely lhs array indexing.  It's both a ref and a def.
    # Must properly handle cases such as foo(foo(17))=42
    # Does the order of A and B matter?
    self.func_expr._resolve(symtab)  # A
    self.args._resolve(symtab)      # B
    self.func_expr._lhs_resolve(symtab)




@extend(node.expr_stmt)
def _resolve(self: node.node, symtab: SymTab):
    self.expr._resolve(symtab)


@extend(node.for_stmt)
def _resolve(self: node.node, symtab: SymTab):
    symtab_copy = copy_symtab_dict(symtab)
    self.ident._lhs_resolve(symtab)
    self.expr._resolve(symtab)
    self.stmt_list._resolve(symtab)
    self.stmt_list._resolve(symtab)  # 2nd time, intentionally
    # Handle the case where FOR loop is not executed
    for k, v in symtab_copy.items():
        symtab.setdefault(k, []).append(v)


@extend(node.func_stmt)
def _resolve(self: node.node, symtab: SymTab):
    if self.ident:
        self.ident._resolve(symtab)
    self.args._lhs_resolve(symtab)
    self.ret._resolve(symtab)


@extend(node.global_list)
@extend(node.concat_list)
@extend(node.expr_list)
def _lhs_resolve(self: node.node, symtab: SymTab):
    for expr in self:
        expr._lhs_resolve(symtab)


@extend(node.global_list)
@extend(node.concat_list)
@extend(node.expr_list)
def _resolve(self: node.node, symtab: SymTab):
    for expr in self:
        expr._resolve(symtab)


@extend(node.global_stmt)
def _resolve(self: node.node, symtab: SymTab):
    self.global_list._lhs_resolve(symtab)



@extend(node.if_stmt)
def _resolve(self: node.node, symtab: SymTab):
    symtab_copy = copy_symtab_dict(symtab)
    self.cond_expr._resolve(symtab)
    self.then_stmt._resolve(symtab)
    if self.else_stmt:
        self.else_stmt._resolve(symtab_copy)
    for k, v in symtab_copy.items():
        symtab.setdefault(k, []).append(v)


@extend(node.let)
def _lhs_resolve(self: node.node, symtab: SymTab):
    self.args._resolve(symtab)
    self.ret._lhs_resolve(symtab)


@extend(node.let)
def _resolve(self: node.node, symtab: SymTab):
    self.args._resolve(symtab)
    self.ret._lhs_resolve(symtab)


@extend(node.null_stmt)
@extend(node.continue_stmt)
@extend(node.break_stmt)
def _resolve(self: node.node, symtab: SymTab):
    pass

"""
@extend(node.setfield)  # a subclass of funcall
def _resolve(self: node.node, symtab: Symtab):
    self.func_expr._resolve(symtab)
    self.args._resolve(symtab)
    self.args[0]._lhs_resolve(symtab)
"""

@extend(node.try_catch)
def _resolve(self: node.node, symtab: SymTab):
    self.try_stmt._resolve(symtab)
    self.catch_stmt._resolve(symtab)  # ???




@extend(node.arrayref)
@extend(node.cellarrayref)
@extend(node.funcall)
def _resolve(self: node.node, symtab: SymTab):
    # Matlab does not allow foo(bar)(bzz), so func_expr is usually
    # an ident, though it may be a field or a dot expression.
    if self.func_expr:
        self.func_expr._resolve(symtab)
    self.args._resolve(symtab)
    #if self.ret:
    #    self.ret._lhs_resolve(symtab)



# @extend(node.call_stmt)
# def _resolve(self,symtab):
#     # TODO: does the order of A and B matter? Only if the
#     # evaluation of function args may change the value of the
#     # func_expr.
#     self.func_expr._resolve(symtab) # A
#     self.args._resolve(symtab)      # B
#     self.ret._lhs_resolve(symtab)


@extend(node.return_stmt)
def _resolve(self: node.node, symtab: SymTab):
    self.ret._resolve(symtab)
    #symtab.clear()


@extend(node.stmt_list)
def _resolve(self: node.node, symtab: SymTab):
    for stmt in self:
        stmt._resolve(symtab)


@extend(node.where_stmt)  # FIXME where_stmt ???
@extend(node.while_stmt)
def _resolve(self: node.node, symtab: SymTab):
    symtab_copy = copy_symtab_dict(symtab)
    self.cond_expr._resolve(symtab)
    self.stmt_list._resolve(symtab)
    self.cond_expr._resolve(symtab)
    self.stmt_list._resolve(symtab)
    # Handle the case where WHILE loop is not executed
    for k, v in symtab_copy.items():
        symtab.setdefault(k, []).append(v)


@extend(node.function)
def _resolve(self: node.node, symtab: SymTab):
    self.head._resolve(symtab)
    self.body._resolve(symtab)
    self.head.ret._resolve(symtab)


@extend(node.classdef_stmt)
def _resolve(self: node.node, symtab: SymTab):
    if self.name:
        self.name._resolve(symtab)
    if self.attrs:
        self.attrs._resolve(symtab)
    if self.super:
        self.super._resolve(symtab)
    if self.props:
        self.props._resolve(symtab)
    if self.methods:
        self.methods._resolve(symtab)
    if self.events:
        self.events._resolve(symtab)


@extend(node.func_args)
def _resolve(self: node.node, symtab: SymTab):
    # TODO, FIXME
    print("TODO func_args _resolve")
