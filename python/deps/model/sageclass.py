import json
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from deps.model.module import Module, File

from deps.model.dependency import Dependency, Relation
from deps.model.importable import Importable


class SageClass(Importable):
    def __init__(
            self,
            module: 'File',
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
        self._dependents = []
        self._score = 0

    def add_dependency(self, dep: Dependency):
        self._dependencies.append(dep)
        dep.target.add_dependent(dep)
    
    def add_dependent(self, dep: Dependency):
        self._dependents.append(dep)

    def filter_dependencies(self):
        """
        Only keep the strongest dependency link for a given targer
        """
        filtered_list = []
        classes = set()
        self._dependencies.sort(key = lambda dep: dep.relation, reverse=True)
        dependency: Dependency
        for dependency in self._dependencies:
            if dependency.target not in classes:
                filtered_list.append(dependency)
                classes.add(dependency.target)
        
        self._dependencies = filtered_list
    
    def to_dict(self) -> dict:
        self_dict = {
            "dependencies": {
                "sub-level-import": [
                    dep.target.full_path_name for dep in self._dependencies if dep.relation == Relation.SUB_METHOD_IMPORT
                ],
                "top-level-import": [
                    dep.target.full_path_name for dep in self._dependencies if dep.relation == Relation.TOP_LEVEL_IMPORT
                ],
                "attribute": [
                    dep.target.full_path_name for dep in self._dependencies if dep.relation == Relation.CLASS_ATTRIBUTE
                ],
                "inheritance": [
                    dep.target.full_path_name for dep in self._dependencies if dep.relation == Relation.INHERITANCE
                ],
            }
        }

        return self_dict
    
    @property
    def in_degree(self) -> int:
        return len(self._dependents)
    
    @property
    def out_degree(self) -> int:
        return len(self._dependencies)

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def module(self) -> 'Module':
        return self._module
    
    @property
    def full_path_name(self) -> str:
        return self.module.full_path_name + "." + self.name

    @property
    def depth(self) -> int:
        return self._module.depth

    def get_dependencies(self) -> list[Dependency]:
        return self._dependencies

    def contained_in(self, other: 'Module'):
        return other == self._module or self._module.contained_in(other)
    
    def depends_on(self, other: 'SageClass | Module', relations=None):
        from model.module import Module
        if isinstance(other, SageClass):
            return any([
                d.target == other and (relations is None or d.relation in relations)
                for d in self._dependencies
            ])
        elif isinstance(other, Module):
            return any([
                d.target.contained_in(other) and (relations is None or d.relation in relations)
                for d in self._dependencies
            ])
    
    def add_file_import(self, alias: str, file: 'File'):
        self._imported_files[alias] = file

    def add_class_import(self, alias: str, sage_class: 'SageClass'):
        self._imported_classes[alias] = sage_class
    
    def add_full_import(self, file: 'File'):
        self._full_imports.append(file)

    def get_import_map(self, split_level=False) -> dict | tuple[dict, dict]:
        class_import_map = {}

        for file in self._full_imports:
            class_import_map.update(file.get_import_map())

        class_import_map.update(self._imported_classes)
        
        class_import_map.update(
            {
                file_alias + "." + sage_class.name  : sage_class
                for file_alias, file in self._imported_files.items()
                for sage_class in file.get_classes()
            }
        )

        top_level_import_map = self._module.get_import_map()
        top_level_import_map.update(
            {
                sage_class.name : sage_class for sage_class in self._module.get_classes()
            }
        )

        if split_level:
            return class_import_map, top_level_import_map

        top_level_import_map.update(class_import_map)
        return top_level_import_map

class PythonClass(SageClass):
    def __init__(
            self,
            module: 'Module',
            name: str,
    ):
        super().__init__(module, name, False, False)

    def to_dict(self) -> dict:
        self_dict = super().to_dict()
        self_dict["name"] = self.name
        self_dict["module"] = self.module.full_path_name
        self_dict["is_abstract"] = self._is_abstract
        self_dict["type"] = "PythonClass"
        return self_dict
        

class CythonClass(SageClass):
    def __init__(
            self,
            module: 'Module',
            name: str,
    ):
        super().__init__(module, name, False, True)


