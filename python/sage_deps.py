import json

from constants import *
from deps.model.module import File, Module
from deps.parser import Parser
from deps.loader import Loader
from deps.data import Data
from deps.graphics import create_class_digraph, create_module_digraph, create_graph_json
from deps.score import DefaultScorer
from deps.filter import PathFilter, MinFanIn, MinFanOut, Or, Not, NameContains, ScoreFilter, Balance

def create_module_class_map():
    class_map = Parser.create_python_module_class_map()
    class_map_json = json.dumps(class_map, indent=4)
    with open(MODULE_JSON_SRC, "w") as f: 
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
            300,
            None,
            PathFilter("sage.rings").add(general_filter),
            PathFilter("sage.combinat").add(general_filter),
            Not(
                PathFilter("sage.rings").add(general_filter),
                PathFilter("sage.combinat").add(general_filter),
            )
        )
    )

if __name__ == "__main__":
    #create_module_class_map()
    #create_import_map()
    #test_loading()
    #create_dependencies()
    #testing()
    #show_graph()
    Loader.initialize(scorer=DefaultScorer())
    generate_graph()

    #print(Loader.get_doc_urls(Data.get_class("sage.rings.polynomial.multi_polynomial_ideal.MPolynomialIdeal")))
