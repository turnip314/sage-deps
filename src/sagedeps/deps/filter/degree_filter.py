from typing import TYPE_CHECKING
from typing import List
from sagedeps.deps.model.dependency import Relation
if TYPE_CHECKING:
    from sagedeps.deps.model.importable import Importable

from sagedeps.deps.filter.filter import Filter

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
    
    @classmethod
    def from_json(cls, data, filters: list[dict]) -> "Filter":
        from deps.filter.loader import get_filter_class
        subfilter_classes = [get_filter_class(filter["name"]) for filter in filters]
        this = cls(
            deg=data.get("min-deg", 0) if isinstance(data, dict) else data,
            relations=data.get("relations", []) if isinstance(data, dict) else [
                Relation.DECLARED_SUB_IMPORT, 
                Relation.DECLARED_TOP_IMPORT, 
                Relation.CLASS_ATTRIBUTE, 
                Relation.INHERITANCE
            ]
        )
        for subfilter_cls, filter in zip(subfilter_classes, filters):
            this.add(subfilter_cls.from_json(filter["data"], filter.get("filters", [])))
        
        return this

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
    
    @classmethod
    def from_json(cls, data, filters: list[dict]) -> "Filter":
        from deps.filter.loader import get_filter_class
        subfilter_classes = [get_filter_class(filter["name"]) for filter in filters]
        this = cls(
            deg=data.get("min-deg", 0) if isinstance(data, dict) else data,
            relations=data.get("relations", []) if isinstance(data, dict) else [
                Relation.DECLARED_SUB_IMPORT, 
                Relation.DECLARED_TOP_IMPORT, 
                Relation.CLASS_ATTRIBUTE, 
                Relation.INHERITANCE
            ]
        )
        for subfilter_cls, filter in zip(subfilter_classes, filters):
            this.add(subfilter_cls.from_json(filter["data"], filter.get("filters", [])))
        
        return this