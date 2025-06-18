import json

from constants import *
from parser import Parser
from loader import Loader
from data import Data

def create_module_class_map():
    class_map = Parser.create_python_module_class_map()
    class_map_json = json.dumps(class_map, indent=4)
    with open(MODULE_JSON_SRC, "w") as f: 
        f.write(class_map_json)

def create_import_map():
    Loader.initialize()
    import_map = Loader.dump_import_map()
    for key, value in import_map.items():
        print(key)
        print(value)
        print()
    with open(IMPORT_MAP_SRC, "w") as f: 
        f.write(json.dumps(import_map, indent=4))

def test_loading():
    Loader.load_all_modules()
    Loader.load_all_classes()
    print(Data.classes)

if __name__ == "__main__":
    #create_module_class_map()
    create_import_map()
    #test_loading()