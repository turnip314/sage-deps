import json

from deps.filter.filter import Filter, EmptyFilter
from deps.filter.balance import Balance
from deps.filter.score_filter import ScoreFilter
from deps.filter.connectors import Not, Or, All
from deps.filter.degree_filter import MinFanIn, MinFanOut
from deps.filter.depth_filter import MinDepthFilter, MaxDepthFilter
from deps.filter.path_filter import PathFilter
from deps.model.dependency import Relation

def parse_metric(name: str):
    match name:
        case "score":
            return lambda object: object.get_score
        case _:
            return lambda object: 0

def parse_filter(name, data):
    result: Filter
    match name:
        case "empty":
            result = EmptyFilter()
        case "score":
            result = ScoreFilter(
                min_score=data
            )
        case "path":
            result = PathFilter(
                path=data
            )
        case "contains":
            result = NameContains(
                name=data
            )
        case "min-depth":
            result = MinDepthFilter(
                min_depth=data
            )
        case "max-depth":
            result = MaxDepthFilter(
                min_depth=data
            )
        case "in-deg":
            result = MinFanIn(
                deg=data.get("min-deg", 0) or data,
                relations=data.get("relations") or [
                    Relation.DECLARED_SUB_IMPORT, 
                    Relation.DECLARED_TOP_IMPORT, 
                    Relation.CLASS_ATTRIBUTE, 
                    Relation.INHERITANCE
                ]
            )
        case "out-deg":
            result = MinFanOut(
                deg=data.get("max-deg", 0) if isinstance(data, dict) else data,
                relations=data.get("relations") or [
                    Relation.DECLARED_SUB_IMPORT, 
                    Relation.DECLARED_TOP_IMPORT, 
                    Relation.CLASS_ATTRIBUTE, 
                    Relation.INHERITANCE
                ]
            )
        case "or":
            result = Or(
                *[
                    parse_filter(
                        x["name"], x["data"]
                    ) for x in data
                ]
            )
        case "all":
            result = All(
                *[
                    parse_filter(
                        x["name"], x["data"]
                    ) for x in data
                ]
            )
        case "not":
            result = Not(
                *[
                    parse_filter(
                        x["name"], x["data"]
                    ) for x in data
                ]
            )
        case "balance":
            weights = data.get("weights", None)
            result = Balance(
                parse_metric(data.get("metric", None)),
                int(data.get("limit")),
                [float(v) for v in weights] if weights else None,
                *[parse_filter(x["name"], x["data"]) for x in data.get("filters", [])]
            )
        case _:
            raise Exception(f"Unknown filter name {name}")
    
    if "filter" in data:
        subdata = data["filter"]
        result.add(parse_filter(subdata.name, subdata.data))

    return result

def from_json_file(file_path: str) -> Filter:
    with open(file_path, "r") as f:
        filter_dict = json.loads(f.read())
        return parse_filter(filter_dict["name"], filter_dict["data"])

    

