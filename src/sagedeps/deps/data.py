from typing import TYPE_CHECKING

from sagedeps.deps.model.module import Module
from sagedeps.deps.model.sageclass import SageClass

from sagedeps.deps.filter.filter import Filter, EmptyFilter

class Data:
    modules = {}
    classes = {}
    instantiations = {}
    aliases = {}
    commit_metadata = {}
    rst_content = {}

    @classmethod
    def add_module(cls, full_module_name: str, module: 'Module'):
        cls.modules[full_module_name] = module

    @classmethod
    def add_class(cls, full_path_name: str, sageclass: 'SageClass'):
        cls.classes[full_path_name] = sageclass

    @classmethod
    def get_module(cls, full_module_name: str) -> 'Module | None':
        return cls.modules.get(full_module_name, None)

    @classmethod
    def get_class(cls, full_path_name: str) -> 'SageClass | None':
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
    def get_classes_filtered(cls, filter: Filter = EmptyFilter()) -> list[SageClass]:
        return filter.apply(cls.classes.values())

    @classmethod
    def get_modules_filtered(cls, filter: Filter = EmptyFilter()) -> list[Module]:
        return filter.apply(cls.modules.values())

    @classmethod
    def set_commit_metadata(cls, metadata: dict):
        cls.commit_metadata = metadata
    
    @classmethod
    def get_commit_metadata(cls, full_path_name: str) -> dict:
        resolved_name = cls.resolve_reference(full_path_name)
        return cls.commit_metadata.get(resolved_name, None)

    @classmethod
    def set_rst_content(cls, content: dict):
        cls.rst_content = content
    
    @classmethod
    def get_rst_references(cls, full_path_name: str):
        resolved_name = cls.resolve_reference(full_path_name).replace(".", "/")
        return [
            reference for reference, content in cls.rst_content.items() if resolved_name in content
        ]