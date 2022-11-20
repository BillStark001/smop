# smop -- Matlab to Python compiler
# Copyright 2011-2013 Victor Leikehman
"""
if i.defs:
    i is defined, possibly more than once.
    Typical for vairable references.

if i.defs is None:
    i is a definition (lhs)

if i.defs == set():
    i is used but not defined.
    Typical for function calls.

symtab is a temporary variable, which maps
variable names (strings) to sets of ident
instances, which possibly define the variable.
It is used in if_stmt, for_stmt, and while_stmt.
"""
'''
The previous is from Victor. 
'''

from typing import Dict, Any, List, Optional, Set

from smop import node
from smop.common import extend


