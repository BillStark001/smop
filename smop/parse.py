# SMOP compiler -- Simple Matlab/Octave to Python compiler
# Copyright 2011-2016 Victor Leikehman

from ply import yacc
from . import lexer
from . lexer import tokens, raise_exception
from . import node
from smop.common import exceptions
from smop.options import options

# ident properties (set in parse.py)
# ----------------------------------
# G global
# P persistent
# A function argument
# F function return value
# I for-loop iteration index
#
# ident properties (set in resolve.py)
# ------------------------------------
# R ref    =...a  or  =...a(b)
# D def    a=...  or   [a,b,c]=...
# U update a(b)=...  or  [a(b) c(d)]=...

precedence = (
    ("right", "COMMA"),
    ("right", "DOTDIVEQ", "DOTMULEQ", "EQ", "EXPEQ", "MULEQ", "MINUSEQ",
     "DIVEQ", "PLUSEQ", "OREQ", "ANDEQ"),
    ("nonassoc", "HANDLE"),
    ("left", "COLON"),
    ("left", "ANDAND", "OROR"),
    ("left", "EQEQ", "NE", "GE", "LE", "GT", "LT"),
    ("left", "OR", "AND"),
    ("left", "PLUS", "MINUS"),
    ("left", "MUL", "DIV", "DOTMUL", "DOTDIV", "BACKSLASH"),
    ("right", "UMINUS", "NEG"),
    ("right", "TRANSPOSE"),
    ("right", "EXP", "DOTEXP", "POW"),
    ("nonassoc", "LPAREN", "RPAREN", "RBRACE", "LBRACE"),
    ("left", "FIELD", "DOT", "PLUSPLUS", "MINUSMINUS"), )

use_nargin = False
use_varargin = False

def p_top(p):
    """
    top :
        | top stmt
      """
    if len(p) == 1:
        p[0] = node.stmt_list()
    else:
        p[0] = p[1]
        p[0].append(p[2])


def p_end(p):
    """
    top : top END_STMT
    """
    p[0] = p[1]


def p_end_function(p):
    """
    top : top END_FUNCTION
    """
    p[0] = p[1]
    p[0].append(node.return_stmt())
    p[0].append(node.comment_stmt("\nif __name__ == '__main__':\n    pass"))


@exceptions
def p_arg1(p):
    """
    arg1 : STRING
         | NUMBER
         | IDENT
         | GLOBAL
    """
    # a hack to support "clear global"
    p[0] = node.string(value=str(p[1]), lineno=p.lineno(1), lexpos=p.lexpos(1))


@exceptions
def p_arg_list(p):
    """
    arg_list : ident_init_opt
             | arg_list COMMA ident_init_opt
    """
    if len(p) == 2:
        p[0] = node.expr_list([p[1]])
    elif len(p) == 4:
        p[0] = p[1]
        p[0].append(p[3])
    else:
        assert 0
    assert isinstance(p[0], node.expr_list)


@exceptions
def p_args(p):
    """
    args : arg1
         | args arg1
    """
    if len(p) == 2:
        p[0] = node.expr_list([p[1]])
    else:
        p[0] = p[1]
        p[0].append(p[2])


@exceptions
def p_break_stmt(p):
    "break_stmt : BREAK SEMI"
    p[0] = node.break_stmt(None)


@exceptions
def p_case_list(p):
    """
    case_list :
              | CASE expr sep stmt_list_opt case_list
              | CASE expr error stmt_list_opt case_list
              | OTHERWISE stmt_list
    """
    if len(p) == 1:
        p[0] = node.stmt_list()
    elif len(p) == 3:
        assert isinstance(p[2], node.stmt_list)
        p[0] = p[2]
    elif len(p) == 6:
        p[0] = node.if_stmt(
            cond_expr=node.expr(
                op="==", args=node.expr_list([p[2]])),
            then_stmt=p[4],
            else_stmt=p[5])
        p[0].cond_expr.args.append(
            None)  # None will be replaced using backpatch()
    else:
        assert 0


@exceptions
def p_cellarray(p):
    """
    cellarray : LBRACE RBRACE
              | LBRACE expr_list RBRACE
              | LBRACE concat_list RBRACE
              | LBRACE concat_list SEMI RBRACE
    """
    if len(p) == 3:
        p[0] = node.cellarray(op="{}", args=node.expr_list())
    else:
        p[0] = node.cellarray(op="{}", args=p[2])


@exceptions
def p_cellarrayref(p):
    """expr : expr LBRACE expr_list RBRACE
            | expr LBRACE RBRACE
    """
    args = node.expr_list() if len(p) == 4 else p[3]
    assert isinstance(args, node.expr_list)
    p[0] = node.cellarrayref(func_expr=p[1], args=args)


@exceptions
def p_command(p):
    """
    command : ident args SEMI
    """
    #    if p[1].name == "load":
    #        # "load filename x" ==> "x=load(filename)"
    #        # "load filename x y z" ==> "(x,y,z)=load(filename)"
    #        ret=node.expr_list([node.ident(t.value) for t in p[2][1:]])
    #        p[0] = node.funcall(func_expr=p[1],
    #                            args=node.expr_list(p[2]),
    #                            ret=ret)
    #    else:
    p[0] = node.funcall(p[1], p[2])


####################


@exceptions
def p_comment_stmt(p):
    """
    comment_stmt : COMMENT
    """
    p[0] = node.comment_stmt(p[1])


@exceptions
def p_concat_list(p):
    """
    concat_list : expr_list SEMI expr_list
                | concat_list SEMI expr_list
    """
    if p[1].__class__ == node.expr_list:
        p[0] = node.concat_list([p[1], p[3]])
    else:
        p[0] = p[1]
        p[0].append(p[3])


@exceptions
def p_continue_stmt(p):
    "continue_stmt : CONTINUE SEMI"
    p[0] = node.continue_stmt(None)


@exceptions
def p_elseif_stmt(p):
    """
    elseif_stmt :
                | ELSE stmt_list_opt
                | ELSEIF expr sep stmt_list_opt elseif_stmt
                | ELSEIF LPAREN expr RPAREN stmt_list_opt elseif_stmt
    """
    if len(p) == 1:
        p[0] = node.stmt_list()
    elif len(p) == 3:
        p[0] = p[2]
    elif len(p) == 6:
        p[0] = node.if_stmt(cond_expr=p[2], then_stmt=p[4], else_stmt=p[5])
    elif len(p) == 7:
        p[0] = node.if_stmt(cond_expr=p[3], then_stmt=p[5], else_stmt=p[6])
    else:
        assert 0


@exceptions
def p_error_stmt(p):
    """
    error_stmt : ERROR_STMT SEMI
    """
    p[0] = node.null_stmt()


@exceptions
def p_expr(p):
    """expr : ident
            | end
            | number
            | string
            | colon
            | NEG
            | matrix
            | cellarray
            | expr2
            | expr1
            | lambda_expr
            | funcall_expr
            | expr PLUSPLUS
            | expr MINUSMINUS
    """
    #        | PLUSPLUS ident
    #        | MINUSMINUS ident
    if p[1] == "~":
        p[0] = node.ident(name="__")
    else:
        p[0] = p[1]


@exceptions
def p_expr1(p):
    """expr1 : MINUS expr %prec UMINUS
             | PLUS expr %prec UMINUS
             | NEG expr
             | HANDLE ident
             | PLUSPLUS ident
             | MINUSMINUS ident
    """
    p[0] = node.expr(op=p[1], args=node.expr_list([p[2]]))


@exceptions
def p_expr2(p):
    """expr2 : expr AND expr
             | expr ANDAND expr
             | expr BACKSLASH expr
             | expr COLON expr
             | expr DIV expr
             | expr DOT expr
             | expr DOTDIV expr
             | expr DOTDIVEQ expr
             | expr DOTEXP expr
             | expr DOTMUL expr
             | expr DOTMULEQ expr
             | expr EQEQ expr
             | expr POW expr
             | expr EXP expr
             | expr EXPEQ expr
             | expr GE expr
             | expr GT expr
             | expr LE expr
             | expr LT expr
             | expr MINUS expr
             | expr MUL expr
             | expr NE expr
             | expr OR expr
             | expr OROR expr
             | expr PLUS expr
             | expr EQ expr
             | expr MULEQ expr
             | expr DIVEQ expr
             | expr MINUSEQ expr
             | expr PLUSEQ expr
             | expr OREQ expr
             | expr ANDEQ expr
    """
    if p[2] == "=":
        if isinstance(p[1], node.let):
            raise_exception(SyntaxError,
                            "Not implemented assignment as expression",
                            new_lexer)
        # The algorithm, which decides if an
        # expression F(X)
        # is arrayref or funcall, is implemented in
        # resolve.py, except the following lines up
        # to XXX. These lines handle the case where
        # an undefined array is updated:
        #    >>> clear a
        #    >>> a[1:10]=123
        # Though legal in matlab, these lines
        # confuse the algorithm, which thinks that
        # the undefined variable is a function name.
        # To prevent the confusion, we mark these
        # nodes arrayref as early as during the parse
        # phase.
        if p[1].__class__ is node.funcall:
            # A(B) = C
            p[1].__class__ = node.arrayref
        elif p[1].__class__ is node.matrix:
            # [A1(B1) A2(B2) ...] = C
            for e in p[1].args:
                if e.__class__ is node.funcall:
                    e.__class__ = node.arrayref
        # XXX

        if isinstance(p[1], node.getfield):
            # import pdb;pdb.set_trace()
            # A.B=C  setfield(A,B,C)
            p[0] = node.setfield(p[1].args[0], p[1].args[1], p[3])
        else:
            # assert len(p[1].args) > 0
            ret = p[1].args if isinstance(p[1], node.matrix) else p[1]
            p[0] = node.let(ret=ret,
                            args=p[3],
                            lineno=p.lineno(2),
                            lexpos=p.lexpos(2))

            if isinstance(p[1], node.matrix):
                # TBD: mark idents as "P" - persistent
                if p[3].__class__ not in (node.ident, node.funcall
                                          ):  # , p[3].__class__
                    raise_exception(SyntaxError,
                                    "multi-assignment",
                                    new_lexer)
                if p[3].__class__ is node.ident:
                    # [A1(B1) A2(B2) ...] = F     implied F()
                    # import pdb; pdb.set_trace()
                    p[3] = node.funcall(func_expr=p[3], args=node.expr_list())
                # [A1(B1) A2(B2) ...] = F(X)
                p[3].nargout = len(p[1].args[0])
    elif p[2] == "*":
        p[0] = node.funcall(
            func_expr=node.ident("dot"), args=node.expr_list([p[1], p[3]]))
    elif p[2] == ".*":
        p[0] = node.funcall(
            func_expr=node.ident("multiply"),
            args=node.expr_list([p[1], p[3]]))

#    elif p[2] == "." and isinstance(p[3],node.expr) and p[3].op=="parens":
#        p[0] = node.getfield(p[1],p[3].args[0])
#        raise SyntaxError(p[3],p.lineno(3),p.lexpos(3))
    elif p[2] == ":" and isinstance(p[1], node.expr) and p[1].op == ":":
        # Colon expression means different things depending on the
        # context.  As an array subscript, it is a slice; otherwise,
        # it is a call to the "range" function, and the parser can't
        # tell which is which.  So understanding of colon expressions
        # is put off until after "resolve".
        p[0] = p[1]
        p[0].args.insert(1, p[3])
    else:
        p[0] = node.expr(op=p[2], args=node.expr_list([p[1], p[3]]))


@exceptions
def p_expr_colon(p):
    "colon : COLON"
    p[0] = node.expr(op=":", args=node.expr_list())


@exceptions
def p_expr_end(p):
    "end : END_EXPR"
    p[0] = node.expr(
        op="end", args=node.expr_list([node.number(0), node.number(0)]))


@exceptions
def p_expr_ident(p):
    "ident : IDENT"
    global use_nargin, use_varargin
    if p[1] == "varargin":
        use_varargin = True
    if p[1] == "nargin":
        use_nargin = True
    # import pdb; pdb.set_trace()
    p[0] = node.ident(
        name=p[1],
        lineno=p.lineno(1),
        column=p.lexpos(1) - p.lexer.lexdata.rfind("\n", 0, p.lexpos(1)),
        lexpos=p.lexpos(1),
        dtype=None,
        props=None,
        init=None)


@exceptions
def p_ident_init_opt(p):
    """
    ident_init_opt : NEG
                   | ident
                   | ident EQ expr
    """
    if p[1] == '~':
        p[0] = node.ident("__")
    else:
        p[0] = p[1]
    if len(p) == 2:
        p[0].init = None
    else:
        p[0].init = p[3]


@exceptions
def p_expr_list(p):
    """
    expr_list : exprs
              | exprs COMMA
    """
    p[0] = p[1]


@exceptions
def p_expr_number(p):
    "number : NUMBER"
    p[0] = node.number(p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))


@exceptions
def p_expr_stmt(p):
    """
    expr_stmt : expr_list SEMI
    """
    assert isinstance(p[1], node.expr_list)
    
    p[0] = node.expr_stmt(expr=p[1])


@exceptions
def p_expr_string(p):
    "string : STRING"
    p[0] = node.string(p[1], lineno=p.lineno(1), lexpos=p.lexpos(1))


@exceptions
def p_exprs(p):
    """
    exprs : expr
          | exprs COMMA expr
    """
    if len(p) == 2:
        p[0] = node.expr_list([p[1]])
    elif len(p) == 4:
        p[0] = p[1]
        p[0].append(p[3])
    else:
        assert (0)
    assert isinstance(p[0], node.expr_list)


@exceptions
def p_field_expr(p):
    """
    expr : expr FIELD
    """
    p[0] = node.expr(
        op=".",
        args=node.expr_list([
            p[1], node.ident(
                name=p[2], lineno=p.lineno(2), lexpos=p.lexpos(2))
        ]))


@exceptions
def p_foo_stmt(p):
    "foo_stmt : expr OROR expr SEMI"
    expr1 = p[1][1][0]
    expr2 = p[3][1][0]
    ident = expr1.ret
    args1 = expr1.args
    args2 = expr2.args
    p[0] = node.let(ret=ident,
                    args=node.expr(op="or", args=node.expr_list([args1, args2])))


@exceptions
def p_for_stmt(p):
    """
    for_stmt : FOR ident EQ expr SEMI stmt_list END_STMT
             | FOR LPAREN ident EQ expr RPAREN SEMI stmt_list END_STMT
             | FOR matrix EQ expr SEMI stmt_list END_STMT
    """
    if len(p) == 8:
        if not isinstance(p[2], node.ident):
            raise_exception(
                SyntaxError, "Not implemented: for loop", new_lexer)
        p[2].props = "I"  # I= for-loop iteration variable
        p[0] = node.for_stmt(ident=p[2], expr=p[4], stmt_list=p[6])

# function


def p_func_head(p):
    """
    func_head : FUNCTION ident
              | FUNCTION ident FIELD
              | FUNCTION ret EQ ident
              | FUNCTION ret EQ ident FIELD
    """
    ret = None
    fname = None
    modif = None
    if len(p) == 3:
        ret = node.expr_list()
        fname = p[2]
        modif = node.expr_list()
    elif len(p) == 4:
        ret = node.expr_list()
        fname = node.ident(name=p[3], lineno=p.lineno(3), lexpos=p.lexpos(3))
        modif = p[2]
    elif len(p) == 5:
        ret = p[2]
        fname = p[4]
        modif = node.expr_list()
    elif len(p) == 6:
        ret = p[2]
        fname = node.ident(name=p[5], lineno=p.lineno(5), lexpos=p.lexpos(5))
        modif = p[4]
    else:
        assert 0, "func head len %d" % len(p)
    p[0] = node.func_stmt(ident=fname, ret=ret, modif=modif,
                          args=None, stmt_list=None, 
                          use_nargin=False, use_varargin=False)


@exceptions
def p_func_stmt(p):
    """func_stmt : func_head SEMI stmt_list END_FUNCTION
                 | func_head lambda_args SEMI stmt_list END_FUNCTION
    """
    # stmt_list of func_stmt is set below
    # marked with XYZZY
    global use_nargin, use_varargin
    _un = use_nargin
    _uv = use_varargin
    use_varargin = use_nargin = False

    assert isinstance(p[1], node.func_stmt)
    p[0] = p[1]

    if len(p) == 5:
        assert isinstance(p[3], node.stmt_list)
        p[0].args = node.expr_list()
        p[0].stmt_list = p[3]

    elif len(p) == 6:
        assert isinstance(p[2], node.expr_list)
        assert isinstance(p[4], node.stmt_list)
        p[0].args = p[2]
        p[0].stmt_list = p[4]

    else:
        assert 0, "Unexpected function statement length %d" % len(p)

    p[0].stmt_list = p[0].stmt_list or node.stmt_list()
    p[0].use_nargin = use_nargin
    p[0].use_varargin = use_varargin
    use_nargin = _un
    use_varargin = _uv

    

@exceptions
def p_funcall_expr(p):
    """
    funcall_expr : expr LPAREN expr_list RPAREN
                 | expr LPAREN RPAREN
                 | expr HANDLE ident LPAREN expr_list RPAREN
                 | expr HANDLE ident LPAREN RPAREN
    """
    
    def ravel_func(p3):
        return len(p3) == 1 and isinstance(p3[0], node.expr) and \
            p3[0].op == ":" and not p3[0].args
    
    if len(p) == 7 or len(p) == 6:
        func_expr = node.func_superclass_handle(p[1], p[3])
    else:
        func_expr = p[1]
        
    if len(p) % 2 == 1:
        args = p[len(p)-2]
    else:
        args = node.expr_list()
        
    if ravel_func(args):
        args = node.expr_list([func_expr])
        func_expr = node.ident("ravel")
        
    assert isinstance(args, node.expr_list), f'funcall args {args} {type(args)}'
    p[0] = node.funcall(func_expr=func_expr, args=args)


@exceptions
def p_global_list(p):
    """global_list : ident
                   | global_list ident
    """
    if len(p) == 2:
        p[0] = node.global_list([p[1]])
    elif len(p) == 3:
        p[0] = p[1]
        p[0].append(p[2])


@exceptions
def p_global_stmt(p):
    """
    global_stmt : GLOBAL global_list SEMI
                | GLOBAL ident EQ expr SEMI
    """
    p[0] = node.global_stmt(p[2])
    for ident in p[0]:
        ident.props = "G"  # G=global


@exceptions
def p_if_stmt(p):
    """
    if_stmt : IF expr sep stmt_list_opt elseif_stmt END_STMT
            | IF LPAREN expr RPAREN stmt_list_opt elseif_stmt END_STMT
    """
    if len(p) == 7:
        p[0] = node.if_stmt(cond_expr=p[2], then_stmt=p[4], else_stmt=p[5])
    elif len(p) == 8:
        p[0] = node.if_stmt(cond_expr=p[3], then_stmt=p[5], else_stmt=p[6])
    else:
        assert 0


@exceptions
def p_lambda_args(p):
    """lambda_args : LPAREN RPAREN
                   | LPAREN arg_list RPAREN
    """
    p[0] = p[2] if len(p) == 4 else node.expr_list()


@exceptions
def p_lambda_expr(p):
    """lambda_expr : HANDLE lambda_args expr
    """
    p[0] = node.lambda_expr(args=p[2], ret=p[3])


@exceptions
def p_matrix(p):
    """matrix : LBRACKET RBRACKET
              | LBRACKET concat_list RBRACKET
              | LBRACKET concat_list SEMI RBRACKET
              | LBRACKET expr_list RBRACKET
              | LBRACKET expr_list SEMI RBRACKET
    """
    if len(p) == 3:
        p[0] = node.matrix()
    else:
        p[0] = node.matrix(p[2])


@exceptions
def p_null_stmt(p):
    """
    null_stmt : SEMI
              | COMMA
    """
    p[0] = node.null_stmt()


@exceptions
def p_parens_expr(p):
    """
    expr :  LPAREN expr RPAREN
    """
    p[0] = node.expr(op="parens", args=node.expr_list([p[2]]))


@exceptions
def p_persistent_stmt(p):
    """
    persistent_stmt :  PERSISTENT global_list SEMI
                    |  PERSISTENT ident EQ expr SEMI
    """
    p[0] = node.null_stmt()


#    if len(p) == 4:
#        p[0] = node.global_stmt(p[2])
#        for ident in p[0]:
#            ident.props="G"  # G=global
#    else:
#    assert p[2].__class__ in (node.let,node.ident), p[2].__class__
#    p[0] = p[2]
#    #print p[2]


@exceptions
def p_ret(p):
    """
    ret : ident
        | LBRACKET RBRACKET
        | LBRACKET expr_list RBRACKET
    """
    if len(p) == 2:
        p[0] = node.expr_list([p[1]])
    elif len(p) == 3:
        p[0] = node.expr_list([])
    elif len(p) == 4:
        assert isinstance(p[2], node.expr_list)
        p[0] = p[2]
    else:
        assert 0
    for ident in p[0]:
        ident.props = "F"


# end func_decl


@exceptions
def p_return_stmt(p):
    "return_stmt : RETURN SEMI"
    p[0] = node.return_stmt()


@exceptions
def p_semi_opt(p):
    """
    semi_opt :
             | semi_opt SEMI
             | semi_opt COMMA
    """
    pass


@exceptions
def p_separator(p):
    """
    sep : COMMA
        | SEMI
    """
    p[0] = p[1]


@exceptions
def p_stmt(p):
    """
    stmt : continue_stmt
         | comment_stmt
         | func_stmt
         | break_stmt
         | expr_stmt
         | global_stmt
         | persistent_stmt
         | error_stmt
         | command
         | for_stmt
         | if_stmt
         | null_stmt
         | return_stmt
         | switch_stmt
         | try_catch
         | while_stmt
         | foo_stmt
         | unwind
         | func_args
         | classdef_stmt
         | class_props
         | class_methods
         | class_events 
    """
    # END_STMT is intentionally left out
    p[0] = p[1]
    # print p[0]


@exceptions
def p_stmt_list(p):
    """
    stmt_list : stmt
              | stmt_list stmt
    """
    if len(p) == 2:
        p[0] = node.stmt_list([p[1]] if p[1] else [])
    elif len(p) == 3:
        p[0] = p[1]
        if p[2]:
            p[0].append(p[2])
    else:
        assert 0


@exceptions
def p_stmt_list_opt(p):
    """
    stmt_list_opt :
                  | stmt_list
    """
    if len(p) == 1:
        p[0] = node.stmt_list()
    else:
        p[0] = p[1]


@exceptions
def p_switch_stmt(p):
    """
    switch_stmt : SWITCH expr semi_opt case_list END_STMT
    """

    def backpatch(expr, stmt):
        if isinstance(stmt, node.if_stmt):
            stmt.cond_expr.args[1] = expr
            backpatch(expr, stmt.else_stmt)

    backpatch(p[2], p[4])
    p[0] = p[4]


@exceptions
def p_transpose_expr(p):
    # p[2] contains the exact combination of plain and conjugate
    # transpose operators, such as "'.''.''''".
    "expr : expr TRANSPOSE"
    p[0] = node.transpose(p[1], node.string(p[2]))


@exceptions
def p_try_catch(p):
    """
    try_catch : TRY stmt_list CATCH stmt_list END_STMT
    """
    ## | TRY stmt_list END_STMT
    assert isinstance(p[2], node.stmt_list)
    # assert isinstance(p[4],node.stmt_list)
    p[0] = node.try_catch(
        try_stmt=p[2],
        catch_stmt=p[4],
        finally_stmt=node.stmt_list())


@exceptions
def p_unwind(p):
    """
    unwind : UNWIND_PROTECT stmt_list UNWIND_PROTECT_CLEANUP stmt_list END_UNWIND_PROTECT
    """
    p[0] = node.try_catch(
        try_stmt=p[2], catch_stmt=node.expr_list(), finally_stmt=p[4])


@exceptions
def p_while_stmt(p):
    """
    while_stmt : WHILE expr SEMI stmt_list END_STMT
    """
    assert isinstance(p[4], node.stmt_list)
    p[0] = node.while_stmt(cond_expr=p[2], stmt_list=p[4])


@exceptions
def p_error(p):
    if p is None:
        raise_exception(SyntaxError, "Unexpected EOF", new_lexer)
    if p.type == "COMMENT":
        # print "Discarded comment", p.value
        parser.errok()
        return
    raise_exception(SyntaxError,
                    ('Unexpected "%s" (parser)' % p.value),
                    new_lexer)


# func args

@exceptions
def p_fa_1(p):
    """
    fa_1 : ident LPAREN expr_list RPAREN
         | ident 
    """
    p[0] = node.func_arg_restr(name=p[1], dim=None, cls=None, val=None, defVal=None)
    if len(p) == 5:
        p[0].dim = p[3]


@exceptions
def p_fa_2(p):
    """
    fa_2 : fa_1
         | fa_1 ident
         | fa_1 LBRACE expr_list RBRACE
         | fa_1 ident LBRACE expr_list RBRACE
    """
    assert isinstance(p[1], node.func_arg_restr)
    p[0] = p[1]
    if len(p) == 3:
        p[0].cls = p[2]
    elif len(p) == 5:
        p[0].val = p[3]
    elif len(p) == 6:
        p[0].cls = p[2]
        p[0].val = p[4]
    elif len(p) == 2:
        pass
    else:
        assert 0, "fa_2 len %d" % len(p)


@exceptions
def p_func_arg_restr(p):
    """
    func_arg_restr : fa_2 SEMI
                   | fa_2 EQ expr SEMI
    """
    assert isinstance(p[1], node.func_arg_restr)
    p[0] = p[1]
    if len(p) == 5:
        p[0].defVal = p[3]
    elif len(p) == 3:
        pass
    else:
        assert 0, "func_arg_restr len %d" % len(p)


@exceptions
def p_func_arg_list(p):
    """
    func_arg_list : func_arg_restr
                  | func_arg_list func_arg_restr
    """
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        if not isinstance(p[1], node.stmt_list):
            p[0] = node.stmt_list([p[1], p[2]])
        else:
            p[1].append(p[2])
            p[0] = p[1]
    else:
        assert 0, "func_arg_list len %d" % len(p)


@exceptions
def p_func_args(p):
    """
    func_args : FUNCTION_ARGUMENTS SEMI func_arg_list END_FUNCTION_ARGUMENTS
              | FUNCTION_ARGUMENTS LPAREN expr_list RPAREN SEMI func_arg_list END_FUNCTION_ARGUMENTS
    """
    if len(p) == 5:
        p[0] = node.func_args(modif=node.expr_list(), restrs=p[3], extstmt=None)
    elif len(p) == 8:
        p[0] = node.func_args(modif=p[3], restrs=p[6], extstmt=None)
    else:
        assert 0, "unexpected length: %d" % len(p)

# classdef

@exceptions
def p_stmt_list_epsilon(p):
    "stmt_list_epsilon : \n | stmt_list"
    if len(p) == 1:
        p[0] = node.stmt_list()
    else:
        p[0] = p[1]
    
    
@exceptions
def p_class_props(p):
    "class_props : CLASSDEF_PROPS SEMI stmt_list_epsilon END_CLASSDEF_PROPS\n| CLASSDEF_PROPS lambda_args SEMI stmt_list_epsilon END_CLASSDEF_PROPS"
    if len(p) == 6:
        restrs = p[2]
        stmt = p[4]
    else:
        restrs = None
        stmt = p[3]
    p[0] = node.class_props(stmt_list=stmt, restrs=restrs)


@exceptions
def p_class_methods(p):
    "class_methods : CLASSDEF_METHODS SEMI stmt_list END_CLASSDEF_METHODS\n| CLASSDEF_METHODS lambda_args SEMI stmt_list END_CLASSDEF_METHODS"
    if len(p) == 6:
        restrs = p[2]
        stmt = p[4]
    else:
        restrs = None
        stmt = p[3]
    p[0] = node.class_methods(stmt_list=stmt, restrs=restrs)


@exceptions
def p_class_events(p):
    "class_events : CLASSDEF_EVENTS SEMI stmt_list END_CLASSDEF_EVENTS"
    p[0] = node.class_events(stmt_list=p[3])


@exceptions
def p_super_class_list(p):
    "super_class_list : ident \n| super_class_list AND ident"
    if len(p) == 2:
        p[0] = node.expr_list([p[1]])
    elif len(p) == 4:
        p[0] = p[1]
        p[0].append(p[3])
    else:
        assert 0, "classdef superclass %d" % len(p)
    assert isinstance(p[0], node.expr_list)


@exceptions
def p_classdef_head_args(p):
    "classdef_head_args : CLASSDEF \n| CLASSDEF lambda_args"
    if len(p) == 3:
        p_args = p[2]
    elif len(p) == 2:
        p_args = None
    else:
        assert 0, "classdef head %d" % len(p)
    p[0] = node.classdef_stmt(attrs=p_args, name=None, super=None, sub=[])


@exceptions
def p_classdef_head(p):
    """
    classdef_head : classdef_head_args ident SEMI
                  | classdef_head_args ident LT super_class_list SEMI
    """
    assert isinstance(
        p[1], node.classdef_stmt), "classdef_head type %s" % type(p[1])
    p[0] = p[1]
    if len(p) == 4:
        p[0].name = p[2]
        p[0].super = node.expr_list()
    elif len(p) == 6:
        p[0].name = p[2]
        p[0].super = p[4]
    else:
        assert 0, "classdef stmt %d" % len(p)


@exceptions
def p_classdef_stmt(p):
    """
    classdef_stmt : classdef_head stmt_list END_CLASSDEF
    """
    assert isinstance(
        p[1], node.classdef_stmt), "classdef_stmt type %s" % type(p[1])
    p[0] = p[1]
    assert isinstance(
        p[2], node.stmt_list), "classdef_stmt list type %s" % type(p[2])
    p[0].sub = p[2]

# main parser


parser = yacc.yacc(start="top")


@exceptions
def parse(buf):
    if options.debug_parser:
        import pdb
        pdb.set_trace()
    global new_lexer  # used in main.main()
    new_lexer = lexer.new()
    p = parser.parse(
        buf, tracking=1, debug=options.debug_parser, lexer=new_lexer)

    if options.debug_parser:
        for i, pi in enumerate(p):
            print(i, pi.__class__.__name__, pi._backend())

#    for i in range(len(p)):
#        if isinstance(p[i], node.func_stmt):
#            break
#    else:
#        return None  # p[i] is a func decl

    return p
#    for j in range(i+1,len(p)):
#        if i < j and isinstance(p[j], node.func_stmt):
#            p.insert(j,node.return_stmt(ret=p[i].ret))
#            j += 1
#            i = j
#    p.append(node.return_stmt(ret=p[i].ret))
#
#    if "2" in options.debug:
#        for i,pi in enumerate(p):
#            print i,pi.__class__.__name__,str(pi)[:50]
