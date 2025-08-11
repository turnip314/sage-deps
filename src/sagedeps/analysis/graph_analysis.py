from typing import List

from sagedeps.deps.data import Data
from sagedeps.deps.filter import Filter, EmptyFilter
from sagedeps.deps.model.sageclass import SageClass
from sagedeps.deps.model.dependency import Relation
import numpy as np
import random
from scipy import sparse
import networkx as nx

class GraphAnalyzer:
    def __init__(
            self,
            filter: Filter = EmptyFilter(),
            weight_by_strength=True,
            edge_types: List[Relation] | None = None,
            weights = None
        ):

        if edge_types is None:
            edge_types = list([
                Relation.INHERITANCE, 
                Relation.CLASS_ATTRIBUTE, 
                Relation.DECLARED_TOP_IMPORT, 
                Relation.DECLARED_SUB_IMPORT
            ])

        classes = Data.get_classes_filtered(filter)
        adj = np.zeros((len(classes), len(classes)))

        self._ids = [sc.full_path_name for sc in classes]

        if weights is not None:
            weights_map = {
                rel: w for rel, w in zip(edge_types or range(6), weights)
            }
        elif weight_by_strength:
            weights_map = {
                rel: rel for rel in edge_types or range(6)
            }
        else:
            weights_map = {
                rel: 1 for rel in edge_types or range(6)
            }

        sage_class: SageClass
        for sage_class in classes:
            for dep in sage_class.get_dependencies(edge_types):
                if dep.target.full_path_name in self._ids:
                    source_idx = self._ids.index(sage_class.full_path_name)
                    dest_idx = self._ids.index(dep.target.full_path_name)
                    weight = weights_map[dep.relation]
                    adj[source_idx, dest_idx] = weight
        
        self._adjacency_matrix = sparse.csr_matrix(adj)

        G = nx.DiGraph()

        sage_class: SageClass
        for sage_class in classes:
            G.add_node(sage_class.full_path_name)

        for sage_class in classes:
            for dep in sage_class.get_dependencies(edge_types):
                if dep.target.full_path_name in self._ids:
                    G.add_edge(
                        sage_class.full_path_name,
                        dep.target.full_path_name, 
                        weight = 1 if not weight_by_strength else dep.relation + 1, 
                    )
        
        self._graph = G

    def _run_analysis(self) -> list:
        raise Exception("Not implemented.")

    def run(self, ascending = False):
        results = self._run_analysis()
        results.sort(reverse = not ascending, key = lambda x: x[1])

        return results
