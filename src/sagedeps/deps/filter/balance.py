from typing import TYPE_CHECKING
from copy import copy

if TYPE_CHECKING:
    from sagedeps.deps.model.importable import Importable

from sagedeps.deps.filter.filter import Filter

class Balance(Filter):
    def __init__(self, metric, limit: int = 200, weights=None, *args):
        super().__init__()
        self._filters = args
        self._metric = metric
        self._limit = limit
        
        if weights is None:
            weights= [1 for _ in args]
        self._weights = [w/len(args) for w in weights]
    
    def applies_to(self, object: 'Importable') -> bool:
        raise Exception("Cannot check filter status of Balance filter.")

    def apply(self, objects: list['Importable']):
        sorted_objects_by_filter = [
            sorted(_filter.apply(objects), key=self._metric, reverse=True)
            for _filter in self._filters
        ]

        returned_objects = set()
        limit = self._limit
        
        for i in range(len(self._filters)):
            w, lst = self._weights[i], sorted_objects_by_filter[i]
            returned_objects = returned_objects.union(lst[:int(w * limit)])
            sorted_objects_by_filter[i] = lst[int(w*limit):]
        limit = self._limit - len(returned_objects)

        while limit > 0 and any([len(lst) > 0 for lst in sorted_objects_by_filter]):
            for lst in sorted_objects_by_filter:
                if lst:
                    returned_objects.add(lst.pop(0))
            limit = self._limit - len(returned_objects)

        return list(returned_objects)
    
    @classmethod
    def from_json(cls, data, filters: list[dict]) -> "Filter":
        def parse_metric(name: str):
            match name:
                case "score":
                    return lambda object: object.get_score
                case _:
                    return lambda object: 0
        from deps.filter.loader import get_filter_class
        if filters:
            print("Connector filters do not take `filters` as parameter. Use `data` instead.")
        subfilters = [
            get_filter_class(data["name"]).from_json(filter["data"], filter.get("filters", [])) 
            for filter in filters
        ]
        weights = data.get("weights", None)
        return cls(
            parse_metric(data.get("metric", None)),
            int(data.get("limit")),
            [float(v) for v in weights] if weights else None,
            *subfilters
        )

