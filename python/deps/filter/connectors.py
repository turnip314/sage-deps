from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from deps.model.importable import Importable

from deps.filter.filter import Filter

class Or(Filter):
    def __init__(self, *args):
        super().__init__()
        self._filters = args

    def _applies_to_self(self, object: 'Importable') -> bool:
        return any(
            [
                filter.applies_to(object) for filter in self._filters
            ]
        )

class Not(Filter):
    def __init__(self, *args):
        super().__init__()
        self._filters = args

    def _applies_to_self(self, object: 'Importable') -> bool:
        return not any(
            [
                filter.applies_to(object) for filter in self._filters
            ]
        )

class All(Filter):
    def __init__(self, *args):
        super().__init__()
        self._filters = args

    def _applies_to_self(self, object: 'Importable') -> bool:
        return all(
            [
                filter.applies_to(object) for filter in self._filters
            ]
        )