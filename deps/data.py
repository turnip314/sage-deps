from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from model.module import Module
    from model.sageclass import SageClass

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