import json

from typing import Type

from analysis import (
    GraphAnalyzer,
    BetweennessAnalyzer, ClusteringAnalyzer, CyclesAnalyzer, PageRankAnalyzer, StabilityAnalyzer
)
from constants import *
from deps.model.dependency import Relation
from deps.model.module import File, Module
from deps.parser import Parser
from deps.loader import Loader
from deps.data import Data
from deps.graphics import create_class_digraph, create_module_digraph, create_graph_json
from deps.score import DefaultScorer
from deps.filter import PathFilter, MinFanIn, MinFanOut, Or, Not, NameContains, ScoreFilter, Balance, Filter

def create_module_class_map(testing=False):
    class_map = Parser.create_python_module_class_map(list_symbols=not testing)
    class_map_json = json.dumps(class_map, indent=4)
    with open(MODULE_JSON_SRC_TEST if testing else MODULE_JSON_SRC, "w") as f: 
        f.write(class_map_json)

def create_import_map():
    Loader.initialize()
    import_map = Loader.dump_import_map(split=True)
    with open(IMPORT_MAP_SRC, "w") as f: 
        f.write(json.dumps(import_map, indent=4))

def create_dependencies():
    Loader.initialize()
    dependencies_map = Loader.dump_dependencies()
    dependencies_map_json = json.dumps(dependencies_map, indent=4)
    with open(DEPENDENCIES_JSON, "w") as f:
        f.write(dependencies_map_json)
    
def show_module_graph(depth=3, path="sage"):
    Loader.initialize()
    create_module_digraph(depth=depth, path=path)

def test_loading():
    Loader.load_all_modules()
    Loader.load_all_classes()
    print(Data.classes)

def generate_graph():
    Loader.initialize(scorer=DefaultScorer())
    general_filter = MinFanOut(1).add(MinFanIn(1)).add(
        Not(
            NameContains("toy"),
            NameContains("example"),
            NameContains("lazy_import"),
            NameContains("test")
        )
    )

    create_graph_json(
        Balance(
            lambda x: x.get_score,
            500,
            None,
            PathFilter("sage.rings").add(general_filter),
            PathFilter("sage.combinat").add(general_filter),
            Not(
                PathFilter("sage.rings").add(general_filter),
                PathFilter("sage.combinat").add(general_filter),
            )
        )
    )

def run_graph_analysis(analyzer_cls: Type[GraphAnalyzer], filter: Filter = PathFilter(), edge_types = None):
    Loader.initialize()
    analyzer = analyzer_cls(filter, edge_types)
    print(analyzer.run())

if __name__ == "__main__":
    create_module_class_map(testing=False)
    #create_import_map()
    #test_loading()
    #create_dependencies()
    #testing()
    #show_graph()
    #Loader.initialize(scorer=DefaultScorer())
    generate_graph()
    #run_graph_analysis(CyclesAnalyzer, edge_types=[Relation.INHERITANCE,Relation.CLASS_ATTRIBUTE,Relation.DECLARED_TOP_IMPORT,])

    #print(Loader.get_doc_urls(Data.get_class("sage.rings.polynomial.multi_polynomial_ideal.MPolynomialIdeal")))
