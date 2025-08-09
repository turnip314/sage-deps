from typing import List

from sagedeps.analysis.graph_analysis import GraphAnalyzer
from sagedeps.deps.filter import Filter, PathFilter
from sagedeps.deps.model.sageclass import SageClass

import networkx as nx
import time
import random
import itertools

from sagedeps.deps.model.dependency import Relation

class CliquesAnalyzer(GraphAnalyzer):
    def __init__(
            self, 
            filter: Filter = PathFilter(),
            size: int = 2,
            edge_types: List[Relation] | None = None
        ):
        super().__init__(filter, edge_types=edge_types, weight_by_strength=False)
        self._size = size
    
    def _run_clique_search(self, size):
        if size > 1:
            sub_cliques = self._run_clique_search(size-1)
        else:
            return [(_id,) for _id in self._ids]
        cliques = []
        for subnodes in sub_cliques:
            for newnode in self._ids:
                if newnode not in subnodes and all(
                    [
                        n1 in self._graph.neighbors(n2) and n2 in self._graph.neighbors(n1)
                        for n1, n2 in itertools.combinations(list(subnodes) + [newnode], 2)
                    ]
                ):
                    cliques.append(tuple(sorted(list(subnodes) + [newnode])))
        
        return list(set(cliques))


    def _run_analysis(self) -> list:
        return self._run_clique_search(self._size)


        