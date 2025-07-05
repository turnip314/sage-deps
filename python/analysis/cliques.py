from typing import List

from analysis.graph_analysis import GraphAnalyzer
from deps.filter import Filter, PathFilter
from deps.model.sageclass import SageClass

import networkx as nx
import time
import random
import itertools

from deps.model.dependency import Relation

class CyclesAnalyzer(GraphAnalyzer):
    def __init__(
            self, 
            filter: Filter = PathFilter(),
            min_size: int = 2,
            max_size: int = 3,
            edge_types: List[Relation] | None = None, 
            **kwargs
        ):
        super().__init__(filter, edge_types=edge_types, weight_by_strength=False)

        self._time_limit = kwargs.get("time_limit", 120)
        self._min_size = min_size
        self._max_size = max_size
    
    def _run_clique_search(self):
        t = time.monotonic()
        cliques = []
        for size in range(self._min_size, self._max_size+1):
            for sublist in itertools.combinations(self._ids, size):
                if all(
                    [
                        n1 in self._graph.neighbors(n2) and n2 in self._graph.neighbors(n1)
                        for n1, n2 in itertools.combinations(sublist, 2)
                    ]
                ):
                    cliques.append(sublist)
                if time.monotonic() - t >= self._time_limit:
                    print("Halting execution - time limit exceeded.")
                    break
        return cliques


    def _run_analysis(self) -> list:
        return self._run_clique_search()
    
        # Finding all cycles is too slow for any reasonably large graph
        #cycles = nx.simple_cycles(self._graph)
        #return [(cycle, len(cycle)) for cycle in cycles]


        