from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sagedeps.deps.model.importable import Importable

class Filter:
    def __init__(self):
        self._base_filter = EmptyFilter()

    def add(self, base_filter: 'Filter'):
        if isinstance(self._base_filter, EmptyFilter):
            self._base_filter = base_filter
        else:
            self._base_filter.add(base_filter)
        return self

    def _applies_to_self(self, object: 'Importable') -> bool:
        raise Exception("Not implemented")
    
    def applies_to(self, object: 'Importable') -> bool:
        return self._applies_to_self(object) and self._base_filter.applies_to(object)

    def apply(self, objects: list['Importable']):
        return list(filter(
            lambda obj: self._applies_to_self(obj),
            self._base_filter.apply(objects)
        ))
    
    @classmethod
    def from_json(cls, data, filters: list[dict]) -> "Filter":
        from sagedeps.deps.filter.loader import get_filter_class
        subfilter_classes = [get_filter_class(filter["name"]) for filter in filters]
        this = cls(data)
        for subfilter_cls, filter in zip(subfilter_classes, filters):
            this.add(subfilter_cls.from_json(filter["data"], filter.get("filters", [])))
        return this

class EmptyFilter(Filter):
    def __init__(self):
        self._base_filter = None

    def _applies_to_self(self, object: 'Importable') -> bool:
        return True
    
    def add(self, base_filter: 'Filter'):
        raise Exception("Cannot compose empty filter.")
    
    def applies_to(self, object: 'Importable') -> bool:
        return True

    def apply(self, objects: list['Importable']):
        return list(objects)
    
    @classmethod
    def from_json(cls, data: dict, filters: list) -> "Filter":
        return cls()