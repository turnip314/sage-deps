from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from model.module import Module
    from model.sageclass import SageClass

class Data:
    modules = {}
    classes = {}

    @classmethod
    def add_module(cls, full_module_name: str, module: 'Module'):
        cls.modules[full_module_name] = module

    @classmethod
    def add_class(cls, full_path_name: str, classname: str, sageclass: 'SageClass'):
        pass

    @classmethod
    def get_module(cls, full_module_name: str) -> 'Module':
        return cls.modules.get(full_module_name, None)

    @classmethod
    def get_class(cls, classname: str) -> 'SageClass':
        pass