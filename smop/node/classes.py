from smop.node.base import *
from smop.node.stmt import *


# class definition related

class classdef_stmt(stmt, recordtype("classdef_stmt", "name attrs super props methods events ctor")):
    pass

class class_props(stmt, recordtype("class_props", "stmt_list restrs")):
    pass

class class_methods(stmt, recordtype("class_methods", "stmt_list restrs")):
    pass

class class_events(stmt, recordtype("class_events", "stmt_list restrs")):
    pass
