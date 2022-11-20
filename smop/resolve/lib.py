

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


'''
@extend(node.ident)
def _lhs_resolve(self: node.ident, symtab: SymTab):
    symtab[self.name] = [self]
'''


@extend(node.expr)
def _resolve(self: node.expr, symtab: SymTab):

    if self.op == '.':
        assert len(self.args) == 2, 'resolve field expr len %d' % len(self.args)

        sid = self.args[0]
        sfl = self.args[1]

        sid._resolve(symtab)
        sfl._resolve(symtab)

        if isinstance(self.args[0], node.ident):
            rec = symtab.find_or_create(sid.name)
            rec.add_feature(sfl)
        else:
            pass  # TODO
        return
    elif self.op == '[]':
        raise Exception('NIE')

    for n in self.args:
        n._resolve(symtab)


@extend(node.let)
def _resolve(self: node.node, symtab: SymTab):
    self.ret._resolve(symtab)
    self.args._resolve(symtab)


"""

@extend(node.let)
def _lhs_resolve(self: node.node, symtab: SymTab):
    self.args._resolve(symtab)
    self.ret._lhs_resolve(symtab)


@extend(node.setfield)  # a subclass of funcall
def _resolve(self: node.node, symtab: Symtab):
    self.func_expr._resolve(symtab)
    self.args._resolve(symtab)
    self.args[0]._lhs_resolve(symtab)
"""


'''
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

'''


@extend(node.expr_stmt)
def _resolve(self: node.node, symtab: SymTab):
    self.expr._resolve(symtab)


@extend(node.for_stmt)
def _resolve(self: node.node, symtab: SymTab):
    symtab_copy = SymTab(outer=symtab)
    self.ident._resolve(symtab_copy)
    self.expr._resolve(symtab)
    self.stmt_list._resolve(symtab_copy)
    self.stmt_list._resolve(symtab_copy)  # 2nd time, intentionally
    # Handle the case where FOR loop is not executed

    # What the hell is this?
    # for k, v in symtab_copy.items():
    #     symtab.setdefault(k, []).append(v)


@extend(node.where_stmt)  # FIXME where_stmt ???
@extend(node.while_stmt)
def _resolve(self: node.node, symtab: SymTab):
    self.cond_expr._resolve(symtab)
    self.stmt_list._resolve(symtab)
    self.cond_expr._resolve(symtab)
    self.stmt_list._resolve(symtab)
    # Handle the case where WHILE loop is not executed
    # for k, v in symtab_copy.items():
    #     symtab.setdefault(k, []).append(v)


@extend(node.if_stmt)
def _resolve(self: node.node, symtab: SymTab):
    # symtab_copy = copy_symtab_dict(symtab)
    self.cond_expr._resolve(symtab)
    self.then_stmt._resolve(symtab)
    if self.else_stmt:
        self.else_stmt._resolve(symtab)
    # for k, v in symtab_copy.items():
    #     symtab.setdefault(k, []).append(v)


@extend(node.try_catch)
def _resolve(self: node.node, symtab: SymTab):
    self.try_stmt._resolve(symtab)
    self.catch_stmt._resolve(symtab)  # ???

# function


@extend(node.func_stmt)
def _resolve(self: node.func_stmt, symtab: SymTab):
    symtab_inner = SymTab(outer=symtab)
    if self.ident:
        self.ident._resolve(symtab)
        rec = symtab.find_or_create(self.ident.name)
        rec.add_feature(FEATURE_IS_FUNC)

    # build args
    self.args._resolve(symtab_inner)
    if self.use_nargin:
        symtab_inner.create('nargin').add_ident(
            node.ident(name='nargin', lineno=-1, lexpos=-1, column=-1)
        )
    if self.use_varargin:
        symtab_inner.create('varargin').add_ident(
            node.ident(name='varargin', lineno=-1, lexpos=-1, column=-1)
        )

    if self.stmt_list:
        self.stmt_list._resolve(symtab_inner)
    self.ret._resolve(symtab_inner)


@extend(node.func_args)
def _resolve(self: node.node, symtab: SymTab):
    # TODO, FIXME
    print("TODO func_args _resolve")


# class def


@extend(node.classdef_stmt)
def _resolve(self: node.node, symtab: SymTab):
    self.name._resolve(symtab)
    if self.attrs:
        self.attrs._resolve(symtab)
    self.super._resolve(symtab)

    symtab_inner = SymTab(outer=symtab)
    self.sub._resolve(symtab_inner)


@extend(node.class_props)
def _resolve(self: node.class_props, symtab: SymTab):
    pass  # TODO expr_stmt


@extend(node.class_methods)
def _resolve(self: node.class_methods, symtab: SymTab):
    pass  # TODO func_stmt


@extend(node.class_events)
def _resolve(self: node.class_events, symtab: SymTab):
    pass  # TODO since we haven't met any class events, postpone it

# TODO


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
