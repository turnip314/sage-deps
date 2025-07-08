from typing import TYPE_CHECKING
from typing import List
from deps.model.dependency import Relation
if TYPE_CHECKING:
    from deps.model.importable import Importable

from deps.filter.filter import Filter

class MinFanIn(Filter):
    def __init__(self, deg: int, relations: List['Relation'] | None = None):
        super().__init__()
        if relations is None:
            self._relations = [
                Relation.DECLARED_SUB_IMPORT,
                Relation.DECLARED_TOP_IMPORT,
                Relation.CLASS_ATTRIBUTE,
                Relation.INHERITANCE
            ]
        else:
            self._relations = relations
        self._deg = deg

    def _applies_to_self(self, object: 'Importable') -> bool:
        return object.in_degree(self._relations) >= self._deg

class MinFanOut(Filter):
    def __init__(self, deg: int, relations: List['Relation'] | None = None):
        super().__init__()
        if relations is None:
            self._relations = [
                Relation.DECLARED_SUB_IMPORT,
                Relation.DECLARED_TOP_IMPORT,
                Relation.CLASS_ATTRIBUTE,
                Relation.INHERITANCE
            ]
        else:
            self._relations = relations
        self._deg = deg

    def _applies_to_self(self, object: 'Importable') -> bool:
        return object.out_degree(self._relations) >= self._deg