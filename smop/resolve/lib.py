

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


@extend(node.stmt_list)
def _resolve(self: node.node, symtab: SymTab):
    for stmt in self:
        stmt._resolve(symtab)


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
    self.decorator_list = self.decorator_list or []
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
        for stmt in self.stmt_list:
            if isinstance(stmt, node.func_args):
                stmt._resolve(symtab_inner, self)
            else:
                stmt._resolve(symtab_inner)
    self.ret._resolve(symtab_inner)


@extend(node.func_args)
def _resolve(self: node.func_args, symtab: SymTab, func: node.func_stmt):
    
    assert func is not None, 'func_args._resolve: A function statement is necessary for the resolution.'
    self.extstmt = self.extstmt or node.stmt_list()
    
    # parse argument attributes
    repeat_flag = False
    output_flag = False
    input_flag = False
    if self.modif:
        for mdf in self.modif:
            assert isinstance(mdf, node.ident)
            if mdf.name == 'Repeating':
                repeat_flag = True
            elif mdf.name == 'Output':
                output_flag = True
            elif mdf.name == 'Input':
                input_flag = True
    assert not (input_flag and output_flag), 'Input and Output keywords cannot appear at the same time.'
    
    # generate native argument table
    args: Dict[str, node.ident] = {}
    if output_flag:
        if isinstance(func.ret, node.ident):
            args[func.ret.name] = func.ret
        elif isinstance(func.ret, node.expr_list):
            for arg in func.ret:
                assert isinstance(arg, node.ident)
                args[arg.name] = arg
    else:
        for arg in func.args:
            assert isinstance(arg, node.ident)
            args[arg.name] = arg
            
    
    if repeat_flag:
        # TODO
        self.extstmt.append(node.comment_stmt(f'Repeating Arguments'))
            
    # get target
    tgt_lst = self.restrs if not isinstance(self.restrs, node.func_arg_restr) else [self.restrs]
    
    for arg in tgt_lst:
        if isinstance(arg, node.ident):
            continue
        assert isinstance(arg, node.func_arg_restr), str(type(arg)) + ' ' + str(type(self.restrs))
        assert arg.name.name in args, 'unexpected arg ident literal: %s' % arg.name.name
        ident = args[arg.name.name]
        if arg.cls:
            ident.dtype = arg.cls
        if arg.defVal:
            ident.init = arg.defVal
        if arg.val:
            self.extstmt.append(node.comment_stmt(f'# {arg.name}: {arg.val}'))
        if arg.dim:
            self.extstmt.append(node.comment_stmt(f'# {arg.name}: ({arg.dim})'))
        
    if output_flag:
        # TODO deal with returns' type, default value, validator, dimension
        for _, ident in args.items():
            if ident.dtype or ident.init:
                ret = node.let(
                    ret=node.ident(ident.name), 
                    args=ident.init if ident.init else node.ident('None'), 
                    dtype=ident.dtype)
                ident.dtype = None
                ident.init = None
                self.extstmt.append(ret)
        pass
    
    self.extstmt._resolve(symtab)


# class def
# TODO

@extend(node.func_stmt)
def _pre_resolve_classmethod(self: node.func_stmt, cls: node.classdef_stmt, symtab: SymTab):
    if self.ident.name == cls.name.name:
        self.ident.name = '__init__'
        ret = self.ret
        if isinstance(ret, node.expr_list):
            assert len(ret) == 1
            ret = ret[0]
        assert isinstance(ret, node.ident)
        
        self.ret = node.expr_list()
        self.args.insert(0, ret)

@extend(node.classdef_stmt)
def _resolve(self: node.node, symtab: SymTab):
    self.name._resolve(symtab)
    if self.attrs:
        self.attrs._resolve(symtab)
    self.super._resolve(symtab)

    # rename functions
    for s in self.sub:
        if isinstance(s, node.class_methods):
            for f in s.stmt_list:
                if isinstance(f, node.func_stmt):
                    f._pre_resolve_classmethod(self, symtab)

    symtab_inner = SymTab(outer=symtab)
    self.sub._resolve(symtab_inner)


@extend(node.class_props)
def _resolve(self: node.class_props, symtab: SymTab):
    for stmt in self.stmt_list:
        if not isinstance(stmt, node.expr_stmt):
            continue
        assert isinstance(stmt.expr, node.expr_list)
        for expr in stmt.expr:
            if isinstance(expr, node.ident):
                expr.init = node.ident('None')
    self.stmt_list._resolve(symtab)


@extend(node.class_methods)
def _resolve(self: node.class_methods, symtab: SymTab):
    # TODO func_stmt
    self.stmt_list._resolve(symtab)


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
