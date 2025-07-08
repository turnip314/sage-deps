from typing import List

from analysis.graph_analysis import GraphAnalyzer
from deps.filter import Filter, PathFilter
from deps.model.sageclass import SageClass

import networkx as nx
import time

from deps.model.dependency import Relation

class CyclesAnalyzer(GraphAnalyzer):
    def __init__(
            self, 
            filter: Filter = PathFilter(), 
            edge_types: List[Relation] | None = None, 
            start_node: SageClass | None = None,
            **kwargs
        ):
        super().__init__(filter, edge_types=edge_types, weight_by_strength=False)
        self._start_node = start_node.full_path_name if start_node is not None else None

        self._time_limit = kwargs.get("time_limit", 120)
        self._max_breadth = kwargs.get("max_breadth", 10000)
        self._depth_first = kwargs.get("depth_first", True)
    
    def _run_cycle_search(self):
        t = time.monotonic()
        cycles = []
        paths: List[List[str]]
        paths = [[self._start_node]]
        while len(paths) > 0:
            if self._depth_first:
                cur_path = paths.pop()
            else:
                cur_path = paths.pop(0)
            next_nodes = self._graph.neighbors(cur_path[-1])
            #print(list(next_nodes))
            #return
            for node in next_nodes:
                if node not in cur_path:
                    paths.append(cur_path + [node])
                elif node == self._start_node:
                    cycles.append(cur_path + [node])

            paths = paths[:self._max_breadth]
            if time.monotonic() - t > self._time_limit:
                print("Halting execution - time limit exceeded.")
                break

        return cycles

    def _run_analysis(self) -> list:
        if self._start_node is None:
            return [(nx.find_cycle(self._graph), 0)]
        return self._run_cycle_search()
    
        # Finding all cycles is too slow for any reasonably large graph
        #cycles = nx.simple_cycles(self._graph)
        #return [(cycle, len(cycle)) for cycle in cycles]


        