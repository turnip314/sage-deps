
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

class File(Module):
    def __init__(self, name: str, parent: 'Module', extension: str):
        super().__init__(name, parent)
        self._extension = extension

    @property
    def extension(self) -> str | None:
        return self._extension
