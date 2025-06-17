import json
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from model.module import Module

from data import Data
from model.dependency import Dependency


class SageClass:
    def __init__(
            self,
            module: 'Module',
            classname,
            is_abstract,
            is_cython,

    ):
        self._name = classname
        self._module = module
        self._is_abstract = is_abstract
        self._is_cython = is_cython
        self._dependencies = []

    def add_dependency(self, dep: Dependency):
        self._dependencies.append(dep)
    
    def to_json(self):
        raise Exception("Not implemented.")
    
    @property
    def name(self):
        return self._name
    
    @property
    def module(self):
        return self._module
    
    @property
    def full_path_name(self):
        return self.module.full_name + "." + self.name

    def contained_in(self, other: 'Module'):
        return other == self._module or self._module.contained_in(other)
    
    def depends_on(self, other: 'SageClass | Module'):
        from model.module import Module
        if isinstance(SageClass, other):
            return any([d.target == other for d in self._dependencies])
        elif isinstance(Module, other):
            return any([d.target.contained_in(other) for d in self._dependencies])
    
    @classmethod
    def from_json(cls, json_obj: str):
        self_dict = json.loads(json_obj)
        base_class = PythonClass if self_dict["type"] == "PythonClass" else CythonClass
        module_name = self_dict["module"]
        module = Data.get_module(module_name)
        return base_class(module, self_dict["name"])
    

class PythonClass(SageClass):
    def __init__(
            self,
            module: 'Module',
            name: str,
    ):
        super().__init__(module, name, False, False)

    def to_json(self) -> str:
        self_dict = {}
        self_dict["name"] = self.name
        self_dict["module"] = self.module
        self_dict["is_abstract"] = self._is_abstract
        self_dict["type"] = "PythonClass"
        return json.dumps(self_dict)
        

class CythonClass(SageClass):
    def __init__(
            self,
            module: 'Module',
            name: str,
    ):
        super().__init__(module, name, False, True)


