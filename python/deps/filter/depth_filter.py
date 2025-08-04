from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from deps.model.importable import Importable

from deps.filter.filter import Filter

class MinDepthFilter(Filter):
    def __init__(self, min_depth: int):
        super().__init__()
        self._min_depth = min_depth

    def _applies_to_self(self, object: 'Importable') -> bool:
        return object.depth >= self._min_depth
    
    @classmethod
    def from_json(cls, data: str, filters: list[dict]) -> "Filter":
        return super().from_json(int(data), filters)

class MaxDepthFilter(Filter):
    def __init__(self, max_depth: int):
        super().__init__()
        self.max_depth = max_depth

    def _applies_to_self(self, object: 'Importable') -> bool:
        return object.depth <= self.max_depth
    
    @classmethod
    def from_json(cls, data: str, filters: list[dict]) -> "Filter":
        return super().from_json(int(data), filters)