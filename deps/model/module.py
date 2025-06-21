from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from model.sageclass import SageClass

from model.importable import Importable

class Module:
    def __init__(self, name: str, parent: 'Module'):
        self._parent = parent
        self._name = name
        self._full_name = parent.full_path_name + "." + name if not self.is_root else name
        self._children = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def full_path_name(self) -> str:
        return self._full_name
    
    @property
    def is_root(self) -> bool:
        return self._parent is None
    
    @property
    def extension(self) -> str | None:
        return None
    
    def add_child(self, other: 'Module') -> None:
        self._children.append(other)
    
    def contained_in(self, other: 'Module | None') -> bool:
        if other is None:
            return False
        return self._parent == other or self._parent.contained_in(other)

    def contains(self, other: 'Module'):
        return other.contained_in(self)

class File(Module, Importable):
    def __init__(self, name: str, parent: 'Module', extension: str):
        super().__init__(name, parent)
        self._extension = extension
        self._classes = []
        self._imported_files = {}
        self._imported_classes = {}
        self._full_imports = []

    @property
    def extension(self) -> str | None:
        return self._extension
    
    def add_class(self, sage_class: 'SageClass'):
        self._classes.append(sage_class)
    
    def get_classes(self):
        return self._classes
    
    def add_file_import(self, alias: str, file: 'File'):
        self._imported_files[alias] = file

    def add_class_import(self, alias: str, sage_class: 'SageClass'):
        self._imported_classes[alias] = sage_class

    def add_full_import(self, file: 'File'):
        self._full_imports.append(file)

    def get_import_map(self, visited: set | None = None) -> dict:
        if visited is None:
            visited = set()
        if self in visited:
            return {}
        visited.add(self)

        import_map = {}
        for file in self._full_imports:
            import_map.update(file.get_import_map(visited))
        
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

        

