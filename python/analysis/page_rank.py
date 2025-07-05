from typing import List
from deps.data import Data
from analysis.graph_analysis import GraphAnalyzer
from deps.filter import Filter, PathFilter
from deps.model.sageclass import SageClass


import numpy as np
from sknetwork.ranking import PageRank

from deps.model.dependency import Relation

class PageRankAnalyzer(GraphAnalyzer):
    def __init__(self, filter: Filter = PathFilter(), edge_types: List[Relation] | None = None):
        super().__init__(filter, edge_types=edge_types, weight_by_strength=True)

    def _run_analysis(self) -> list:
        pagerank = PageRank()
        scores = pagerank.fit_predict(self._adjacency_matrix)
        return [(scid, score) for scid, score in zip(self._ids, scores)]
        