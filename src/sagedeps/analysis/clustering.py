from typing import List
from sagedeps.analysis.graph_analysis import GraphAnalyzer
from sagedeps.deps.filter import Filter, PathFilter

import networkx as nx
from sagedeps.deps.model.dependency import Relation

class ClusteringAnalyzer(GraphAnalyzer):
    def __init__(self, filter: Filter = PathFilter(), edge_types: List[Relation] | None = None):
        super().__init__(filter, edge_types=edge_types, weight_by_strength=True)

    def _run_analysis(self) -> list:
        scores = nx.clustering(self._graph)
        return [(scid, scores[scid]) for scid in self._ids]
