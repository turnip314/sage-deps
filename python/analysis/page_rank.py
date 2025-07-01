from deps.data import Data
from analysis.graph_analysis import GraphAnalyzer
from deps.filter import Filter, PathFilter
from deps.model.sageclass import SageClass


import numpy as np
from sknetwork.ranking import PageRank

class PageRankAnalyzer(GraphAnalyzer):
    def __init__(self, filter: Filter = PathFilter()):
        super().__init__(filter, weight_by_strength=True)

    def _run_analysis(self) -> list:
        pagerank = PageRank()
        scores = pagerank.fit_predict(self._adjacency_matrix)
        return [(scid, score) for scid, score in zip(self._ids, scores)]
        