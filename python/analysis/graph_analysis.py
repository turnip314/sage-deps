from deps.data import Data
from deps.filter import Filter, PathFilter
from deps.model.sageclass import SageClass
import networkx as nx
import random

class GraphAnalyzer:
    def __init__(self, filter: Filter = PathFilter()):
        G = nx.DiGraph()
        classes = Data.get_classes_filtered(filter)
        
        sage_class: SageClass
        for sage_class in classes:
            G.add_node(hash(sage_class))

        for sage_class in classes:
            for dep in sage_class.get_dependencies():
                G.add_edge(
                    hash(sage_class),
                    hash(dep.target), 
                    #relation = dep.relation, 
                    #color = relation_to_colour(dep.relation)
                )
        
        self._graph = G

    def _run_analysis(self):
        raise Exception("Not implemented.")

    def run(self, ascending = False):
        results = self._run_analysis()
        results.sort(reversed = not ascending)

        return results
    
    def analyze_stability(self, ascending=False):
        pass

    def analyze_distance_from_main_sequence(self):
        pass

    def analyze_cycles(self):
        pass

    def analyze_cohesion(self):
        pass

    def analyze_centrality(self):
        pass