import json
from typing import Type
from sagedeps.deps.filter.filter import Filter, EmptyFilter

def parse_metric(name: str):
    match name:
        case "score":
            return lambda object: object.get_score
        case _:
            return lambda object: 0

def get_filter_class(name) -> Type[Filter]:
    from sagedeps.deps.filter.balance import Balance
    from sagedeps.deps.filter.score_filter import ScoreFilter
    from sagedeps.deps.filter.connectors import Not, Or, All
    from sagedeps.deps.filter.distance_filter import DistanceFilter
    from sagedeps.deps.filter.degree_filter import MinFanIn, MinFanOut
    from sagedeps.deps.filter.depth_filter import MinDepthFilter, MaxDepthFilter
    from sagedeps.deps.filter.path_filter import NameContains, PathFilter
    from sagedeps.deps.model.dependency import Relation
    result: Filter
    match name:
        case "empty":
            return EmptyFilter
        case "score":
            return ScoreFilter
        case "path":
            return PathFilter
        case "contains":
            return NameContains
        case "min-depth":
            return MinDepthFilter
        case "max-depth":
            return MaxDepthFilter
        case "in-deg":
            return MinFanIn
        case "out-deg":
            return MinFanOut
        case "or":
            return Or
        case "all":
            return All
        case "not":
            return Not
        case "balance":
            return Balance
        case "distance":
            return DistanceFilter
        case _:
            raise Exception(f"Unknown filter name {name}")
    

    return result

def from_json_file(file):
    with open(file, "r") as f:
        filter = json.loads(f.read())
        filter_cls = get_filter_class(filter["name"])
        return filter_cls.from_json(filter["data"], filter.get("filters", []))

