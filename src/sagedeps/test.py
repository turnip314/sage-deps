import json

from typing import Type

from sagedeps.analysis import *
from sagedeps.constants import *
from sagedeps.deps.model.dependency import Relation
from sagedeps.deps.model.module import File, Module
from sagedeps.deps.parser import Parser
from sagedeps.deps.loader import Loader
from sagedeps.deps.data import Data
from sagedeps.deps.graphics import create_class_digraph, create_module_digraph, create_graph_json
from sagedeps.deps.score import DefaultScorer
from sagedeps.deps.filter import PathFilter, MinFanIn, MinFanOut, Or, Not, NameContains, EmptyFilter, Balance, Filter

def create_module_class_map(testing=False):
    class_map = Parser.create_python_module_class_map(list_symbols=not testing)
    class_map_json = json.dumps(class_map, indent=4)
    with open(MODULE_JSON_SRC_TEST if testing else MODULE_JSON_SRC, "w") as f: 
        f.write(class_map_json)

def create_import_map():
    import_map = Loader.dump_import_map(split=True)
    with open(IMPORT_MAP_SRC, "w+") as f: 
        f.write(json.dumps(import_map, indent=4))

def create_dependencies():
    dependencies_map = Loader.dump_dependencies()
    dependencies_map_json = json.dumps(dependencies_map, indent=4)
    with open(DEPENDENCIES_JSON, "w+") as f:
        f.write(dependencies_map_json)
    
def show_module_graph(depth=3, path="sage"):
    create_module_digraph(depth=depth, path=path)

def test_loading():
    print(Data.classes)

def generate_graph():
    general_filter = Or(
        MinFanOut(1),
        MinFanIn(1)
    ).add(
        Not(
            NameContains("toy"),
            NameContains("example"),
            NameContains("lazy_import"),
            NameContains("test")
        )
    )

    result = create_graph_json(
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

    with open(GRAPH_JSON, "w") as f:
        f.write(json.dumps(result, indent=4))

def run_graph_analysis(analyzer: GraphAnalyzer):
    print(analyzer.run())

if __name__ == "__main__":
    #create_module_class_map(testing=False)
    Loader.initialize(scorer=DefaultScorer())
    #create_import_map()
    #test_loading()
    #create_dependencies()
    #testing()
    #show_graph()
    #Loader.initialize(scorer=DefaultScorer())
    #generate_graph()
    #run_graph_analysis(CyclesAnalyzer(
    #        start_node=Data.get_class("sage.rings.polynomial.multi_polynomial_ideal.MPolynomialIdeal")))

    run_graph_analysis(
        DistanceAnalyzer(
            starting_node = "sage.rings.rational_field.RationalField",
            max_distance=5,
            filter=EmptyFilter(),
            edge_types=[Relation.INHERITANCE],
            direction="up"
        )
    )
    #print(Loader.get_doc_urls(Data.get_class("sage.rings.polynomial.multi_polynomial_ideal.MPolynomialIdeal")))
