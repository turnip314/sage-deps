from typing import List
from deps.data import Data
from analysis.graph_analysis import GraphAnalyzer
from deps.filter import Filter, PathFilter
from deps.model.sageclass import SageClass


import networkx as nx

from deps.model.dependency import Relation

class DistanceAnalyzer(GraphAnalyzer):
    def __init__(
            self, 
            starting_node: str,
            max_distance: int,
            filter: Filter = PathFilter(),
            edge_types: List[Relation] | None = None,
            edge_weights: List[int] | None = None,
            upstream: bool = True
        ):
        super().__init__(filter, edge_types=edge_types, weight_by_strength=False, weights=edge_weights)
        self._starting_node = starting_node
        self._max_distance = max_distance
        if upstream:
            self._graph.reverse(copy=False)
            self._adjacency_matrix.transpose(copy=False)

    def _run_analysis(self) -> dict:
        distances = nx.single_source_shortest_path_length(self._graph.reverse(), self._starting_node, self._max_distance)
        nodes_by_distance = {
            distance: [node for node, dist in distances.items() if dist == distance]
            for distance in range(self._max_distance+1)
        }
        
        return nodes_by_distance
    
    def run(self) -> dict:
        return self._run_analysis()
        