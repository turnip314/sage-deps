from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from deps.model.importable import Importable

from deps.filter.filter import Filter

class PathFilter(Filter):
    def __init__(self, path: str = "sage.rings"):
        super().__init__()
        self._path = path

    def _applies_to_self(self, object: 'Importable') -> bool:
        return object.full_path_name.startswith(self._path)

class NameContains(Filter):
    def __init__(self, name: str = ""):
        super().__init__()
        self._name = name

    def _applies_to_self(self, object: 'Importable') -> bool:
        return self._name in object.full_path_name