import json

from constants import *
from deps.data import Filter
from deps.model.module import File, Module
from deps.parser import Parser
from deps.loader import Loader
from deps.data import Data
from deps.analysis import create_class_digraph, create_module_digraph, create_graph_json

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

def testing():
    Loader.initialize()
    sc = Data.get_class("sage.homology.chains.Cochains")
    print(sc._module.full_path_name)
    print(sc._module._imported_classes)
    print(sc._module.get_import_map())
    print(sc._module.get_import_map(visited=set()))
    print(sc._dependencies)

def default_scorer():
    """
    If in .all import: +50 score
    For each node (incoming or outgoing) +1 score

    Module score = max of child score
    """
    for module in Data.get_modules_filtered(Filter()):
        if module.full_path_name.endswith("all"):
            if not isinstance(module, File):
                continue
            for imported_item in module.get_import_map().values():
                imported_item.set_score(50)
    
    for sage_class in Data.get_classes_filtered(Filter()):
        sage_class.set_score(sage_class.get_score + sage_class.in_degree + sage_class.out_degree)
    
    for module in Data.get_modules_filtered(Filter()):
        module.set_score(max([0] + [sage_class.get_score for sage_class in module.get_classes()]))

if __name__ == "__main__":
    #create_module_class_map()
    #create_import_map()
    #test_loading()
    #create_dependencies()
    #testing()
    #show_graph()
    Loader.initialize(scorer=default_scorer)
    create_graph_json(min_in = 1, min_out = 1, excludes=["toy", "example", "lazy_import"], path="sage.rings")
