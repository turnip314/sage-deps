from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from model.module import Module
    from model.sageclass import SageClass
    from model.importable import Importable

class Filter:
    def __init__(self):
        self._in_path = "sage"
        self._not_in_paths = []
        self._contains = []
        self._not_contains = []
        self._depth = None
        self._min_depth = None
        self._max_depth = None
    
    def in_path(self, path: str) -> 'Filter':
        self._in_path = path
        return self
    
    def exclude_path(self, path: str) -> 'Filter':
        self._not_in_paths.append(path)
        return self
    
    def contains(self, word: str) -> 'Filter':
        self._contains.append(word)
        return self
    
    def not_contains(self, word: str) -> 'Filter':
        self._not_contains.append(word)
        return self
    
    def depth(self, depth: int) -> 'Filter':
        self._depth = depth
        return self
    
    def min_depth(self, depth: int) -> 'Filter':
        self._min_depth = depth
        return self

    def max_depth(self, depth: int) -> 'Filter':
        self._max_depth = depth
        return self
    
    def applies_to(self, object: 'Importable') -> bool:
        name = object.full_path_name
        return name.startswith(self._in_path) and \
            (not any([name.startswith(x) for x in self._not_in_paths])) and \
            all([x in name for x in self._contains]) and \
            (not any([x in name for x in self._not_contains])) and \
            (self._depth is None or self._depth == object.depth) and \
            (self._min_depth is None or self._depth <= object.depth) and \
            (self._max_depth is None or self._depth >= object.depth)

    def apply(self, objects: list['Importable']):
        return list(filter(
            lambda obj: self.applies_to(obj),
            objects
        ))

class Data:
    modules = {}
    classes = {}
    instantiations = {}
    aliases = {}

    @classmethod
    def add_module(cls, full_module_name: str, module: 'Module'):
        cls.modules[full_module_name] = module

    @classmethod
    def add_class(cls, full_path_name: str, sageclass: 'SageClass'):
        cls.classes[full_path_name] = sageclass

    @classmethod
    def get_module(cls, full_module_name: str) -> 'Module':
        return cls.modules.get(full_module_name, None)

    @classmethod
    def get_class(cls, full_path_name: str) -> 'SageClass':
        resolved_name = cls.resolve_reference(full_path_name)
        return cls.classes.get(resolved_name, None)
    
    @classmethod
    def add_instantiation(cls, full_path_name: str, referenced_name: str):
        cls.instantiations[full_path_name] = referenced_name
    
    @classmethod
    def add_alias(cls, full_path_name: str, referenced_name: str):
        cls.aliases[full_path_name] = referenced_name
    
    @classmethod
    def resolve_reference(cls, full_path_name: str) -> str:
        resolved_name = full_path_name
        while resolved_name in cls.aliases:
            resolved_name = cls.aliases[resolved_name]
        if resolved_name in cls.instantiations:
            resolved_name = cls.instantiations[resolved_name]
        
        return resolved_name
    
    @classmethod
    def get_classes_filtered(cls, filter: Filter):
        return filter.apply(cls.classes.values())
    
    @classmethod
    def get_modules_filtered(cls, filter: Filter):
        return filter.apply(cls.modules.values())