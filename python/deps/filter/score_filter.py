from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from deps.model.importable import Importable

from deps.filter.filter import Filter

class ScoreFilter(Filter):
    def __init__(self, min_score: int):
        super().__init__()
        self._min_score = min_score

    def _applies_to_self(self, object: 'Importable') -> bool:
        return object.get_score >= self._min_score
