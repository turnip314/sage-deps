from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from deps.model.importable import Importable

from deps.filter.filter import Filter

class MinFanIn(Filter):
    def __init__(self, deg: int):
        super().__init__()
        self._deg = deg

    def _applies_to_self(self, object: 'Importable') -> bool:
        return object.in_degree() >= self._deg

class MinFanOut(Filter):
    def __init__(self, deg: int):
        super().__init__()
        self._deg = deg

    def _applies_to_self(self, object: 'Importable') -> bool:
        return object.out_degree() >= self._deg