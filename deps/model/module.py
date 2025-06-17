from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from model.sageclass import SageClass

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

class File(Module):
    def __init__(self, name: str, parent: 'Module', extension: str):
        super().__init__(name, parent)
        self._extension = extension
        self._classes = []
        self._imported_files = []
        self._imported_classes = []

    @property
    def extension(self) -> str | None:
        return self._extension
    
    def add_class(self, sage_class: 'SageClass'):
        self._classes.append(sage_class)
    
    def add_import(self, item_imported: 'File | SageClass'):
        from model.sageclass import SageClass
        if isinstance(SageClass, item_imported):
            self._imported_classes.append(item_imported)
        elif isinstance(File, item_imported):
            self._imported_files.append(item_imported)

