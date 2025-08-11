from typing import List
from sagedeps.deps.data import Data
from sagedeps.analysis.graph_analysis import GraphAnalyzer
from sagedeps.deps.filter import Filter, EmptyFilter
from sagedeps.deps.model.sageclass import SageClass


import networkx as nx

from sagedeps.deps.model.dependency import Relation

class DistanceAnalyzer(GraphAnalyzer):
    def __init__(
            self, 
            starting_node: str,
            max_distance: int,
            filter: Filter = EmptyFilter(),
            edge_types: List[Relation] | None = None,
            edge_weights: List[int] | None = None,
            direction: str = "up"
        ):
        super().__init__(filter, edge_types=edge_types, weight_by_strength=False, weights=edge_weights)
        self._starting_node = starting_node
        self._max_distance = max_distance
        if direction == "up":
            self._graph.reverse(copy=False)
            self._adjacency_matrix.transpose(copy=False)
        elif direction == "all":
            self._graph = self._graph.to_undirected()

    def _run_analysis(self) -> dict:
        distances = nx.single_source_shortest_path_length(self._graph, self._starting_node, self._max_distance)
        nodes_by_distance = {
            distance: [node for node, dist in distances.items() if dist == distance]
            for distance in range(self._max_distance+1)
        }
        
        return nodes_by_distance
    
    def run(self) -> dict:
        return self._run_analysis()
        