import json
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from model.module import Module, File

from data import Data
from model.dependency import Dependency
from model.importable import Importable


class SageClass(Importable):
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
        self._imported_files = {}
        self._imported_classes = {}
        self._full_imports = []
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
        return self.module.full_path_name + "." + self.name

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
    
    def add_file_import(self, alias: str, file: 'File'):
        self._imported_files[alias] = file

    def add_class_import(self, alias: str, sage_class: 'SageClass'):
        self._imported_classes[alias] = sage_class
    
    def add_full_import(self, file: 'File'):
        self._full_imports.append(file)

    def get_import_map(self) -> dict:
        import_map = {}
        for file in self._full_imports:
            import_map.update(file.get_import_map())
        
        import_map.update(
            self._imported_classes
        )

        import_map.update(
            {
                file_alias + "." + sage_class.name  : sage_class
                for file_alias, file in self._imported_files.items()
                for sage_class in file.get_classes()
            }
        )

        return import_map

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


