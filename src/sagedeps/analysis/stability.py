from typing import List
from sagedeps.deps.data import Data
from sagedeps.deps.model.dependency import Relation
from sagedeps.analysis.graph_analysis import GraphAnalyzer
from sagedeps.deps.filter import Filter, PathFilter
from sagedeps.deps.model.sageclass import SageClass

import networkx as nx
import numpy as np
from sknetwork.ranking import PageRank

class StabilityAnalyzer(GraphAnalyzer):
    def __init__(self, filter: Filter = PathFilter(), edge_types: List[Relation] | None = None):
        self._edge_types = edge_types
        self._classes = Data.get_classes_filtered(filter)

    def _class_metric(self, sage_class: SageClass):
        return sage_class.out_degree(self._edge_types)/ \
            (sage_class.out_degree(self._edge_types), sage_class.in_degree(self._edge_types))

    def _run_analysis(self) -> list:
        return [(sage_class, self._class_metric(sage_class)) for sage_class in self._classes]

    
        