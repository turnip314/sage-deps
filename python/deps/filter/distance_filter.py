from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from deps.model.importable import Importable

from deps.filter.filter import Filter, EmptyFilter

class DistanceFilter(Filter):
    def __init__(self, source: str, distance: int, direction: str = "all"):
        super().__init__()
        from analysis.distance import DistanceAnalyzer
        self._analyzer = DistanceAnalyzer(
            starting_node=source,
            max_distance=distance,
            direction=direction,
            filter=EmptyFilter()
        )
        self._results = [node for lst in self._analyzer.run().values() for node in lst]

    def _applies_to_self(self, object: 'Importable') -> bool:
        return object.full_path_name in self._results
    
    @classmethod
    def from_json(cls, data, filters: list[dict]) -> "Filter":
        from deps.filter.loader import get_filter_class
        subfilter_classes = [get_filter_class(filter["name"]) for filter in filters]
        this = cls(data["source"], int(data["distance"]), direction = data.get("direction", "all"))
        for subfilter_cls, filter in zip(subfilter_classes, filters):
            this.add(subfilter_cls.from_json(filter["data"], filter.get("filters", [])))
        
        return this