from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from model.sageclass import SageClass

from model.importable import Importable
from model.dependency import Relation

class Module(Importable):
    def __init__(self, name: str, parent: 'Module | None'):
        self._parent = parent
        self._name = name
        self._full_name = parent.full_path_name + "." + name if not self.is_root else name
        self._children = []

        # cached variables
        self._classes = None

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def parent(self) -> 'Module | None':
        return self._parent

    @property
    def full_path_name(self) -> str:
        return self._full_name
    
    @property
    def is_root(self) -> bool:
        return self._parent is None
    
    @property
    def extension(self) -> str | None:
        return None

    @property
    def depth(self) -> int:
        if self._parent is None:
            return 0
        return self._parent.depth + 1
    
    def add_child(self, other: 'Module') -> None:
        self._children.append(other)
    
    def contained_in(self, other: 'Module | None') -> bool:
        if other is None:
            return False
        if self._parent is None:
            return False
        return self._parent == other or self._parent.contained_in(other)

    def contains(self, other: 'Module'):
        return other.contained_in(self)
    
    def get_classes(self):
        if self._classes is not None:
            return self._classes
        self._classes = [sage_class for submodule in self._children for sage_class in submodule.get_classes()]
        return self.get_classes()

    def depends_on(self, other: 'Module', relations = None):
        sage_class: SageClass
        for sage_class in self.get_classes():
            if sage_class.depends_on(other, relations=relations):
                return True
        
        return False
    
    @property
    def in_degree(self) -> int:
        return sum([c.in_degree for c in self._children])

    @property
    def out_degree(self) -> int:
        return sum([c.out_degree for c in self._children])

class File(Module):
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
    
    @property
    def in_degree(self) -> int:
        return sum([c.in_degree for c in self._classes])

    @property
    def out_degree(self) -> int:
        return sum([c.out_degree for c in self._classes])
    
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

        

