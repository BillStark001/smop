import copy

from smop.resolve.base import *


SymtabDict = Dict[str, 'SymRecord']

def copy_symtab_dict(symtab: SymtabDict) -> SymtabDict:
    new_symtab = copy.copy(symtab)
    for k, v in new_symtab.items():
        new_symtab[k] = copy.copy(v)
    return new_symtab


class SymType(object):
    
    def __init__(self, name: str):
        pass
        # TODO

class SymRecord(object):
    
    def __init__(self, name: str):
        self.__rec: List[node.ident]  = []
        self.name = name
        self.__feat: Set[str] = set()
        
    def add_ident(self, i: node.ident):
        self.__rec.append(i)
        
    def add_feature(self, feature: str):
        self.__feat.add(feature)
        
    def rename(self, name: str):
        for ident in self.__rec:
            ident.name = name
            
    def copy(self) -> 'SymRecord':
        rec = copy.copy(self.__rec)
        feat = copy.copy(self.__feat)
        ret = SymRecord(name=self.name)
        ret.__rec = rec
        ret.__feat = feat
        return ret
        
SymRecord.FEATURE_IS_NUMBER = '[is_number]'
SymRecord.FEATURE_IS_STRING = '[is_string]'
SymRecord.FEATURE_IS_LOGICAL = '[is_logical]'

class SymTab(object):
    
    def __init__(self, outer: Optional['SymTab'] = None):
        self.__tab: SymtabDict = {}
        self.__outer = outer
    
    @property
    def outer(self) -> Optional['SymTab']:
        return self.__outer
    
    def find(self, symbol: str) -> Optional[SymRecord]:
        if symbol in self.__tab:
            return self.__tab[symbol]
        elif self.__outer is not None:
            return self.__outer.find(symbol)
        return None
    
    def create(self, symbol: str) -> SymRecord:
        rec = SymRecord(symbol)
        self.__tab[symbol] = rec
        return rec
        
    def find_or_create(self, symbol: str) -> SymRecord:
        return self.find(symbol) or self.create(symbol)
        
    def copy(self) -> 'SymTab':
        tab = {}
        for k, v in self.__tab.items():
            tab[k] = v.copy()
            
        ret = SymTab(outer=self.__outer)
        ret.__tab = tab
        return ret
        