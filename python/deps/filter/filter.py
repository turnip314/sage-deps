from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deps.model.importable import Importable

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